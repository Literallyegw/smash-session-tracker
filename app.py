# app.py

import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from PIL import Image, ImageTk

from constants import GAME_DATA, MATCH_TYPES, EXCEL_FILE, STAGE_ASSETS
import storage

STAGE_THUMB_SIZE = (80, 50)

import sys


def get_base_path():
    """Επιστρέφει το path είτε τρέχει ως κανονικό script είτε ως PyInstaller .exe"""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def load_stage_image(game_code: str, stage_name: str):
    subfolder = "ssbm" if game_code == "SSBM" else "ssbu"
    filename = STAGE_ASSETS.get(game_code, {}).get(stage_name, "")

    base_dir = get_base_path()
    img_path = os.path.join(base_dir, "assets", "stages", subfolder, filename)

    if os.path.exists(img_path):
        try:
            pil_img = Image.open(img_path).convert("RGBA")
            pil_img = pil_img.resize(STAGE_THUMB_SIZE, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_img)
        except Exception:
            return None
    return None


class SmashSessionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smash Session Tracker & Telemetry")
        self.geometry("900x700")
        self.minsize(840, 620)

        # 1. Config & State
        self.config_data = storage.load_config()
        initial_game = self.config_data.get("last_game", "SSBU")
        self.current_game_var = tk.StringVar(value=initial_game)

        self.stage_check_vars = {}
        self.stage_images = {}  # References για να μην σβήνονται οι εικόνες από τον garbage collector
        self.all_current_records = []

        # 2. Tabs Container
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Log Session
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text=" 📝 Log Session ")
        self.build_log_tab()

        # Tab 2: Sessions & Search History
        self.tab_search = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_search, text=" 🔍 Sessions & History ")
        self.build_search_tab()

        # Tab 3: Analytics & Winrate Breakdown
        self.tab_analytics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analytics, text=" 📊 Analytics & Winrates ")
        self.build_analytics_tab()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.update_game_state(initial_game, is_startup=True)

    # ================= TAB 1: LOG SESSION =================
    def build_log_tab(self):
        top_frame = ttk.LabelFrame(self.tab_log, text="Player & Game Setup", padding=(15, 8))
        top_frame.pack(fill="x", padx=20, pady=(10, 4))

        ttk.Label(top_frame, text="My Tag:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 5))
        self.user_tag_var = tk.StringVar(value=self.config_data.get("user_tag", "Player"))
        user_tag_entry = ttk.Entry(top_frame, textvariable=self.user_tag_var, width=15)
        user_tag_entry.pack(side="left", padx=(0, 15))
        self.user_tag_var.trace_add("write", lambda *args: storage.update_preferences(user_tag=self.user_tag_var.get()))

        ttk.Separator(top_frame, orient="vertical").pack(side="left", fill="y", padx=15)

        ttk.Radiobutton(
            top_frame,
            text=GAME_DATA["SSBU"]["display_name"],
            variable=self.current_game_var,
            value="SSBU",
            command=self.on_game_switched
        ).pack(side="left", padx=10)

        ttk.Radiobutton(
            top_frame,
            text=GAME_DATA["SSBM"]["display_name"],
            variable=self.current_game_var,
            value="SSBM",
            command=self.on_game_switched
        ).pack(side="left", padx=10)

        form_frame = ttk.LabelFrame(self.tab_log, text="Session Details", padding=(15, 8))
        form_frame.pack(fill="x", padx=20, pady=4)

        ttk.Label(form_frame, text="Match Type:").grid(row=0, column=0, sticky="w", pady=4)
        self.match_type_var = tk.StringVar(value=MATCH_TYPES[0])
        type_cb = ttk.Combobox(form_frame, textvariable=self.match_type_var, values=MATCH_TYPES, state="readonly", width=18)
        type_cb.grid(row=0, column=1, sticky="w", padx=10, pady=4)

        ttk.Label(form_frame, text="My Character:").grid(row=0, column=2, sticky="w", pady=4, padx=(20, 0))
        self.my_char_var = tk.StringVar()
        self.my_char_cb = ttk.Combobox(form_frame, textvariable=self.my_char_var, width=20)
        self.my_char_cb.grid(row=0, column=3, sticky="w", padx=10, pady=4)

        ttk.Label(form_frame, text="Opponent Tag:").grid(row=1, column=0, sticky="w", pady=4)
        self.opp_tag_var = tk.StringVar()
        self.opp_tag_cb = ttk.Combobox(form_frame, textvariable=self.opp_tag_var, width=18)
        self.opp_tag_cb.grid(row=1, column=1, sticky="w", padx=10, pady=4)

        ttk.Label(form_frame, text="Opponent Character:").grid(row=1, column=2, sticky="w", pady=4, padx=(20, 0))
        self.opp_char_var = tk.StringVar()
        self.opp_char_cb = ttk.Combobox(form_frame, textvariable=self.opp_char_var, width=20)
        self.opp_char_cb.grid(row=1, column=3, sticky="w", padx=10, pady=4)

        score_frame = ttk.Frame(form_frame)
        score_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=6)

        ttk.Label(score_frame, text="Games Won:").pack(side="left", padx=(0, 5))
        self.won_var = tk.IntVar(value=0)
        sp_won = ttk.Spinbox(score_frame, from_=0, to=99, width=5, textvariable=self.won_var, command=self.update_total_games_label)
        sp_won.pack(side="left", padx=(0, 15))

        ttk.Label(score_frame, text="Games Lost:").pack(side="left", padx=(0, 5))
        self.lost_var = tk.IntVar(value=0)
        sp_lost = ttk.Spinbox(score_frame, from_=0, to=99, width=5, textvariable=self.lost_var, command=self.update_total_games_label)
        sp_lost.pack(side="left", padx=(0, 15))

        self.total_lbl = ttk.Label(score_frame, text="Total Games: 0", font=("Arial", 9, "bold"), foreground="#1976d2")
        self.total_lbl.pack(side="left", padx=(10, 0))

        mental_frame = ttk.Frame(form_frame)
        mental_frame.grid(row=3, column=0, columnspan=4, sticky="w", pady=4)

        ttk.Label(mental_frame, text="Mental (1-10):").pack(side="left", padx=(0, 10))
        self.mental_var = tk.IntVar(value=7)
        mental_slider = ttk.Scale(
            mental_frame, from_=1, to=10, variable=self.mental_var, orient="horizontal", length=180,
            command=lambda v: self.mental_val_lbl.config(text=str(round(float(v))))
        )
        mental_slider.pack(side="left", padx=(0, 10))

        self.mental_val_lbl = ttk.Label(mental_frame, text="7", font=("Arial", 9, "bold"), foreground="#388e3c")
        self.mental_val_lbl.pack(side="left")

        # Stages Checkbox / Image Card Area
        self.stages_group = ttk.LabelFrame(self.tab_log, text="Stages I Lost In (Click to toggle loss)", padding=(10, 6))
        self.stages_group.pack(fill="both", expand=True, padx=20, pady=4)

        self.stages_inner_frame = ttk.Frame(self.stages_group)
        self.stages_inner_frame.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(self.tab_log)
        btn_frame.pack(pady=4)

        ttk.Button(btn_frame, text="💾 Save Session", command=self.on_save_session).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="↩️ Undo Last", command=self.on_undo_session).pack(side="left", padx=6)

        self.status_lbl = ttk.Label(self.tab_log, text="", font=("Arial", 9, "italic"))
        self.status_lbl.pack(pady=(0, 4))

    # ================= TAB 2: SESSIONS & SEARCH =================
    def build_search_tab(self):
        top_bar = ttk.Frame(self.tab_search, padding=(12, 8))
        top_bar.pack(fill="x")

        ttk.Label(top_bar, text="Game:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 4))
        self.viewer_game_var = tk.StringVar(value=self.current_game_var.get())
        self.viewer_game_cb = ttk.Combobox(top_bar, textvariable=self.viewer_game_var, values=["SSBU", "SSBM"], state="readonly", width=8)
        self.viewer_game_cb.pack(side="left", padx=(0, 12))
        self.viewer_game_cb.bind("<<ComboboxSelected>>", lambda e: self.load_viewer_data())

        ttk.Label(top_bar, text="🔍 Search:").pack(side="left", padx=(0, 4))
        self.search_query_var = tk.StringVar()
        self.search_query_var.trace_add("write", self.apply_filter)
        ttk.Entry(top_bar, textvariable=self.search_query_var, width=22).pack(side="left", padx=(0, 10))

        ttk.Button(top_bar, text="🔄 Reload", command=self.load_viewer_data).pack(side="left", padx=4)
        ttk.Button(top_bar, text="📊 Open Excel", command=self.open_excel_externally).pack(side="right", padx=4)

        table_frame = ttk.Frame(self.tab_search, padding=(12, 0))
        table_frame.pack(fill="both", expand=True)

        cols = ("type", "date", "my_tag", "my_char", "opponent", "character", "score", "mental", "stages_lost")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("type", text="Type")
        self.tree.heading("date", text="Date")
        self.tree.heading("my_tag", text="My Tag")
        self.tree.heading("my_char", text="My Char")
        self.tree.heading("opponent", text="Opponent")
        self.tree.heading("character", text="Opp Char")
        self.tree.heading("score", text="Score (W-L)")
        self.tree.heading("mental", text="Mental")
        self.tree.heading("stages_lost", text="Stages Lost In")

        self.tree.column("type", width=85, anchor="center")
        self.tree.column("date", width=85, anchor="center")
        self.tree.column("my_tag", width=80, anchor="center")
        self.tree.column("my_char", width=90, anchor="center")
        self.tree.column("opponent", width=95, anchor="center")
        self.tree.column("character", width=95, anchor="center")
        self.tree.column("score", width=80, anchor="center")
        self.tree.column("mental", width=55, anchor="center")
        self.tree.column("stages_lost", width=220, anchor="w")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.tag_configure("positive", background="#e8f5e9")
        self.tree.tag_configure("negative", background="#ffebee")
        self.tree.tag_configure("even", background="#fffde7")

        self.metrics_lbl = ttk.Label(self.tab_search, text="", font=("Arial", 9, "bold"), padding=(12, 6))
        self.metrics_lbl.pack(fill="x")

    # ================= TAB 3: ANALYTICS & WINRATES =================
    def build_analytics_tab(self):
        ctrl_bar = ttk.Frame(self.tab_analytics, padding=(12, 10))
        ctrl_bar.pack(fill="x")

        ttk.Label(ctrl_bar, text="Game:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 4))
        self.analytics_game_var = tk.StringVar(value=self.current_game_var.get())
        cb_game = ttk.Combobox(ctrl_bar, textvariable=self.analytics_game_var, values=["SSBU", "SSBM"], state="readonly", width=8)
        cb_game.pack(side="left", padx=(0, 15))
        cb_game.bind("<<ComboboxSelected>>", lambda e: self.calculate_and_render_analytics())

        ttk.Label(ctrl_bar, text="Analysis Metric:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 4))
        self.analysis_mode_var = tk.StringVar(value="Matchup (vs Character)")
        self.mode_cb = ttk.Combobox(
            ctrl_bar,
            textvariable=self.analysis_mode_var,
            values=[
                "Matchup (vs Character)",
                "Opponent (vs Player Tag)",
                "Stage Breakdown (Losses)",
                "Stage vs Character"
            ],
            state="readonly",
            width=26
        )
        self.mode_cb.pack(side="left", padx=(0, 12))
        self.mode_cb.bind("<<ComboboxSelected>>", lambda e: self.calculate_and_render_analytics())

        ttk.Button(ctrl_bar, text="🔄 Recalculate", command=self.calculate_and_render_analytics).pack(side="left", padx=4)

        analytics_frame = ttk.Frame(self.tab_analytics, padding=(12, 0))
        analytics_frame.pack(fill="both", expand=True)

        self.analytics_tree = ttk.Treeview(analytics_frame, show="headings", selectmode="browse")
        scroll_an = ttk.Scrollbar(analytics_frame, orient="vertical", command=self.analytics_tree.yview)
        self.analytics_tree.configure(yscrollcommand=scroll_an.set)

        self.analytics_tree.pack(side="left", fill="both", expand=True)
        scroll_an.pack(side="right", fill="y")

        self.analytics_tree.tag_configure("high_win", background="#e8f5e9")
        self.analytics_tree.tag_configure("low_win", background="#ffebee")

        self.analytics_summary_lbl = ttk.Label(self.tab_analytics, text="", font=("Arial", 9, "italic"), padding=(12, 6))
        self.analytics_summary_lbl.pack(fill="x")

    # ================= LOGIC & CALCULATIONS =================
    def update_total_games_label(self):
        total = self.won_var.get() + self.lost_var.get()
        self.total_lbl.config(text=f"Total Games: {total}")

    def update_game_state(self, game_code, is_startup=False):
        game_info = GAME_DATA[game_code]
        self.my_char_cb["values"] = game_info["characters"]
        self.opp_char_cb["values"] = game_info["characters"]
        self.opp_tag_cb["values"] = self.config_data.get("known_opponents", [])

        saved_char_key = "last_char_ssbu" if game_code == "SSBU" else "last_char_ssbm"
        last_char = self.config_data.get(saved_char_key, "")
        self.my_char_var.set(last_char)
        self.opp_char_var.set("")

        # Καθαρισμός προηγούμενων widgets & εικόνων
        for widget in self.stages_inner_frame.winfo_children():
            widget.destroy()

        self.stage_check_vars.clear()
        self.stage_images.clear()

        # Grid διάταξη των visual stage cards
        for idx, stage in enumerate(game_info["stages"]):
            var = tk.BooleanVar(value=False)
            self.stage_check_vars[stage] = var

            img = load_stage_image(game_code, stage)
            if img:
                self.stage_images[stage] = img

            cb = ttk.Checkbutton(
                self.stages_inner_frame,
                text=stage,
                image=self.stage_images.get(stage),
                compound="top" if stage in self.stage_images else "none",
                variable=var,
                style="Toolbutton"
            )
            row = idx // 3
            col = idx % 3
            cb.grid(row=row, column=col, padx=8, pady=4, sticky="nsew")

        self.viewer_game_var.set(game_code)
        self.analytics_game_var.set(game_code)

    def on_game_switched(self):
        new_game = self.current_game_var.get()
        self.update_game_state(new_game)
        storage.update_preferences(game=new_game)

    def on_save_session(self):
        my_tag = self.user_tag_var.get().strip()
        my_char = self.my_char_var.get().strip()
        opp_tag = self.opp_tag_var.get().strip()
        opp_char = self.opp_char_var.get().strip()

        if not my_tag:
            messagebox.showwarning("Missing Tag", "Συμπλήρωσε το δικό σου Tag!")
            return
        if not my_char:
            messagebox.showwarning("Missing Character", "Επίλεξε τον δικό σου χαρακτήρα!")
            return
        if not opp_tag or not opp_char:
            messagebox.showwarning("Incomplete Opponent", "Συμπλήρωσε το Tag και τον χαρακτήρα του αντιπάλου!")
            return

        won = self.won_var.get()
        lost = self.lost_var.get()
        if won + lost == 0:
            messagebox.showwarning("Zero Games", "Τα Total Games δεν μπορούν να είναι 0!")
            return

        lost_stages_dict = {stage: var.get() for stage, var in self.stage_check_vars.items()}
        game = self.current_game_var.get()
        match_type = self.match_type_var.get()
        mental = round(float(self.mental_var.get()))

        try:
            date_str = storage.save_session(
                game=game,
                match_type=match_type,
                my_tag=my_tag,
                my_char=my_char,
                opp_tag=opp_tag,
                opp_char=opp_char,
                games_won=won,
                games_lost=lost,
                mental=mental,
                lost_stages_dict=lost_stages_dict
            )

            self.config_data = storage.update_preferences(
                game=game,
                user_tag=my_tag,
                my_char=my_char,
                new_opponent=opp_tag
            )
            self.opp_tag_cb["values"] = self.config_data.get("known_opponents", [])

            self.status_lbl.config(text=f"✅ [{game}] Saved session: {my_tag} ({my_char}) vs {opp_tag} ({opp_char}) — {won}W/{lost}L")

            self.opp_tag_var.set("")
            self.opp_char_var.set("")
            self.won_var.set(0)
            self.lost_var.set(0)
            self.update_total_games_label()
            for var in self.stage_check_vars.values():
                var.set(False)

        except PermissionError as e:
            messagebox.showerror("File In Use", str(e))

    def on_undo_session(self):
        game = self.current_game_var.get()
        if messagebox.askyesno("Confirm Undo", f"Θέλεις να διαγραφεί το τελευταίο session από το sheet '{game}';"):
            try:
                if storage.delete_last_session(game):
                    self.status_lbl.config(text=f"↩️ Το τελευταίο session του {game} διαγράφηκε.")
                    if self.notebook.index(self.notebook.select()) == 1:
                        self.load_viewer_data()
                    elif self.notebook.index(self.notebook.select()) == 2:
                        self.calculate_and_render_analytics()
                else:
                    messagebox.showinfo("Undo", "Δεν υπάρχουν εγγραφές προς διαγραφή.")
            except PermissionError as e:
                messagebox.showerror("File In Use", str(e))

    def on_tab_changed(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 1:
            self.load_viewer_data()
        elif idx == 2:
            self.calculate_and_render_analytics()

    def load_viewer_data(self):
        target_game = self.viewer_game_var.get()
        try:
            self.all_current_records = storage.load_sessions(target_game)
            self.apply_filter()
        except PermissionError as e:
            messagebox.showerror("File In Use", str(e))

    def apply_filter(self, *args):
        q = self.search_query_var.get().lower().strip()
        if not q:
            filtered = self.all_current_records
        else:
            filtered = [
                r for r in self.all_current_records
                if q in r.get("Opponent", "").lower()
                or q in r.get("Character", "").lower()
                or q in r.get("MyTag", "").lower()
                or q in r.get("MyChar", "").lower()
                or q in r.get("StagesLost", "").lower()
                or q in r.get("MatchType", "").lower()
            ]
        self.render_tree_view(filtered)

    def render_tree_view(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_won = 0
        total_lost = 0

        for r in records:
            won = int(r.get("Won", 0))
            lost = int(r.get("Lost", 0))
            total_won += won
            total_lost += lost

            if won > lost:
                tag = "positive"
            elif won < lost:
                tag = "negative"
            else:
                tag = "even"

            score_str = f"{won} - {lost}"
            self.tree.insert(
                "", "end",
                values=(
                    r.get("MatchType", ""),
                    r.get("Date", ""),
                    r.get("MyTag", ""),
                    r.get("MyChar", ""),
                    r.get("Opponent", ""),
                    r.get("Character", ""),
                    score_str,
                    r.get("Mental", ""),
                    r.get("StagesLost", "")
                ),
                tags=(tag,)
            )

        total_games = total_won + total_lost
        wr = (total_won / total_games * 100) if total_games > 0 else 0
        self.metrics_lbl.config(
            text=f"Showing: {len(records)} sessions | Total Games: {total_games} | Overall Score: {total_won}W - {total_lost}L | Win Rate: {wr:.1f}%"
        )

    # ================= ANALYTICS ENGINE =================
    def calculate_and_render_analytics(self):
        target_game = self.analytics_game_var.get()
        mode = self.analysis_mode_var.get()

        try:
            records = storage.load_sessions(target_game)
        except PermissionError as e:
            messagebox.showerror("File In Use", str(e))
            return

        for item in self.analytics_tree.get_children():
            self.analytics_tree.delete(item)

        if not records:
            self.analytics_summary_lbl.config(text=f"Δεν υπάρχουν καταγεγραμμένα sessions για το {target_game}.")
            return

        if mode == "Matchup (vs Character)":
            self.render_matchup_analytics(records)
        elif mode == "Opponent (vs Player Tag)":
            self.render_opponent_analytics(records)
        elif mode == "Stage Breakdown (Losses)":
            self.render_stage_analytics(records, target_game)
        elif mode == "Stage vs Character":
            self.render_stage_vs_char_analytics(records)

    def render_matchup_analytics(self, records):
        self.analytics_tree["columns"] = ("char", "sessions", "record", "total_games", "winrate")
        self.analytics_tree.heading("char", text="Opponent Character")
        self.analytics_tree.heading("sessions", text="Sessions")
        self.analytics_tree.heading("record", text="Games (W - L)")
        self.analytics_tree.heading("total_games", text="Total Games")
        self.analytics_tree.heading("winrate", text="Game Win Rate")

        self.analytics_tree.column("char", width=160, anchor="w")
        self.analytics_tree.column("sessions", width=100, anchor="center")
        self.analytics_tree.column("record", width=120, anchor="center")
        self.analytics_tree.column("total_games", width=100, anchor="center")
        self.analytics_tree.column("winrate", width=130, anchor="center")

        data = defaultdict(lambda: {"sessions": 0, "won": 0, "lost": 0})
        for r in records:
            char = r.get("Character", "Unknown")
            data[char]["sessions"] += 1
            data[char]["won"] += r.get("Won", 0)
            data[char]["lost"] += r.get("Lost", 0)

        sorted_chars = sorted(data.keys(), key=lambda c: (data[c]["won"] + data[c]["lost"]), reverse=True)

        for char in sorted_chars:
            w = data[char]["won"]
            l = data[char]["lost"]
            total = w + l
            wr = (w / total * 100) if total > 0 else 0
            tag = "high_win" if wr >= 50.0 else "low_win"

            self.analytics_tree.insert(
                "", "end",
                values=(char, data[char]["sessions"], f"{w} - {l}", total, f"{wr:.1f}%"),
                tags=(tag,)
            )

        self.analytics_summary_lbl.config(text=f"Υπολογίστηκαν {len(sorted_chars)} μοναδικά matchups.")

    def render_opponent_analytics(self, records):
        self.analytics_tree["columns"] = ("opp", "sessions", "record", "total_games", "winrate", "avg_mental")
        self.analytics_tree.heading("opp", text="Opponent Tag")
        self.analytics_tree.heading("sessions", text="Sessions")
        self.analytics_tree.heading("record", text="Games (W - L)")
        self.analytics_tree.heading("total_games", text="Total Games")
        self.analytics_tree.heading("winrate", text="Win Rate")
        self.analytics_tree.heading("avg_mental", text="Avg Mental")

        self.analytics_tree.column("opp", width=150, anchor="w")
        self.analytics_tree.column("sessions", width=90, anchor="center")
        self.analytics_tree.column("record", width=110, anchor="center")
        self.analytics_tree.column("total_games", width=100, anchor="center")
        self.analytics_tree.column("winrate", width=110, anchor="center")
        self.analytics_tree.column("avg_mental", width=100, anchor="center")

        data = defaultdict(lambda: {"sessions": 0, "won": 0, "lost": 0, "mental_sum": 0})
        for r in records:
            opp = r.get("Opponent", "Unknown")
            data[opp]["sessions"] += 1
            data[opp]["won"] += r.get("Won", 0)
            data[opp]["lost"] += r.get("Lost", 0)
            data[opp]["mental_sum"] += r.get("Mental", 0)

        sorted_opps = sorted(data.keys(), key=lambda o: (data[o]["won"] + data[o]["lost"]), reverse=True)

        for opp in sorted_opps:
            w = data[opp]["won"]
            l = data[opp]["lost"]
            total = w + l
            wr = (w / total * 100) if total > 0 else 0
            avg_m = (data[opp]["mental_sum"] / data[opp]["sessions"]) if data[opp]["sessions"] > 0 else 0
            tag = "high_win" if wr >= 50.0 else "low_win"

            self.analytics_tree.insert(
                "", "end",
                values=(opp, data[opp]["sessions"], f"{w} - {l}", total, f"{wr:.1f}%", f"{avg_m:.1f}/10"),
                tags=(tag,)
            )

        self.analytics_summary_lbl.config(text=f"Υπολογίστηκαν {len(sorted_opps)} μοναδικοί αντίπαλοι.")

    def render_stage_analytics(self, records, target_game):
        self.analytics_tree["columns"] = ("stage", "times_lost", "share")
        self.analytics_tree.heading("stage", text="Stage")
        self.analytics_tree.heading("times_lost", text="Sessions Lost In")
        self.analytics_tree.heading("share", text="% of Total Stage Loss Flags")

        self.analytics_tree.column("stage", width=220, anchor="w")
        self.analytics_tree.column("times_lost", width=150, anchor="center")
        self.analytics_tree.column("share", width=200, anchor="center")

        stage_losses = defaultdict(int)
        total_flags = 0

        for r in records:
            flags = r.get("StageFlags", {})
            for stage, was_lost in flags.items():
                if was_lost:
                    stage_losses[stage] += 1
                    total_flags += 1

        all_legal_stages = GAME_DATA[target_game]["stages"]
        sorted_stages = sorted(all_legal_stages, key=lambda s: stage_losses[s], reverse=True)

        for stage in sorted_stages:
            lost_count = stage_losses[stage]
            share = (lost_count / total_flags * 100) if total_flags > 0 else 0
            tag = "low_win" if lost_count > 0 else "high_win"

            self.analytics_tree.insert(
                "", "end",
                values=(stage, lost_count, f"{share:.1f}%"),
                tags=(tag,)
            )

        self.analytics_summary_lbl.config(text="Τα stages με τα περισσότερα losses προτείνονται για competitive bans.")

    def render_stage_vs_char_analytics(self, records):
        self.analytics_tree["columns"] = ("char", "stage", "times_lost")
        self.analytics_tree.heading("char", text="Opponent Character")
        self.analytics_tree.heading("stage", text="Stage Lost In")
        self.analytics_tree.heading("times_lost", text="Times Lost")

        self.analytics_tree.column("char", width=180, anchor="w")
        self.analytics_tree.column("stage", width=220, anchor="w")
        self.analytics_tree.column("times_lost", width=140, anchor="center")

        cross_data = defaultdict(int)
        for r in records:
            char = r.get("Character", "Unknown")
            flags = r.get("StageFlags", {})
            for stage, was_lost in flags.items():
                if was_lost:
                    cross_data[(char, stage)] += 1

        sorted_cross = sorted(cross_data.items(), key=lambda item: item[1], reverse=True)

        for (char, stage), count in sorted_cross:
            self.analytics_tree.insert(
                "", "end",
                values=(char, stage, count),
                tags=("low_win",)
            )

        self.analytics_summary_lbl.config(text="Αναλυτικός συσχετισμός stage losses ανά αντίπαλο χαρακτήρα.")

    def open_excel_externally(self):
        if not os.path.exists(EXCEL_FILE):
            messagebox.showinfo("No File", "Το αρχείο Excel δεν έχει δημιουργηθεί.")
            return
        sys_name = platform.system()
        if sys_name == "Windows":
            os.startfile(EXCEL_FILE)
        elif sys_name == "Darwin":
            subprocess.run(["open", EXCEL_FILE], check=False)
        else:
            subprocess.run(["xdg-open", EXCEL_FILE], check=False)


if __name__ == "__main__":
    app = SmashSessionApp()
    app.mainloop()