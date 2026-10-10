"""Static game data.

Affix and skill IDs are reverse-engineered facts confirmed via single-affix
filter exports from Diablo IV. They are copied verbatim from index.html,
which is the source of truth. Never invent or alter an ID here.
"""

DB = {
    # Offensive
    "Weapon Damage":                       0x0027fc93,
    "Strength":                            0x001beac2,
    "Intelligence":                        0x001beabe,
    "Willpower":                           0x001beab4,
    "Dexterity":                           0x001beaba,
    "Thorns":                              0x001beb22,
    "All Damage Multiplier":               0x001beac6,
    "Attack Speed":                        0x001beace,
    "Critical Strike Chance":              0x001bead2,
    "Critical Strike Damage Multiplier":   0x001bead4,
    "Vulnerable Damage Multiplier":        0x001bfc80,
    "Damage Over Time Multiplier":         0x001bead6,
    "Cold Damage Multiplier":              0x00270af5,
    "Fire Damage Multiplier":              0x00270af7,
    "Holy Damage Multiplier":              0x00270aff,
    "Lightning Damage Multiplier":         0x00270afd,
    "Physical Damage Multiplier":          0x00270ad0,
    "Poison Damage Multiplier":            0x00270afb,
    "Shadow Damage Multiplier":            0x00270af9,
    # Defensive
    "Maximum Life":                        0x001bead8,
    "Life Regeneration":                   0x001beada,
    "Life On Hit":                         0x001d5e13,
    "Life on Kill":                        0x0025da8c,
    "Armor":                               0x001beab2,
    "Resistance to All Elements":          0x001bfd38,
    "Fire Resistance":                     0x001beaee,
    "Cold Resistance":                     0x001beb2e,
    "Lightning Resistance":                0x001beaf2,
    "Poison Resistance":                   0x001beaf4,
    "Shadow Resistance":                   0x001beaf6,
    "Physical Resistance":                 0x002557e4,
    "Damage Reduction":                    0x001d6e63,
    "Dodge Chance":                        0x001bfc85,
    # Resource
    "Maximum Resource":                    0x001bfc79,
    "Energy Regeneration":                 0x001d5e30,
    "Essence Regeneration":                0x001d5e3a,
    "Fury Regeneration":                   0x001d5e38,
    "Mana Regeneration":                   0x001d5e36,
    "Spirit Regeneration":                 0x001d5e33,
    "Vigor Regeneration":                  0x001eb549,
    "Faith Regeneration":                  0x002674b9,
    "Wrath Regeneration":                  0x0026a37c,
    "Energy On Kill":                      0x001d5e25,
    "Essence On Kill":                     0x001d5e27,
    "Fury On Kill":                        0x001d5e29,
    "Mana On Kill":                        0x001d5e2b,
    "Spirit On Kill":                      0x001d5e2d,
    "Vigor On Kill":                       0x001eb481,
    "Faith On Kill":                       0x002674bb,
    "Wrath every 10 Kills":               0x0026a374,
    "Resource Cost Reduction":             0x001d3a0f,
    "Resource Generation":                 0x001beb20,
    "Lucky Hit Restore Primary Resource": 0x0024527f,
    # Utility
    "Potion Capacity":                     0x001beae2,
    "Lucky Hit Chance":                    0x001beadc,
    "Healing Received":                    0x001bfcbf,
    "Fortify Generation":                  0x00266b1e,
    "Barrier Generation":                  0x00266b22,
    # Mobility
    "Movement Speed":                      0x001beade,
    "Attacks Reduce Evade Cooldown":       0x0026c56c,
    "Maximum Evade Charge":                0x0026c56e,
    "Evade Grants Movement Speed":         0x0026c570,
}

SKILLS = [
    # Warlock (confirmed)
    {"name": "Hell Fracture",       "id": 0x00273c0a, "class": "Warlock",    "confirmed": True},
    {"name": "Abyss Skills",        "id": 0x0026ad42, "class": "Warlock",    "confirmed": True},
    {"name": "Hellfire Skills",     "id": 0x0026adc4, "class": "Warlock",    "confirmed": True},
    {"name": "Occult Skills",       "id": 0x0026adc6, "class": "Warlock",    "confirmed": True},
    {"name": "Demonology Skills",   "id": 0x0026adcd, "class": "Warlock",    "confirmed": True},
    {"name": "Sigil of Chaos",      "id": 0x0026adc2, "class": "Warlock",    "confirmed": True},
    {"name": "Sigil of Summons",    "id": 0x0026adc8, "class": "Warlock",    "confirmed": True},
    {"name": "Sigil of Subversion", "id": 0x0026ad87, "class": "Warlock",    "confirmed": True},
    {"name": "Blazing Scream",      "id": 0x0026ad89, "class": "Warlock",    "confirmed": True},
    {"name": "Bombardment",         "id": 0x0026ad8b, "class": "Warlock",    "confirmed": True},
    {"name": "Rampage",             "id": 0x0026ad7e, "class": "Warlock",    "confirmed": True},
    {"name": "Tyrant's Grasp",      "id": 0x0026ad46, "class": "Warlock",    "confirmed": True},
    {"name": "Dread Claws",         "id": 0x0026ad48, "class": "Warlock",    "confirmed": True},
    # Generic (confirmed)
    {"name": "Core Skills",         "id": 0x001d6e31, "class": "All",        "confirmed": True},
    {"name": "All Skills",          "id": 0x0026ad83, "class": "All",        "confirmed": True},
    # Other classes — IDs pending (placeholders, never selected or encoded)
    {"name": "Bash",                "id": None, "class": "Barbarian",  "confirmed": False},
    {"name": "Whirlwind",           "id": None, "class": "Barbarian",  "confirmed": False},
    {"name": "Hammer of the Ancients", "id": None, "class": "Barbarian", "confirmed": False},
    {"name": "Leap",                "id": None, "class": "Barbarian",  "confirmed": False},
    {"name": "Rend",                "id": None, "class": "Barbarian",  "confirmed": False},
    {"name": "Weapon Mastery Skills", "id": None, "class": "Barbarian", "confirmed": False},
    {"name": "Landslide",           "id": None, "class": "Druid",      "confirmed": False},
    {"name": "Tornado",             "id": None, "class": "Druid",      "confirmed": False},
    {"name": "Pulverize",           "id": None, "class": "Druid",      "confirmed": False},
    {"name": "Shred",               "id": None, "class": "Druid",      "confirmed": False},
    {"name": "Wolves",              "id": None, "class": "Druid",      "confirmed": False},
    {"name": "Bone Spear",          "id": None, "class": "Necromancer", "confirmed": False},
    {"name": "Blood Surge",         "id": None, "class": "Necromancer", "confirmed": False},
    {"name": "Corpse Explosion",    "id": None, "class": "Necromancer", "confirmed": False},
    {"name": "Bone Skills",         "id": None, "class": "Necromancer", "confirmed": False},
    {"name": "Blood Skills",        "id": None, "class": "Necromancer", "confirmed": False},
    {"name": "Twisting Blades",     "id": None, "class": "Rogue",      "confirmed": False},
    {"name": "Rapid Fire",          "id": None, "class": "Rogue",      "confirmed": False},
    {"name": "Penetrating Shot",    "id": None, "class": "Rogue",      "confirmed": False},
    {"name": "Marksman Skills",     "id": None, "class": "Rogue",      "confirmed": False},
    {"name": "Cutthroat Skills",    "id": None, "class": "Rogue",      "confirmed": False},
    {"name": "Fireball",            "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Ice Shards",          "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Chain Lightning",     "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Blizzard",            "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Frost Skills",        "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Pyromancy Skills",    "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Shock Skills",        "id": None, "class": "Sorcerer",   "confirmed": False},
    {"name": "Quill Volley",        "id": None, "class": "Spiritborn", "confirmed": False},
    {"name": "Soar",                "id": None, "class": "Spiritborn", "confirmed": False},
    {"name": "Thunderspike",        "id": None, "class": "Spiritborn", "confirmed": False},
    {"name": "Eagle Skills",        "id": None, "class": "Spiritborn", "confirmed": False},
    {"name": "Jaguar Skills",       "id": None, "class": "Spiritborn", "confirmed": False},
]

# Rarity bitmasks and item-type IDs (reverse-engineered, load-bearing).
SHOW, RECOLOR, HIDE_ALL = 0, 2, 3
COMMON, MAGIC, RARE, LEGENDARY, UNIQUE, MYTHIC, TALISMAN = 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40
LEG_PLUS = LEGENDARY | UNIQUE | MYTHIC | TALISMAN
ALL_RAR = 0x7F
CHARM = 0x00237e80
SEAL = 0x0022ed05

# Packed little-endian ARGB colors (alpha<<24 | b<<16 | g<<8 | r).
def make_color(r, g, b, a=255):
    return ((a << 24) | (b << 16) | (g << 8) | r) & 0xFFFFFFFF

C_CYAN = make_color(0, 255, 255)
C_GREEN = make_color(0, 200, 0)
C_ORANGE = make_color(255, 140, 0)
C_GOLD = make_color(255, 215, 0)
C_DEF = 0xFFFF0000
