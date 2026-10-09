# constants.py

EXCEL_FILE = "game_database.xlsx"
CONFIG_FILE = "config.json"

MATCH_TYPES = ["Ranked", "Tournament", "Friendlies / Practice"]

# Οι κοινές αρχικές στήλες
BASE_HEADERS = [
    "Ranked or Not",
    "Date",
    "My Tag",
    "My Character",
    "Opponent Tag",
    "Opponent Character",
    "Total games",
    "Games won",
    "Games lost",
    "Mental",
]

# constants.py (προσθήκη filename στα stages)

STAGE_ASSETS = {
    "SSBM": {
        "Battlefield": "battlefield.png",
        "Final Destination": "final_destination.png",
        "Dream Land 64": "dream_land_64.png",
        "Yoshi's Story": "yoshis_story.png",
        "Fountain of Dreams": "fountain_of_dreams.png",
        "Pokemon Stadium": "pokemon_stadium.png",
    },
    "SSBU": {
        "Battlefield": "battlefield.png",
        "Small Battlefield": "small_battlefield.png",
        "Final Destination": "final_destination.png",
        "Pokemon Stadium 2": "pokemon_stadium_2.png",
        "Smashville": "smashville.png",
        "Town & City": "town_and_city.png",
        "Hollow Bastion": "hollow_bastion.png",
        "Kalos Pokemon League": "kalos_pokemon_league.png",
        "Yoshi's Story": "yoshis_story.png",
    },
}

GAME_DATA = {
    "SSBM": {
        "display_name": "Super Smash Bros. Melee",
        "stages": [
            "Battlefield",
            "Final Destination",
            "Dream Land 64",
            "Yoshi's Story",
            "Fountain of Dreams",
            "Pokemon Stadium",
        ],
        "characters": [
            "Bowser", "Captain Falcon", "Donkey Kong", "Dr. Mario", "Falco",
            "Fox", "Game & Watch", "Ganondorf", "Ice Climbers", "Jigglypuff",
            "Kirby", "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Ness",
            "Peach", "Pichu", "Pikachu", "Roy", "Samus", "Sheik", "Yoshi",
            "Young Link", "Zelda"
        ],
    },
    "SSBU": {
        "display_name": "Super Smash Bros. Ultimate",
        "stages": [
            "Battlefield",
            "Small Battlefield",
            "Final Destination",
            "Pokemon Stadium 2",
            "Smashville",
            "Town & City",
            "Hollow Bastion",
            "Kalos Pokemon League",
            "Yoshi's Story",
        ],
        "characters": [
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
            "Pikachu", "Piranha Plant", "Pit", "Pokemon Trainer", "Pyra / Mythra",
            "Richter", "Ridley", "R.O.B.", "Robin", "Rosalina & Luma", "Roy",
            "Ryu", "Samus", "Sephiroth", "Sheik", "Shulk", "Simon", "Snake",
            "Sonic", "Sora", "Steve", "Terry", "Toon Link", "Villager",
            "Wario", "Wii Fit Trainer", "Wolf", "Yoshi", "Young Link",
            "Zelda", "Zero Suit Samus"
        ],
    },
}

def get_sheet_headers(game_code: str) -> list[str]:
    return BASE_HEADERS + GAME_DATA[game_code]["stages"]