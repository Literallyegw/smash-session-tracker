from datetime import date
import os
import tkinter as tk
from tkinter import messagebox, ttk
import openpyxl

EXCEL_FILE = "game_database.xlsx"

STAGES = [
    "Battlefield",
    "Small Battlefield",
    "Yoshi's Story",
    "Final Destination",
    "Pokemon Stadium 2",
    "Smashville",
    "Town & City",
    "Hollow Bastion",
    "Kalos Pokemon League"
]

CHARACTERS = sorted([
    "Banjo & Kazooie", "Bayonetta", "Bowser", "Bowser Jr.", "Byleth",
    "Captain Falcon", "Chrom", "Cloud", "Corrin", "Daisy", "Dark Pit",
    "Dark Samus", "Diddy Kong", "Donkey Kong", "Dr. Mario", "Duck Hunt",
    "Falco", "Fox", "Ganondorf", "Greninja", "Hero", "Ice Climbers",
    "Ike", "Incineroar", "Inkling", "Isabelle", "Jigglypuff", "Joker",
    "Kazuya", "Ken", "King Dedede", "King K. Rool", "Kirby", "Link",
    "Little Mac", "Lucario", "Lucas", "Lucina", "Luigi", "Mario",
    "Marth", "Mega Man", "Meta Knight", "Mewtwo", "Mii Brawler",
    "Mii Gunner", "Mii Swordfighter", "Min Min", "Mr. Game & Watch",
    "Ness", "Olimar", "Pac-Man", "Palutena", "Peach", "Pichu",
    "Pikachu", "Piranha Plant", "Pit", "Pokemon Trainer", "Pyra/Mythra",
    "R.O.B.", "Richter", "Ridley", "Robin", "Rosalina & Luma", "Roy",
    "Ryu", "Samus", "Sephiroth", "Sheik", "Shulk", "Simon", "Snake",
    "Sonic", "Sora", "Steve", "Terry", "Toon Link", "Villager",
    "Wario", "Wii Fit Trainer", "Wolf", "Yoshi", "Young Link", "Zelda",
    "Zero Suit Samus"
])

def init_excel():
    """Initializes Excel with formatted headers if it doesn't exist."""
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sessions"

        # Headers with '{Stage} Loss' format
        headers = [
            "Type",
            "Date",
            "Opponent",
            "Character",
            "Total Games",
            "Games Won",
            "Games Lost",
            "Win Rate %",
            "Mental"
        ] + [f"{stage} Loss" for stage in STAGES]

        ws.append(headers)
        wb.save(EXCEL_FILE)

def append_session_to_excel(row_data):
    """Safely appends a row to the Excel file, catching PermissionError."""
    init_excel()
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        ws.append(row_data)
        wb.save(EXCEL_FILE)
        return True, None
    except PermissionError:
        return False, "Excel file is currently open!\nPlease close Excel and click save again."
    except Exception as e:
        return False, f"An error occurred: {e}"

def save_data():
    """Validates inputs and commits data to Excel."""
    opponent = entry_opponent.get().strip()
    character = combo_char.get().strip()

    if not opponent or not character:
        messagebox.showwarning("Missing Information", "Please fill in both Opponent and Character!")
        return

    try:
        won_g = int(entry_won.get().strip())
        lost_g = int(entry_lost.get().strip())
        mental_val = int(spin_mental.get().strip())

        if won_g < 0 or lost_g < 0:
            messagebox.showerror("Invalid Score", "Wins and losses cannot be negative!")
            return

        total_g = won_g + lost_g
        if total_g == 0:
            messagebox.showerror("Invalid Session", "Total games must be greater than 0!")
            return

        win_rate = round((won_g / total_g) * 100, 1)

    except ValueError:
        messagebox.showerror("Value Error", "Games and Mental fields must be integers!")
        return

    stage_losses = [stage_vars[stage].get() for stage in STAGES]
    today = date.today().strftime("%Y-%m-%d")

    row_data = [
        combo_ranked.get(),
        today,
        opponent,
        character,
        total_g,
        won_g,
        lost_g,
        win_rate,
        mental_val
    ] + stage_losses

    success, error_msg = append_session_to_excel(row_data)

    if not success:
        messagebox.showerror("Save Failed", error_msg)
        return

    messagebox.showinfo("Success", f"Session saved!\nTotal: {total_g} | Win Rate: {win_rate}%")

    # Clear fields
    entry_opponent.delete(0, tk.END)
    combo_char.set("")
    entry_won.delete(0, tk.END)
    entry_lost.delete(0, tk.END)
    lbl_live_calc.config(text="Total: 0 | Win Rate: 0.0%")
    for var in stage_vars.values():
        var.set(0)

def update_live_calc(*_):
    """Dynamically updates the live Win Rate indicator."""
    try:
        w_text = entry_won.get().strip()
        l_text = entry_lost.get().strip()
        if not w_text and not l_text:
            lbl_live_calc.config(text="Total: 0 | Win Rate: 0.0%")
            return

        w = int(w_text) if w_text else 0
        l = int(l_text) if l_text else 0
        total = w + l
        if total > 0:
            rate = round((w / total) * 100, 1)
            lbl_live_calc.config(text=f"Total: {total} | Win Rate: {rate}%")
        else:
            lbl_live_calc.config(text="Total: 0 | Win Rate: 0.0%")
    except ValueError:
        lbl_live_calc.config(text="Total: - | Win Rate: -")

# --- UI Setup ---
root = tk.Tk()
root.title("Smash Session Tracker")
root.geometry("460x650")
root.resizable(False, False)

# 1. Match Details Frame
frame_main = ttk.LabelFrame(root, text=" Match Details ", padding=10)
frame_main.pack(fill="x", padx=15, pady=6)
frame_main.columnconfigure(1, weight=1)  # Ευθυγραμμίζει απόλυτα τα inputs

ttk.Label(frame_main, text="Match Type:").grid(row=0, column=0, sticky="w", pady=4, padx=(0, 10))
combo_ranked = ttk.Combobox(frame_main, values=["Ranked", "Tournament", "Friendlies"], state="readonly")
combo_ranked.current(0)
combo_ranked.grid(row=0, column=1, sticky="ew", pady=4)

ttk.Label(frame_main, text="Opponent:").grid(row=1, column=0, sticky="w", pady=4, padx=(0, 10))
entry_opponent = ttk.Entry(frame_main)
entry_opponent.grid(row=1, column=1, sticky="ew", pady=4)

ttk.Label(frame_main, text="Opponent Character:").grid(row=2, column=0, sticky="w", pady=4, padx=(0, 10))
combo_char = ttk.Combobox(frame_main, values=CHARACTERS)
combo_char.grid(row=2, column=1, sticky="ew", pady=4)

# 2. Score & Mental Frame
frame_stats = ttk.LabelFrame(root, text=" Score & Mental ", padding=10)
frame_stats.pack(fill="x", padx=15, pady=6)

ttk.Label(frame_stats, text="Games Won:").grid(row=0, column=0, sticky="w", pady=4)
entry_won = ttk.Entry(frame_stats, width=10)
entry_won.grid(row=0, column=1, sticky="e", pady=4)

ttk.Label(frame_stats, text="Games Lost:").grid(row=1, column=0, sticky="w", pady=4)
entry_lost = ttk.Entry(frame_stats, width=10)
entry_lost.grid(row=1, column=1, sticky="e", pady=4)

lbl_live_calc = ttk.Label(frame_stats, text="Total: 0 | Win Rate: 0.0%", font=("Arial", 9, "bold"))
lbl_live_calc.grid(row=2, column=0, columnspan=2, pady=6)

entry_won.bind("<KeyRelease>", update_live_calc)
entry_lost.bind("<KeyRelease>", update_live_calc)

ttk.Label(frame_stats, text="Mental State (1-10):").grid(row=3, column=0, sticky="w", pady=4)
spin_mental = ttk.Spinbox(frame_stats, from_=1, to=10, width=8)
spin_mental.set(7)
spin_mental.grid(row=3, column=1, sticky="e", pady=4)

# 3. Stage Losses Frame
frame_stages = ttk.LabelFrame(root, text=" Stages Lost (Checkboxes) ", padding=10)
frame_stages.pack(fill="x", padx=15, pady=6)

stage_vars = {}
for idx, stage in enumerate(STAGES):
    var = tk.IntVar(value=0)
    stage_vars[stage] = var
    chk = ttk.Checkbutton(frame_stages, text=stage, variable=var)
    chk.grid(row=idx // 2, column=idx % 2, sticky="w", padx=6, pady=3)

# 4. Save Button
btn_save = ttk.Button(root, text="Save Session", command=save_data)
btn_save.pack(pady=12, ipady=4, ipadx=10)

init_excel()
root.mainloop()