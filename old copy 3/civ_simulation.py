# ════════════════════════════════════════════════════════════
# FILE: config.py
# ════════════════════════════════════════════════════════════

"""
Autonomous Civilization Simulation - Configuration & Constants
All game configuration, enums, stylesheets, and static data definitions.
"""
from enum import IntEnum
from PySide6.QtGui import QColor


# ── Database ────────────────────────────────────────────────
DB_PATH = "civ_simulation.sqlite"
TILE_SIZE = 12

# ── Terrain Enum ────────────────────────────────────────────
class Terrain(IntEnum):
    OCEAN = 0; PLAINS = 1; FOREST = 2; MOUNTAIN = 3; DESERT = 4
    JUNGLE = 5; HILLS = 6; TUNDRA = 7; COAST = 8; GRASSLAND = 9

# ── Diplomacy Enum ──────────────────────────────────────────
class Relation(IntEnum):
    NEUTRAL = 0; FRIENDLY = 1; ALLIED = 2; HOSTILE = 3; AT_WAR = 4

# ── Map Generation Presets ──────────────────────────────────
class TerrainPreset:
    """Different world generation strategies - each uses a unique algorithm."""
    CONTINENT = "Continent"
    ARCHIPELAGO = "Archipelago"
    PANGAEA = "Pangaea"
    ISLANDS = "Islands"
    HIGHLANDS = "Highlands"
    RIVER_VALLEY = "River Valley"
    CRATER = "Crater Lake"
    MEDITERRANEAN = "Mediterranean"

TERRAIN_PRESETS = {
    TerrainPreset.CONTINENT: {
        "description": "1-3 large landmasses with coastal shelves and deep oceans between",
        "water_ratio": 0.40,
    },
    TerrainPreset.ARCHIPELAGO: {
        "description": "Scattered island chains with narrow straits and shallow seas",
        "water_ratio": 0.55,
    },
    TerrainPreset.PANGAEA: {
        "description": "One giant supercontinent surrounded by a vast ocean",
        "water_ratio": 0.30,
    },
    TerrainPreset.ISLANDS: {
        "description": "Many small isolated islands dotting a wide ocean",
        "water_ratio": 0.60,
    },
    TerrainPreset.HIGHLANDS: {
        "description": "Mountainous terrain with valleys, ridges, and sparse lowlands",
        "water_ratio": 0.20,
    },
    TerrainPreset.RIVER_VALLEY: {
        "description": "A long river carves through fertile land with mountain walls",
        "water_ratio": 0.25,
    },
    TerrainPreset.CRATER: {
        "description": "A massive crater ring with a central lake and rim mountains",
        "water_ratio": 0.30,
    },
    TerrainPreset.MEDITERRANEAN: {
        "description": "A large inland sea surrounded by coastlines and peninsulas",
        "water_ratio": 0.35,
    },
}

# ── Visual Constants ────────────────────────────────────────
TERRAIN_COLORS = {
    0: QColor(22, 50, 115), 1: QColor(125, 182, 82), 2: QColor(42, 122, 42),
    3: QColor(142, 132, 122), 4: QColor(208, 182, 102), 5: QColor(34, 139, 34),
    6: QColor(139, 119, 101), 7: QColor(180, 210, 230), 8: QColor(72, 145, 220),
    9: QColor(100, 200, 100)
}

RESOURCE_TYPES = {
    "iron": QColor(160, 160, 170), "wheat": QColor(240, 220, 130),
    "gold_ore": QColor(255, 215, 0), "horses": QColor(139, 90, 43),
    "stone": QColor(180, 180, 180), "fish": QColor(100, 180, 255),
}

RELIGIONS = [
    {"name": "Sun Worship", "color": "#FFD700", "bonus_type": "growth", "bonus_val": 0.05},
    {"name": "War Cult", "color": "#FF4500", "bonus_type": "military", "bonus_val": 0.05},
    {"name": "Mystic Order", "color": "#9370DB", "bonus_type": "culture", "bonus_val": 0.08},
    {"name": "Trade Creed", "color": "#37AFAF", "bonus_type": "trade", "bonus_val": 0.06},
]

WONDERS = [
    {"name": "Great Lighthouse", "effect": "trade", "bonus": 0.30, "cost": 200},
    {"name": "Colossus", "effect": "military", "bonus": 0.20, "cost": 150},
    {"name": "Hanging Gardens", "effect": "growth", "bonus": 0.25, "cost": 180},
    {"name": "Great Library", "effect": "tech", "bonus": 0.30, "cost": 200},
    {"name": "Temple of Artemis", "effect": "culture", "bonus": 0.20, "cost": 170},
    {"name": "Pyramids", "effect": "growth", "bonus": 0.15, "cost": 160},
]

SEASON_NAMES = ["Spring", "Summer", "Autumn", "Winter"]
FOOD_MULTIPLIERS = [1.0, 1.3, 0.9, 0.5]
SEASON_COLORS = [
    QColor(100, 200, 100, 40), QColor(255, 200, 50, 40),
    QColor(200, 120, 50, 40), QColor(150, 200, 255, 40)
]

REBEL_NAMES = ["Free State", "Independents", "Rebels", "Liberators", "Uprising"]

# ── Forms of Government ─────────────────────────────────────
# Each government type affects:
#   succession       - how leaders are replaced: hereditary, election, coup, theocratic
#   leader_term_min  - minimum years a leader rules before succession check
#   leader_term_max  - maximum years a leader can rule
#   stability_mod    - per-turn stability modifier
#   gold_mod         - treasury income multiplier
#   science_mod      - technology growth multiplier
#   military_mod     - military strength multiplier
#   culture_mod      - culture growth multiplier
#   war_threshold_mod - modifier to archetype war_threshold (lower = more aggressive)
#   diplo_bonus      - bonus to alliance/trade chance
#   rebel_chance     - chance of revolution per turn (low stability)
#   allowed_govts    - government types this one can transition to
#   description      - flavor text

GOVERNMENTS = {
    "chiefdom": {
        "label": "Chiefdom",
        "succession": "hereditary",
        "leader_term_min": 20,
        "leader_term_max": 40,
        "stability_mod": 0.3,
        "gold_mod": 0.8,
        "science_mod": 0.7,
        "military_mod": 1.0,
        "culture_mod": 0.8,
        "war_threshold_mod": -5,
        "diplo_bonus": 0.0,
        "rebel_chance": 0.01,
        "allowed_govts": ["monarchy", "republic", "theocracy"],
        "description": "A tribal society ruled by a hereditary chief. Simple but resilient, with strong personal leadership.",
        "era_min": 0,
    },
    "monarchy": {
        "label": "Monarchy",
        "succession": "hereditary",
        "leader_term_min": 25,
        "leader_term_max": 50,
        "stability_mod": 0.5,
        "gold_mod": 1.0,
        "science_mod": 0.9,
        "military_mod": 1.1,
        "culture_mod": 1.0,
        "war_threshold_mod": 0,
        "diplo_bonus": 0.05,
        "rebel_chance": 0.008,
        "allowed_govts": ["republic", "theocracy", "dictatorship", "oligarchy"],
        "description": "A hereditary kingdom where rulers reign for life. Stable governance with strong military tradition.",
        "era_min": 1,
    },
    "republic": {
        "label": "Republic",
        "succession": "election",
        "leader_term_min": 8,
        "leader_term_max": 16,
        "stability_mod": 0.2,
        "gold_mod": 1.2,
        "science_mod": 1.2,
        "military_mod": 0.9,
        "culture_mod": 1.1,
        "war_threshold_mod": 10,
        "diplo_bonus": 0.15,
        "rebel_chance": 0.004,
        "allowed_govts": ["democracy", "oligarchy", "dictatorship", "monarchy"],
        "description": "Elected leaders govern for fixed terms. Prosperity and science flourish, but military may suffer.",
        "era_min": 2,
    },
    "theocracy": {
        "label": "Theocracy",
        "succession": "theocratic",
        "leader_term_min": 15,
        "leader_term_max": 35,
        "stability_mod": 0.7,
        "gold_mod": 0.9,
        "science_mod": 0.7,
        "military_mod": 1.0,
        "culture_mod": 1.5,
        "war_threshold_mod": -3,
        "diplo_bonus": 0.1,
        "rebel_chance": 0.005,
        "allowed_govts": ["monarchy", "republic", "dictatorship"],
        "description": "Divine rule where religious leaders guide the state. Unshakeable faith, powerful culture, slower progress.",
        "era_min": 1,
    },
    "dictatorship": {
        "label": "Dictatorship",
        "succession": "coup",
        "leader_term_min": 10,
        "leader_term_max": 30,
        "stability_mod": -0.2,
        "gold_mod": 1.1,
        "science_mod": 0.8,
        "military_mod": 1.3,
        "culture_mod": 0.6,
        "war_threshold_mod": -15,
        "diplo_bonus": -0.1,
        "rebel_chance": 0.02,
        "allowed_govts": ["monarchy", "republic", "oligarchy"],
        "description": "Iron-fisted rule by a strongman. Massive military power, but constant threat of coups and rebellion.",
        "era_min": 2,
    },
    "oligarchy": {
        "label": "Oligarchy",
        "succession": "election",
        "leader_term_min": 12,
        "leader_term_max": 24,
        "stability_mod": 0.1,
        "gold_mod": 1.4,
        "science_mod": 1.0,
        "military_mod": 0.8,
        "culture_mod": 0.9,
        "war_threshold_mod": 5,
        "diplo_bonus": 0.2,
        "rebel_chance": 0.006,
        "allowed_govts": ["republic", "dictatorship", "monarchy"],
        "description": "A small elite rules for profit. Gold flows freely, but the military is often neglected for commerce.",
        "era_min": 2,
    },
    "democracy": {
        "label": "Democracy",
        "succession": "election",
        "leader_term_min": 6,
        "leader_term_max": 12,
        "stability_mod": 0.4,
        "gold_mod": 1.1,
        "science_mod": 1.3,
        "military_mod": 0.8,
        "culture_mod": 1.3,
        "war_threshold_mod": 15,
        "diplo_bonus": 0.25,
        "rebel_chance": 0.002,
        "allowed_govts": ["republic", "oligarchy"],
        "description": "Full representative democracy. Rapid progress and cultural flourishing, but slow military response.",
        "era_min": 3,
    },
}

# ── Leader Name Pools ───────────────────────────────────────
# Pools of first names and titles organized by flavor/origin.
# Leaders are generated by combining a first name with a title or epithet.

LEADER_FIRST_NAMES = [
    "Aldric", "Berenice", "Caius", "Darius", "Elena", "Felix", "Gaius",
    "Helena", "Ivan", "Julia", "Kaspar", "Livia", "Magnus", "Nadia",
    "Octavia", "Publius", "Quintus", "Rufina", "Severus", "Tatiana",
    "Ursus", "Valeria", "Wolfram", "Xanthippe", "Yevgeny", "Zeno",
    "Alaric", "Brunhilde", "Cyrus", "Demetria", "Erik", "Freya",
    "Gundahar", "Hrotsvitha", "Iskandar", "Jahanara", "Khosrow",
    "Lysistrata", "Mithridates", "Nefertari", "Ozymandias", "Priam",
    "Rhadamanthus", "Semiramis", "Themistocles", "Vercingetorix",
    "Xerxes", "Zenobia", "Ashoka", "Boudicca",
]

LEADER_TITLES = {
    "chiefdom": ["Chieftain", "Headman", "Elder", "Matriarch", "Patriarch"],
    "monarchy": ["King", "Queen", "Emperor", "Empress", "Sovereign", "High King"],
    "republic": ["Consul", "Chancellor", "Premier", "Tribune", "Magistrate"],
    "theocracy": ["High Priest", "Prophet", "Pontiff", "Oracle", "Hierophant"],
    "dictatorship": ["Generalissimo", "Supreme Leader", "Commandant", "Autarch", "Protector"],
    "oligarchy": ["Director", "Chairman", "Patrician", "Archon", "Syndic"],
    "democracy": ["President", "Prime Minister", "Premier", "Speaker", "Minister"],
}

LEADER_EPITHETS = [
    "the Bold", "the Wise", "the Cruel", "the Just", "the Great",
    "the Unready", "the Conqueror", "the Peacemaker", "the Mad",
    "the Pious", "the Terrible", "the Enlightened", "the Iron",
    "the Golden", "the Fierce", "the Patient", "the Venerable",
    "the Proud", "the Cunning", "the Merciful", "the Stubborn",
    "the Young", "the Old", "the Silent", "the Storm",
]

# ── Personality Archetypes ──────────────────────────────────
# Each civilization has a named archetype that defines their playstyle.
# "archetype" is a flavor label; the actual behavior comes from the
# utility-AI weights + the unique per-archetype modifiers below.
#
# Modifier keys:
#   war_threshold      - grievance level before declaring war (lower = more aggressive)
#   alliance_eagerness - probability multiplier for forming alliances
#   trade_eagerness    - probability multiplier for forming trade routes
#   expansion_greed    - how many tiles they try to claim at once (affects expand score)
#   wonder_hunger      - how early they start pursuing wonders (lower = earlier)
#   stability_resilience - how fast they recover stability each turn
#   tolerance          - how much religious friction they can tolerate before grievances
#   starting_bonus     - bonus applied once at game start: {stat: amount}

PERSONALITY_ARCHETYPES = {
    "warlord": {
        "label": "Warlord",
        "description": "Conquers through raw military might. Expands aggressively, builds armies, and attacks neighbors at the slightest provocation.",
        "war_threshold": 25,
        "alliance_eagerness": 0.3,
        "trade_eagerness": 0.4,
        "expansion_greed": 1.4,
        "wonder_hunger": 0.6,
        "stability_resilience": 0.8,
        "tolerance": 10,
        "starting_bonus": {"military": 50},
        "weights": {"expansion": 1.4, "military": 1.6, "tech": 0.6, "culture": 0.5,
                     "economy": 0.7, "trade": 0.4, "diplomacy": 0.3, "wonder": 0.2},
    },
    "philosopher": {
        "label": "Philosopher",
        "description": "Pursues knowledge above all. Rapidly advances technology and builds universities, preferring diplomacy over conflict.",
        "war_threshold": 80,
        "alliance_eagerness": 0.8,
        "trade_eagerness": 0.9,
        "expansion_greed": 0.7,
        "wonder_hunger": 0.7,
        "stability_resilience": 1.2,
        "tolerance": 60,
        "starting_bonus": {"technology": 3.0},
        "weights": {"expansion": 0.6, "military": 0.5, "tech": 1.8, "culture": 1.2,
                     "economy": 1.0, "trade": 1.0, "diplomacy": 1.2, "wonder": 0.8},
    },
    "merchant": {
        "label": "Merchant Republic",
        "description": "Gold rules everything. Amasses vast treasuries through trade networks, markets, and strategic wonder investments.",
        "war_threshold": 60,
        "alliance_eagerness": 1.0,
        "trade_eagerness": 1.5,
        "expansion_greed": 0.8,
        "wonder_hunger": 0.5,
        "stability_resilience": 1.0,
        "tolerance": 40,
        "starting_bonus": {"treasury": 300},
        "weights": {"expansion": 0.7, "military": 0.6, "tech": 1.0, "culture": 0.8,
                     "economy": 1.6, "trade": 1.8, "diplomacy": 1.1, "wonder": 1.0},
    },
    "zealot": {
        "label": "Zealot",
        "description": "Spreads faith and culture relentlessly. Found religions early and convert neighbors through cultural pressure and holy wars.",
        "war_threshold": 40,
        "alliance_eagerness": 0.6,
        "trade_eagerness": 0.5,
        "expansion_greed": 1.0,
        "wonder_hunger": 0.8,
        "stability_resilience": 1.4,
        "tolerance": 15,
        "starting_bonus": {"culture": 100},
        "weights": {"expansion": 0.9, "military": 1.0, "tech": 0.8, "culture": 1.8,
                     "economy": 0.8, "trade": 0.5, "diplomacy": 0.7, "wonder": 1.2},
    },
    "builder": {
        "label": "Builder",
        "description": "Constructs an indestructible fortress civilization. Maximizes buildings, stability, and wonders while expanding cautiously.",
        "war_threshold": 70,
        "alliance_eagerness": 0.7,
        "trade_eagerness": 0.8,
        "expansion_greed": 0.6,
        "wonder_hunger": 0.3,
        "stability_resilience": 2.0,
        "tolerance": 50,
        "starting_bonus": {"treasury": 200},
        "weights": {"expansion": 0.5, "military": 0.7, "tech": 1.1, "culture": 0.9,
                     "economy": 1.5, "trade": 1.0, "diplomacy": 0.9, "wonder": 1.6},
    },
    "diplomat": {
        "label": "Diplomat",
        "description": "Wins through alliances and treaties. Maintains peace, builds coalitions, and uses trade as a weapon. Almost never starts wars.",
        "war_threshold": 90,
        "alliance_eagerness": 1.5,
        "trade_eagerness": 1.3,
        "expansion_greed": 0.7,
        "wonder_hunger": 0.6,
        "stability_resilience": 1.3,
        "tolerance": 70,
        "starting_bonus": {"culture": 50},
        "weights": {"expansion": 0.6, "military": 0.4, "tech": 1.0, "culture": 1.2,
                     "economy": 1.0, "trade": 1.3, "diplomacy": 2.0, "wonder": 0.7},
    },
    "raider": {
        "label": "Raider",
        "description": "Fast, unpredictable, and vicious. Expands rapidly in bursts, raids neighbors for resources, and destabilizes rivals.",
        "war_threshold": 30,
        "alliance_eagerness": 0.2,
        "trade_eagerness": 0.3,
        "expansion_greed": 1.8,
        "wonder_hunger": 0.9,
        "stability_resilience": 0.6,
        "tolerance": 8,
        "starting_bonus": {"military": 30, "treasury": -100},
        "weights": {"expansion": 1.7, "military": 1.5, "tech": 0.7, "culture": 0.4,
                     "economy": 0.5, "trade": 0.3, "diplomacy": 0.2, "wonder": 0.1},
    },
    "survivor": {
        "label": "Survivor",
        "description": "Endures every storm. Maximizes stability and population, adapts to threats, and outlasts opponents through sheer resilience.",
        "war_threshold": 55,
        "alliance_eagerness": 0.8,
        "trade_eagerness": 0.7,
        "expansion_greed": 0.8,
        "wonder_hunger": 0.5,
        "stability_resilience": 2.5,
        "tolerance": 45,
        "starting_bonus": {"population": 200, "stability": 10},
        "weights": {"expansion": 0.8, "military": 0.8, "tech": 1.0, "culture": 0.9,
                     "economy": 1.2, "trade": 0.9, "diplomacy": 1.0, "wonder": 0.6},
    },
}

# ── Default Civilization Templates ──────────────────────────
CIV_TEMPLATES = [
    {
        "name": "Aethoria", "color": "#D73737", "archetype": "warlord",
        "personality": {"expansion": 1.4, "military": 1.6, "tech": 0.6, "culture": 0.5,
                         "economy": 0.7, "trade": 0.4, "diplomacy": 0.3, "wonder": 0.2},
    },
    {
        "name": "Byzantia", "color": "#3769D7", "archetype": "diplomat",
        "personality": {"expansion": 0.6, "military": 0.4, "tech": 1.0, "culture": 1.2,
                         "economy": 1.0, "trade": 1.3, "diplomacy": 2.0, "wonder": 0.7},
    },
    {
        "name": "Celestia", "color": "#37AF37", "archetype": "zealot",
        "personality": {"expansion": 0.9, "military": 1.0, "tech": 0.8, "culture": 1.8,
                         "economy": 0.8, "trade": 0.5, "diplomacy": 0.7, "wonder": 1.2},
    },
    {
        "name": "Drakonia", "color": "#D7AF1E", "archetype": "raider",
        "personality": {"expansion": 1.7, "military": 1.5, "tech": 0.7, "culture": 0.4,
                         "economy": 0.5, "trade": 0.3, "diplomacy": 0.2, "wonder": 0.1},
    },
    {
        "name": "Solaria", "color": "#FF8C00", "archetype": "philosopher",
        "personality": {"expansion": 0.6, "military": 0.5, "tech": 1.8, "culture": 1.2,
                         "economy": 1.0, "trade": 1.0, "diplomacy": 1.2, "wonder": 0.8},
    },
    {
        "name": "Ironhold", "color": "#8B8B8B", "archetype": "warlord",
        "personality": {"expansion": 1.3, "military": 1.5, "tech": 0.7, "culture": 0.5,
                         "economy": 0.8, "trade": 0.5, "diplomacy": 0.4, "wonder": 0.3},
    },
    {
        "name": "Verdania", "color": "#2E8B57", "archetype": "builder",
        "personality": {"expansion": 0.5, "military": 0.7, "tech": 1.1, "culture": 0.9,
                         "economy": 1.5, "trade": 1.0, "diplomacy": 0.9, "wonder": 1.6},
    },
    {
        "name": "Crimsonia", "color": "#DC143C", "archetype": "merchant",
        "personality": {"expansion": 0.7, "military": 0.6, "tech": 1.0, "culture": 0.8,
                         "economy": 1.6, "trade": 1.8, "diplomacy": 1.1, "wonder": 1.0},
    },
    {
        "name": "Thornwall", "color": "#6B4C9A", "archetype": "survivor",
        "personality": {"expansion": 0.8, "military": 0.8, "tech": 1.0, "culture": 0.9,
                         "economy": 1.2, "trade": 0.9, "diplomacy": 1.0, "wonder": 0.6},
    },
    {
        "name": "Ashford", "color": "#C8A951", "archetype": "merchant",
        "personality": {"expansion": 0.6, "military": 0.5, "tech": 1.0, "culture": 0.7,
                         "economy": 1.7, "trade": 1.9, "diplomacy": 1.2, "wonder": 0.9},
    },
]

# ── Dark Theme Stylesheet ───────────────────────────────────
DARK_STYLESHEET = """
QMainWindow { background-color: #1e1e1e; }
QWidget { background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 12px; }
QGraphicsView { border: 1px solid #3e3e3e; background-color: #2d2d2d; border-radius: 2px; }
QToolBar { background-color: #2d2d2d; border-bottom: 1px solid #1a1a1a; spacing: 6px; padding: 3px 6px; }
QPushButton { background-color: #0e639e; color: white; border: none; padding: 5px 10px; border-radius: 3px; font-size: 11px; }
QPushButton:hover { background-color: #1177bb; }
QPushButton:pressed { background-color: #0a5080; }
QSlider::groove:horizontal { background: #3e3e3e; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #0e639e; width: 14px; margin: -4px 0; border-radius: 7px; }
QSlider::handle:horizontal:hover { background: #1177bb; }
QTextEdit { border: 1px solid #3e3e3e; background-color: #1e1e1e; border-radius: 4px; }
QSplitter::handle { background-color: #3e3e3e; width: 3px; }
QSplitter::handle:hover { background-color: #0e639e; }
QScrollBar:vertical { border: none; background: #2d2d2d; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #4e4e4e; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #5e5e5e; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QComboBox { background-color: #3e3e3e; border: 1px solid #555; border-radius: 3px; padding: 3px 8px; color: white; font-size: 11px; }
QComboBox:hover { border-color: #0e639e; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #2d2d2d; color: white; selection-background-color: #0e639e; border: 1px solid #3e3e3e; }
QCheckBox { spacing: 4px; }
QCheckBox::indicator { width: 14px; height: 14px; border-radius: 3px; border: 1px solid #555; background-color: #2d2d2d; }
QCheckBox::indicator:checked { background-color: #0e639e; border-color: #0e639e; }
QGroupBox { border: 1px solid #3e3e3e; border-radius: 4px; margin-top: 8px; padding-top: 12px; font-weight: bold; color: #0ea5e9; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; }
QToolTip { background-color: #2d2d2d; color: #d4d4d4; border: 1px solid #0e639e; padding: 6px; border-radius: 4px; font-size: 11px; }
QScrollArea { border: none; background-color: #1e1e1e; }
QTabWidget::pane { border: 1px solid #3e3e3e; background-color: #1e1e1e; }
QStatusBar { background-color: #252526; border-top: 1px solid #3e3e3e; }
QStatusBar QLabel { padding: 0 8px; }
QFrame { border: none; }
QFrame[frameShape="6"] { color: #3e3e3e; }  /* HLine separator */
"""

# ── Simulation Defaults ─────────────────────────────────────
DEFAULT_MAP_WIDTH = 80
DEFAULT_MAP_HEIGHT = 60
DEFAULT_CIV_COUNT = 4
MIN_CIV_COUNT = 2
MAX_CIV_COUNT = 10
AUTO_SAVE_INTERVAL = 100  # generations between auto-saves
SEASON_LENGTH = 25  # turns per season

# ── Population Dynamics ─────────────────────────────────────
# Per-turn birth/death rates as fractions of current population.
# Net growth = (BIRTH_RATE - DEATH_RATE) * pop * stability_factor.
# When pop > pop_cap * FAMINE_THRESHOLD, famine deaths kick in,
# scaling linearly with how far over cap the population is.
BIRTH_RATE = 0.005
DEATH_RATE = 0.003
FAMINE_THRESHOLD = 1.10  # Pop above 110% of cap starts starving
FAMINE_DEATH_RATE = 0.05  # Base famine death rate, scales with overpop
STABILITY_BIRTH_MULT = 0.5  # At stability=0, births reduced by 50%
STABILITY_DEATH_MULT = 0.5  # At stability=0, deaths increased by 50%
# Hard cap: population cannot exceed pop_cap * POP_HARD_CAP_MULT.
# This prevents runaway growth from outpacing famine deaths.
POP_HARD_CAP_MULT = 1.5

# ── Tech Diffusion ──────────────────────────────────────────
# When bordering a civ with higher tech, slowly catch up.
# Per turn: gain = TECH_DIFFUSION_RATE * (neighbor_tech - our_tech) * border_ratio
TECH_DIFFUSION_RATE = 0.005
TECH_DIFFUSION_MIN_GAP = 2.0  # Only diffuse if gap > this

# ── Border Friction ─────────────────────────────────────────
# Civs that share borders slowly accumulate grievances even without
# explicit conflict, simulating territorial disputes and raids.
BORDER_FRICTION_BASE = 0.05  # Per shared border civ per turn
BORDER_FRICTION_RELIGION_MULT = 2.0  # Multiplier if religions differ

# ── Rebel Inheritance ───────────────────────────────────────
# When a rebellion spawns, the rebel civ inherits a fraction of the
# parent civ's tech/culture (not just pop/military).
REBEL_TECH_INHERIT = 0.6
REBEL_CULTURE_INHERIT = 0.3
REBEL_POP_INHERIT = 0.2  # (already used by existing code)
REBEL_MILITARY_INHERIT = 0.15  # (already used by existing code)

# ── Keyboard Shortcuts ──────────────────────────────────────
SHORTCUTS = {
    "play_pause": "Space",
    "speed_up": "+",
    "speed_down": "-",
    "reset_view": "R",
    "save_game": "Ctrl+S",
    "load_game": "Ctrl+O",
    "toggle_fog": "F",
    "toggle_resources": "G",
    "toggle_borders": "B",
}


# ════════════════════════════════════════════════════════════
# FILE: database.py
# ════════════════════════════════════════════════════════════

"""
Autonomous Civilization Simulation - Database Layer
SQLite schema, game definitions, and analytics storage.

Performance optimizations:
- Dict-based building/tech lookups by name (O(1) instead of O(n) linear scan)
- Batched analytics commits (accumulate rows, commit in bulk)
- WAL journal mode for better concurrent read/write performance
- Pre-compiled column name lists for dict construction
"""
import sqlite3


# ── Schema SQL ──────────────────────────────────────────────
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS def_terrain (
    id INTEGER PRIMARY KEY, name TEXT, cr INTEGER, cg INTEGER, cb INTEGER,
    food REAL DEFAULT 0, production REAL DEFAULT 0, trade REAL DEFAULT 0,
    movement_cost REAL DEFAULT 1, defense_bonus REAL DEFAULT 0, is_water INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS def_buildings (
    id INTEGER PRIMARY KEY, name TEXT, category TEXT, cost REAL, min_era_id INTEGER,
    effect TEXT, bonus REAL, maintenance REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS def_technologies (
    id INTEGER PRIMARY KEY, name TEXT, era_id INTEGER, cost REAL, category TEXT, effect TEXT, bonus REAL
);
CREATE TABLE IF NOT EXISTS def_eras (
    id INTEGER PRIMARY KEY, tech_threshold REAL, era_name TEXT
);
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT, game_id INTEGER, year INTEGER, civ_name TEXT,
    population REAL, technology REAL, military REAL, territory INTEGER, score REAL, action_taken TEXT
);
CREATE INDEX IF NOT EXISTS idx_analytics_civ_year ON analytics_snapshots(civ_name, year);
"""

# ── Default Data ────────────────────────────────────────────
DEFAULT_TERRAIN = [
    (0, "Ocean", 22, 50, 115, 0.0, 0.0, 0.0, 99, 0.0, 1),
    (1, "Plains", 125, 182, 82, 2.0, 1.0, 1.0, 1, 0.0, 0),
    (2, "Forest", 42, 122, 42, 1.0, 2.0, 0.5, 2, 0.15, 0),
    (3, "Mountain", 142, 132, 122, 0.0, 3.0, 0.0, 4, 0.35, 0),
    (4, "Desert", 208, 182, 102, 0.0, 0.5, 1.0, 2, 0.0, 0),
    (5, "Jungle", 34, 139, 34, 1.0, 0.5, 0.5, 3, 0.10, 0),
    (6, "Hills", 139, 119, 101, 1.0, 2.0, 0.5, 2, 0.20, 0),
    (7, "Tundra", 180, 210, 230, 0.5, 0.0, 0.0, 2, 0.00, 0),
    (8, "Coast", 72, 145, 220, 1.0, 0.0, 2.0, 2, 0.00, 1),
    (9, "Grassland", 100, 200, 100, 2.5, 0.5, 0.5, 1, 0.00, 0)
]

DEFAULT_BUILDINGS = [
    (0, "Granary", "economic", 10, 0, "growth", 0.10, 0),
    (1, "Barracks", "military", 25, 0, "military", 0.10, 1),
    (2, "Library", "tech", 40, 0, "tech", 0.15, 1),
    (3, "Market", "trade", 30, 1, "trade", 0.15, 1),
    (4, "Theater", "culture", 35, 1, "culture", 0.20, 1),
    (5, "Temple", "religion", 50, 1, "culture", 0.25, 2),
    (6, "Walls", "military", 35, 0, "military", 0.08, 1),
    (7, "Harbor", "trade", 45, 1, "trade", 0.20, 2),
    (8, "University", "tech", 60, 2, "tech", 0.25, 2),
    (9, "Cathedral", "culture", 70, 2, "culture", 0.30, 3),
]

DEFAULT_TECHS = [
    (0, "Pottery", 0, 5, "economic", "growth", 0.05),
    (1, "Bronze Working", 0, 12, "military", "military", 0.10),
    (2, "Writing", 0, 15, "tech", "tech", 0.15),
    (3, "Masonry", 0, 10, "economic", "growth", 0.08),
    (4, "Diplomacy", 1, 25, "culture", "culture", 0.20),
    (5, "Theology", 1, 30, "religion", "culture", 0.25),
    (6, "Mathematics", 1, 28, "tech", "tech", 0.20),
    (7, "Feudalism", 2, 45, "culture", "military", 0.15),
    (8, "Engineering", 2, 50, "tech", "growth", 0.20),
    (9, "Chivalry", 2, 55, "military", "military", 0.25),
]

DEFAULT_ERAS = [
    (0, 0.0, "Ancient"),
    (1, 15.0, "Classical"),
    (2, 40.0, "Medieval"),
    (3, 70.0, "Renaissance"),
]

# Pre-computed column names for dict construction
_BUILDING_COLS = ["id", "name", "category", "cost", "min_era_id", "effect", "bonus", "maintenance"]
_TECH_COLS = ["id", "name", "era_id", "cost", "category", "effect", "bonus"]
_ERA_COLS = ["id", "tech_threshold", "era_name"]


class GameDefs:
    """Loads and caches game definition data from SQLite.

    Performance improvements:
    - Dict-based lookups by name for buildings/techs (O(1) instead of O(n))
    - WAL journal mode for concurrent access
    - Pre-computed column name lists
    """

    def __init__(self, db_path: str = DB_PATH):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        # Enable WAL mode for better concurrent read/write performance
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._cur = self._conn.cursor()
        self._cur.executescript(SCHEMA_SQL)
        self._populate_if_empty()
        self._load_defs()

    def _populate_if_empty(self) -> None:
        self._cur.execute("SELECT COUNT(*) FROM def_terrain")
        if self._cur.fetchone()[0] == 0:
            self._cur.executemany("INSERT INTO def_terrain VALUES (?,?,?,?,?,?,?,?,?,?,?)", DEFAULT_TERRAIN)
            self._cur.executemany("INSERT INTO def_buildings VALUES (?,?,?,?,?,?,?,?)", DEFAULT_BUILDINGS)
            self._cur.executemany("INSERT INTO def_technologies VALUES (?,?,?,?,?,?,?)", DEFAULT_TECHS)
            self._cur.executemany("INSERT INTO def_eras VALUES (?,?,?)", DEFAULT_ERAS)
            self._conn.commit()

    def _load_defs(self) -> None:
        self.terrain_stats: dict[Terrain, dict] = {}
        self._cur.execute("SELECT id, food, production, trade, movement_cost, is_water FROM def_terrain")
        for row in self._cur.fetchall():
            self.terrain_stats[Terrain(row[0])] = {
                "food": row[1], "prod": row[2], "trade": row[3],
                "move": row[4], "is_water": bool(row[5])
            }
        self.buildings = [
            dict(zip(_BUILDING_COLS, row))
            for row in self._cur.execute("SELECT * FROM def_buildings").fetchall()
        ]
        self.techs = [
            dict(zip(_TECH_COLS, row))
            for row in self._cur.execute("SELECT * FROM def_technologies").fetchall()
        ]
        self.eras = [
            dict(zip(_ERA_COLS, row))
            for row in self._cur.execute("SELECT * FROM def_eras ORDER BY tech_threshold ASC").fetchall()
        ]

        # Performance: O(1) lookups by name
        self.buildings_by_name: dict[str, dict] = {b["name"]: b for b in self.buildings}
        self.techs_by_name: dict[str, dict] = {t["name"]: t for t in self.techs}

    def get_building_by_name(self, name: str) -> dict | None:
        """O(1) building lookup by name."""
        return self.buildings_by_name.get(name)

    def get_tech_by_name(self, name: str) -> dict | None:
        """O(1) tech lookup by name."""
        return self.techs_by_name.get(name)


class AnalyticsDB:
    """Stores per-turn analytics snapshots for timeline graphs and post-game analysis.

    Performance improvements:
    - Batched row accumulation with bulk commit
    - WAL journal mode for concurrent access
    - Index on (civ_name, year) for fast history queries
    """

    def __init__(self, db_path: str = DB_PATH):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._cur = self._conn.cursor()
        self.game_id: int = 1
        # Batch accumulation
        self._pending_rows: list[tuple] = []
        self._batch_size = 50  # Commit every N rows

    def log_snapshot(self, year: int, civ_name: str, pop: float, tech: float,
                     mil: float, terr: int, score: float, action: str) -> None:
        """Queue a snapshot for batched insertion."""
        self._pending_rows.append(
            (self.game_id, year, civ_name, pop, tech, mil, terr, score, action)
        )
        if len(self._pending_rows) >= self._batch_size:
            self.commit()

    def commit(self) -> None:
        """Flush all pending rows to the database."""
        if self._pending_rows:
            self._cur.executemany(
                "INSERT INTO analytics_snapshots "
                "(game_id, year, civ_name, population, technology, military, territory, score, action_taken) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                self._pending_rows
            )
            self._conn.commit()
            self._pending_rows.clear()

    def get_civ_history(self, civ_name: str, limit: int = 500) -> list[dict]:
        """Retrieve historical snapshots for a specific civilization."""
        self.commit()  # Ensure pending data is flushed before query
        self._cur.execute(
            "SELECT year, population, technology, military, territory, score, action_taken "
            "FROM analytics_snapshots WHERE civ_name = ? ORDER BY year DESC LIMIT ?",
            (civ_name, limit)
        )
        cols = ["year", "population", "technology", "military", "territory", "score", "action"]
        return [dict(zip(cols, row)) for row in self._cur.fetchall()]


# ════════════════════════════════════════════════════════════
# FILE: ai.py
# ════════════════════════════════════════════════════════════

"""
Autonomous Civilization Simulation - AI Systems
D* Lite dynamic pathfinding and Utility AI decision-making for civilizations.

AI Improvements:
- Strategic State Machine: civs switch between EXPANSION, CONSOLIDATION, CRISIS,
  TOTAL_WAR, GOLDEN_AGE, RECOVERY, SIEGE
- Rich Context: 25+ context variables (game phase, war status, territory ratio, etc.)
- Action Memory: tracks recent actions to avoid loops and enable adaptive behavior
- Compensation Factor: prevents all-zero score degeneracy in utility evaluation
- Archetype-aware execution: each personality type makes different strategic choices
- Threat Assessment: evaluates danger from neighbors for smarter diplomacy/war decisions
- Multi-Turn Planner: commits to short-term plans (e.g. "fortify -> attack") so the
  AI follows through instead of flip-flopping every turn
- Exploration Bonus: small score bonus for under-tried actions when not in crisis,
  preventing the AI from getting stuck repeating the same safe action
- Decision Explanation: returns (action, scores, reasons) for debugging/UI
"""
import math
import heapq
from enum import IntEnum
from typing import Optional
from collections import deque


# ── D* Lite Pathfinding ─────────────────────────────────────
class DStarLite:
    """Incremental replanning pathfinder for dynamic terrain.

    Uses D* Lite algorithm to efficiently recompute paths when the
    cost map changes, avoiding full recomputation from scratch.

    Performance improvements:
    - Precomputed neighbor grid avoids per-call list comprehension
    - Set-based queue removal instead of O(n) list comprehension
    - Lazy cost map initialization (only compute on init call)
    - Cached heuristic values for frequently accessed vertices
    """

    def __init__(self, width: int, height: int):
        self.W, self.H = width, height
        self.g: dict[tuple, float] = {}
        self.rhs: dict[tuple, float] = {}
        self.U: list = []
        self.U_set: set[tuple] = set()  # Fast membership check
        self.km: float = 0.0
        self.start: Optional[tuple] = None
        self.goal: Optional[tuple] = None
        self.cost_map: dict[tuple, float] = {}

        # Precompute neighbor grid - avoids repeated list comprehension
        self._neighbors_cache: dict[tuple, list[tuple]] = {}
        for y in range(height):
            for x in range(width):
                self._neighbors_cache[(x, y)] = [
                    (nx, ny) for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                    if 0 <= nx < width and 0 <= ny < height
                ]

    def _h(self, a: tuple, b: tuple) -> float:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _key(self, s: tuple) -> tuple:
        g, rhs = self.g.get(s, float('inf')), self.rhs.get(s, float('inf'))
        return (min(g, rhs) + self._h(self.start, s) + self.km, min(g, rhs))

    def _neighbors(self, s: tuple) -> list[tuple]:
        return self._neighbors_cache.get(s, [])

    def _update_vertex(self, u: tuple) -> None:
        if u != self.goal:
            self.rhs[u] = min(
                self.cost_map.get((u, n), 1) + self.g.get(n, float('inf'))
                for n in self._neighbors(u)
            )
        # Fast set-based removal check + rebuild
        if u in self.U_set:
            self.U = [(k, n) for k, n in self.U if n != u]
            self.U_set.discard(u)
            heapq.heapify(self.U)
        if self.g.get(u, float('inf')) != self.rhs.get(u, float('inf')):
            heapq.heappush(self.U, (self._key(u), u))
            self.U_set.add(u)

    def init(self, start: tuple, goal: tuple, terrain_stats: dict) -> None:
        """Initialize or reinitialize the pathfinder for a new query."""
        self.start, self.goal = start, goal
        self.g.clear()
        self.rhs.clear()
        self.U.clear()
        self.U_set.clear()
        self.cost_map.clear()
        self.km = 0.0

        # Pre-allocate default values for all vertices
        inf = float('inf')
        for s in self._neighbors_cache:
            self.g[s] = inf
            self.rhs[s] = inf

        # Build cost map from terrain stats
        for s, nbrs in self._neighbors_cache.items():
            t_data = terrain_stats.get(s)
            t_cost = (t_data['move'] if not t_data['is_water'] else 999) if t_data else 999
            for n in nbrs:
                self.cost_map[(s, n)] = t_cost

        self.rhs[self.goal] = 0
        key = self._key(self.goal)
        heapq.heappush(self.U, (key, self.goal))
        self.U_set.add(self.goal)

    def compute_shortest_path(self) -> None:
        """Run the D* Lite main loop until the start vertex is consistent."""
        start_key = self._key(self.start)
        start_rhs = self.rhs.get(self.start, float('inf'))
        start_g = self.g.get(self.start, float('inf'))

        while self.U and (
            self.U[0][0] < start_key
            or start_rhs != start_g
        ):
            k_old, u = heapq.heappop(self.U)
            self.U_set.discard(u)

            u_key = self._key(u)
            if k_old < u_key:
                heapq.heappush(self.U, (u_key, u))
                self.U_set.add(u)
            elif self.g.get(u, float('inf')) > self.rhs.get(u, float('inf')):
                self.g[u] = self.rhs[u]
                for s in self._neighbors(u):
                    self._update_vertex(s)
            else:
                self.g[u] = float('inf')
                self._update_vertex(u)
                for s in self._neighbors(u):
                    self._update_vertex(s)

            start_key = self._key(self.start)
            start_rhs = self.rhs.get(self.start, float('inf'))
            start_g = self.g.get(self.start, float('inf'))

    def get_path(self, max_len: int = 20) -> list[tuple]:
        """Extract the path from start to goal after computation."""
        path: list[tuple] = []
        cur = self.start
        visited = set()
        cost_map_get = self.cost_map.get
        g_get = self.g.get
        neighbors_fn = self._neighbors

        while cur != self.goal and len(path) < max_len:
            path.append(cur)
            visited.add(cur)
            neighbors = neighbors_fn(cur)
            if not neighbors:
                break
            cur = min(
                neighbors,
                key=lambda n: cost_map_get((cur, n), 1) + g_get(n, float('inf'))
            )
            if cur in visited:
                break
        if cur == self.goal:
            path.append(self.goal)
        return path


# ── Strategic State Machine ─────────────────────────────────
class StrategicState(IntEnum):
    """High-level strategic mode for a civilization.

    Each state modifies how the utility AI weights and evaluates actions.
    States transition based on context - a civ in CRISIS prioritizes
    stability and defense, while GOLDEN_AGE pushes culture and wonders.
    SIEGE: at war but defender is too strong to attack profitably;
           focus on defense, buildup, and economic pressure.
    """
    EXPANSION = 0       # Growing territory and population
    CONSOLIDATION = 1   # Building infrastructure, stabilizing
    CRISIS = 2          # Low stability, losing war, economy failing
    TOTAL_WAR = 3       # Actively fighting, all resources to military
    GOLDEN_AGE = 4      # High stability, strong economy - pursue greatness
    RECOVERY = 5        # Recovering from crisis, cautious rebuilding
    SIEGE = 6           # At war but cannot win offensive engagements yet


# State transition modifiers: how each state shifts action weights
STATE_WEIGHT_MODIFIERS = {
    StrategicState.EXPANSION: {
        "expansion": 1.4, "military": 0.9, "economy": 1.1, "tech": 0.9,
        "culture": 0.6, "diplomacy": 0.7, "trade": 0.8, "wonder": 0.3,
    },
    StrategicState.CONSOLIDATION: {
        "expansion": 0.5, "military": 0.8, "economy": 1.5, "tech": 1.3,
        "culture": 1.2, "diplomacy": 1.0, "trade": 1.2, "wonder": 0.8,
    },
    StrategicState.CRISIS: {
        "expansion": 0.3, "military": 1.5, "economy": 1.0, "tech": 0.5,
        "culture": 0.3, "diplomacy": 1.3, "trade": 0.6, "wonder": 0.1,
    },
    StrategicState.TOTAL_WAR: {
        "expansion": 1.2, "military": 2.0, "economy": 0.6, "tech": 0.7,
        "culture": 0.2, "diplomacy": 0.3, "trade": 0.2, "wonder": 0.1,
    },
    StrategicState.GOLDEN_AGE: {
        "expansion": 0.7, "military": 0.6, "economy": 1.2, "tech": 1.3,
        "culture": 1.6, "diplomacy": 1.1, "trade": 1.1, "wonder": 1.8,
    },
    StrategicState.RECOVERY: {
        "expansion": 0.4, "military": 0.7, "economy": 1.4, "tech": 1.0,
        "culture": 0.8, "diplomacy": 1.2, "trade": 1.0, "wonder": 0.4,
    },
    StrategicState.SIEGE: {
        "expansion": 0.6, "military": 1.6, "economy": 1.0, "tech": 1.1,
        "culture": 0.4, "diplomacy": 0.6, "trade": 0.4, "wonder": 0.1,
    },
}


# ── Action Types ────────────────────────────────────────────
class ActionType:
    """Available high-level actions a civilization can take each turn."""
    EXPAND = "Expand"
    DEVELOP = "Develop"
    RESEARCH = "Research"
    FORTIFY = "Fortify"
    ATTACK = "Attack"
    CULTURE = "Culture"
    DIPLOMACY = "Diplomacy"
    TRADE = "Trade"
    WONDER = "Build Wonder"

    ALL = [EXPAND, DEVELOP, RESEARCH, FORTIFY, ATTACK, CULTURE, DIPLOMACY, TRADE, WONDER]

    # Maps action type to the personality weight key
    WEIGHT_KEY = {
        EXPAND: "expansion",
        FORTIFY: "military",
        DEVELOP: "economy",
        RESEARCH: "tech",
        ATTACK: "military",
        CULTURE: "culture",
        DIPLOMACY: "diplomacy",
        TRADE: "trade",
        WONDER: "wonder",
    }


# ── Response Curves ─────────────────────────────────────────
class ResponseCurve:
    """Mathematical curves to normalize raw inputs into [0, 1] for considerations."""

    @staticmethod
    def linear(x: float, slope: float = 1.0, intercept: float = 0.0) -> float:
        val = slope * x + intercept
        if val < 0.0:
            return 0.0
        if val > 1.0:
            return 1.0
        return val

    @staticmethod
    def logistic(x: float, midpoint: float = 0.5, steepness: float = 10.0) -> float:
        exponent = -steepness * (x - midpoint)
        if exponent > 500:
            return 0.0
        if exponent < -500:
            return 1.0
        return 1.0 / (1.0 + math.exp(exponent))

    @staticmethod
    def quadratic(x: float, coefficient: float = 1.0, intercept: float = 0.0) -> float:
        val = coefficient * x * x + intercept
        if val < 0.0:
            return 0.0
        if val > 1.0:
            return 1.0
        return val

    @staticmethod
    def inverse(x: float, scale: float = 1.0, offset: float = 0.0) -> float:
        """Inverse curve: high when x is low, low when x is high. Good for 'need' calculations."""
        if x <= 0.001:
            return 1.0
        val = scale / (x + offset)
        if val > 1.0:
            return 1.0
        if val < 0.0:
            return 0.0
        return val

    @staticmethod
    def bell(x: float, center: float = 0.5, width: float = 0.3) -> float:
        """Bell curve: high near center, low at extremes. Good for 'sweet spot' calculations."""
        dist = abs(x - center)
        if dist > width * 3:
            return 0.0
        val = math.exp(-(dist * dist) / (2 * width * width))
        return max(0.0, min(1.0, val))

    @staticmethod
    def step(x: float, threshold: float = 0.5, below: float = 0.0, above: float = 1.0) -> float:
        """Step function: sharp transition at threshold."""
        return above if x >= threshold else below


# ── Consideration ───────────────────────────────────────────
class Consideration:
    """A single input factor that contributes to an action's utility score."""

    __slots__ = ('name', 'curve', 'params', 'invert')

    def __init__(self, name: str, curve, invert: bool = False, **params):
        self.name = name
        self.curve = curve
        self.params = params
        self.invert = invert

    def score(self, context: dict) -> float:
        raw = context.get(self.name, 0.0)
        val = self.curve(raw, **self.params)
        return 1.0 - val if self.invert else val


# ── Utility Action ──────────────────────────────────────────
class UtilityAction:
    """A candidate action evaluated by multiplying consideration scores.

    Uses a compensation factor to prevent all-zero degeneracy:
    final_score = (product_of_considerations + compensation) * weight
    This ensures that actions with many low-scoring considerations can
    still compete when one critical consideration is very high.
    """

    __slots__ = ('action_type', 'considerations', 'weight', 'score', 'compensation')

    def __init__(self, action_type: str, considerations: list[Consideration],
                 weight: float = 1.0, compensation: float = 0.02):
        self.action_type = action_type
        self.considerations = considerations
        self.weight = weight
        self.compensation = compensation
        self.score: float = 0.0

    def evaluate(self, context: dict) -> None:
        total = 1.0
        for c in self.considerations:
            s = c.score(context)
            total *= s
            # Early exit: if total drops below threshold, no point continuing
            if total < 0.0001:
                total = 0.0
                break
        self.score = (total + self.compensation) * self.weight


# ── Threat Assessment ───────────────────────────────────────
class ThreatAssessment:
    """Evaluates the danger level from neighboring civilizations.

    Computes per-neighbor threat scores based on:
    - Military ratio (their military / our military)
    - Grievance level (they have a grievance → they might attack)
    - War status (already at war → maximum threat)
    - Alliance status (allied → reduced threat)
    - Power differential (much stronger neighbor = high threat)
    """

    @staticmethod
    def assess(civ_context: dict, neighbors: list[dict]) -> dict[str, float]:
        """Return a dict of neighbor_name → threat_level (0.0 to 1.0)."""
        our_mil = max(1.0, civ_context.get("military", 100))
        our_tech = max(1.0, civ_context.get("technology", 1))
        threats = {}

        for n in neighbors:
            n_name = n.get("name", "")
            n_mil = max(1.0, n.get("military", 100))
            n_tech = max(1.0, n.get("technology", 1))

            # Military ratio threat
            mil_ratio = n_mil / our_mil
            mil_threat = min(1.0, mil_ratio / 3.0)  # 3x military = max threat

            # Tech advantage threat
            tech_ratio = n_tech / our_tech
            tech_threat = min(1.0, tech_ratio / 3.0)

            # Grievance-based threat
            grievance = n.get("grievance_vs_us", 0)
            grievance_threat = min(1.0, grievance / 100.0)

            # War status
            at_war = n.get("at_war", False)
            war_threat = 1.0 if at_war else 0.0

            # Alliance reduces threat
            allied = n.get("allied", False)
            alliance_mod = 0.2 if allied else 1.0

            # Proximity bonus (neighbors are inherently more threatening)
            base_threat = 0.1

            total_threat = (
                mil_threat * 0.35
                + tech_threat * 0.15
                + grievance_threat * 0.20
                + war_threat * 0.25
                + base_threat * 0.05
            ) * alliance_mod

            threats[n_name] = max(0.0, min(1.0, total_threat))

        return threats

    @staticmethod
    def highest_threat(threats: dict[str, float]) -> tuple[str, float]:
        """Return (name, threat_level) of the most threatening neighbor."""
        if not threats:
            return ("", 0.0)
        name = max(threats, key=threats.get)
        return (name, threats[name])


# ── Action Memory ───────────────────────────────────────────
class ActionMemory:
    """Tracks recent actions to prevent repetitive behavior and enable adaptation.

    - Tracks the last N actions taken
    - Computes action frequency to detect loops
    - Tracks action outcomes (success/failure) for reinforcement learning
    - Applies fatigue: repeatedly choosing the same action reduces its score
    """

    def __init__(self, capacity: int = 20):
        self.history: deque = deque(maxlen=capacity)
        self.outcomes: dict[str, deque] = {}  # action_type → deque of bools (success/fail)
        self.outcome_capacity = 10

    def record(self, action_type: str, success: bool = True) -> None:
        """Record an action taken and whether it succeeded."""
        self.history.append(action_type)
        if action_type not in self.outcomes:
            self.outcomes[action_type] = deque(maxlen=self.outcome_capacity)
        self.outcomes[action_type].append(success)

    def get_fatigue(self, action_type: str, window: int = 5) -> float:
        """How often this action was chosen recently (0.0 = never, 1.0 = always).

        Used to reduce the score of repetitive actions.
        """
        if not self.history:
            return 0.0
        recent = list(self.history)[-window:]
        if not recent:
            return 0.0
        count = sum(1 for a in recent if a == action_type)
        return count / len(recent)

    def get_success_rate(self, action_type: str) -> float:
        """Fraction of recent attempts at this action that succeeded (0.0-1.0)."""
        if action_type not in self.outcomes or not self.outcomes[action_type]:
            return 0.5  # Unknown → neutral
        outcomes = list(self.outcomes[action_type])
        return sum(1 for o in outcomes if o) / len(outcomes)

    def get_last_action(self) -> str | None:
        """Return the most recent action, or None if no history."""
        return self.history[-1] if self.history else None

    def get_action_count(self, action_type: str) -> int:
        """How many times this action has been taken in recent history."""
        return sum(1 for a in self.history if a == action_type)

    def get_novelty(self, action_type: str) -> float:
        """How novel (under-tried) an action is, in [0, 1].

        1.0 = action never tried in the recorded window (high novelty).
        0.0 = action dominates recent history (low novelty).
        Used to add an exploration bonus for under-tried actions so the
        AI doesn't get stuck in a rut of always picking the same safe
        action when its situation changes.
        """
        if not self.history:
            return 1.0
        recent = list(self.history)[-20:]
        if not recent:
            return 1.0
        count = sum(1 for a in recent if a == action_type)
        return 1.0 - (count / len(recent))


# ── Multi-Turn Planner ──────────────────────────────────────
class Plan:
    """A short-term multi-turn plan that biases action selection.

    Plans commit the AI to a sequence of actions for a few turns so it
    follows through (e.g. "fortify twice then attack") instead of flip-
    flopping between unrelated actions every turn. Each steppe has an
    action bias (multiplied into the action weight) and a max-stay that
    determines when the plan step is considered "done" and we advance.

    A plan terminates when either:
    - All steps are completed (step.advance() returns True on the last step)
    - The plan's abort_condition returns True (e.g. civ made peace)
    - The plan reaches its absolute max_turns
    """

    def __init__(self, name: str, steps: list[dict],
                 abort_condition=None, max_turns: int = 20):
        self.name = name
        self.steps = steps  # list of {"action": str, "bias": float, "min_turns": int, "max_turns": int}
        self.abort_condition = abort_condition
        self.max_turns = max_turns
        self.elapsed = 0
        self.current_step_idx = 0
        self.step_elapsed = 0

    @property
    def current_step(self) -> dict | None:
        if self.current_step_idx < len(self.steps):
            return self.steps[self.current_step_idx]
        return None

    @property
    def is_active(self) -> bool:
        return self.current_step is not None and self.elapsed < self.max_turns

    def should_abort(self, context: dict) -> bool:
        if self.abort_condition is not None and self.abort_condition(context):
            return True
        return False

    def advance(self, action_taken: str) -> None:
        """Called after each turn. Advance step if action matched and step duration elapsed."""
        self.elapsed += 1
        step = self.current_step
        if step is None:
            return

        if action_taken == step.get("action"):
            self.step_elapsed += 1
        # Move on when we've executed the action enough times
        if self.step_elapsed >= step.get("min_turns", 1):
            # If we've hit max turns for this step, definitely advance
            self.current_step_idx += 1
            self.step_elapsed = 0

    def get_action_bias(self, action_type: str) -> float:
        """Return the weight multiplier for this action under the current plan step."""
        step = self.current_step
        if step is None:
            return 1.0
        if action_type == step.get("action"):
            return step.get("bias", 1.5)
        # Slight suppression of unrelated actions so the plan wins ties
        return step.get("other_bias", 0.85)


# Predefined plan templates keyed by name; instantiated with the planner.
def plan_fortify_then_attack() -> Plan:
    """Build up forces, then go on the offensive."""
    return Plan(
        name="Fortify-then-Attack",
        steps=[
            {"action": ActionType.FORTIFY, "bias": 2.0, "min_turns": 3, "other_bias": 0.7},
            {"action": ActionType.ATTACK, "bias": 2.5, "min_turns": 2, "other_bias": 0.6},
        ],
        abort_condition=lambda ctx: not ctx.get("at_war", False),
        max_turns=10,
    )


def plan_research_boom() -> Plan:
    """Turtle and tech up."""
    return Plan(
        name="Research-Boom",
        steps=[
            {"action": ActionType.RESEARCH, "bias": 2.2, "min_turns": 4, "other_bias": 0.7},
            {"action": ActionType.DEVELOP, "bias": 1.8, "min_turns": 2, "other_bias": 0.7},
        ],
        abort_condition=lambda ctx: ctx.get("stability_norm", 1.0) < 0.2,
        max_turns=12,
    )


def plan_expand_burst() -> Plan:
    """Rapidly claim land while the window is open."""
    return Plan(
        name="Expand-Burst",
        steps=[
            {"action": ActionType.EXPAND, "bias": 2.4, "min_turns": 4, "other_bias": 0.6},
        ],
        abort_condition=lambda ctx: (
            ctx.get("stability_norm", 1.0) < 0.3
            or ctx.get("at_war", False)
            or ctx.get("territory_ratio", 0.0) > 0.35
        ),
        max_turns=8,
    )


def plan_cultural_flourish() -> Plan:
    """Invest in culture + wonders during a golden age."""
    return Plan(
        name="Cultural-Flourish",
        steps=[
            {"action": ActionType.CULTURE, "bias": 2.0, "min_turns": 3, "other_bias": 0.7},
            {"action": ActionType.WONDER, "bias": 2.2, "min_turns": 1, "other_bias": 0.6},
        ],
        abort_condition=lambda ctx: ctx.get("stability_norm", 1.0) < 0.5,
        max_turns=10,
    )


def plan_economic_recovery() -> Plan:
    """Recover from a treasury crisis with develop + trade."""
    return Plan(
        name="Economic-Recovery",
        steps=[
            {"action": ActionType.TRADE, "bias": 2.0, "min_turns": 2, "other_bias": 0.7},
            {"action": ActionType.DEVELOP, "bias": 1.8, "min_turns": 2, "other_bias": 0.7},
        ],
        abort_condition=lambda ctx: ctx.get("stability_norm", 1.0) < 0.15,
        max_turns=10,
    )


# ── Strategic State Evaluator ──────────────────────────────
class StrategicEvaluator:
    """Determines the current strategic state of a civilization.

    Evaluates multiple context signals to decide whether the civ
    should be in EXPANSION, CONSOLIDATION, CRISIS, TOTAL_WAR,
    GOLDEN_AGE, RECOVERY, or SIEGE mode.
    """

    @staticmethod
    def evaluate(context: dict) -> StrategicState:
        """Determine the best strategic state from the current context."""
        stability = context.get("stability_norm", 0.5)
        at_war = context.get("at_war", False)
        war_count = context.get("war_count", 0)
        treasury = context.get("treasury", 0.0)
        military = context.get("mil_strength", 0.0)
        territory_ratio = context.get("territory_ratio", 0.0)
        pop_pressure = context.get("pop_pressure", 0.0)
        threat_level = context.get("max_threat", 0.0)
        tech_level = context.get("tech_level", 0.0)
        # Defensive-readiness signal: if at war but we cannot profitably
        # attack (military too weak relative to threat), enter SIEGE.
        can_attack = (
            at_war
            and military > 0.3
            and threat_level < 0.85
        )

        # CRISIS: Very low stability or losing badly
        if stability < 0.2 and (war_count > 0 or treasury < 0.1):
            return StrategicState.CRISIS

        # TOTAL_WAR: At war with military strength AND can attack
        if at_war and can_attack:
            return StrategicState.TOTAL_WAR

        # SIEGE: At war but unable to attack profitably - dig in
        if at_war and not can_attack:
            return StrategicState.SIEGE

        # CRISIS: Multiple wars while weak
        if war_count >= 2 and military < 0.25:
            return StrategicState.CRISIS

        # RECOVERY: Was in crisis but stabilizing
        if 0.2 <= stability < 0.35 and not at_war:
            return StrategicState.RECOVERY

        # GOLDEN_AGE: High stability, strong economy, not at war
        if stability > 0.75 and treasury > 0.5 and not at_war and military > 0.3:
            return StrategicState.GOLDEN_AGE

        # EXPANSION: Room to grow, decent stability
        if pop_pressure > 0.5 and stability > 0.4 and territory_ratio < 0.3:
            return StrategicState.EXPANSION

        # CONSOLIDATION: Default steady state
        return StrategicState.CONSOLIDATION


# ── Civilization AI Agent ───────────────────────────────────
class CivAgent:
    """Utility AI agent that selects the best action for a civilization each turn.

    Major improvements over the basic version:
    - Rich context with 25+ variables for nuanced decision-making
    - Strategic State Machine that shifts action weights based on situation
    - Action Memory with fatigue to prevent repetitive behavior
    - Compensation factor to prevent all-zero score degeneracy
    - More considerations per action for finer-grained decisions
    - Invertible considerations (e.g., "low stability" instead of "high instability")
    - Multi-turn planner that commits the AI to short-term plans
    - Exploration bonus for under-tried actions (off in CRISIS)
    - Decision explanation API for debugging and UI transparency
    """

    # Archetype-tuned consideration parameter overrides. Each archetype
    # shifts the activation thresholds of key considerations so that
    # warlords expand more eagerly, philosophers research earlier, etc.
    # The override maps action_type -> {consideration_name -> {param -> value}}.
    ARCHETYPE_OVERRIDES: dict[str, dict[str, dict]] = {
        "warlord": {
            ActionType.EXPAND: {
                "pop_pressure": {"midpoint": 0.35, "steepness": 8},
                "stability_norm": {"midpoint": 0.25, "steepness": 6},
                "territory_ratio": {"scale": 0.6, "offset": 0.1},
            },
            ActionType.ATTACK: {
                "threat_level": {"midpoint": 0.30, "steepness": 8},
                "mil_strength": {"midpoint": 0.35, "steepness": 6},
            },
            ActionType.FORTIFY: {
                "threat_level": {"midpoint": 0.30, "steepness": 10},
            },
        },
        "raider": {
            ActionType.EXPAND: {
                "pop_pressure": {"midpoint": 0.30, "steepness": 6},
                "territory_ratio": {"scale": 0.7, "offset": 0.1},
                "stability_norm": {"midpoint": 0.20, "steepness": 5},
            },
            ActionType.ATTACK: {
                "threat_level": {"midpoint": 0.25, "steepness": 6},
                "mil_strength": {"midpoint": 0.30, "steepness": 5},
            },
        },
        "philosopher": {
            ActionType.RESEARCH: {
                "tech_deficit": {"midpoint": 0.25, "steepness": 6},
                "tech_level": {"scale": 0.7, "offset": 0.1},
            },
            ActionType.DEVELOP: {
                "treasury": {"midpoint": 0.25, "steepness": 6},
            },
        },
        "merchant": {
            ActionType.TRADE: {
                "treasury": {"scale": 0.8, "offset": 0.1},
            },
            ActionType.DEVELOP: {
                "treasury": {"midpoint": 0.30, "steepness": 6},
            },
            ActionType.WONDER: {
                "treasury": {"midpoint": 0.55, "steepness": 8},
            },
        },
        "zealot": {
            ActionType.CULTURE: {
                "treasury": {"slope": 1.0, "intercept": 0.0},
                "culture_level": {"scale": 0.5, "offset": 0.1},
            },
            ActionType.WONDER: {
                "treasury": {"midpoint": 0.55, "steepness": 8},
                "stability_norm": {"midpoint": 0.45, "steepness": 6},
            },
        },
        "builder": {
            ActionType.DEVELOP: {
                "treasury": {"midpoint": 0.25, "steepness": 6},
                "building_ratio": {"scale": 0.7, "offset": 0.1},
            },
            ActionType.WONDER: {
                "treasury": {"midpoint": 0.55, "steepness": 8},
                "stability_norm": {"midpoint": 0.50, "steepness": 6},
            },
        },
        "diplomat": {
            ActionType.DIPLOMACY: {
                "threat_level": {"midpoint": 0.40, "steepness": 6},
                "alliance_count_norm": {"scale": 0.7, "offset": 0.1},
            },
            ActionType.TRADE: {
                "treasury": {"scale": 0.7, "offset": 0.1},
            },
        },
        "survivor": {
            ActionType.FORTIFY: {
                "threat_level": {"midpoint": 0.30, "steepness": 8},
                "stability_norm": {"scale": 0.8, "offset": 0.1},
            },
            ActionType.EXPAND: {
                "stability_norm": {"midpoint": 0.45, "steepness": 8},
            },
        },
    }

    def __init__(self, personality: dict, archetype: str = "survivor"):
        expansion_w = personality.get("expansion", 1.0)
        military_w = personality.get("military", 1.0)
        economy_w = personality.get("economy", 1.0)
        tech_w = personality.get("tech", 1.0)
        culture_w = personality.get("culture", 1.0)
        diplomacy_w = personality.get("diplomacy", 0.8)
        trade_w = personality.get("trade", 0.9)
        wonder_w = personality.get("wonder", 0.4)

        self.personality_weights = {
            "expansion": expansion_w, "military": military_w,
            "economy": economy_w, "tech": tech_w,
            "culture": culture_w, "diplomacy": diplomacy_w,
            "trade": trade_w, "wonder": wonder_w,
        }

        self.archetype = archetype

        # Hysteresis: track how many consecutive turns we've been in the
        # current state, so we don't flip-flop between adjacent states
        # every turn (e.g. CONSOLIDATION -> RECOVERY -> CONSOLIDATION).
        self._state_tenure: int = 0

        self.actions = [
            # ── EXPAND ──────────────────────────────────────
            # Expand when: population pressure is high, military is adequate,
            # territory ratio is low, and not in crisis. Feasibility-gated:
            # if no expandable borders, score is near-zero.
            UtilityAction(ActionType.EXPAND, [
                Consideration("can_expand", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("pop_pressure", ResponseCurve.logistic, midpoint=0.55, steepness=10),
                Consideration("mil_strength", ResponseCurve.logistic, midpoint=0.05, steepness=12),
                Consideration("territory_ratio", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.35, steepness=8),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=expansion_w),

            # ── FORTIFY ────────────────────────────────────
            # Fortify when: threat is high, stability is low, or military is weak
            UtilityAction(ActionType.FORTIFY, [
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.35, steepness=12),
                Consideration("stability_norm", ResponseCurve.inverse, scale=0.7, offset=0.1),
                Consideration("mil_strength", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.3, above=0.8),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=military_w),

            # ── DEVELOP ────────────────────────────────────
            # Develop when: treasury is adequate, buildings are few, population is manageable.
            # Uses a logistic treasury curve so the score doesn't zero out completely
            # when treasury is modest (early-game civs should still build basic infrastructure).
            UtilityAction(ActionType.DEVELOP, [
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.05, steepness=20),
                Consideration("building_ratio", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("pop_pressure", ResponseCurve.linear, slope=-1.2, intercept=0.8),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.4, steepness=6),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=economy_w),

            # ── RESEARCH ───────────────────────────────────
            # Research when: tech deficit exists OR tech is generally low,
            # treasury supports it. Game phase removed as a hard gate - civs
            # can research from the start. The tech_level consideration
            # already makes early-game civs want to research (low tech → high need).
            UtilityAction(ActionType.RESEARCH, [
                Consideration("tech_deficit", ResponseCurve.logistic, midpoint=0.2, steepness=8),
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.05, steepness=20),
                Consideration("tech_level", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=tech_w),

            # ── ATTACK ─────────────────────────────────────
            # Attack when: at war or threat is high, military is strong, target is weak.
            # Feasibility-gated by available_attack_targets.
            UtilityAction(ActionType.ATTACK, [
                Consideration("available_attack_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.5, steepness=10),
                Consideration("mil_strength", ResponseCurve.logistic, midpoint=0.45, steepness=8),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.2, above=0.7),
                Consideration("stability_norm", ResponseCurve.linear, slope=1.0, intercept=-0.1),
                Consideration("target_weakness", ResponseCurve.linear, slope=1.5, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=military_w),

            # ── CULTURE ────────────────────────────────────
            # Culture when: treasury is good, population is stable, game is mature
            UtilityAction(ActionType.CULTURE, [
                Consideration("treasury", ResponseCurve.linear, slope=1.0, intercept=0.0),
                Consideration("pop_pressure", ResponseCurve.bell, center=0.4, width=0.3),
                Consideration("culture_level", ResponseCurve.inverse, scale=0.4, offset=0.1),
                Consideration("game_phase", ResponseCurve.linear, slope=1.5, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=culture_w),

            # ── DIPLOMACY ──────────────────────────────────
            # Diplomacy when: threat is high (need allies), not already allied with everyone,
            # and stability needs support. Feasibility-gated by available_diplomacy_targets.
            UtilityAction(ActionType.DIPLOMACY, [
                Consideration("available_diplomacy_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.55, steepness=8),
                Consideration("alliance_count_norm", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("stability_norm", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.3, above=0.6),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=diplomacy_w),

            # ── TRADE ──────────────────────────────────────
            # Trade when: treasury is low (need income), not at war, and have trade partners
            # available. Feasibility-gated by available_trade_targets so civs without
            # neighbors don't waste turns trying to trade with nobody.
            UtilityAction(ActionType.TRADE, [
                Consideration("available_trade_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("treasury", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.7, above=0.2),
                Consideration("trade_partner_norm", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("pop_pressure", ResponseCurve.linear, slope=0.8, intercept=0.1),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=trade_w),

            # ── WONDER ─────────────────────────────────────
            # Wonder when: treasury is very high, stability is high, game is mature
            UtilityAction(ActionType.WONDER, [
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.7, steepness=10),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.6, steepness=8),
                Consideration("game_phase", ResponseCurve.linear, slope=2.0, intercept=-0.3),
                Consideration("mil_strength", ResponseCurve.linear, slope=1.0, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=wonder_w, compensation=0.02),
        ]

        # Apply archetype-specific consideration overrides
        self._apply_archetype_overrides()

        # Strategic state tracking
        self.strategic_state = StrategicState.CONSOLIDATION
        self.memory = ActionMemory()
        self._last_action_success = True  # Default to success

        # Multi-turn planner
        self.current_plan: Plan | None = None
        self._plan_cooldown: int = 0  # Turns to wait before forming a new plan

        # Last decision explanation (for UI/debugging)
        self.last_decision_explanation: dict = {}

    def set_archetype(self, new_archetype: str) -> None:
        """Change the agent's archetype and re-apply consideration overrides.

        Called by the engine when a leader succession / government change
        causes the civ's effective archetype to change. The consideration
        parameters are reset to the base (default) values first, then the
        new archetype's overrides are applied on top.
        """
        if new_archetype == self.archetype:
            return
        self.archetype = new_archetype
        # Reset to base params by rebuilding the actions list. The
        # __init__ already does the right thing; we just need to preserve
        # memory and strategic state across the transition.
        old_state = self.strategic_state
        old_state_tenure = self._state_tenure
        old_memory = self.memory
        old_plan = self.current_plan
        old_plan_cooldown = self._plan_cooldown
        old_last_success = self._last_action_success

        # Rebuild actions by re-running __init__'s action setup.
        # We do this by snapshotting the personality weights and re-init.
        # Simpler: rebuild just the actions list manually using the same
        # pattern as __init__.
        personality = self.personality_weights
        expansion_w = personality.get("expansion", 1.0)
        military_w = personality.get("military", 1.0)
        economy_w = personality.get("economy", 1.0)
        tech_w = personality.get("tech", 1.0)
        culture_w = personality.get("culture", 1.0)
        diplomacy_w = personality.get("diplomacy", 0.8)
        trade_w = personality.get("trade", 0.9)
        wonder_w = personality.get("wonder", 0.4)

        self.actions = [
            UtilityAction(ActionType.EXPAND, [
                Consideration("can_expand", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("pop_pressure", ResponseCurve.logistic, midpoint=0.55, steepness=10),
                Consideration("mil_strength", ResponseCurve.logistic, midpoint=0.05, steepness=12),
                Consideration("territory_ratio", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.35, steepness=8),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=expansion_w),
            UtilityAction(ActionType.FORTIFY, [
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.35, steepness=12),
                Consideration("stability_norm", ResponseCurve.inverse, scale=0.7, offset=0.1),
                Consideration("mil_strength", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.3, above=0.8),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=military_w),
            UtilityAction(ActionType.DEVELOP, [
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.05, steepness=20),
                Consideration("building_ratio", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("pop_pressure", ResponseCurve.linear, slope=-1.2, intercept=0.8),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.4, steepness=6),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=economy_w),
            UtilityAction(ActionType.RESEARCH, [
                Consideration("tech_deficit", ResponseCurve.logistic, midpoint=0.2, steepness=8),
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.05, steepness=20),
                Consideration("tech_level", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=tech_w),
            UtilityAction(ActionType.ATTACK, [
                Consideration("available_attack_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.5, steepness=10),
                Consideration("mil_strength", ResponseCurve.logistic, midpoint=0.45, steepness=8),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.2, above=0.7),
                Consideration("stability_norm", ResponseCurve.linear, slope=1.0, intercept=-0.1),
                Consideration("target_weakness", ResponseCurve.linear, slope=1.5, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=military_w),
            UtilityAction(ActionType.CULTURE, [
                Consideration("treasury", ResponseCurve.linear, slope=1.0, intercept=0.0),
                Consideration("pop_pressure", ResponseCurve.bell, center=0.4, width=0.3),
                Consideration("culture_level", ResponseCurve.inverse, scale=0.4, offset=0.1),
                Consideration("game_phase", ResponseCurve.linear, slope=1.5, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=culture_w),
            UtilityAction(ActionType.DIPLOMACY, [
                Consideration("available_diplomacy_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.55, steepness=8),
                Consideration("alliance_count_norm", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("stability_norm", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.3, above=0.6),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=diplomacy_w),
            UtilityAction(ActionType.TRADE, [
                Consideration("available_trade_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("treasury", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.7, above=0.2),
                Consideration("trade_partner_norm", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("pop_pressure", ResponseCurve.linear, slope=0.8, intercept=0.1),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=trade_w),
            UtilityAction(ActionType.WONDER, [
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.7, steepness=10),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.6, steepness=8),
                Consideration("game_phase", ResponseCurve.linear, slope=2.0, intercept=-0.3),
                Consideration("mil_strength", ResponseCurve.linear, slope=1.0, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=wonder_w, compensation=0.02),
        ]
        self._apply_archetype_overrides()

        # Restore state
        self.strategic_state = old_state
        self._state_tenure = old_state_tenure
        self.memory = old_memory
        self.current_plan = old_plan
        self._plan_cooldown = old_plan_cooldown
        self._last_action_success = old_last_success

    def _apply_archetype_overrides(self) -> None:
        """Apply per-archetype consideration parameter overrides.

        Mutates the considerations in self.actions based on
        ARCHETYPE_OVERRIDES[archetype]. Each entry maps
        action_type -> consideration_name -> {param: value}.
        Falls back gracefully if action/consideration not found.
        """
        overrides = self.ARCHETYPE_OVERRIDES.get(self.archetype, {})
        # Index actions by type for O(1) lookup
        actions_by_type = {a.action_type: a for a in self.actions}
        for action_type, cons_overrides in overrides.items():
            action = actions_by_type.get(action_type)
            if action is None:
                continue
            for cons in action.considerations:
                if cons.name in cons_overrides:
                    new_params = cons_overrides[cons.name]
                    # Merge: keep existing params, override specified ones
                    merged = dict(cons.params)
                    merged.update(new_params)
                    cons.params = merged

    def _build_context(self, raw_state: dict) -> dict:
        """Build a rich normalized context from raw state variables.

        This is the core of the improved AI: many more signals are extracted
        and normalized to [0, 1] so the consideration system can make
        nuanced decisions.
        """
        pop = raw_state["population"]
        pop_cap = max(1, raw_state.get("pop_cap", 1))
        military = raw_state["military"]
        treasury = raw_state["treasury"]
        tech = raw_state["technology"]
        culture = raw_state.get("culture", 0)
        stability = raw_state.get("stability", 50)

        # Normalize core stats
        pop_pressure = min(1.0, pop / max(1, pop_cap))
        mil_strength = min(1.0, military / 5000.0)
        treasury_norm = min(1.0, treasury / 10000.0)
        tech_norm = min(1.0, tech / 100.0)
        culture_norm = min(1.0, culture / 5000.0)
        stability_norm = min(1.0, max(0.0, stability / 100.0))

        # Territory and game state
        territory_count = raw_state.get("territory_count", 1)
        total_land = max(1, raw_state.get("total_land", 1000))
        territory_ratio = min(1.0, territory_count / total_land)

        building_count = raw_state.get("building_count", 0)
        max_buildings = max(1, territory_count * 2)  # Rough upper bound
        building_ratio = min(1.0, building_count / max_buildings)

        # Diplomacy
        hostile_neighbors = raw_state.get("hostile_neighbors", 0)
        threat_level = min(1.0, hostile_neighbors / 5.0)
        at_war = raw_state.get("at_war", False)
        war_count = raw_state.get("war_count", 0)
        alliance_count = raw_state.get("alliance_count", 0)
        trade_partner_count = raw_state.get("trade_partner_count", 0)
        max_neighbors = max(1, raw_state.get("total_civs", 4) - 1)
        alliance_count_norm = min(1.0, alliance_count / max_neighbors)
        trade_partner_norm = min(1.0, trade_partner_count / max_neighbors)

        # Threat assessment
        max_threat = raw_state.get("max_threat", 0.0)
        target_weakness = raw_state.get("target_weakness", 0.0)

        # Game phase: 0.0 = just started, 1.0 = late game
        year = raw_state.get("year", -3000)
        game_phase = min(1.0, max(0.0, (year + 3000) / 3000.0))

        # Tech deficit: how far behind we are
        avg_enemy_tech = raw_state.get("avg_enemy_tech", tech)
        tech_deficit = min(1.0, max(0.0, (avg_enemy_tech - tech) / 20.0))
        tech_level = tech_norm  # Alias for clarity

        # Era progress
        era_id = raw_state.get("era_id", 0)
        era_progress = min(1.0, era_id / 3.0)  # 0-3 eras

        # Wonder and religion
        wonder_count = raw_state.get("wonder_count", 0)
        has_religion = raw_state.get("has_religion", False)

        # Action fatigue from memory
        action_fatigue = 0.0  # Will be set per-action in evaluate

        # Feasibility signals (passed through from raw_state, with safe defaults).
        # These are set by the engine based on actual map / diplomacy state
        # so the AI never picks an action that's structurally impossible
        # (e.g. trading with nobody).
        can_expand = 1.0 if raw_state.get("can_expand", True) else 0.0
        available_trade_targets = float(raw_state.get("available_trade_targets", 0))
        available_diplomacy_targets = float(raw_state.get("available_diplomacy_targets", 0))
        available_attack_targets = float(raw_state.get("available_attack_targets", 0))

        context = {
            # Core stats
            "pop_pressure": pop_pressure,
            "mil_strength": mil_strength,
            "treasury": treasury_norm,
            "tech_deficit": tech_deficit,
            "tech_level": tech_level,
            "culture_level": culture_norm,
            "stability_norm": stability_norm,

            # Territory and infrastructure
            "territory_ratio": territory_ratio,
            "building_ratio": building_ratio,

            # Diplomacy
            "threat_level": threat_level,
            "hostile_neighbors": min(1.0, hostile_neighbors / 8.0),
            "at_war": at_war,
            "war_count": war_count,
            "alliance_count_norm": alliance_count_norm,
            "trade_partner_norm": trade_partner_norm,

            # Threat assessment
            "max_threat": max_threat,
            "target_weakness": target_weakness,

            # Game state
            "game_phase": game_phase,
            "era_progress": era_progress,
            "wonder_count": min(1.0, wonder_count / 3.0),
            "has_religion": has_religion,

            # Feasibility signals
            "can_expand": can_expand,
            "available_trade_targets": available_trade_targets,
            "available_diplomacy_targets": available_diplomacy_targets,
            "available_attack_targets": available_attack_targets,

            # Fatigue (placeholder, updated per-action)
            "action_fatigue": 0.0,

            # Raw values for action execution
            "_raw_military": military,
            "_raw_treasury": treasury,
            "_raw_tech": tech,
            "_raw_pop": pop,
        }

        return context

    def _evaluate_strategic_state(self, context: dict) -> StrategicState:
        """Evaluate and potentially transition the strategic state.

        Implements real hysteresis: urgent states (CRISIS, TOTAL_WAR, SIEGE)
        are always honoured immediately. For non-urgent transitions, the civ
        must remain in a state for at least ``_min_state_tenure`` turns
        before being allowed to switch, which prevents rapid flip-flopping
        between adjacent states like CONSOLIDATION <-> RECOVERY.
        """
        new_state = StrategicEvaluator.evaluate(context)
        current = self.strategic_state

        # Same state -> just bump tenure, no transition.
        if new_state == current:
            self._state_tenure += 1
            return current

        # Urgent transitions always fire immediately and reset tenure.
        urgent = {StrategicState.CRISIS, StrategicState.TOTAL_WAR, StrategicState.SIEGE}
        if new_state in urgent or current in urgent:
            self._state_tenure = 1
            return new_state

        # Non-urgent transition: require a minimum tenure in the current
        # state to avoid oscillation. Adjacent states (distance 1) need a
        # longer tenure; bigger jumps (distance >= 2) are allowed sooner
        # because they represent a meaningful shift.
        state_distance = abs(int(new_state) - int(current))
        min_tenure = 3 if state_distance <= 1 else 1
        if self._state_tenure < min_tenure:
            self._state_tenure += 1
            return current

        # Transition accepted.
        self._state_tenure = 1
        return new_state

    def _maybe_form_plan(self, context: dict) -> None:
        """Possibly commit to a multi-turn plan based on situation.

        Called once per turn before action evaluation. If a plan is
        already active, we keep it. Otherwise, with some probability,
        we form a new plan that fits the current situation.
        """
        # Decrement cooldown
        if self._plan_cooldown > 0:
            self._plan_cooldown -= 1

        # Existing plan still active?
        if self.current_plan and self.current_plan.is_active:
            # Abort check
            if self.current_plan.should_abort(context):
                self.current_plan = None
                self._plan_cooldown = 2
            return

        # Don't form a plan while cooling down or in crisis
        if self._plan_cooldown > 0:
            return
        if self.strategic_state == StrategicState.CRISIS:
            return

        # Pick a plan that fits the situation. Probabilistic so the
        # AI doesn't always pick the same plan in the same situation.
        # 30% chance per turn to commit to a new plan when conditions fit.
        if (context.get("game_phase", 0) or 0) < 0.05:
            # Very early game - skip planning, let utility drive
            return
        roll = (hash((id(self), self.memory.get_last_action() or "", len(self.memory.history))) % 100) / 100.0
        if roll > 0.30:
            return

        # Choose plan based on strategic state + situation
        state = self.strategic_state
        at_war = context.get("at_war", False)
        treasury = context.get("treasury", 0.0)
        pop_pressure = context.get("pop_pressure", 0.0)
        territory_ratio = context.get("territory_ratio", 0.0)
        stability = context.get("stability_norm", 0.5)
        mil = context.get("mil_strength", 0.0)

        if state == StrategicState.TOTAL_WAR and mil < 0.6:
            self.current_plan = plan_fortify_then_attack()
        elif state == StrategicState.GOLDEN_AGE:
            self.current_plan = plan_cultural_flourish()
        elif state == StrategicState.SIEGE:
            self.current_plan = plan_fortify_then_attack()
        elif (state == StrategicState.EXPANSION
              and territory_ratio < 0.25 and pop_pressure > 0.4 and stability > 0.4):
            self.current_plan = plan_expand_burst()
        elif treasury < 0.15 and state in (StrategicState.RECOVERY, StrategicState.CONSOLIDATION):
            self.current_plan = plan_economic_recovery()
        elif (state in (StrategicState.CONSOLIDATION, StrategicState.RECOVERY)
              and context.get("tech_deficit", 0) > 0.3 and treasury > 0.3):
            self.current_plan = plan_research_boom()

    def decide(self, raw_state: dict) -> str:
        """Evaluate all actions and return the best action type string.

        Enhanced with:
        1. Strategic state evaluation
        2. State-based weight modification
        3. Action memory fatigue
        4. Per-action fatigue injection
        5. Multi-turn plan bias
        6. Exploration bonus for under-tried actions (off in CRISIS)
        """
        context = self._build_context(raw_state)

        # Update strategic state
        self.strategic_state = self._evaluate_strategic_state(context)

        # Update / form multi-turn plan
        self._maybe_form_plan(context)

        # Get state-based weight modifiers
        state_mods = STATE_WEIGHT_MODIFIERS.get(self.strategic_state, {})

        # Evaluate all actions with modified weights
        best_action: Optional[str] = None
        best_score = -1.0
        scores: dict[str, float] = {}
        weights_used: dict[str, float] = {}
        reasons: list[str] = []

        for a in self.actions:
            # Get the personality weight key for this action
            weight_key = ActionType.WEIGHT_KEY.get(a.action_type, "")
            base_weight = self.personality_weights.get(weight_key, 1.0)
            state_mod = state_mods.get(weight_key, 1.0)

            # Apply fatigue from memory
            fatigue = self.memory.get_fatigue(a.action_type, window=5)
            context["action_fatigue"] = fatigue

            # Apply success rate modifier: if an action keeps failing, reduce its weight
            # aggressively. Range: 0.2 (all fail) to 1.0 (all succeed). The strong
            # penalty is needed so the AI stops picking actions that keep auto-failing
            # (e.g. Expand when there's nowhere to go, Trade with no neighbors).
            success_rate = self.memory.get_success_rate(a.action_type)
            success_mod = 0.2 + 0.8 * success_rate  # Range: 0.2 (all fail) to 1.0 (all succeed)

            # Apply multi-turn plan bias
            plan_bias = 1.0
            if self.current_plan and self.current_plan.is_active:
                plan_bias = self.current_plan.get_action_bias(a.action_type)

            # Exploration bonus: small lift for under-tried actions when not in crisis
            # This prevents the AI from getting stuck repeating the same safe action.
            exploration_bonus = 1.0
            if self.strategic_state not in (StrategicState.CRISIS, StrategicState.TOTAL_WAR, StrategicState.SIEGE):
                novelty = self.memory.get_novelty(a.action_type)
                # Up to 25% bonus for an action never tried recently
                exploration_bonus = 1.0 + 0.25 * novelty

            # Combined weight
            combined = base_weight * state_mod * success_mod * plan_bias * exploration_bonus
            a.weight = combined
            weights_used[a.action_type] = combined

            a.evaluate(context)
            scores[a.action_type] = a.score
            if a.score > best_score:
                best_score = a.score
                best_action = a.action_type

        # Build a human-readable explanation
        if best_action:
            # Find the dominant reason (highest-weighted consideration)
            chosen_action_obj = next((a for a in self.actions if a.action_type == best_action), None)
            top_reason = ""
            if chosen_action_obj:
                # Score considerations individually to find the strongest
                consideration_scores = []
                for c in chosen_action_obj.considerations:
                    consideration_scores.append((c.name, c.score(context)))
                consideration_scores.sort(key=lambda x: x[1], reverse=True)
                if consideration_scores:
                    top_reason = f"{consideration_scores[0][0]}={consideration_scores[0][1]:.2f}"
            reasons.append(f"State: {self.strategic_state.name}")
            if self.current_plan and self.current_plan.is_active:
                step = self.current_plan.current_step
                if step:
                    reasons.append(f"Plan: {self.current_plan.name} (step: {step.get('action')})")
            if top_reason:
                reasons.append(f"Top consideration: {top_reason}")
            reasons.append(f"Score: {best_score:.3f}")

        self.last_decision_explanation = {
            "action": best_action,
            "scores": scores,
            "weights": weights_used,
            "state": self.strategic_state.name,
            "plan": self.current_plan.name if (self.current_plan and self.current_plan.is_active) else None,
            "plan_step": (
                self.current_plan.current_step.get("action")
                if (self.current_plan and self.current_plan.is_active and self.current_plan.current_step)
                else None
            ),
            "reasons": reasons,
        }

        # Record the chosen action (success will be updated later)
        if best_action:
            self.memory.record(best_action, self._last_action_success)
            # Advance the plan
            if self.current_plan and self.current_plan.is_active:
                self.current_plan.advance(best_action)
                if not self.current_plan.is_active:
                    # Plan just ended - cooldown before next
                    self.current_plan = None
                    self._plan_cooldown = 3

        return best_action or ActionType.FORTIFY

    def record_outcome(self, action_type: str, success: bool) -> None:
        """Record whether the last action succeeded or failed.

        Called by the engine after executing an action so the AI
        can learn from its decisions. Also: if a planned action
        fails repeatedly, abort the plan.
        """
        self._last_action_success = success
        # Update the most recent outcome in memory
        if self.memory.history and self.memory.history[-1] == action_type:
            if action_type in self.memory.outcomes and self.memory.outcomes[action_type]:
                self.memory.outcomes[action_type][-1] = success
        # If we're following a plan and the planned action keeps failing,
        # abort the plan to avoid getting stuck.
        if (not success and self.current_plan and self.current_plan.is_active
                and self.current_plan.current_step
                and self.current_plan.current_step.get("action") == action_type):
            # Check if recent outcomes are mostly failures
            rate = self.memory.get_success_rate(action_type)
            if rate < 0.3:
                self.current_plan = None
                self._plan_cooldown = 4

    def get_all_scores(self, raw_state: dict) -> dict[str, float]:
        """Return all action scores for debugging/visualization."""
        context = self._build_context(raw_state)
        state_mods = STATE_WEIGHT_MODIFIERS.get(self.strategic_state, {})
        scores = {}

        for a in self.actions:
            weight_key = ActionType.WEIGHT_KEY.get(a.action_type, "")
            base_weight = self.personality_weights.get(weight_key, 1.0)
            state_mod = state_mods.get(weight_key, 1.0)
            fatigue = self.memory.get_fatigue(a.action_type, window=5)
            context["action_fatigue"] = fatigue
            a.weight = base_weight * state_mod
            a.evaluate(context)
            scores[a.action_type] = a.score

        return scores

    @property
    def state_name(self) -> str:
        """Human-readable name of the current strategic state."""
        return self.strategic_state.name

    @property
    def plan_name(self) -> str | None:
        """Name of the active multi-turn plan, or None."""
        if self.current_plan and self.current_plan.is_active:
            return self.current_plan.name
        return None


# ════════════════════════════════════════════════════════════
# FILE: models.py
# ════════════════════════════════════════════════════════════

"""
Autonomous Civilization Simulation - Data Models
Core game objects: Leader, Civilization, WorldEvent, snapshots, and generation reports.
"""
import random
from PySide6.QtGui import QColor


# ── Leader ──────────────────────────────────────────────────
class Leader:
    """Represents a civilization's leader with a name, title, archetype, and tenure.

    Each leader has their own personality archetype that shifts the civ's
    behavior while they rule. When a leader dies or is replaced, the new
    leader may have a different archetype, causing the civilization to
    change strategic direction.
    """

    def __init__(self, name: str, title: str, epithet: str,
                 archetype: str, government: str):
        self.name = name
        self.title = title
        self.epithet = epithet
        self.archetype = archetype  # This leader's personality archetype
        self.government = government
        self.tenure = 0  # Years in power
        self.accomplishments: list[str] = []

    @property
    def full_name(self) -> str:
        """E.g. 'King Darius the Great' or 'Consul Elena the Wise'."""
        parts = [self.title, self.name]
        if self.epithet:
            parts.append(self.epithet)
        return " ".join(parts)

    @property
    def short_name(self) -> str:
        """E.g. 'Darius the Great'."""
        parts = [self.name]
        if self.epithet:
            parts.append(self.epithet)
        return " ".join(parts)

    @classmethod
    def generate(cls, government: str, archetype: str | None = None) -> "Leader":
        """Generate a random leader appropriate for the given government type.

        The archetype is picked with weighted randomness that favors archetypes
        matching the government flavor, but can surprise with any archetype.
        """
        first_name = random.choice(LEADER_FIRST_NAMES)
        titles = LEADER_TITLES.get(government, ["Leader"])
        title = random.choice(titles)

        # 60% chance of getting an epithet after first 3 leaders, or always for monarchs
        epithet = ""
        if government in ("monarchy", "chiefdom") or random.random() < 0.6:
            epithet = random.choice(LEADER_EPITHETS)

        # Pick archetype: if provided, use it; otherwise pick based on government flavor
        if archetype is None:
            archetype = cls._pick_archetype_for_government(government)

        return cls(first_name, title, epithet, archetype, government)

    @staticmethod
    def _pick_archetype_for_government(government: str) -> str:
        """Pick an archetype weighted toward government flavor."""
        gov_archetype_weights = {
            "chiefdom": {"warlord": 3, "raider": 2, "survivor": 2, "builder": 1},
            "monarchy": {"warlord": 2, "builder": 2, "philosopher": 1, "diplomat": 1, "survivor": 1},
            "republic": {"diplomat": 3, "philosopher": 2, "merchant": 2, "builder": 1},
            "theocracy": {"zealot": 4, "builder": 1, "diplomat": 1},
            "dictatorship": {"warlord": 3, "raider": 2, "merchant": 1, "survivor": 1},
            "oligarchy": {"merchant": 4, "builder": 2, "diplomat": 1, "philosopher": 1},
            "democracy": {"diplomat": 3, "philosopher": 3, "merchant": 1, "builder": 1},
        }
        weights = gov_archetype_weights.get(government, {"survivor": 1})
        archetypes = list(weights.keys())
        w = [weights[a] for a in archetypes]
        return random.choices(archetypes, weights=w, k=1)[0]

    def to_dict(self) -> dict:
        return {
            "name": self.name, "title": self.title, "epithet": self.epithet,
            "archetype": self.archetype, "government": self.government,
            "tenure": self.tenure, "accomplishments": self.accomplishments,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Leader":
        leader = cls(
            data["name"], data["title"], data.get("epithet", ""),
            data["archetype"], data["government"],
        )
        leader.tenure = data.get("tenure", 0)
        leader.accomplishments = data.get("accomplishments", [])
        return leader


# ── World Event ─────────────────────────────────────────────
class WorldEvent:
    """A temporary event affecting a civilization (plague, golden age, etc.)."""

    def __init__(self, name: str, desc: str, effect_fn, duration: int,
                 visual_color: str, target_civ: str):
        self.name = name
        self.desc = desc
        self.effect_fn = effect_fn
        self.duration = duration
        self.remaining = duration
        self.visual_color = visual_color
        self.target_civ = target_civ


# ── Civilization ────────────────────────────────────────────
class Civ:
    """Represents a single civilization in the simulation.

    Each civ has a Leader (who has their own archetype), and a Government
    type that modifies various stats and behaviors. When a leader changes,
    the civ's effective archetype changes with them.
    """

    def __init__(self, name: str, color: str, x: int, y: int,
                 personality: dict | None = None, archetype: str = "survivor",
                 government: str = "chiefdom"):
        self.name = name
        self.color = color
        self.capital: tuple[int, int] = (x, y)
        self.territory: set[tuple[int, int]] = {self.capital}
        self._base_archetype = archetype  # Starting archetype, can be overridden by leader

        # Core stats
        self.population: float = 1000.0
        self.military: float = 100.0
        self.technology: float = 1.0
        self.treasury: float = 500.0
        self.culture: float = 10.0
        self.stability: float = 100.0
        self.score: float = 0.0
        self.pop_cap: float = 1000.0
        self.last_action: str = "None"

        # Infrastructure
        self.buildings: list[dict] = []
        self.wonders: list[str] = []
        self.techs_researched: list[str] = []

        # Diplomacy
        self.grievances: dict[str, float] = {}
        self.at_war_with: set[str] = set()
        self.alliances: set[str] = set()
        self.trade_partners: set[str] = set()

        # Religion & Era
        self.religion: str | None = None
        self.era_id: int = 0
        self.era_name: str = "Ancient"

        # Government & Leadership
        self.government: str = government
        self.gov_tenure: int = 0  # Years under current government
        self.leader: Leader | None = None
        self.previous_leaders: list[Leader] = []
        self.leader_history_count: int = 0  # Total leaders this civ has had

        # AI Agent
        if personality is None:
            personality = {"expansion": 1.0, "military": 1.0, "tech": 1.0,
                           "culture": 1.0, "economy": 1.0}
        self.agent = CivAgent(personality, archetype=archetype)

    @property
    def archetype(self) -> str:
        """Current effective archetype - comes from the current leader if set."""
        if self.leader and self.leader.archetype:
            return self.leader.archetype
        return self._base_archetype

    @property
    def archetype_label(self) -> str:
        """Human-readable archetype name (e.g. 'Warlord', 'Philosopher')."""
        return PERSONALITY_ARCHETYPES.get(self.archetype, {}).get("label", self.archetype.title())

    @property
    def archetype_desc(self) -> str:
        """Short description of this civ's playstyle."""
        return PERSONALITY_ARCHETYPES.get(self.archetype, {}).get("description", "")

    @property
    def strategic_state_name(self) -> str:
        """Human-readable name of the AI's current strategic state."""
        return self.agent.state_name

    @property
    def plan_name(self) -> str | None:
        """Name of the AI's current multi-turn plan, or None if no plan active."""
        return self.agent.plan_name

    @property
    def last_decision_explanation(self) -> dict:
        """Last decision explanation from the AI agent (for debugging/UI)."""
        return self.agent.last_decision_explanation

    @property
    def government_label(self) -> str:
        """Human-readable government name."""
        return GOVERNMENTS.get(self.government, {}).get("label", self.government.title())

    @property
    def government_desc(self) -> str:
        """Short description of the government type."""
        return GOVERNMENTS.get(self.government, {}).get("description", "")

    @property
    def leader_name(self) -> str:
        """Full name of current leader."""
        if self.leader:
            return self.leader.full_name
        return "No Leader"

    @property
    def leader_short_name(self) -> str:
        """Short name of current leader."""
        if self.leader:
            return self.leader.short_name
        return "?"

    @classmethod
    def from_template(cls, template: dict, x: int, y: int) -> "Civ":
        """Create a Civ from a CIV_TEMPLATES entry."""
        return cls(
            name=template["name"],
            color=template["color"],
            x=x, y=y,
            personality=template.get("personality", {}),
            archetype=template.get("archetype", "survivor"),
            government=template.get("government", "chiefdom"),
        )

    def to_dict(self) -> dict:
        """Serialize civilization state for save games."""
        return {
            "name": self.name, "color": self.color,
            "capital": list(self.capital),
            "territory": [list(t) for t in self.territory],
            "population": self.population, "military": self.military,
            "technology": self.technology, "treasury": self.treasury,
            "culture": self.culture, "stability": self.stability,
            "score": self.score, "pop_cap": self.pop_cap,
            "last_action": self.last_action,
            "buildings": self.buildings,
            "wonders": self.wonders,
            "techs_researched": self.techs_researched,
            "grievances": self.grievances,
            "at_war_with": list(self.at_war_with),
            "alliances": list(self.alliances),
            "trade_partners": list(self.trade_partners),
            "religion": self.religion,
            "era_id": self.era_id, "era_name": self.era_name,
            "personality": {
                "expansion": self.agent.personality_weights.get("expansion", 1.0),
                "military": self.agent.personality_weights.get("military", 1.0),
                "economy": self.agent.personality_weights.get("economy", 1.0),
                "tech": self.agent.personality_weights.get("tech", 1.0),
                "culture": self.agent.personality_weights.get("culture", 1.0),
                "diplomacy": self.agent.personality_weights.get("diplomacy", 0.8),
                "trade": self.agent.personality_weights.get("trade", 0.9),
                "wonder": self.agent.personality_weights.get("wonder", 0.4),
            },
            "archetype": self._base_archetype,
            "government": self.government,
            "gov_tenure": self.gov_tenure,
            "leader": self.leader.to_dict() if self.leader else None,
            "previous_leaders": [l.to_dict() for l in self.previous_leaders[-5:]],  # Keep last 5
            "leader_history_count": self.leader_history_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Civ":
        """Deserialize civilization from saved state."""
        cap = data["capital"]
        civ = cls(data["name"], data["color"], cap[0], cap[1],
                  data.get("personality", {}),
                  archetype=data.get("archetype", "survivor"),
                  government=data.get("government", "chiefdom"))
        civ.territory = {tuple(t) for t in data["territory"]}
        for key in ["population", "military", "technology", "treasury", "culture",
                     "stability", "score", "pop_cap", "last_action"]:
            setattr(civ, key, data[key])
        civ.buildings = data.get("buildings", [])
        civ.wonders = data.get("wonders", [])
        civ.techs_researched = data.get("techs_researched", [])
        civ.grievances = data.get("grievances", {})
        civ.at_war_with = set(data.get("at_war_with", []))
        civ.alliances = set(data.get("alliances", []))
        civ.trade_partners = set(data.get("trade_partners", []))
        civ.religion = data.get("religion")
        civ.era_id = data.get("era_id", 0)
        civ.era_name = data.get("era_name", "Ancient")
        civ.government = data.get("government", "chiefdom")
        civ.gov_tenure = data.get("gov_tenure", 0)
        civ.leader_history_count = data.get("leader_history_count", 0)

        # Restore leader
        leader_data = data.get("leader")
        if leader_data:
            civ.leader = Leader.from_dict(leader_data)
        civ.previous_leaders = [
            Leader.from_dict(l) for l in data.get("previous_leaders", [])
        ]
        return civ


# ── Generation Snapshot ─────────────────────────────────────
class CivSnapshot:
    """Captures a civilization's state at a point in time for before/after comparison."""
    __slots__ = [
        'name', 'population', 'military', 'technology', 'treasury',
        'culture', 'stability', 'territory_count', 'score', 'pop_cap',
        'buildings_count', 'wonders', 'religion', 'era_name', 'rank',
        'alliances', 'trade_partners', 'at_war_with', 'last_action',
        'government', 'leader_name'
    ]

    def __init__(self, civ: Civ, rank: int = 0):
        self.name = civ.name
        self.population = civ.population
        self.military = civ.military
        self.technology = civ.technology
        self.treasury = civ.treasury
        self.culture = civ.culture
        self.stability = civ.stability
        self.territory_count = len(civ.territory)
        self.score = civ.score
        self.pop_cap = civ.pop_cap
        self.buildings_count = len(civ.buildings)
        self.wonders = list(civ.wonders) if hasattr(civ.wonders, '__iter__') else []
        self.religion = civ.religion
        self.era_name = civ.era_name
        self.rank = rank
        self.alliances = set(civ.alliances)
        self.trade_partners = set(civ.trade_partners)
        self.at_war_with = set(civ.at_war_with)
        self.last_action = civ.last_action
        self.government = civ.government_label
        self.leader_name = civ.leader_short_name


# ── Generation Report ───────────────────────────────────────
class GenerationReport:
    """Builds formatted HTML and plain-text reports comparing before/after snapshots."""

    @staticmethod
    def format_delta(before: CivSnapshot, after: CivSnapshot,
                     key: str, fmt: str = "d") -> tuple:
        b_val = getattr(before, key)
        a_val = getattr(after, key)
        delta = a_val - b_val

        if fmt == "d":
            b_str, a_str = str(int(b_val)), str(int(a_val))
            d_str = str(int(delta))
        elif fmt == "f1":
            b_str, a_str = f"{b_val:.1f}", f"{a_val:.1f}"
            d_str = f"{delta:+.1f}"
        else:
            b_str, a_str = str(b_val), str(a_val)
            d_str = str(delta)

        if delta > 0:
            sign, color_tag = "+", "color:#37AF37"
        elif delta < 0:
            sign, color_tag = "-", "color:#D73737"
        else:
            sign, color_tag = "=", "color:gray"
        return b_str, a_str, f"{sign}{d_str}", color_tag

    @staticmethod
    def build_html_report(year: int, generation: int, season_name: str,
                          before_snapshots: list, after_snapshots: list,
                          events_log: list) -> str:
        lines = []
        lines.append(
            f"<div style='margin:8px 0; padding:8px; border:2px solid #0e639e; "
            f"border-radius:5px; background-color:#1a2a3a;'>"
        )
        lines.append(
            f"<b style='font-size:14px; color:#0ea5e9;'>"
            f"═══ GENERATION {generation} ═══ Year {year} ═══ {season_name} ═══</b>"
        )
        lines.append("</div>")

        if events_log:
            lines.append(
                "<div style='margin:4px 0; padding:4px 8px; "
                "border-left:3px solid #D7AF1E; background:#2a2a1a;'>"
            )
            lines.append("<b style='color:#D7AF1E;'>Events:</b><br>")
            for ev in events_log:
                lines.append(f"<span style='color:#D7AF1E;'>&#8226; {ev}</span><br>")
            lines.append("</div>")

        for before in before_snapshots:
            after = next((a for a in after_snapshots if a.name == before.name), None)
            if not after:
                continue
            civ_color = "#FFFFFF"
            lines.append(
                "<div style='margin:6px 0; padding:6px; border:1px solid #3e3e3e; "
                "border-radius:4px; background:#222;'>"
            )
            lines.append(f"<b style='color:{civ_color}; font-size:13px;'>{before.name}</b>")

            # Show leader + government
            if hasattr(before, 'leader_name') and before.leader_name:
                lines.append(
                    f"&nbsp; <span style='color:#9370DB; font-size:10px;'>"
                    f"{before.leader_name}</span>"
                )
            if hasattr(before, 'government') and before.government:
                lines.append(
                    f"&nbsp; <span style='color:#0ea5e9; font-size:10px;'>"
                    f"[{before.government}]</span>"
                )

            rank_delta = before.rank - after.rank
            if rank_delta > 0:
                rank_str = f"+{rank_delta}"
            elif rank_delta < 0:
                rank_str = f"-{abs(rank_delta)}"
            else:
                rank_str = "="
            lines.append(
                f"&nbsp; <span style='color:#aaa; font-size:11px;'>"
                f"Rank: {after.rank} ({rank_str})</span>"
            )

            # Check for leader change
            if (hasattr(before, 'leader_name') and hasattr(after, 'leader_name')
                    and before.leader_name != after.leader_name
                    and before.leader_name and after.leader_name):
                lines.append(
                    f"&nbsp; <span style='color:#9370DB; font-size:11px; font-weight:bold;'>"
                    f"NEW LEADER: {before.leader_name} -> {after.leader_name}</span>"
                )

            # Check for government change
            if (hasattr(before, 'government') and hasattr(after, 'government')
                    and before.government != after.government
                    and before.government and after.government):
                lines.append(
                    f"&nbsp; <span style='color:#0ea5e9; font-size:11px; font-weight:bold;'>"
                    f"GOV'T CHANGE: {before.government} -> {after.government}</span>"
                )

            if before.era_name != after.era_name:
                lines.append(
                    f"&nbsp; <span style='color:#FFD700; font-size:11px; font-weight:bold;'>"
                    f"ERA: {before.era_name} -> {after.era_name}!</span>"
                )
            lines.append(
                f"&nbsp; <span style='color:#aaa; font-size:11px;'>"
                f"Action: {before.last_action} -> </span>"
                f"<span style='color:#0ea5e9; font-size:11px; font-weight:bold;'>"
                f"{after.last_action}</span>"
            )

            lines.append(
                "<table style='margin-top:4px; font-size:11px; width:100%; "
                "border-collapse:collapse;'>"
            )
            lines.append(
                "<tr style='color:#888; border-bottom:1px solid #333;'>"
                "<td style='width:90px;'>Stat</td>"
                "<td style='width:80px; text-align:right;'>Before</td>"
                "<td style='width:20px; text-align:center;'>-></td>"
                "<td style='width:80px; text-align:right;'>After</td>"
                "<td style='width:90px; text-align:right;'>Delta</td></tr>"
            )

            stat_rows = [
                ("Population", "population", "d"), ("Pop Cap", "pop_cap", "d"),
                ("Military", "military", "d"), ("Technology", "technology", "f1"),
                ("Treasury", "treasury", "d"), ("Culture", "culture", "d"),
                ("Stability", "stability", "f1"), ("Territory", "territory_count", "d"),
                ("Score", "score", "d")
            ]
            for label, key, fmt in stat_rows:
                b_str, a_str, d_str, color = GenerationReport.format_delta(
                    before, after, key, fmt
                )
                lines.append(
                    f"<tr><td style='color:#aaa;'>{label}</td>"
                    f"<td style='text-align:right; color:#888;'>{b_str}</td>"
                    f"<td style='text-align:center; color:#555;'>-></td>"
                    f"<td style='text-align:right; color:#ccc;'>{a_str}</td>"
                    f"<td style='text-align:right; {color}; font-weight:bold;'>"
                    f"{d_str}</td></tr>"
                )
            lines.append("</table>")

            diplo_parts = []
            new_alliances = after.alliances - before.alliances
            lost_alliances = before.alliances - after.alliances
            new_trades = after.trade_partners - before.trade_partners
            lost_trades = before.trade_partners - after.trade_partners
            new_wars = after.at_war_with - before.at_war_with
            peace_made = before.at_war_with - after.at_war_with

            if new_alliances:
                diplo_parts.append(f"<span style='color:#37AF37;'>Allied: {', '.join(new_alliances)}</span>")
            if lost_alliances:
                diplo_parts.append(f"<span style='color:#D73737;'>Alliance broken: {', '.join(lost_alliances)}</span>")
            if new_trades:
                diplo_parts.append(f"<span style='color:#37AF37;'>Trade started: {', '.join(new_trades)}</span>")
            if lost_trades:
                diplo_parts.append(f"<span style='color:#D73737;'>Trade ended: {', '.join(lost_trades)}</span>")
            if new_wars:
                diplo_parts.append(f"<span style='color:#FF4500;'>WAR: {', '.join(new_wars)}</span>")
            if peace_made:
                diplo_parts.append(f"<span style='color:#37AF37;'>Peace: {', '.join(peace_made)}</span>")
            if after.religion != before.religion:
                if before.religion is None:
                    diplo_parts.append(f"<span style='color:#9370DB;'>Founded religion: {after.religion}</span>")
                else:
                    diplo_parts.append(f"<span style='color:#9370DB;'>Religion: {before.religion} -> {after.religion}</span>")
            new_wonders = set(after.wonders) - set(before.wonders)
            if new_wonders:
                diplo_parts.append(f"<span style='color:#FFD700;'>Wonder built: {', '.join(new_wonders)}</span>")
            bld_delta = after.buildings_count - before.buildings_count
            if bld_delta > 0:
                diplo_parts.append(f"<span style='color:#0ea5e9;'>Buildings: +{bld_delta}</span>")

            if diplo_parts:
                lines.append(
                    "<div style='margin-top:4px; padding-top:4px; "
                    "border-top:1px solid #333;'>"
                )
                for dp in diplo_parts:
                    lines.append(f"{dp}<br>")
                lines.append("</div>")
            lines.append("</div>")

        lines.append(
            "<div style='margin:6px 0; padding:6px; border:1px dashed #555; "
            "background:#1a1a1a;'>"
        )
        lines.append("<b style='color:#888; font-size:10px;'>COPY-PASTE FORMAT:</b><br>")
        lines.append("<pre style='color:#aaa; font-size:10px; margin:2px;'>")
        lines.append(f"GEN {generation} | Year {year} | {season_name}")
        for before in before_snapshots:
            after = next((a for a in after_snapshots if a.name == before.name), None)
            if not after:
                continue
            rk_d = before.rank - after.rank
            rk_s = f"+{rk_d}" if rk_d > 0 else f"-{abs(rk_d)}" if rk_d < 0 else "="
            lines.append(f"  [{before.name}] Rank: {after.rank} ({rk_s}) Era: {after.era_name}")
            for label, key, fmt in [
                ("Pop", "population", "d"), ("Cap", "pop_cap", "d"),
                ("Mil", "military", "d"), ("Tech", "technology", "f1"),
                ("Gold", "treasury", "d"), ("Cult", "culture", "d"),
                ("Stab", "stability", "f1"), ("Terr", "territory_count", "d"),
                ("Score", "score", "d")
            ]:
                b_str, a_str, d_str, _ = GenerationReport.format_delta(
                    before, after, key, fmt
                )
                lines.append(f"    {label}: {b_str} -> {a_str} ({d_str})")
            lines.append(f"    Action: {before.last_action} -> {after.last_action}")
        lines.append("</pre></div>")
        return "".join(lines)

    @staticmethod
    def build_plain_text_report(year: int, generation: int, season_name: str,
                                before_snapshots: list, after_snapshots: list,
                                events_log: list) -> str:
        lines = [f"GEN {generation} | Year {year} | {season_name}"]
        if events_log:
            for ev in events_log:
                lines.append(f"  EVENT: {ev}")
        for before in before_snapshots:
            after = next((a for a in after_snapshots if a.name == before.name), None)
            if not after:
                continue
            rk_d = before.rank - after.rank
            rk_s = f"+{rk_d}" if rk_d > 0 else f"-{abs(rk_d)}" if rk_d < 0 else "="
            lines.append(f"  [{before.name}] Rank: {after.rank} ({rk_s}) Era: {after.era_name}")
            for label, key, fmt in [
                ("Pop", "population", "d"), ("Cap", "pop_cap", "d"),
                ("Mil", "military", "d"), ("Tech", "technology", "f1"),
                ("Gold", "treasury", "d"), ("Cult", "culture", "d"),
                ("Stab", "stability", "f1"), ("Terr", "territory_count", "d"),
                ("Score", "score", "d")
            ]:
                b_str, a_str, d_str, _ = GenerationReport.format_delta(
                    before, after, key, fmt
                )
                lines.append(f"    {label}: {b_str} -> {a_str} ({d_str})")
            lines.append(f"    Action: {before.last_action} -> {after.last_action}")
            new_wars = after.at_war_with - before.at_war_with
            peace = before.at_war_with - after.at_war_with
            new_ally = after.alliances - before.alliances
            if new_wars:
                lines.append(f"    WAR: {', '.join(new_wars)}")
            if peace:
                lines.append(f"    PEACE: {', '.join(peace)}")
            if new_ally:
                lines.append(f"    ALLIED: {', '.join(new_ally)}")
        lines.append("")
        return "\n".join(lines)


# ════════════════════════════════════════════════════════════
# FILE: engine.py
# ════════════════════════════════════════════════════════════

"""
Autonomous Civilization Simulation - Simulation Engine
Core game loop, world generation, turn processing, and event system.

Map generation uses distinct procedural algorithms per terrain preset.
Personality archetypes drive diplomacy thresholds, stability, and war behavior.

Performance optimizations:
- Cached civ name→Civ dict (O(1) lookups instead of O(n) scans)
- Cached archetype per civ (avoid re-scanning templates every call)
- Incremental explored set (add new territory instead of full rebuild)
- Batch analytics DB commits (every N turns instead of every turn)
- Precomputed terrain stat lookups (avoid repeated Terrain() enum creation)
- Neighbor iteration using local variable binding for speed
"""
import json
import math
import os
import random
from PySide6.QtCore import QThread, Signal


# ════════════════════════════════════════════════════════════
# MAP GENERATOR - Procedural terrain with per-preset algorithms
# ════════════════════════════════════════════════════════════
class MapGenerator:
    """Generates terrain maps using distinct algorithms for each preset type.

    Each preset produces visually and strategically different worlds:
    - Continent: 2-3 large landmasses via radial blob placement
    - Archipelago: Scattered island chains from noise clusters
    - Pangaea: Single supercontinent from a central massive blob
    - Islands: Many tiny isolated land patches
    - Highlands: Mostly land with mountain ridges from wave interference
    - River Valley: A carved river channel with mountain walls
    - Crater: Ring-shaped landmass around a central lake
    - Mediterranean: Large inland sea with surrounding coastline
    """

    def __init__(self, W: int, H: int):
        self.W, self.H = W, H

    # ── Public Interface ────────────────────────────────────
    def generate(self, preset: str) -> dict[tuple, int]:
        """Return a terrain_map {(x,y): Terrain.id} for the given preset."""
        method = {
            TerrainPreset.CONTINENT: self._gen_continent,
            TerrainPreset.ARCHIPELAGO: self._gen_archipelago,
            TerrainPreset.PANGAEA: self._gen_pangaea,
            TerrainPreset.ISLANDS: self._gen_islands,
            TerrainPreset.HIGHLANDS: self._gen_highlands,
            TerrainPreset.RIVER_VALLEY: self._gen_river_valley,
            TerrainPreset.CRATER: self._gen_crater,
            TerrainPreset.MEDITERRANEAN: self._gen_mediterranean,
        }.get(preset, self._gen_continent)
        return method()

    # ── Helpers ─────────────────────────────────────────────
    def _empty_ocean(self) -> dict[tuple, int]:
        return {(x, y): Terrain.OCEAN for y in range(self.H) for x in range(self.W)}

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.W and 0 <= y < self.H

    def _set_circle(self, tmap: dict, cx: float, cy: float, radius: float,
                    terrain_id: int, falloff: bool = True) -> None:
        """Fill a circle (with soft edge falloff) with the given terrain."""
        ri = int(radius) + 2
        cx_i, cy_i = int(cx), int(cy)
        W, H = self.W, self.H
        for dy in range(-ri, ri + 1):
            y = cy_i + dy
            if y < 0 or y >= H:
                continue
            dy2 = dy * dy
            for dx in range(-ri, ri + 1):
                x = cx_i + dx
                if x < 0 or x >= W:
                    continue
                dist = math.sqrt(dx * dx + dy2)
                if falloff:
                    if dist < radius * 0.7:
                        tmap[(x, y)] = terrain_id
                    elif dist < radius and random.random() < (radius - dist) / (radius * 0.3):
                        tmap[(x, y)] = terrain_id
                else:
                    if dist < radius:
                        tmap[(x, y)] = terrain_id

    def _set_ellipse(self, tmap: dict, cx: float, cy: float,
                     rx: float, ry: float, terrain_id: int) -> None:
        """Fill an ellipse with the given terrain."""
        cx_i, cy_i = int(cx), int(cy)
        ry_i, rx_i = int(ry), int(rx)
        W, H = self.W, self.H
        rx_safe = max(rx, 0.1)
        ry_safe = max(ry, 0.1)
        for dy in range(-ry_i - 2, ry_i + 3):
            y = cy_i + dy
            if y < 0 or y >= H:
                continue
            for dx in range(-rx_i - 2, rx_i + 3):
                x = cx_i + dx
                if x < 0 or x >= W:
                    continue
                dist = math.sqrt((dx / rx_safe) ** 2 + (dy / ry_safe) ** 2)
                if dist < 0.7:
                    tmap[(x, y)] = terrain_id
                elif dist < 1.0 and random.random() < (1.0 - dist) / 0.3:
                    tmap[(x, y)] = terrain_id

    def _add_coast(self, tmap: dict) -> None:
        """Convert ocean tiles adjacent to land into coast tiles."""
        coast = set()
        W, H = self.W, self.H
        OCEAN = Terrain.OCEAN
        COAST = Terrain.COAST
        for y in range(H):
            for x in range(W):
                if tmap[(x, y)] == OCEAN:
                    if ((x > 0 and tmap[(x-1, y)] != OCEAN)
                        or (x < W-1 and tmap[(x+1, y)] != OCEAN)
                        or (y > 0 and tmap[(x, y-1)] != OCEAN)
                        or (y < H-1 and tmap[(x, y+1)] != OCEAN)):
                        coast.add((x, y))
        for x, y in coast:
            tmap[(x, y)] = COAST

    def _add_rivers(self, tmap: dict, count: int = 3) -> None:
        """Carve simple rivers from high terrain toward the nearest ocean."""
        MOUNTAIN = Terrain.MOUNTAIN
        HILLS = Terrain.HILLS
        OCEAN = Terrain.OCEAN
        COAST = Terrain.COAST
        for _ in range(count):
            candidates = [
                (x, y) for y in range(self.H) for x in range(self.W)
                if tmap[(x, y)] in (MOUNTAIN, HILLS)
            ]
            if not candidates:
                continue
            sx, sy = random.choice(candidates)
            for _ in range(60):
                tmap[(sx, sy)] = COAST
                neighbors = [
                    (nx, ny) for nx, ny in [(sx+1, sy), (sx-1, sy), (sx, sy+1), (sx, sy-1)]
                    if self._in_bounds(nx, ny)
                ]
                if not neighbors:
                    break
                water_n = [n for n in neighbors if tmap[n] in (OCEAN, COAST)]
                if water_n:
                    break
                best = min(neighbors, key=lambda n: self._terrain_elevation(tmap[n]))
                sx, sy = best

    def _terrain_elevation(self, tid: int) -> int:
        order = {
            Terrain.OCEAN: 0, Terrain.COAST: 1, Terrain.GRASSLAND: 3,
            Terrain.PLAINS: 3, Terrain.FOREST: 4, Terrain.JUNGLE: 4,
            Terrain.HILLS: 6, Terrain.DESERT: 3, Terrain.TUNDRA: 5,
            Terrain.MOUNTAIN: 9,
        }
        return order.get(tid, 3)

    def _assign_land_biomes(self, tmap: dict, default: str = "mixed") -> None:
        """Assign terrain types to land tiles based on latitude and noise."""
        OCEAN = Terrain.OCEAN
        COAST = Terrain.COAST
        for y in range(self.H):
            for x in range(self.W):
                if tmap[(x, y)] not in (OCEAN, COAST):
                    tmap[(x, y)] = self._pick_biome(x, y, default)

    def _pick_biome(self, x: int, y: int, style: str) -> int:
        """Pick a land terrain type based on position and generation style."""
        lat = y / self.H
        r = random.random()

        if style == "highlands":
            if r < 0.25: return Terrain.MOUNTAIN
            if r < 0.50: return Terrain.HILLS
            if r < 0.70: return Terrain.FOREST
            if r < 0.85: return Terrain.PLAINS
            return Terrain.GRASSLAND

        if style == "desert":
            if r < 0.35: return Terrain.DESERT
            if r < 0.55: return Terrain.PLAINS
            if r < 0.70: return Terrain.HILLS
            if r < 0.85: return Terrain.GRASSLAND
            return Terrain.FOREST

        if style == "tropical":
            if r < 0.25: return Terrain.JUNGLE
            if r < 0.45: return Terrain.FOREST
            if r < 0.65: return Terrain.GRASSLAND
            if r < 0.80: return Terrain.PLAINS
            if r < 0.90: return Terrain.HILLS
            return Terrain.MOUNTAIN

        # "mixed" - latitude-based biomes
        if lat < 0.12 or lat > 0.88:
            if r < 0.50: return Terrain.TUNDRA
            if r < 0.75: return Terrain.HILLS
            return Terrain.MOUNTAIN
        elif lat < 0.25 or lat > 0.75:
            if r < 0.25: return Terrain.FOREST
            if r < 0.45: return Terrain.PLAINS
            if r < 0.60: return Terrain.GRASSLAND
            if r < 0.75: return Terrain.HILLS
            if r < 0.88: return Terrain.DESERT
            return Terrain.MOUNTAIN
        else:
            if r < 0.20: return Terrain.JUNGLE
            if r < 0.40: return Terrain.FOREST
            if r < 0.55: return Terrain.GRASSLAND
            if r < 0.70: return Terrain.PLAINS
            if r < 0.82: return Terrain.DESERT
            if r < 0.92: return Terrain.HILLS
            return Terrain.MOUNTAIN

    # ── Preset: Continent ───────────────────────────────────
    def _gen_continent(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        num_continents = random.randint(2, 3)
        margin_x, margin_y = self.W * 0.2, self.H * 0.2
        for i in range(num_continents):
            cx = margin_x + (self.W - 2 * margin_x) * ((i + 0.5) / num_continents) + random.uniform(-5, 5)
            cy = self.H * 0.5 + random.uniform(-self.H * 0.2, self.H * 0.2)
            rx = random.uniform(self.W * 0.18, self.W * 0.28)
            ry = random.uniform(self.H * 0.25, self.H * 0.40)
            self._set_ellipse(tmap, cx, cy, rx, ry, Terrain.GRASSLAND)
            for _ in range(random.randint(2, 5)):
                px = cx + random.uniform(-rx * 0.6, rx * 0.6)
                py = cy + random.uniform(-ry * 0.6, ry * 0.6)
                pr = random.uniform(5, 12)
                self._set_circle(tmap, px, py, pr, Terrain.PLAINS)
        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        self._add_rivers(tmap, random.randint(2, 4))
        return tmap

    # ── Preset: Archipelago ─────────────────────────────────
    def _gen_archipelago(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        num_islands = random.randint(8, 15)
        for _ in range(num_islands):
            cx = random.uniform(self.W * 0.1, self.W * 0.9)
            cy = random.uniform(self.H * 0.1, self.H * 0.9)
            r = random.uniform(4, 10)
            self._set_circle(tmap, cx, cy, r, Terrain.GRASSLAND)
            # Small satellite islands
            for _ in range(random.randint(1, 3)):
                sx = cx + random.uniform(-r * 2, r * 2)
                sy = cy + random.uniform(-r * 2, r * 2)
                sr = random.uniform(2, 5)
                self._set_circle(tmap, sx, sy, sr, Terrain.PLAINS)
        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        self._add_rivers(tmap, random.randint(1, 2))
        return tmap

    # ── Preset: Pangaea ─────────────────────────────────────
    def _gen_pangaea(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        cx, cy = self.W * 0.5, self.H * 0.5
        rx = self.W * 0.38
        ry = self.H * 0.38
        self._set_ellipse(tmap, cx, cy, rx, ry, Terrain.GRASSLAND)
        # Irregular edges
        for _ in range(random.randint(6, 12)):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.5, 0.9)
            px = cx + math.cos(angle) * rx * dist
            py = cy + math.sin(angle) * ry * dist
            pr = random.uniform(5, 15)
            self._set_circle(tmap, px, py, pr, Terrain.PLAINS)
        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        self._add_rivers(tmap, random.randint(3, 6))
        return tmap

    # ── Preset: Islands ─────────────────────────────────────
    def _gen_islands(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        num_islands = random.randint(20, 35)
        for _ in range(num_islands):
            cx = random.uniform(self.W * 0.05, self.W * 0.95)
            cy = random.uniform(self.H * 0.05, self.H * 0.95)
            r = random.uniform(2, 6)
            self._set_circle(tmap, cx, cy, r, Terrain.PLAINS)
        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        return tmap

    # ── Preset: Highlands ───────────────────────────────────
    def _gen_highlands(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        # Start with mostly land
        for y in range(self.H):
            for x in range(self.W):
                tmap[(x, y)] = Terrain.HILLS
        # Mountain ridges using wave interference
        num_ridges = random.randint(3, 6)
        for _ in range(num_ridges):
            angle = random.uniform(0, math.pi)
            offset = random.uniform(0, self.W)
            for y in range(self.H):
                for x in range(self.W):
                    dist = abs((x - offset) * math.cos(angle) + (y - self.H/2) * math.sin(angle))
                    if dist < 4 and random.random() < 0.7:
                        tmap[(x, y)] = Terrain.MOUNTAIN
                    elif dist < 8 and random.random() < 0.3:
                        tmap[(x, y)] = Terrain.MOUNTAIN
        # Small lakes
        for _ in range(random.randint(2, 5)):
            lx = random.randint(0, self.W - 1)
            ly = random.randint(0, self.H - 1)
            self._set_circle(tmap, lx, ly, random.uniform(3, 6), Terrain.OCEAN, falloff=False)
        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "highlands")
        self._add_rivers(tmap, random.randint(1, 3))
        return tmap

    # ── Preset: River Valley ────────────────────────────────
    def _gen_river_valley(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        # Land borders
        border_w = max(5, self.W // 6)
        for y in range(self.H):
            for x in range(self.W):
                if x < border_w or x > self.W - border_w:
                    tmap[(x, y)] = Terrain.MOUNTAIN
                elif x < border_w + 4 or x > self.W - border_w - 4:
                    tmap[(x, y)] = Terrain.HILLS
                else:
                    tmap[(x, y)] = Terrain.PLAINS
        # River down the middle
        river_x = self.W // 2
        for y in range(self.H):
            river_x += random.randint(-1, 1)
            river_x = max(border_w + 5, min(self.W - border_w - 5, river_x))
            for dx in range(-1, 2):
                if self._in_bounds(river_x + dx, y):
                    tmap[(river_x + dx, y)] = Terrain.COAST
        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        return tmap

    # ── Preset: Crater ──────────────────────────────────────
    def _gen_crater(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        cx, cy = self.W / 2, self.H / 2
        outer_r = min(self.W, self.H) * 0.42
        inner_r = outer_r * 0.35

        for y in range(self.H):
            for x in range(self.W):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if inner_r < dist < outer_r:
                    if dist < inner_r + (outer_r - inner_r) * 0.2:
                        tmap[(x, y)] = Terrain.MOUNTAIN
                    elif dist > outer_r - (outer_r - inner_r) * 0.15:
                        tmap[(x, y)] = Terrain.HILLS
                    else:
                        tmap[(x, y)] = Terrain.PLAINS

        for y in range(self.H):
            for x in range(self.W):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist < inner_r * 0.9:
                    tmap[(x, y)] = Terrain.OCEAN
                elif dist < inner_r:
                    tmap[(x, y)] = Terrain.COAST

        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        self._add_rivers(tmap, random.randint(1, 2))
        return tmap

    # ── Preset: Mediterranean ───────────────────────────────
    def _gen_mediterranean(self) -> dict[tuple, int]:
        tmap = self._empty_ocean()
        # Large central sea
        sea_rx = self.W * 0.3
        sea_ry = self.H * 0.25
        self._set_ellipse(tmap, self.W * 0.5, self.H * 0.5, sea_rx, sea_ry, Terrain.OCEAN)
        # Surrounding land
        for y in range(self.H):
            for x in range(self.W):
                dist_x = abs(x - self.W / 2) / (self.W / 2)
                dist_y = abs(y - self.H / 2) / (self.H / 2)
                if dist_x > 0.6 or dist_y > 0.6:
                    if tmap[(x, y)] == Terrain.OCEAN:
                        tmap[(x, y)] = Terrain.GRASSLAND
        # Peninsulas
        for _ in range(random.randint(2, 4)):
            angle = random.uniform(0, 2 * math.pi)
            bx = self.W / 2 + math.cos(angle) * sea_rx * 0.7
            by = self.H / 2 + math.sin(angle) * sea_ry * 0.7
            px = bx + math.cos(angle) * 15
            py = by + math.sin(angle) * 15
            self._set_circle(tmap, px, py, random.uniform(5, 10), Terrain.PLAINS)
        # Small islands inside the sea
        for _ in range(random.randint(2, 5)):
            ix = self.W * 0.5 + random.uniform(-sea_rx * 0.5, sea_rx * 0.5)
            iy = self.H * 0.5 + random.uniform(-sea_ry * 0.5, sea_ry * 0.5)
            self._set_circle(tmap, ix, iy, random.uniform(2, 4), Terrain.PLAINS)

        self._add_coast(tmap)
        self._assign_land_biomes(tmap, "mixed")
        self._add_rivers(tmap, random.randint(2, 3))
        return tmap


# ════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ════════════════════════════════════════════════════════════
class SimulationEngine(QThread):
    """Runs the civilization simulation in a background thread.

    Emits signals to update the UI with map data, log messages, and
    generation reports. Supports save/load, configurable terrain presets,
    and variable numbers of civilizations.

    Performance optimizations:
    - _civ_by_name dict for O(1) civ lookups instead of O(n) scans
    - Cached archetype per civ (set once during placement)
    - Incremental explored set (only add new territory cells)
    - Batched analytics commits (every 10 turns instead of every turn)
    - Precomputed is_water lookup array (avoid Terrain() enum creation)
    - Local variable binding for hot-path attribute access
    """

    update_signal = Signal(dict)
    log_signal = Signal(str)
    gen_report_signal = Signal(str, str)
    notification_signal = Signal(str, str)
    autosave_signal = Signal(str)

    def __init__(self, map_width: int = DEFAULT_MAP_WIDTH,
                 map_height: int = DEFAULT_MAP_HEIGHT,
                 civ_count: int = 4,
                 terrain_preset: str = TerrainPreset.CONTINENT):
        super().__init__()
        self.running = False
        self.speed = 150
        self.year = -3000
        self.generation = 0
        self.W, self.H = map_width, map_height
        self.civ_count = civ_count
        self.terrain_preset = terrain_preset

        self.defs = GameDefs()
        self.analytics = AnalyticsDB()
        self.terrain_map: dict[tuple, int] = {}
        self.owner_map: dict[tuple, str | None] = {}
        self.resource_map: dict[tuple, str] = {}
        self.explored: set[tuple] = set()
        self.civs: list[Civ] = []
        self.pathfinder = DStarLite(self.W, self.H)
        self.last_path: list[tuple] = []
        self.active_events: list[WorldEvent] = []
        self.wonders_built: list[str] = []
        self.season = 0
        self.season_timer = 0
        self.max_years = 0
        self.finished = False
        self.turn_events_log: list[str] = []
        self.total_land_tiles = 0

        # Performance: O(1) civ lookup by name
        self._civ_by_name: dict[str, Civ] = {}
        # Performance: cached archetype per civ (avoid template scan per call)
        self._civ_archetype: dict[str, dict] = {}
        # Performance: precomputed is_water lookup from terrain integer
        self._is_water_cache: dict[int, bool] = {}
        for t, stats in self.defs.terrain_stats.items():
            self._is_water_cache[int(t)] = stats['is_water']
        # Performance: precomputed full terrain stats by int ID
        self._terrain_stats_by_id: dict[int, dict] = {}
        for t, stats in self.defs.terrain_stats.items():
            self._terrain_stats_by_id[int(t)] = stats
        # Performance: batched analytics commit counter
        self._analytics_pending = 0
        self._analytics_batch_size = 10  # Commit every N turns

        # Performance: O(1) lookup for wonders and religions by name.
        # Avoids both O(n) scans and the StopIteration risk of bare next().
        self._wonders_by_name: dict[str, dict] = {w['name']: w for w in WONDERS}
        self._religions_by_name: dict[str, dict] = {r['name']: r for r in RELIGIONS}

        self._generate_world()

    # ── World Generation ────────────────────────────────────
    def _generate_world(self) -> None:
        """Generate terrain, resources, and place civilizations using MapGenerator."""
        gen = MapGenerator(self.W, self.H)
        self.terrain_map = gen.generate(self.terrain_preset)

        # Build owner map and count land
        self.owner_map = {}
        self.resource_map = {}
        self.total_land_tiles = 0
        is_water_cache = self._is_water_cache
        terrain_map = self.terrain_map

        for y in range(self.H):
            for x in range(self.W):
                self.owner_map[(x, y)] = None
                tid = terrain_map[(x, y)]
                if not is_water_cache.get(tid, True):
                    self.total_land_tiles += 1
                    # Place resources
                    if random.random() < 0.04:
                        if tid == Terrain.HILLS:
                            self.resource_map[(x, y)] = random.choice(["iron", "stone"])
                        elif tid == Terrain.MOUNTAIN:
                            self.resource_map[(x, y)] = random.choice(["iron", "gold_ore", "stone"])
                        elif tid in (Terrain.PLAINS, Terrain.GRASSLAND):
                            self.resource_map[(x, y)] = random.choice(["wheat", "horses", "iron"])
                        elif tid == Terrain.FOREST:
                            self.resource_map[(x, y)] = random.choice(["wheat", "stone"])
                        else:
                            self.resource_map[(x, y)] = random.choice(list(RESOURCE_TYPES.keys()))
                elif tid == Terrain.COAST:
                    if random.random() < 0.06:
                        self.resource_map[(x, y)] = "fish"

        # Place civilizations on good starting locations
        templates = CIV_TEMPLATES[:self.civ_count]
        self._place_civilizations(templates)

    def _place_civilizations(self, templates: list[dict]) -> None:
        """Place each civilization on a suitable starting tile with good spacing."""
        placed_positions: list[tuple[int, int]] = []
        min_distance = max(10, min(self.W, self.H) // 5)
        is_water_cache = self._is_water_cache
        terrain_map = self.terrain_map
        owner_map = self.owner_map

        for template in templates:
            best_pos = None
            best_score = -1

            for _ in range(2000):
                x = random.randint(0, self.W - 1)
                y = random.randint(0, self.H - 1)

                if is_water_cache.get(terrain_map[(x, y)], True):
                    continue
                if owner_map[(x, y)] is not None:
                    continue

                tid = terrain_map[(x, y)]
                terrain_score = {
                    Terrain.PLAINS: 10, Terrain.GRASSLAND: 10,
                    Terrain.FOREST: 7, Terrain.HILLS: 5,
                    Terrain.JUNGLE: 4, Terrain.DESERT: 2,
                    Terrain.TUNDRA: 2, Terrain.MOUNTAIN: 1,
                }.get(tid, 3)

                if placed_positions:
                    min_dist = min(
                        abs(x - px) + abs(y - py)
                        for px, py in placed_positions
                    )
                    dist_score = min(min_dist / min_distance, 2.0)
                else:
                    dist_score = 2.0

                near_coast = any(
                    terrain_map.get((x + dx, y + dy)) in (Terrain.COAST, Terrain.OCEAN)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if self._in_bounds(x + dx, y + dy)
                )
                coast_bonus = 3 if near_coast else 0

                total = terrain_score + dist_score * 5 + coast_bonus
                if total > best_score:
                    best_score = total
                    best_pos = (x, y)

            if best_pos:
                civ = Civ.from_template(template, best_pos[0], best_pos[1])
                self.civs.append(civ)
                owner_map[best_pos] = civ.name
                placed_positions.append(best_pos)

                # Cache civ by name for O(1) lookup
                self._civ_by_name[civ.name] = civ

                # Cache archetype for this civ (avoid template scan per call)
                archetype_key = template.get("archetype", "survivor")
                arch = PERSONALITY_ARCHETYPES.get(archetype_key, {})
                self._civ_archetype[civ.name] = arch

                # Generate initial leader and set government
                govt = template.get("government", "chiefdom")
                civ.government = govt
                civ.leader = Leader.generate(govt, archetype_key)
                civ.leader_history_count = 1

                # Apply archetype starting bonuses
                for stat, bonus in arch.get("starting_bonus", {}).items():
                    current = getattr(civ, stat, 0)
                    setattr(civ, stat, current + bonus)

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.W and 0 <= y < self.H

    # ── Main Loop ───────────────────────────────────────────
    def run(self) -> None:
        self.running = True
        while self.running:
            if not self.finished:
                self.process_turn()
            self.msleep(self.speed)

    def _get_ranks(self) -> dict[str, int]:
        sorted_civs = sorted(self.civs, key=lambda c: c.score, reverse=True)
        return {c.name: i + 1 for i, c in enumerate(sorted_civs)}

    # ── Turn Processing ─────────────────────────────────────
    def process_turn(self) -> None:
        if self.max_years > 0 and self.year - (-3000) >= self.max_years:
            self.finished = True
            self.log_signal.emit(f"SIMULATION COMPLETE - Max duration reached at Year {self.year}")
            self._end_game()
            return

        self.year += 1
        self.generation += 1
        self.last_path = []
        self.turn_events_log = []

        before_ranks = self._get_ranks()
        before_snapshots = [CivSnapshot(c, rank=before_ranks.get(c.name, 99)) for c in self.civs]

        self.season_timer += 1
        if self.season_timer >= SEASON_LENGTH:
            self.season = (self.season + 1) % 4
            self.season_timer = 0
        food_mult = FOOD_MULTIPLIERS[self.season]

        for civ in self.civs:
            self._process_civ_economy(civ, food_mult)
            self._process_civ_diplomacy(civ)
            self._process_leadership(civ)

        # Cross-civ dynamics: tech diffusion and border friction
        # (run after per-civ processing so we use post-update states).
        self._process_tech_diffusion()
        self._process_border_friction()

        self._process_events()

        for civ in self.civs:
            if len(civ.territory) > 0:
                self._process_civ_turn(civ)
            civ.score = (
                civ.population * 0.1
                + civ.technology * 10
                + len(civ.territory) * 50
                + len(civ.buildings) * 100
                + civ.culture
            )
            # Batched analytics logging
            self.analytics.log_snapshot(
                self.year, civ.name, civ.population, civ.technology,
                civ.military, len(civ.territory), civ.score, civ.last_action
            )
            self._analytics_pending += 1

            old_era = civ.era_name
            for era_def in self.defs.eras[::-1]:
                if civ.technology >= era_def['tech_threshold'] and civ.era_id < era_def['id']:
                    civ.era_id = era_def['id']
                    civ.era_name = era_def['era_name']
                    break
            if civ.era_name != old_era:
                self.log_signal.emit(f"{self.year}: {civ.name} entered the {civ.era_name} Era!")
                self.turn_events_log.append(f"{civ.name} entered the {civ.era_name} Era!")
                self.notification_signal.emit("Era Advance", f"{civ.name} entered the {civ.era_name} Era!")

        # Batch commit analytics every N turns
        if self._analytics_pending >= self._analytics_batch_size:
            self.analytics.commit()
            self._analytics_pending = 0

        # Incremental explored set update - only add new territory cells
        # This avoids the expensive full-rebuild of explored every turn
        self._update_explored_incremental()

        after_ranks = self._get_ranks()
        after_snapshots = [CivSnapshot(c, rank=after_ranks.get(c.name, 99)) for c in self.civs]
        season_name = SEASON_NAMES[self.season]

        html_report = GenerationReport.build_html_report(
            self.year, self.generation, season_name,
            before_snapshots, after_snapshots, self.turn_events_log
        )
        plain_report = GenerationReport.build_plain_text_report(
            self.year, self.generation, season_name,
            before_snapshots, after_snapshots, self.turn_events_log
        )
        self.gen_report_signal.emit(html_report, plain_report)
        self.update_signal.emit(self._build_data())

        if self.generation % AUTO_SAVE_INTERVAL == 0:
            self._auto_save()

    def _update_explored_incremental(self) -> None:
        """Incrementally update explored set by only adding new territory tiles.

        Much faster than clearing and rebuilding the entire set each turn,
        since territory changes are typically small (1-3 tiles per civ per turn).
        We do a full rebuild only periodically to clean up stale entries.
        """
        W, H = self.W, self.H
        explored = self.explored
        explored_add = explored.add

        for civ in self.civs:
            for x, y in civ.territory:
                for dx in range(-3, 4):
                    nx = x + dx
                    if nx < 0 or nx >= W:
                        continue
                    for dy in range(-3, 4):
                        ny = y + dy
                        if ny < 0 or ny >= H:
                            continue
                        explored_add((nx, ny))

        # Periodic cleanup: full rebuild every 100 turns to remove stale entries
        # (territory that was lost). This is cheaper than checking every turn.
        if self.generation % 100 == 0:
            self._rebuild_explored()

    def _rebuild_explored(self) -> None:
        """Full rebuild of explored set - used for periodic cleanup."""
        W, H = self.W, self.H
        new_explored: set[tuple] = set()
        add = new_explored.add
        for civ in self.civs:
            for x, y in civ.territory:
                for dx in range(-3, 4):
                    nx = x + dx
                    if nx < 0 or nx >= W:
                        continue
                    for dy in range(-3, 4):
                        ny = y + dy
                        if ny < 0 or ny >= H:
                            continue
                        add((nx, ny))
        self.explored = new_explored

    # ── Economy Processing ──────────────────────────────────
    def _process_civ_economy(self, civ: Civ, food_mult: float) -> None:
        base_cap = len(civ.territory) * 100.0
        bld_cap = sum(b['bonus'] * 500 for b in civ.buildings if b['effect'] == 'growth')
        wonder_cap = sum(w['bonus'] * 1000 for w in WONDERS if w['name'] in civ.wonders and w['effect'] == 'growth')
        civ.pop_cap = base_cap + bld_cap + wonder_cap

        # Government modifiers
        govt_data = GOVERNMENTS.get(civ.government, {})
        gold_mod = govt_data.get("gold_mod", 1.0)
        science_mod = govt_data.get("science_mod", 1.0)
        military_mod = govt_data.get("military_mod", 1.0)
        culture_mod = govt_data.get("culture_mod", 1.0)

        # Performance: cache terrain stats lookups
        terrain_map = self.terrain_map
        terrain_stats_by_id = self._terrain_stats_by_id
        resource_map = self.resource_map
        civ_pop = civ.population
        civ_treasury = civ.treasury
        civ_military = civ.military
        civ_culture = civ.culture
        pop_cap = civ.pop_cap

        for x, y in civ.territory:
            stats = terrain_stats_by_id.get(terrain_map[(x, y)])
            if stats is None:
                continue
            growth_factor = (
                min(1.0, pop_cap / max(1.0, civ_pop))
                if civ_pop > pop_cap else 1.0
            )
            civ_pop += stats['food'] * 5 * food_mult * growth_factor
            civ_treasury += stats['trade'] * 5 * gold_mod

            res = resource_map.get((x, y))
            if res is not None:
                if res == "iron":      civ_military += 2 * military_mod
                elif res == "wheat":   civ_pop += 5 * food_mult * growth_factor
                elif res == "gold_ore": civ_treasury += 8 * gold_mod
                elif res == "horses":  civ_military += 1 * military_mod
                elif res == "stone":   civ_treasury += 3 * gold_mod
                elif res == "fish":    civ_pop += 3 * food_mult * growth_factor

        civ.population = civ_pop
        civ.treasury = civ_treasury
        civ.military = civ_military

        for b in civ.buildings:
            eff = b['effect']
            bon = b['bonus']
            if eff == 'growth':    civ_pop += bon * 100 * food_mult; civ.population = civ_pop
            elif eff == 'trade':   civ.treasury += bon * 50 * gold_mod
            elif eff == 'tech':    civ.technology += bon * 0.5 * science_mod
            elif eff == 'military': civ.military += bon * 10 * military_mod
            elif eff == 'culture':  civ.culture += bon * 20 * culture_mod

        # Apply wonder effects using O(1) lookup (and gracefully skip
        # any wonder name that's not in the global WONDERS table, e.g.
        # from a save file that references a removed wonder).
        wonders_by_name = self._wonders_by_name
        for w_name in civ.wonders:
            w = wonders_by_name.get(w_name)
            if w is None:
                continue
            eff = w['effect']
            bon = w['bonus']
            if eff == 'growth':    civ.population += bon * 50
            elif eff == 'trade':   civ.treasury += bon * 25
            elif eff == 'military': civ.military += bon * 5
            elif eff == 'tech':    civ.technology += bon * 0.2
            elif eff == 'culture':  civ.culture += bon * 30

        if civ.religion:
            r = self._religions_by_name.get(civ.religion)
            if r:
                bt = r['bonus_type']
                bv = r['bonus_val']
                # NOTE: the original 0.01 multiplier for culture/trade
                # religions made them ~100x weaker than growth/military
                # religions. Brought the multiplier in line so all four
                # religion types are viable choices.
                if bt == 'growth':    civ.population += civ.culture * bv
                elif bt == 'military': civ.military += civ.culture * bv
                elif bt == 'culture':  civ.culture += civ.population * bv * 0.1
                elif bt == 'trade':    civ.treasury += civ.population * bv * 0.1

        civ.culture += (civ.population / 500.0)

        # ── Population Dynamics ───────────────────────────────
        # Birth/death model: net growth depends on stability. Famine
        # kicks in when pop exceeds cap by FAMINE_THRESHOLD, causing
        # additional deaths that SCALE with how far over cap we are.
        # A hard cap (POP_HARD_CAP_MULT) prevents runaway growth from
        # food income outpacing famine deaths.
        stability_norm = max(0.0, min(1.0, civ.stability / 100.0))
        birth_mult = 1.0 - STABILITY_BIRTH_MULT * (1.0 - stability_norm)
        death_mult = 1.0 + STABILITY_DEATH_MULT * (1.0 - stability_norm)
        births = civ.population * BIRTH_RATE * birth_mult
        deaths = civ.population * DEATH_RATE * death_mult
        civ.population = max(1.0, civ.population + births - deaths)

        # Famine: overpopulation beyond cap. Death rate scales linearly
        # with how far over cap the population is, so a pop at 1.5x cap
        # loses (0.5 * FAMINE_DEATH_RATE) per turn, while a pop at 2x cap
        # loses (1.0 * FAMINE_DEATH_RATE) per turn. This creates strong
        # pressure back toward the cap.
        if civ.population > civ.pop_cap * FAMINE_THRESHOLD:
            over_ratio = (civ.population / max(1.0, civ.pop_cap)) - 1.0
            famine_deaths = civ.population * FAMINE_DEATH_RATE * over_ratio
            civ.population = max(1.0, civ.population - famine_deaths)
            civ.stability -= 0.5 * over_ratio
            # Log famine only when severe (avoid log spam for mild overpop)
            if over_ratio > 0.15 and random.random() < 0.3:
                self.turn_events_log.append(f"{civ.name} suffers famine! (-{int(famine_deaths)} pop)")
        elif civ.population > civ.pop_cap * 1.05:
            # Mild overpopulation - stability hit only, no deaths
            civ.stability -= (civ.population - civ.pop_cap * 1.05) / 2000.0

        # Hard cap: never let population exceed pop_cap * POP_HARD_CAP_MULT.
        # This is a safety net for cases where food income massively
        # outpaces famine deaths (e.g., huge territory with lots of wheat).
        hard_cap = civ.pop_cap * POP_HARD_CAP_MULT
        if civ.population > hard_cap:
            civ.population = hard_cap

        civ.treasury -= civ.military * 0.02
        if civ.treasury < 0:
            deserters = int(abs(civ.treasury) / 10)
            civ.military = max(10, civ.military - deserters)
            civ.stability -= 1.0
            if deserters > 0:
                self.turn_events_log.append(f"{civ.name} troops deserting! (-{deserters})")

    # ── Cross-Civ Dynamics ───────────────────────────────────
    def _process_tech_diffusion(self) -> None:
        """Diffuse technology from higher-tech neighbors to lower-tech civs.

        For each pair of bordering civs where the tech gap exceeds
        TECH_DIFFUSION_MIN_GAP, the lower-tech civ gains a small tech
        boost proportional to the gap. This represents knowledge
        transfer along trade routes and shared borders, and prevents
        runaway tech disparities in long games.
        """
        if len(self.civs) < 2:
            return
        owner_map = self.owner_map
        civ_by_name = self._civ_by_name.get
        # Collect unique bordering pairs to avoid double-counting
        bordering_pairs: set[tuple[str, str]] = set()
        for civ in self.civs:
            civ_name = civ.name
            for x, y in civ.territory:
                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    no = owner_map.get((nx, ny))
                    if no and no != civ_name:
                        pair = tuple(sorted((civ_name, no)))
                        bordering_pairs.add(pair)
        for a_name, b_name in bordering_pairs:
            a = civ_by_name(a_name)
            b = civ_by_name(b_name)
            if not a or not b:
                continue
            # Determine direction: lower-tech civ learns from higher-tech
            if a.technology > b.technology + TECH_DIFFUSION_MIN_GAP:
                giver, learner = a, b
            elif b.technology > a.technology + TECH_DIFFUSION_MIN_GAP:
                giver, learner = b, a
            else:
                continue
            gain = TECH_DIFFUSION_RATE * (giver.technology - learner.technology)
            learner.technology += gain
            # Also gain a small culture boost (knowledge brings ideas)
            learner.culture += gain * 5.0

    def _process_border_friction(self) -> None:
        """Generate slow grievance buildup from territorial contact.

        Civs that share borders accumulate small grievances over time,
        simulating raids, border disputes, and resource competition.
        Religious differences amplify the friction. This makes long
        borders naturally tense even without explicit conflict.
        """
        if len(self.civs) < 2:
            return
        owner_map = self.owner_map
        civ_by_name = self._civ_by_name.get
        # Collect unique bordering pairs (same as tech diffusion)
        bordering_pairs: set[tuple[str, str]] = set()
        for civ in self.civs:
            civ_name = civ.name
            for x, y in civ.territory:
                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    no = owner_map.get((nx, ny))
                    if no and no != civ_name:
                        pair = tuple(sorted((civ_name, no)))
                        bordering_pairs.add(pair)
        for a_name, b_name in bordering_pairs:
            a = civ_by_name(a_name)
            b = civ_by_name(b_name)
            if not a or not b:
                continue
            # Skip pairs already at war (grievances already maxed)
            if a_name in b.at_war_with:
                continue
            # Skip allied pairs (friendship overrides friction)
            if a_name in b.alliances:
                continue
            friction = BORDER_FRICTION_BASE
            # Religious differences amplify friction
            if a.religion and b.religion and a.religion != b.religion:
                friction *= BORDER_FRICTION_RELIGION_MULT
            a.grievances[b_name] = a.grievances.get(b_name, 0) + friction
            b.grievances[a_name] = b.grievances.get(a_name, 0) + friction

    # ── Diplomacy Processing (personality-aware) ────────────
    def _get_archetype(self, civ: Civ) -> dict:
        """Look up cached archetype modifiers for a civilization."""
        return self._civ_archetype.get(civ.name, {})

    def _get_civ_by_name(self, name: str) -> Civ | None:
        """O(1) civ lookup by name instead of O(n) linear scan."""
        return self._civ_by_name.get(name)

    def _register_civ(self, civ: Civ, archetype_key: str = "survivor") -> None:
        """Register a civ in the fast-lookup cache."""
        self._civ_by_name[civ.name] = civ
        self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(archetype_key, {})

    # ── Leadership & Government ────────────────────────────
    def _process_leadership(self, civ: Civ) -> None:
        """Process leader succession, tenure tracking, and government changes.

        Each turn, the leader's tenure increases. When it exceeds the government's
        term limits, a succession event occurs based on the government type:
        - hereditary: leader dies, a new one with same archetype tendency inherits
        - election: leader is replaced, new archetype may differ
        - coup: military strongman seizes power (dictatorship, low stability)
        - theocratic: religious leader succeeds, archetype biased toward zealot
        """
        if not civ.leader:
            civ.leader = Leader.generate(civ.government, civ.archetype)
            civ.leader_history_count += 1
            return

        civ.leader.tenure += 1
        civ.gov_tenure += 1

        govt_data = GOVERNMENTS.get(civ.government, {})
        term_max = govt_data.get("leader_term_max", 40)
        term_min = govt_data.get("leader_term_min", 20)
        succession = govt_data.get("succession", "hereditary")

        # Check for forced succession (term exceeded)
        must_succeed = civ.leader.tenure >= term_max

        # Check for early succession based on type
        early_succession = False
        if civ.leader.tenure >= term_min:
            # Probability increases with tenure past minimum
            over_tenure = civ.leader.tenure - term_min
            base_prob = 0.02 + over_tenure * 0.01

            if succession == "election":
                # Elections are more regular
                base_prob = 0.08 + over_tenure * 0.03
            elif succession == "coup":
                # Coups more likely when stability is low
                if civ.stability < 40:
                    base_prob = 0.10 + over_tenure * 0.04
            elif succession == "theocratic":
                # Theocratic succession is more stable
                base_prob = 0.01 + over_tenure * 0.005

            early_succession = random.random() < base_prob

        if must_succeed or early_succession:
            self._succeed_leader(civ, succession)

        # Check for government reform/revolution
        self._process_government_reform(civ, govt_data)

    def _succeed_leader(self, civ: Civ, succession: str) -> None:
        """Handle leader succession with appropriate flavor."""
        old_leader = civ.leader
        old_archetype = civ.archetype

        # Record old leader in history
        if old_leader:
            # Add accomplishment summary
            if civ.stability > 70:
                old_leader.accomplishments.append("Stable reign")
            if len(civ.territory) > 20:
                old_leader.accomplishments.append("Expanded borders")
            if civ.technology > 10:
                old_leader.accomplishments.append("Advanced learning")
            civ.previous_leaders.append(old_leader)
            # Keep only last 5 previous leaders
            if len(civ.previous_leaders) > 5:
                civ.previous_leaders = civ.previous_leaders[-5:]

        # Determine new archetype based on succession type
        new_archetype = self._pick_successor_archetype(civ, succession)

        # Generate new leader
        new_leader = Leader.generate(civ.government, new_archetype)
        civ.leader = new_leader
        civ.leader_history_count += 1

        # Update cached archetype to reflect leader's archetype
        self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(new_archetype, {})

        # Update the AI agent's archetype so its consideration overrides
        # match the new leader's personality.
        if new_archetype != old_archetype:
            civ.agent.set_archetype(new_archetype)

        # Log the succession
        succession_flavor = {
            "hereditary": "has died. Long live",
            "election": "has been voted out. Elected:",
            "coup": "has been overthrown! Seizing power:",
            "theocratic": "has passed to the divine. Anointed:",
        }
        flavor = succession_flavor.get(succession, "is replaced by")
        old_name = old_leader.short_name if old_leader else "Previous ruler"
        self.log_signal.emit(
            f"{self.year}: {civ.name}: {old_name} {flavor} {new_leader.full_name}"
        )
        self.turn_events_log.append(
            f"{civ.name}: {old_name} {flavor} {new_leader.full_name}"
        )
        self.notification_signal.emit(
            "New Leader",
            f"{civ.name}: {new_leader.full_name} takes power!"
        )

        # Archetype change notification
        if new_archetype != old_archetype:
            old_label = PERSONALITY_ARCHETYPES.get(old_archetype, {}).get("label", old_archetype)
            new_label = PERSONALITY_ARCHETYPES.get(new_archetype, {}).get("label", new_archetype)
            self.log_signal.emit(
                f"{self.year}: {civ.name} shifts from {old_label} to {new_label} under {new_leader.short_name}"
            )
            self.turn_events_log.append(
                f"{civ.name} archetype: {old_label} -> {new_label}"
            )

        # Succession stability hit/bonus
        if succession == "coup":
            civ.stability = max(0, civ.stability - 20)
        elif succession == "hereditary":
            civ.stability = max(0, civ.stability - 5)
        elif succession == "election":
            civ.stability = min(100, civ.stability + 5)
        elif succession == "theocratic":
            civ.stability = min(100, civ.stability + 3)

    def _pick_successor_archetype(self, civ: Civ, succession: str) -> str:
        """Pick a new leader's archetype based on succession type and civ context.

        Hereditary: 60% same as previous, 40% random weighted by government
        Election: weighted by government flavor, can be very different
        Coup: heavy bias toward warlord/raider
        Theocratic: heavy bias toward zealot/builder
        """
        current = civ.archetype
        govt = civ.government

        if succession == "hereditary":
            # 60% chance of same dynasty archetype
            if random.random() < 0.6:
                return current
            return Leader._pick_archetype_for_government(govt)

        elif succession == "election":
            # Elections can bring in anyone, but weighted by government
            return Leader._pick_archetype_for_government(govt)

        elif succession == "coup":
            # Military coups favor warlords and raiders
            coup_weights = {"warlord": 5, "raider": 3, "survivor": 1, "merchant": 1}
            archetypes = list(coup_weights.keys())
            w = [coup_weights[a] for a in archetypes]
            return random.choices(archetypes, weights=w, k=1)[0]

        elif succession == "theocratic":
            # Religious succession favors zealots
            theo_weights = {"zealot": 5, "builder": 2, "diplomat": 1, "survivor": 1}
            archetypes = list(theo_weights.keys())
            w = [theo_weights[a] for a in archetypes]
            return random.choices(archetypes, weights=w, k=1)[0]

        return current

    def _process_government_reform(self, civ: Civ, govt_data: dict) -> None:
        """Check for government reforms and revolutions.

        Government changes happen when:
        1. Stability is very low -> revolution risk (can change to any allowed govt)
        2. Era advancement -> reform opportunity (peaceful transition)
        3. High culture + republic/democracy -> stable reform
        """
        current_govt = civ.government
        allowed = govt_data.get("allowed_govts", [])
        rebel_chance = govt_data.get("rebel_chance", 0.01)

        # Revolution: very low stability + rebel chance
        if civ.stability < 20 and random.random() < rebel_chance * 3:
            self._change_government(civ, allowed, "revolution")
            return

        # Low stability rebel chance
        if civ.stability < 40 and random.random() < rebel_chance:
            self._change_government(civ, allowed, "uprising")
            return

        # Era-based reform: when civ advances to a new era, chance to reform
        # to a government type that matches that era
        if random.random() < 0.005:  # ~0.5% per turn
            # Find eligible governments for current era
            eligible = []
            for govt_key, govt_info in GOVERNMENTS.items():
                if govt_key != current_govt and govt_key in allowed:
                    if civ.era_id >= govt_info.get("era_min", 0):
                        eligible.append(govt_key)
            if eligible:
                chosen = random.choice(eligible)
                self._change_government(civ, [chosen], "reform")

    def _change_government(self, civ: Civ, allowed: list[str], reason: str) -> None:
        """Change a civ's government type, possibly triggering a new leader."""
        if not allowed:
            return

        # Filter to only those whose era_min we qualify for
        eligible = [
            g for g in allowed
            if civ.era_id >= GOVERNMENTS.get(g, {}).get("era_min", 0)
        ]
        if not eligible:
            return

        old_govt = civ.government
        old_label = GOVERNMENTS.get(old_govt, {}).get("label", old_govt)
        new_govt = random.choice(eligible)
        new_label = GOVERNMENTS.get(new_govt, {}).get("label", new_govt)

        civ.government = new_govt
        civ.gov_tenure = 0

        # Generate a new leader appropriate for the new government
        new_archetype = Leader._pick_archetype_for_government(new_govt)
        new_leader = Leader.generate(new_govt, new_archetype)

        if civ.leader:
            civ.previous_leaders.append(civ.leader)
            if len(civ.previous_leaders) > 5:
                civ.previous_leaders = civ.previous_leaders[-5:]

        civ.leader = new_leader
        civ.leader_history_count += 1

        # Update archetype cache
        self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(new_archetype, {})

        # Update the AI agent's archetype to match the new leader
        civ.agent.set_archetype(new_archetype)

        # Stability effects
        if reason == "revolution":
            civ.stability = max(0, civ.stability - 30)
        elif reason == "uprising":
            civ.stability = max(0, civ.stability - 15)
        elif reason == "reform":
            civ.stability = min(100, civ.stability + 5)

        # Log
        flavor = {
            "revolution": "overthrown in revolution! New government:",
            "uprising": "forced to reform by uprising! New government:",
            "reform": "peacefully reformed to",
        }
        msg = flavor.get(reason, "changed government to")
        self.log_signal.emit(
            f"{self.year}: {civ.name} {msg} {new_label} under {new_leader.full_name}"
        )
        self.turn_events_log.append(
            f"{civ.name} government: {old_label} -> {new_label} ({reason})"
        )
        self.notification_signal.emit(
            "Government Change",
            f"{civ.name}: {old_label} -> {new_label}"
        )

    def _process_civ_diplomacy(self, civ: Civ) -> None:
        arch = self._get_archetype(civ)
        civ_by_name = self._civ_by_name.get

        for p in list(civ.trade_partners):
            pn = civ_by_name(p)
            if pn and pn.name not in civ.at_war_with:
                civ.treasury += 15
            else:
                civ.trade_partners.discard(p)

        base_recovery = 0.5
        resilience = arch.get("stability_resilience", 1.0)
        tolerance = arch.get("tolerance", 30)

        for o in list(civ.grievances.keys()):
            civ.grievances[o] = max(0, civ.grievances[o] - 0.5)
            war_threshold = arch.get("war_threshold", 50)
            if civ.grievances[o] < war_threshold * 0.3 and o in civ.at_war_with:
                civ.at_war_with.discard(o)
                on = civ_by_name(o)
                if on:
                    on.at_war_with.discard(civ.name)
                    self.log_signal.emit(f"{self.year}: {civ.name} made peace with {o}")
                    self.turn_events_log.append(f"{civ.name} made peace with {o}")
                    self.notification_signal.emit("Peace Treaty", f"{civ.name} made peace with {o}")

        self._process_religion(civ, tolerance)
        self._process_stability(civ, resilience)
        self._process_culture(civ)

    # ── Event Processing ────────────────────────────────────
    def _process_events(self) -> None:
        if random.random() < 0.03 and self.civs:
            tc = random.choice(self.civs)
            evts = [
                ("Plague", "A plague sweeps {}",
                 lambda c: setattr(c, 'population', c.population * 0.85), 5, "#8B0000"),
                ("Earthquake", "Earthquake strikes {}!",
                 lambda c: setattr(c, 'stability', max(0, c.stability - 20)), 0, "#A0522D"),
                ("Golden Age", "{} enters a Golden Age!",
                 lambda c: setattr(c, 'culture', c.culture + 100), 20, "#FFD700"),
                ("Drought", "Drought ravages {}!",
                 lambda c: setattr(c, 'stability', max(0, c.stability - 15)), 15, "#CD853F"),
                ("Barbarians", "Barbarians raid {}!",
                 lambda c: setattr(c, 'military', max(10, c.military - 80)), 0, "#FF4500"),
                ("Comet", "A comet is seen over {}!",
                 lambda c: setattr(c, 'culture', c.culture + 50), 10, "#9370DB"),
                # ── New event types for richer dynamics ─────────
                # Famine: triggers pop loss + stability hit (compounds with overpop)
                ("Famine", "Famine stalks {}!",
                 lambda c: (setattr(c, 'population', c.population * 0.95),
                            setattr(c, 'stability', max(0, c.stability - 10))), 8, "#8B4513"),
                # Schism: religious turmoil - large culture loss + stability hit
                ("Schism", "Religious schism tears {} apart!",
                 lambda c: (setattr(c, 'culture', c.culture * 0.85),
                            setattr(c, 'stability', max(0, c.stability - 15))), 6, "#4B0082"),
                # Renaissance: massive culture + tech boost (rare good event)
                ("Renaissance", "A renaissance blooms in {}!",
                 lambda c: (setattr(c, 'culture', c.culture + 200),
                            setattr(c, 'technology', c.technology + 2)), 15, "#FF69B4"),
                # Boom: economic boom - treasury boost
                ("Boom", "Economic boom enriches {}!",
                 lambda c: setattr(c, 'treasury', c.treasury + 300), 10, "#32CD32"),
                # Invasion: large military threat
                ("Invasion", "Barbarian invasion threatens {}!",
                 lambda c: setattr(c, 'military', max(10, c.military - 150)), 5, "#8B0000"),
            ]
            n, d, f, du, col = random.choice(evts)
            f(tc)
            ev = WorldEvent(n, d.format(tc.name), f, du, col, tc.name)
            self.active_events.append(ev)
            self.log_signal.emit(f"{self.year}: {ev.desc}")
            self.turn_events_log.append(ev.desc)
            self.notification_signal.emit(ev.name, ev.desc)

        civ_by_name = self._civ_by_name.get
        for ev in self.active_events[:]:
            ev.remaining -= 1
            if ev.remaining <= 0:
                self.active_events.remove(ev)
            else:
                c = civ_by_name(ev.target_civ)
                if c:
                    if ev.name == "Drought":    c.population *= 0.998; c.stability = max(0, c.stability - 1)
                    elif ev.name == "Golden Age": c.treasury += 30; c.culture += 10
                    elif ev.name == "Plague":    c.population *= 0.997
                    elif ev.name == "Comet":     c.culture += 5
                    elif ev.name == "Famine":    c.population *= 0.995; c.stability = max(0, c.stability - 0.5)
                    elif ev.name == "Schism":    c.culture = max(0, c.culture - 5); c.stability = max(0, c.stability - 0.5)
                    elif ev.name == "Renaissance": c.culture += 15; c.technology += 0.05
                    elif ev.name == "Boom":      c.treasury += 25
                    elif ev.name == "Invasion":  c.military = max(10, c.military - 5)

    # ── Sub-systems (personality-aware) ─────────────────────
    def _process_religion(self, civ: Civ, tolerance: float = 30) -> None:
        if not civ.religion and civ.culture > 500:
            civ.religion = random.choice(RELIGIONS)['name']
            self.log_signal.emit(f"{self.year}: {civ.name} founded {civ.religion}!")
            self.turn_events_log.append(f"{civ.name} founded {civ.religion}")
            self.notification_signal.emit("New Religion", f"{civ.name} founded {civ.religion}!")
        if civ.religion:
            civ_by_name = self._civ_by_name.get
            owner_map = self.owner_map
            # Build the set of distinct neighbor civs that border our
            # territory, then apply religious friction once per neighbor
            # pair. The previous implementation added grievance for every
            # border tile (so a 50-tile border with one neighbor could
            # add 50x grievance per turn, causing runaway wars).
            bordering_civs: set[str] = set()
            civ_name = civ.name
            for x, y in civ.territory:
                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    no = owner_map.get((nx, ny))
                    if no and no != civ_name:
                        bordering_civs.add(no)

            grievance_amount = 0.2 * (30 / max(tolerance, 5))
            for neighbor_name in bordering_civs:
                nc = civ_by_name(neighbor_name)
                if nc and nc.religion and nc.religion != civ.religion:
                    nc.grievances[civ.name] = nc.grievances.get(civ.name, 0) + grievance_amount
                    civ.grievances[nc.name] = civ.grievances.get(nc.name, 0) + grievance_amount

    def _process_stability(self, civ: Civ, resilience: float = 1.0) -> None:
        if civ.at_war_with:
            civ.stability -= len(civ.at_war_with) * 1.5
        if len(civ.territory) > civ.military / 10:
            civ.stability -= 1.0

        civ_by_name = self._civ_by_name.get
        owner_map = self.owner_map
        civ_name = civ.name
        civ_culture = civ.culture

        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                no = owner_map.get((nx, ny))
                if no and no != civ_name:
                    en = civ_by_name(no)
                    if en and en.culture > civ_culture * 1.5:
                        civ.stability -= 0.1

        # Apply government stability modifier
        govt_data = GOVERNMENTS.get(civ.government, {})
        govt_stab_mod = govt_data.get("stability_mod", 0.0)

        civ.stability += 1.5 * resilience + govt_stab_mod
        civ.stability = max(0, min(100, civ.stability))
        if civ.stability < 20 and len(civ.territory) > 5 and random.random() < 0.05:
            self._spawn_rebellion(civ)

    def _spawn_rebellion(self, civ: Civ) -> None:
        ft = sorted(
            civ.territory,
            key=lambda t: abs(t[0] - civ.capital[0]) + abs(t[1] - civ.capital[1]),
            reverse=True
        )
        rc = ft[0]
        rt = {rc}
        for x, y in ft[1:]:
            if abs(x - rc[0]) + abs(y - rc[1]) <= 4 and random.random() < 0.6:
                rt.add((x, y))
        if len(rt) < 3:
            return
        # Guard against an empty civ.name (shouldn't normally happen, but
        # an empty string would crash .split()[0]).
        civ_first_word = civ.name.split()[0] if civ.name else "Unknown"
        nn = f"{random.choice(REBEL_NAMES)} of {civ_first_word}"
        from PySide6.QtGui import QColor
        nc = Civ(
            nn,
            QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)).name(),
            rc[0], rc[1]
        )
        nc.population = civ.population * REBEL_POP_INHERIT
        nc.military = civ.military * REBEL_MILITARY_INHERIT
        nc.culture = civ.culture * REBEL_CULTURE_INHERIT
        nc.technology = civ.technology * REBEL_TECH_INHERIT
        nc.stability = 70
        # Rebels inherit a fraction of researched techs (knowledge spreads)
        nc.techs_researched = list(civ.techs_researched)
        # Rebels inherit a fraction of buildings (those in rebelling territory)
        nc.buildings = list(civ.buildings)[:max(1, len(civ.buildings) // 4)]
        for t in rt:
            civ.territory.discard(t)
            self.owner_map[t] = nn
            nc.territory.add(t)
        civ.population *= 0.8
        civ.military *= 0.85
        civ.stability = 50
        civ.at_war_with.add(nn)
        nc.at_war_with.add(civ.name)
        civ.grievances[nn] = 100
        nc.grievances[civ.name] = 100
        self.civs.append(nc)
        # Register new civ in fast lookup
        self._register_civ(nc, "survivor")
        self.log_signal.emit(f"{self.year}: REBELLION! {nn} broke from {civ.name}!")
        self.turn_events_log.append(f"REBELLION! {nn} broke from {civ.name}")
        self.notification_signal.emit("Rebellion!", f"{nn} broke from {civ.name}!")

    def _process_culture(self, civ: Civ) -> None:
        """Culture-flip mechanic with culture pressure gradient.

        A civ's culture exerts pressure on neighboring tiles owned by
        other civs. The flip probability depends on the culture ratio
        and adjacency to multiple friendly tiles (multiple fronts of
        cultural pressure flip tiles faster than a single point of
        contact). Capitals are immune to flipping.
        """
        if civ.culture < 100:
            return
        civ_by_name = self._civ_by_name.get
        owner_map = self.owner_map
        civ_name = civ.name
        civ_culture = civ.culture
        W, H = self.W, self.H

        # Iterate over a snapshot of territory to avoid "set changed size during iteration"
        for x, y in list(civ.territory):
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if (0 <= nx < W and 0 <= ny < H
                        and owner_map[(nx, ny)]
                        and owner_map[(nx, ny)] != civ_name):
                    en = owner_map[(nx, ny)]
                    ec = civ_by_name(en)
                    if not ec or (nx, ny) == ec.capital:
                        continue
                    # Culture ratio: how much stronger our culture is
                    culture_ratio = civ_culture / max(1.0, ec.culture)
                    # Need at least 2.5x culture to even consider flipping
                    if culture_ratio < 2.5:
                        continue
                    # Count adjacent own tiles for cultural pressure bonus
                    adjacent_own = sum(
                        1 for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]
                        if owner_map.get((nx+dx, ny+dy)) == civ_name
                    )
                    # Pressure: ratio * adjacency factor, scaled to probability
                    pressure = (culture_ratio - 2.5) * 0.02 * adjacent_own
                    pressure = min(0.15, pressure)  # Cap at 15% per turn
                    if random.random() < pressure:
                        ec.territory.discard((nx, ny))
                        civ.territory.add((nx, ny))
                        owner_map[(nx, ny)] = civ_name
                        ec.grievances[civ_name] = ec.grievances.get(civ_name, 0) + 20
                        self.log_signal.emit(f"{self.year}: {civ_name}'s culture flipped tile from {en}!")
                        self.turn_events_log.append(f"{civ_name} culture-flipped tile from {en}")

    # ── AI Decision Execution (personality-aware) ───────────
    def _get_neighbors(self, civ: Civ) -> list[Civ]:
        """Get neighboring civs using O(1) lookup."""
        seen = set()
        owner_map = self.owner_map
        civ_by_name = self._civ_by_name.get
        civ_name = civ.name
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                no = owner_map.get((nx, ny))
                if no and no != civ_name and no not in seen:
                    seen.add(no)
        return [civ_by_name(n) for n in seen if civ_by_name(n) is not None]

    # ── Threat Assessment Helpers ──────────────────────────
    def _assess_threats(self, civ: Civ, neighbors: list[Civ]) -> dict[str, float]:
        """Compute per-neighbor threat levels for the AI context."""
        civ_context = {
            "military": civ.military,
            "technology": civ.technology,
        }
        neighbor_data = []
        for n in neighbors:
            neighbor_data.append({
                "name": n.name,
                "military": n.military,
                "technology": n.technology,
                "grievance_vs_us": n.grievances.get(civ.name, 0),
                "at_war": n.name in civ.at_war_with,
                "allied": n.name in civ.alliances,
            })
        return ThreatAssessment.assess(civ_context, neighbor_data)

    def _build_ai_context(self, civ: Civ, arch: dict) -> dict:
        """Build the full AI decision context with all 25+ variables."""
        owner_map = self.owner_map
        terrain_map = self.terrain_map
        is_water_cache = self._is_water_cache
        civ_name = civ.name
        hc = 0
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                no = owner_map.get((nx, ny))
                if no and no != civ_name:
                    hc += 1

        # Threat assessment
        neighbors = self._get_neighbors(civ)
        threats = self._assess_threats(civ, neighbors)
        _, max_threat = ThreatAssessment.highest_threat(threats)

        # Find weakest war target for attack consideration
        war_targets = [c for c in self.civs if c.name in civ.at_war_with and c.territory]
        target_weakness = 0.0
        if war_targets:
            weakest = min(war_targets, key=lambda t: t.military)
            target_weakness = max(0.0, min(1.0, 1.0 - weakest.military / max(1, civ.military)))

        # Check if any dominant civ exists (score > 2x average). Surface
        # this as a normalized dominance signal so the AI can factor it
        # into diplomacy decisions (e.g. coalition building).
        avg_score = sum(c.score for c in self.civs) / max(1, len(self.civs))
        dominant_civ = None
        dominant_score = avg_score * 2.0
        for c in self.civs:
            if c.name != civ_name and c.score > dominant_score and c.score > 500:
                dominant_civ = c.name
                break

        # ── Feasibility signals ──────────────────────────────
        # These tell the AI whether an action is even possible, so it
        # doesn't waste turns picking actions that will auto-fail.
        # can_expand: any adjacent non-water tile that we don't own
        can_expand = False
        # available_trade_targets: neighbors we're not at war with & not already trading
        available_trade_targets = 0
        # available_diplomacy_targets: neighbors we're not at war with & not already allied
        available_diplomacy_targets = 0
        # available_attack_targets: war targets with border tiles
        available_attack_targets = len(war_targets)

        W, H = self.W, self.H
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                if is_water_cache.get(terrain_map[(nx, ny)], True):
                    continue
                if owner_map.get((nx, ny)) != civ_name:
                    can_expand = True
        for n in neighbors:
            if n.name in civ.at_war_with:
                continue
            if n.name not in civ.trade_partners:
                available_trade_targets += 1
            if n.name not in civ.alliances:
                available_diplomacy_targets += 1

        rs = {
            # Core stats
            "population": civ.population,
            "pop_cap": civ.pop_cap,
            "military": civ.military,
            "technology": civ.technology,
            "treasury": civ.treasury,
            "culture": civ.culture,
            "stability": civ.stability,

            # Territory and infrastructure
            "territory_count": len(civ.territory),
            "total_land": self.total_land_tiles,
            "building_count": len(civ.buildings),
            "wonder_count": len(civ.wonders),

            # Diplomacy
            "hostile_neighbors": hc,
            "at_war": len(civ.at_war_with) > 0,
            "war_count": len(civ.at_war_with),
            "alliance_count": len(civ.alliances),
            "trade_partner_count": len(civ.trade_partners),
            "total_civs": len(self.civs),

            # Tech comparison
            "avg_enemy_tech": sum(c.technology for c in self.civs if c != civ) / max(1, len(self.civs) - 1),

            # Game state
            "year": self.year,
            "era_id": civ.era_id,
            "has_religion": civ.religion is not None,

            # Government & Leadership
            "government": civ.government,
            "gov_tenure": civ.gov_tenure,
            "leader_tenure": civ.leader.tenure if civ.leader else 0,

            # Threat assessment
            "max_threat": max_threat,
            "target_weakness": target_weakness,

            # Coalition signal: name of any runaway dominant civ (or None).
            "dominant_civ": dominant_civ,

            # Feasibility signals (used by AI to avoid dead-end actions)
            "can_expand": can_expand,
            "available_trade_targets": available_trade_targets,
            "available_diplomacy_targets": available_diplomacy_targets,
            "available_attack_targets": available_attack_targets,
        }
        return rs

    def _process_civ_turn(self, civ: Civ) -> None:
        arch = self._get_archetype(civ)
        rs = self._build_ai_context(civ, arch)
        at = civ.agent.decide(rs)
        civ.last_action = at

        # Execute action and track success
        success = False

        if at == ActionType.EXPAND:
            success = self._exec_expand(civ, arch)
        elif at == ActionType.FORTIFY:
            success = self._exec_fortify(civ, arch)
        elif at == ActionType.DEVELOP:
            success = self._exec_develop(civ, arch)
        elif at == ActionType.RESEARCH:
            success = self._exec_research(civ, arch)
        elif at == ActionType.ATTACK:
            success = self._exec_attack(civ, arch)
        elif at == ActionType.CULTURE:
            success = self._exec_culture(civ, arch)
        elif at == ActionType.DIPLOMACY:
            success = self._exec_diplo(civ, arch)
        elif at == ActionType.TRADE:
            success = self._exec_trade(civ, arch)
        elif at == ActionType.WONDER:
            success = self._exec_wonder(civ, arch)

        # Record outcome for AI learning
        civ.agent.record_outcome(at, success)

    # ── Improved Action Execution ─────────────────────────
    def _exec_fortify(self, civ: Civ, arch: dict) -> bool:
        """Fortify: train troops and build defenses.

        Archetype-aware: warlords get more troops, builders get wall bonuses.
        """
        if civ.treasury < 10:
            # Minimal training even when broke - return True so the AI
            # records the partial success (troops were trained) rather
            # than logging a misleading failure.
            civ.military += 20
            return True

        base_troops = 50 + len(civ.buildings) * 5

        # Warlords train more aggressively
        if arch.get("label", "") == "Warlord":
            base_troops = int(base_troops * 1.3)
        # Raiders train in bursts
        elif arch.get("label", "") == "Raider":
            base_troops = int(base_troops * 1.2)
        # Builders invest in walls (stability bonus)
        elif arch.get("label", "") == "Builder":
            civ.stability = min(100, civ.stability + 2)

        civ.military += base_troops
        civ.treasury -= 30

        # In TOTAL_WAR state, extra military spending
        if civ.agent.strategic_state == StrategicState.TOTAL_WAR:
            extra = min(civ.treasury * 0.3, 100)
            civ.military += int(extra)
            civ.treasury -= extra

        return True

    def _exec_develop(self, civ: Civ, arch: dict) -> bool:
        """Develop: build the most needed building strategically.

        Instead of random choice, picks the building that addresses
        the civ's greatest weakness or amplifies their strength.
        """
        # Pre-compute owned building names as a set for O(1) membership
        # checks (previously rebuilt a list comprehension per candidate).
        owned_building_names = {cb['name'] for cb in civ.buildings}
        av = [
            b for b in self.defs.buildings
            if b['cost'] <= civ.treasury
            and b['min_era_id'] <= civ.era_id
            and b['name'] not in owned_building_names
        ]
        if not av:
            return False

        # Strategic building selection based on current needs
        def building_priority(b: dict) -> float:
            eff = b['effect']
            bon = b['bonus']
            score = bon  # Base: higher bonus is better

            # Prioritize what we need most
            if eff == 'growth' and civ.population < civ.pop_cap * 0.6:
                score *= 2.0  # Need population
            elif eff == 'military' and civ.military < 200:
                score *= 2.5  # Need defense
            elif eff == 'tech' and civ.technology < 10:
                score *= 2.0  # Need technology
            elif eff == 'trade' and civ.treasury < 300:
                score *= 1.8  # Need money
            elif eff == 'culture' and civ.culture < 100:
                score *= 1.5  # Need culture

            # Archetype preferences
            label = arch.get("label", "")
            if label == "Builder" and eff in ('growth', 'trade'):
                score *= 1.3
            elif label == "Warlord" and eff == 'military':
                score *= 1.5
            elif label == "Philosopher" and eff == 'tech':
                score *= 1.5
            elif label == "Merchant Republic" and eff == 'trade':
                score *= 1.5
            elif label == "Zealot" and eff == 'culture':
                score *= 1.4

            # Cost efficiency: prefer cheaper buildings when treasury is low
            if civ.treasury < 100:
                score *= (1.0 / max(1, b['cost'])) * 20

            return score

        b = max(av, key=building_priority)
        civ.treasury -= b['cost']
        civ.buildings.append(b)
        self.log_signal.emit(f"{self.year}: {civ.name} built {b['name']}")
        self.turn_events_log.append(f"{civ.name} built {b['name']}")
        return True

    def _exec_research(self, civ: Civ, arch: dict) -> bool:
        """Research: choose the most strategically valuable technology.

        Instead of random choice, picks tech that addresses needs
        or amplifies the civ's archetype strengths.
        """
        # Local set for O(1) membership checks (techs_researched is a list).
        researched = set(civ.techs_researched)
        av = [
            t for t in self.defs.techs
            if t['cost'] <= civ.treasury
            and t['era_id'] <= civ.era_id
            and t['name'] not in researched
        ]
        if not av:
            return False

        def tech_priority(t: dict) -> float:
            eff = t['effect']
            bon = t['bonus']
            score = bon  # Base: higher bonus

            # Prioritize techs that address weaknesses
            if eff == 'military' and civ.military < 200:
                score *= 2.0
            elif eff == 'growth' and civ.population < civ.pop_cap * 0.5:
                score *= 2.0
            elif eff == 'tech' and civ.technology < 10:
                score *= 1.8
            elif eff == 'culture' and civ.culture < 100:
                score *= 1.5

            # Archetype preferences
            label = arch.get("label", "")
            if label == "Philosopher" and eff == 'tech':
                score *= 2.0
            elif label == "Warlord" and eff == 'military':
                score *= 1.8
            elif label == "Merchant Republic" and eff in ('growth', 'culture'):
                score *= 1.3
            elif label == "Zealot" and eff == 'culture':
                score *= 1.6

            # Prefer cheaper techs when treasury is low
            if civ.treasury < 50:
                score *= (1.0 / max(1, t['cost'])) * 10

            return score

        t = max(av, key=tech_priority)
        civ.technology += t['bonus']
        civ.treasury -= t['cost']
        civ.techs_researched.append(t['name'])
        self.log_signal.emit(f"{self.year}: {civ.name} researched {t['name']}")
        self.turn_events_log.append(f"{civ.name} researched {t['name']}")
        return True

    def _exec_culture(self, civ: Civ, arch: dict) -> bool:
        """Culture: invest in cultural growth.

        Archetype-aware: zealots get culture bonuses, philosophers
        get science-culture synergy, diplomats get influence bonuses.
        """
        if civ.treasury < 10:
            return False

        base_culture = 50
        investment = min(40, civ.treasury)

        # Archetype bonuses
        label = arch.get("label", "")
        if label == "Zealot":
            base_culture = int(base_culture * 1.4)
        elif label == "Philosopher":
            civ.technology += 0.3  # Science-culture synergy
        elif label == "Diplomat":
            # Reduce grievances with all neighbors
            for n in self._get_neighbors(civ):
                n.grievances[civ.name] = max(0, n.grievances.get(civ.name, 0) - 5)
                civ.grievances[n.name] = max(0, civ.grievances.get(n.name, 0) - 5)

        civ.culture += base_culture
        civ.treasury -= investment

        # Golden Age state gives extra culture
        if civ.agent.strategic_state == StrategicState.GOLDEN_AGE:
            civ.culture += 30

        return True

    def _exec_diplo(self, civ: Civ, arch: dict) -> bool:
        """Diplomacy: form alliances, make peace, or coordinate against threats.

        Enhanced with coalition-building against dominant civilizations.
        """
        eagerness = arch.get("alliance_eagerness", 0.8)
        ns = self._get_neighbors(civ)
        war_threshold = arch.get("war_threshold", 50)

        # Priority 1: Make peace if in multiple wars and weak
        if len(civ.at_war_with) >= 2 and civ.military < 300:
            for enemy_name in list(civ.at_war_with):
                en = self._civ_by_name.get(enemy_name)
                if en and civ.grievances.get(enemy_name, 0) < war_threshold * 0.5:
                    civ.at_war_with.discard(enemy_name)
                    en.at_war_with.discard(civ.name)
                    civ.grievances[enemy_name] = max(0, civ.grievances.get(enemy_name, 0) - 20)
                    en.grievances[civ.name] = max(0, en.grievances.get(civ.name, 0) - 20)
                    self.log_signal.emit(f"{self.year}: {civ.name} made peace with {enemy_name}")
                    self.turn_events_log.append(f"{civ.name} made peace with {enemy_name}")
                    self.notification_signal.emit("Peace Treaty", f"{civ.name} made peace with {enemy_name}")
                    return True

        # Priority 2: Form alliance with least-grievance neighbor
        cs = [
            n for n in ns
            if n.name not in civ.at_war_with
            and n.name not in civ.alliances
            and civ.grievances.get(n.name, 0) < war_threshold * 0.4
        ]
        if cs:
            # Prefer allying with civs that share enemies (coalition building)
            def alliance_value(n: Civ) -> float:
                val = -civ.grievances.get(n.name, 0)  # Lower grievance = better
                # Bonus for shared enemies
                shared_enemies = len(civ.at_war_with & n.at_war_with)
                val += shared_enemies * 20
                # Bonus for strong allies
                val += n.military * 0.01
                return val

            t = max(cs, key=alliance_value)
            if t.grievances.get(civ.name, 0) < war_threshold * 0.4 and random.random() < 0.3 * eagerness:
                civ.alliances.add(t.name)
                t.alliances.add(civ.name)
                self.log_signal.emit(f"{self.year}: {civ.name} allied with {t.name}!")
                self.turn_events_log.append(f"{civ.name} allied with {t.name}")
                self.notification_signal.emit("Alliance Formed", f"{civ.name} allied with {t.name}!")
                return True
            else:
                # Improve relations even if alliance fails
                for n in cs:
                    n.grievances[civ.name] = max(0, n.grievances.get(civ.name, 0) - 10)
                    civ.grievances[n.name] = max(0, civ.grievances.get(n.name, 0) - 10)
                return True  # Partial success

        return False

    def _exec_trade(self, civ: Civ, arch: dict) -> bool:
        """Trade: establish trade routes for income.

        Enhanced: prefers trading with allies, avoids enemies,
        merchants get trade bonuses.
        """
        eagerness = arch.get("trade_eagerness", 0.9)
        war_threshold = arch.get("war_threshold", 50)
        ns = self._get_neighbors(civ)
        cs = [n for n in ns if n.name not in civ.at_war_with and n.name not in civ.trade_partners]
        if not cs:
            return False

        # Prefer trading with allies, then by lowest grievance
        def trade_value(n: Civ) -> float:
            val = 0.0
            if n.name in civ.alliances:
                val += 50  # Strong preference for allies
            val -= civ.grievances.get(n.name, 0)  # Avoid hostile partners
            val -= n.grievances.get(civ.name, 0)  # They might refuse too
            val += n.treasury * 0.001  # Rich partners are better
            return val

        cs.sort(key=trade_value, reverse=True)
        t = cs[0]  # Pick the best partner

        if t.grievances.get(civ.name, 0) < war_threshold * 0.6 and random.random() < 0.4 * eagerness:
            civ.trade_partners.add(t.name)
            t.trade_partners.add(civ.name)

            # Merchants get bonus trade income
            label = arch.get("label", "")
            if label == "Merchant Republic":
                civ.treasury += 10  # Extra trade bonus
                t.treasury += 5
            elif label == "Diplomat":
                # Trade improves relations
                civ.grievances[t.name] = max(0, civ.grievances.get(t.name, 0) - 3)
                t.grievances[civ.name] = max(0, t.grievances.get(civ.name, 0) - 3)

            self.log_signal.emit(f"{self.year}: {civ.name} traded with {t.name}")
            self.turn_events_log.append(f"{civ.name} traded with {t.name}")
            return True

        return False

    def _exec_wonder(self, civ: Civ, arch: dict) -> bool:
        """Wonder: build a world wonder for powerful bonuses.

        Enhanced: strategic wonder selection based on archetype needs.
        """
        wonder_hunger = arch.get("wonder_hunger", 0.5)
        treasury_threshold = 10000 * wonder_hunger
        # O(1) membership check via local set (wonders_built is a list).
        built = set(self.wonders_built)
        av = [w for w in WONDERS if w['name'] not in built and w['cost'] <= civ.treasury]
        if not av or civ.treasury <= treasury_threshold:
            return False

        # Strategic wonder selection
        def wonder_value(w: dict) -> float:
            val = w['bonus']  # Base: higher bonus is better
            eff = w['effect']

            # Prioritize wonders that address weaknesses
            if eff == 'military' and civ.military < 300:
                val *= 1.5
            elif eff == 'tech' and civ.technology < 15:
                val *= 1.5
            elif eff == 'growth' and civ.population < civ.pop_cap * 0.5:
                val *= 1.5
            elif eff == 'culture' and civ.culture < 200:
                val *= 1.3
            elif eff == 'trade' and civ.treasury < 500:
                val *= 1.4

            # Archetype preferences
            label = arch.get("label", "")
            if label == "Builder":
                val *= 1.3  # Builders love all wonders
            elif label == "Philosopher" and eff == 'tech':
                val *= 1.6
            elif label == "Warlord" and eff == 'military':
                val *= 1.5
            elif label == "Merchant Republic" and eff == 'trade':
                val *= 1.6
            elif label == "Zealot" and eff == 'culture':
                val *= 1.5

            return val

        w = max(av, key=wonder_value)
        civ.treasury -= w['cost']
        civ.wonders.append(w['name'])
        self.wonders_built.append(w['name'])
        self.log_signal.emit(f"{self.year}: {civ.name} built the {w['name']}!")
        self.turn_events_log.append(f"{civ.name} built the {w['name']}")
        self.notification_signal.emit("Wonder Built", f"{civ.name} built the {w['name']}!")
        return True

    def _exec_attack(self, civ: Civ, arch: dict) -> bool:
        """Attack: launch a military assault on an enemy.

        Enhanced with:
        - Target selection: attack weakest war target first
        - Tile selection: prefer high-value tiles, tiles near capital, resource tiles
        - Warlords get combat bonuses, raiders get speed bonuses
        - Coordinate with allies (joint attacks are more effective)
        - Multi-target: when at war with several civs, can attack each
          (limited by military strength) - reduces deadlocks in multi-front wars
        """
        wt = [c for c in self.civs if c.name in civ.at_war_with and c.territory]
        if not wt or civ.military < 150:
            civ.last_action = ActionType.FORTIFY
            civ.military += 30
            return False

        # Target selection: prefer weakest enemy for easier conquest.
        # Sort by (military, -territory) so we attack the weakest with the most land.
        wt_sorted = sorted(wt, key=lambda t: (t.military, -len(t.territory)))

        # Multi-target: attack up to N targets depending on military strength.
        # At mil=300, attack 1 target. At mil=1500+, attack up to 3.
        max_targets = max(1, min(3, int(civ.military / 500)))
        # Raiders can hit one extra target per turn (hit-and-run doctrine)
        if arch.get("label", "") == "Raider":
            max_targets += 1

        any_success = False
        for tc in wt_sorted[:max_targets]:
            if civ.military < 100:
                break  # Too exhausted to continue
            success = self._attack_single_target(civ, arch, tc)
            any_success = any_success or success

        return any_success

    def _attack_single_target(self, civ: Civ, arch: dict, tc: Civ) -> bool:
        """Execute a single attack against target civ tc. Returns True if successful."""
        owner_map = self.owner_map
        terrain_map = self.terrain_map
        tc_name = tc.name
        borders = [
            (nx, ny) for x, y in civ.territory
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            if 0 <= nx < self.W and 0 <= ny < self.H
            and owner_map.get((nx, ny)) == tc_name
        ]
        if not borders:
            return False

        # Tile selection: prefer tiles with resources, near enemy capital, or high-value terrain
        def tile_attack_value(t: tuple) -> float:
            val = 1.0
            # Resource tiles are more valuable
            if t in self.resource_map:
                val += 3.0
            # Tiles closer to enemy capital are strategically valuable
            dist_to_cap = abs(t[0] - tc.capital[0]) + abs(t[1] - tc.capital[1])
            val += max(0, 5 - dist_to_cap * 0.1)
            # Terrain with defense bonus is harder but more valuable once captured
            tid = terrain_map.get(t, 0)
            t_stats = self._terrain_stats_by_id.get(tid, {})
            if t_stats.get('food', 0) > 1.5:
                val += 1.0  # Good food production
            if t_stats.get('trade', 0) > 1.0:
                val += 1.0  # Good trade
            return val

        tt = max(borders, key=tile_attack_value)

        expansion_greed = arch.get("expansion_greed", 1.0)
        attack_bonus = 1.0 + (expansion_greed - 1.0) * 0.3

        # Warlord combat bonus
        label = arch.get("label", "")
        if label == "Warlord":
            attack_bonus *= 1.15
        elif label == "Raider":
            attack_bonus *= 1.1  # Raider hit-and-run

        # Ally coordination bonus: if allies are also at war with target, bonus
        ally_bonus = 1.0
        for ally_name in civ.alliances:
            ac = self._civ_by_name.get(ally_name)
            if ac and tc_name in ac.at_war_with:
                ally_bonus += 0.1  # Each allied co-belligerent adds 10%

        ap = civ.military * random.uniform(0.9, 1.3) * attack_bonus * ally_bonus
        dp = tc.military * random.uniform(0.7, 1.1)
        civ.military -= 40

        if ap > dp:
            # Guard against race condition
            if tt in tc.territory:
                tc.territory.discard(tt)
                tc.military -= 50
                civ.territory.add(tt)
                owner_map[tt] = civ.name

                # Raider bonus: steal treasury on conquest
                if label == "Raider" and tc.treasury > 0:
                    stolen = min(tc.treasury * 0.1, 50)
                    civ.treasury += stolen
                    tc.treasury -= stolen

                self.log_signal.emit(f"{self.year}: {civ.name} conquered {tt} from {tc_name}!")
                self.turn_events_log.append(f"{civ.name} conquered tile from {tc_name}")
            else:
                self.log_signal.emit(f"{self.year}: {civ.name} attack on {tc_name} - tile already lost")
                self.turn_events_log.append(f"{civ.name} attack on {tc_name} - tile already lost")
        else:
            self.log_signal.emit(f"{self.year}: {civ.name} failed to attack {tc_name}")
            self.turn_events_log.append(f"{civ.name} failed to attack {tc_name}")
            # Failed attack: defender gets a counter-attack chance
            if random.random() < 0.3 and tc.military > 200:
                civ.military -= 20

        # Alliance defense cascade (always triggers on attack, regardless of outcome)
        civ_by_name = self._civ_by_name.get
        for an in tc.alliances:
            ac = civ_by_name(an)
            if ac and civ.name not in ac.at_war_with:
                ac.at_war_with.add(civ.name)
                civ.at_war_with.add(ac.name)
                self.log_signal.emit(f"{self.year}: {ac.name} joins war defending {tc_name}!")
                self.turn_events_log.append(f"{ac.name} joins war defending {tc_name}")

        return ap > dp

    def _exec_expand(self, civ: Civ, arch: dict) -> bool:
        """Expand: claim new territory tiles.

        Enhanced with:
        - Strategic tile selection: prioritize resource tiles, tiles near capital,
          tiles that connect territory, and tiles with good terrain stats
        - Expansion greed modifier from archetype
        - Raiders can claim multiple tiles per turn
        - Avoid expanding into overwhelming enemy territory
        """
        war_threshold = arch.get("war_threshold", 50)
        owner_map = self.owner_map
        terrain_map = self.terrain_map
        is_water_cache = self._is_water_cache
        resource_map = self.resource_map
        civ_name = civ.name
        W, H = self.W, self.H

        borders = [
            (nx, ny) for x, y in civ.territory
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            if 0 <= nx < W and 0 <= ny < H
            and owner_map.get((nx, ny)) != civ_name
            and not is_water_cache.get(terrain_map[(nx, ny)], True)
        ]
        if not borders or civ.military <= 20:
            return False

        # Strategic tile selection
        terrain_stats_by_id = self._terrain_stats_by_id
        capital = civ.capital

        def tile_expand_value(t: tuple) -> float:
            val = 0.0

            # Terrain quality (food + trade are most valuable for growth)
            stats = terrain_stats_by_id.get(terrain_map[t], {})
            val += stats.get('food', 0) * 3.0
            val += stats.get('trade', 0) * 2.0
            val += stats.get('prod', 0) * 1.0

            # Resource bonus
            if t in resource_map:
                val += 5.0

            # Proximity to capital (prefer closer expansion for cohesion)
            dist_to_cap = abs(t[0] - capital[0]) + abs(t[1] - capital[1])
            val += max(0, 3 - dist_to_cap * 0.05)

            # Connectivity bonus: tiles adjacent to more of our territory are better
            adjacent_own = sum(
                1 for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]
                if owner_map.get((t[0]+dx, t[1]+dy)) == civ_name
            )
            val += adjacent_own * 2.0

            # Avoid tiles that would trigger war with strong civs
            co = owner_map.get(t)
            if co:
                en = self._civ_by_name.get(co)
                if en:
                    # Avoid expanding into territory of civs much stronger than us
                    if en.military > civ.military * 2 and en.name not in civ.at_war_with:
                        val -= 10.0  # Strong deterrent
                    # But target weak civs if we're aggressive
                    elif en.military < civ.military * 0.5 and arch.get("label", "") == "Warlord":
                        val += 3.0  # Warlords love picking on the weak

            return val

        bt = max(borders, key=tile_expand_value)
        co = owner_map.get(bt)
        if co:
            en = self._civ_by_name.get(co)
            if en:
                en.grievances[civ_name] = en.grievances.get(civ_name, 0) + 30
                if en.grievances[civ_name] > war_threshold:
                    en.at_war_with.add(civ_name)
                    civ.at_war_with.add(en.name)
                    self.log_signal.emit(f"{self.year}: {civ_name} & {en.name} went to WAR!")
                    self.turn_events_log.append(f"{civ_name} & {en.name} went to WAR!")
                    self.notification_signal.emit("War Declared!", f"{civ_name} & {en.name} went to WAR!")

        self.pathfinder.init(civ.capital, bt, self.defs.terrain_stats)
        self.pathfinder.compute_shortest_path()
        path = self.pathfinder.get_path(max_len=8)
        if path and len(path) > 1:
            civ.territory.add(bt)
            owner_map[bt] = civ_name
            civ.military -= 15
            self.last_path = path
            self.log_signal.emit(f"{self.year}: {civ_name} expanded to {bt}")
            self.turn_events_log.append(f"{civ_name} expanded to new tile")

            # Raider bonus: can claim an extra tile per turn
            expansion_greed = arch.get("expansion_greed", 1.0)
            if expansion_greed > 1.3 and civ.military > 50 and len(borders) > 1:
                # Try to claim one more tile
                remaining = [b for b in borders if b != bt and owner_map.get(b) is None]
                if remaining:
                    bt2 = max(remaining, key=tile_expand_value)
                    co2 = owner_map.get(bt2)
                    if co2 is None:  # Only claim unclaimed tiles on bonus expansion
                        civ.territory.add(bt2)
                        owner_map[bt2] = civ_name
                        civ.military -= 10
                        self.log_signal.emit(f"{self.year}: {civ_name} rapidly expanded to {bt2}")
                        self.turn_events_log.append(f"{civ_name} rapidly expanded")

            return True

        return False

    # ── End Game ────────────────────────────────────────────
    def _end_game(self) -> None:
        # Flush any pending analytics snapshots so post-game queries
        # against the DB see the final turn.
        try:
            self.analytics.commit()
        except Exception:
            pass
        self.update_signal.emit(self._build_data())
        for i, c in enumerate(sorted(self.civs, key=lambda x: x.score, reverse=True)):
            self.log_signal.emit(
                f"  #{i+1} {c.name} - Score: {int(c.score)} | "
                f"Pop: {int(c.population)} | Territory: {len(c.territory)}"
            )

    # ── Build UI Data ───────────────────────────────────────
    def _build_data(self) -> dict:
        tr = []
        seen_pairs: set[tuple] = set()
        for c in self.civs:
            for t in c.trade_partners:
                pair = tuple(sorted((c.name, t)))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    tr.append(pair)
        return {
            'terrain': self.terrain_map, 'owners': self.owner_map,
            'civs': self.civs, 'year': self.year,
            'generation': self.generation, 'last_path': self.last_path,
            'capitals': {c.name: c.capital for c in self.civs},
            'explored': self.explored, 'trade_routes': tr,
            'active_events': self.active_events,
            'resource_map': self.resource_map, 'season': self.season,
        }

    # ── Save / Load ────────────────────────────────────────
    def save_game(self, filepath: str) -> None:
        state = {
            "year": self.year, "generation": self.generation,
            "season": self.season, "season_timer": self.season_timer,
            "max_years": self.max_years, "terrain_preset": self.terrain_preset,
            "W": self.W, "H": self.H,
            "terrain_map": {f"{k[0]},{k[1]}": v for k, v in self.terrain_map.items()},
            "owner_map": {f"{k[0]},{k[1]}": v for k, v in self.owner_map.items()},
            "resource_map": {f"{k[0]},{k[1]}": v for k, v in self.resource_map.items()},
            "wonders_built": self.wonders_built,
            "civs": [c.to_dict() for c in self.civs],
        }
        with open(filepath, 'w') as f:
            json.dump(state, f)
        self.log_signal.emit(f"Game saved to {filepath}")

    def load_game(self, filepath: str) -> None:
        with open(filepath, 'r') as f:
            state = json.load(f)
        self.year = state["year"]
        self.generation = state["generation"]
        self.season = state["season"]
        self.season_timer = state["season_timer"]
        self.max_years = state.get("max_years", 0)
        self.terrain_preset = state.get("terrain_preset", TerrainPreset.CONTINENT)
        self.W = state["W"]
        self.H = state["H"]
        self.wonders_built = state.get("wonders_built", [])
        self.finished = False
        self.terrain_map = {tuple(map(int, k.split(','))): v for k, v in state["terrain_map"].items()}
        self.owner_map = {tuple(map(int, k.split(','))): v for k, v in state["owner_map"].items()}
        self.resource_map = {tuple(map(int, k.split(','))): v for k, v in state["resource_map"].items()}
        self.civs = [Civ.from_dict(cd) for cd in state["civs"]]
        self.pathfinder = DStarLite(self.W, self.H)
        self.last_path = []
        self.active_events = []

        # Rebuild fast-lookup caches
        self._civ_by_name.clear()
        self._civ_archetype.clear()
        for civ in self.civs:
            self._civ_by_name[civ.name] = civ
            # Use the leader's archetype if available, otherwise fall back to template
            arch_key = civ.archetype  # This reads from leader.archetype via property
            if arch_key:
                self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(arch_key, {})
            else:
                # Fallback: try to find from templates
                for t in CIV_TEMPLATES:
                    if t["name"] == civ.name:
                        key = t.get("archetype", "survivor")
                        self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(key, {})
                        break
                else:
                    self._civ_archetype[civ.name] = {}

        # Rebuild explored set
        self._rebuild_explored()

        self.log_signal.emit(f"Game loaded from {filepath}")
        self.update_signal.emit(self._build_data())

    def _auto_save(self) -> None:
        # Use an absolute path under the project's saves directory so
        # autosaves don't litter the process CWD (which may be read-only
        # or change between runs). Falls back to CWD if not writable.
        saves_dir = os.path.join(os.path.expanduser("~"), ".civsim", "saves")
        try:
            os.makedirs(saves_dir, exist_ok=True)
            path = os.path.join(saves_dir, f"autosave_gen{self.generation}.json")
        except OSError:
            path = f"autosave_gen{self.generation}.json"
        self.save_game(path)
        self.autosave_signal.emit(path)


# ════════════════════════════════════════════════════════════
# ──────────────────────────────────────────────────────────────────────
# new_widgets.py – Enhanced widget set for civilization simulation
# Tokyo Night theme · concatenated after config, database, ai, models, engine
# ──────────────────────────────────────────────────────────────────────

# ── 1. ENHANCED_STYLESHEET ────────────────────────────────────────────

ENHANCED_STYLESHEET = """
QMainWindow { background-color: #1a1b26; }
QWidget { background-color: #1a1b26; color: #c0caf5; font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif; font-size: 12px; }
QGraphicsView { border: 1px solid #3b4261; background-color: #1a1b26; border-radius: 2px; }
QToolBar { background-color: #24283b; border-bottom: 1px solid #1a1a2a; spacing: 5px; padding: 3px 8px; }
QPushButton { background-color: #2f3450; color: #c0caf5; border: 1px solid #3b4261; border-radius: 4px; padding: 4px 12px; font-size: 11px; }
QPushButton:hover { background-color: #3b4261; border-color: #7aa2f7; }
QPushButton:pressed { background-color: #1a1b26; }
QPushButton:checked { background-color: #7aa2f7; color: #1a1b26; font-weight: bold; }
QSlider::groove:horizontal { background: #24283b; height: 4px; border-radius: 2px; }
QSlider::handle:horizontal { background: #7aa2f7; width: 14px; margin: -5px 0; border-radius: 7px; }
QSlider::handle:horizontal:hover { background: #89b4fa; }
QTextEdit { border: 1px solid #3b4261; background-color: #1a1b26; border-radius: 4px; color: #a9b1d6; }
QSplitter::handle { background-color: #3b4261; width: 3px; }
QSplitter::handle:hover { background-color: #7aa2f7; }
QScrollBar:vertical { background: transparent; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #3b4261; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #565f89; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: transparent; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #3b4261; border-radius: 4px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #565f89; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
QComboBox { background-color: #2f3450; border: 1px solid #3b4261; border-radius: 4px; padding: 3px 8px; color: #c0caf5; font-size: 11px; }
QComboBox:hover { border-color: #7aa2f7; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background-color: #24283b; color: #c0caf5; selection-background-color: #7aa2f7; border: 1px solid #3b4261; }
QCheckBox { spacing: 4px; }
QCheckBox::indicator { width: 14px; height: 14px; border-radius: 3px; border: 1px solid #565f89; background-color: #24283b; }
QCheckBox::indicator:checked { background-color: #7aa2f7; border-color: #7aa2f7; }
QGroupBox { border: 1px solid #3b4261; border-radius: 6px; margin-top: 10px; padding: 14px 8px 8px 8px; font-weight: bold; color: #7aa2f7; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QToolTip { background-color: #24283b; color: #c0caf5; border: 1px solid #7aa2f7; padding: 6px 10px; border-radius: 4px; font-size: 11px; }
QScrollArea { border: none; background-color: #1a1b26; }
QTabWidget::pane { border: 1px solid #3b4261; background-color: #1a1b26; border-radius: 4px; }
QStatusBar { background-color: #24283b; border-top: 1px solid #3b4261; color: #a9b1d6; }
QStatusBar QLabel { padding: 0 8px; }
QFrame { border: none; }
QFrame[frameShape="6"] { color: #3b4261; }
"""


# ── 2. SparklineChart ─────────────────────────────────────────────────

class SparklineChart(QWidget):
    """Mini sparkline area chart for embedding in CivCards."""

    def __init__(self, color="#7aa2f7", label="", parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._label = label
        self._data = []
        self._max_points = 100
        self.setFixedHeight(50)
        self.setMinimumWidth(60)

    def add_point(self, value: float):
        self._data.append(float(value))
        if len(self._data) > self._max_points:
            self._data = self._data[-self._max_points:]
        self.update()

    def clear_data(self):
        self._data.clear()
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pad_top, pad_bot = 4, 4
        plot_h = h - pad_top - pad_bot
        data_min = min(self._data)
        data_max = max(self._data)
        data_range = data_max - data_min if data_max != data_min else 1.0

        def to_screen(i, v):
            x = (i / max(len(self._data) - 1, 1)) * (w - 20)
            y = pad_top + plot_h - ((v - data_min) / data_range) * plot_h
            return x, y

        # Build path
        path = QPainterPath()
        for i, v in enumerate(self._data):
            sx, sy = to_screen(i, v)
            if i == 0:
                path.moveTo(sx, sy)
            else:
                path.lineTo(sx, sy)

        # Area fill – gradient from transparent at bottom to colour at top
        area_path = QPainterPath(path)
        last_x, _ = to_screen(len(self._data) - 1, self._data[-1])
        first_x, _ = to_screen(0, self._data[0])
        area_path.lineTo(last_x, h - pad_bot)
        area_path.lineTo(first_x, h - pad_bot)
        area_path.closeSubpath()

        grad = QLinearGradient(0, pad_top, 0, h - pad_bot)
        top_color = QColor(self._color)
        top_color.setAlpha(0)
        bot_color = QColor(self._color)
        bot_color.setAlpha(90)
        grad.setColorAt(0, bot_color)
        grad.setColorAt(1, top_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawPath(area_path)

        # Line
        line_pen = QPen(self._color, 1.5)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Current value text
        cur = self._data[-1]
        painter.setPen(QColor("#c0caf5"))
        painter.setFont(QFont("Segoe UI", 8))
        txt = f"{cur:.0f}" if cur == int(cur) else f"{cur:.1f}"
        painter.drawText(w - 18, h - 2, txt)

        painter.end()


# ── 3. StatBar ────────────────────────────────────────────────────────

class StatBar(QWidget):
    """Custom progress bar with gradient fill and label."""

    def __init__(self, label="", color="#7aa2f7", parent=None):
        super().__init__(parent)
        self._label = label
        self._color = QColor(color)
        self._value = 0.0
        self._max_value = 1.0
        self._display_text = ""
        self.setFixedHeight(20)

    def set_value(self, value: float, max_value: float = None, display_text: str = ""):
        self._value = float(value)
        if max_value is not None:
            self._max_value = float(max_value)
        self._display_text = display_text
        self.update()

    @staticmethod
    def _fmt(v):
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if v >= 1_000:
            return f"{v / 1_000:.1f}K"
        return f"{v:.0f}" if v == int(v) else f"{v:.1f}"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        left_margin = 50
        right_margin = 50
        bar_x = left_margin
        bar_w = w - left_margin - right_margin
        if bar_w < 10:
            bar_w = 10
        bar_rect = QRectF(bar_x, 3, bar_w, h - 6)

        # Label
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#a9b1d6"))
        painter.drawText(0, 0, left_margin - 4, h, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._label)

        # Value text
        val_txt = self._display_text or self._fmt(self._value)
        painter.setPen(QColor("#c0caf5"))
        fnt = painter.font()
        fnt.setBold(True)
        painter.setFont(fnt)
        painter.drawText(w - right_margin, 0, right_margin, h, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, val_txt)

        # Background bar
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1a1b26"))
        painter.drawRoundedRect(bar_rect, 3, 3)

        # Filled portion
        ratio = min(self._value / self._max_value, 1.0) if self._max_value else 0
        fill_w = bar_w * ratio
        if fill_w > 0:
            fill_rect = QRectF(bar_x, 3, fill_w, h - 6)
            grad = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
            grad.setColorAt(0, self._color.darker(150))
            grad.setColorAt(1, self._color)
            painter.setBrush(grad)
            painter.drawRoundedRect(fill_rect, 3, 3)

        painter.end()


# ── 4. TimelineGraph ──────────────────────────────────────────────────

class TimelineGraph(QWidget):
    """Enhanced timeline chart with area fills and Tokyo Night palette."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._civs_data = []
        self._history = []          # list of snapshots: [ {name, color, score}, … ]
        self.setMinimumSize(300, 140)
        self.setMaximumHeight(200)

    def update_data(self, civs_data):
        """civs_data: list of dicts with 'name', 'color', 'score'."""
        self._civs_data = civs_data
        snapshot = [
            {"name": d.get("name", "?"), "color": d.get("color", "#7aa2f7"), "score": d.get("score", 0)}
            for d in civs_data
        ]
        self._history.append(snapshot)
        if len(self._history) > 200:
            self._history = self._history[-200:]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        bg = "#1a1b26"
        grid = "#2f3450"
        border = "#3b4261"
        y_label_color = "#565f89"

        # Background
        painter.fillRect(0, 0, w, h, QColor(bg))
        painter.setPen(QPen(QColor(border), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        if len(self._history) < 2:
            painter.setPen(QColor(y_label_color))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Waiting for data\u2026")
            painter.end()
            return

        margin_l, margin_r, margin_t, margin_b = 40, 10, 20, 20
        plot_w = w - margin_l - margin_r
        plot_h = h - margin_t - margin_b

        # Gather all scores for Y range
        all_scores = [s for snap in self._history for s in (c["score"] for c in snap)]
        if not all_scores:
            painter.end()
            return
        y_min = min(all_scores)
        y_max = max(all_scores)
        y_range = y_max - y_min if y_max != y_min else 1

        num_gen = len(self._history)

        def to_xy(gen_idx, score):
            x = margin_l + (gen_idx / max(num_gen - 1, 1)) * plot_w
            y = margin_t + plot_h - ((score - y_min) / y_range) * plot_h
            return x, y

        # Horizontal grid lines (5)
        painter.setPen(QPen(QColor(grid), 1, Qt.PenStyle.DotLine))
        for i in range(6):
            y_val = y_min + (y_range * i / 5)
            _, gy = to_xy(0, y_val)
            painter.drawLine(int(margin_l), int(gy), int(w - margin_r), int(gy))
            painter.setPen(QColor(y_label_color))
            painter.setFont(QFont("Segoe UI", 7))
            painter.drawText(2, int(gy) - 6, margin_l - 4, 12, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{y_val:.0f}")
            painter.setPen(QPen(QColor(grid), 1, Qt.PenStyle.DotLine))

        # Collect civ names + colors (from latest snapshot)
        civ_info = {}
        for c in self._history[-1]:
            civ_info[c["name"]] = c["color"]

        # Draw each civ line + area
        for civ_name, civ_color in civ_info.items():
            color = QColor(civ_color)
            points = []
            for gi, snap in enumerate(self._history):
                for c in snap:
                    if c["name"] == civ_name:
                        points.append((gi, c["score"]))
                        break
            if len(points) < 2:
                continue

            # Area path
            area = QPainterPath()
            line_path = QPainterPath()
            for idx, (gi, score) in enumerate(points):
                x, y = to_xy(gi, score)
                if idx == 0:
                    area.moveTo(x, y)
                    line_path.moveTo(x, y)
                else:
                    area.lineTo(x, y)
                    line_path.lineTo(x, y)

            last_x = to_xy(points[-1][0], points[-1][1])[0]
            first_x = to_xy(points[0][0], points[0][1])[0]
            area.lineTo(last_x, margin_t + plot_h)
            area.lineTo(first_x, margin_t + plot_h)
            area.closeSubpath()

            # Area gradient (30 % opacity)
            area_color = QColor(color)
            area_color.setAlpha(75)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(area_color)
            painter.drawPath(area)

            # Line
            painter.setPen(QPen(color, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(line_path)

        # Legend
        lx = margin_l + 4
        ly = margin_t + 2
        painter.setFont(QFont("Segoe UI", 7))
        for civ_name, civ_color in civ_info.items():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(civ_color))
            painter.drawEllipse(int(lx), int(ly), 6, 6)
            painter.setPen(QColor("#a9b1d6"))
            painter.drawText(int(lx + 10), int(ly), 80, 12, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, civ_name)
            lx += 90
            if lx > w - 60:
                lx = margin_l + 4
                ly += 14

        painter.end()


# ── 5. CivCard ────────────────────────────────────────────────────────

class CivCard(QFrame):
    """Rich info card for a single civilisation."""

    def __init__(self, data: dict):
        super().__init__()
        self.setObjectName("CivCard")
        self.setStyleSheet(
            "CivCard { background: #24283b; border: 1px solid #3b4261; border-radius: 6px; }"
        )

        self._color = data.get("color", "#7aa2f7")

        # Sparkline history storage
        self._pop_history = []
        self._tech_history = []
        self._mil_history = []

        self._build_ui()
        self.update_data(data)

    # ── helpers ──

    @staticmethod
    def _dim_color(hex_color, factor=0.6):
        c = QColor(hex_color)
        return QColor(int(c.red() * factor), int(c.green() * factor), int(c.blue() * factor))

    @staticmethod
    def _pill(text, bg="#2f3450", fg="#7aa2f7", size=9):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"background:{bg}; color:{fg}; border-radius:8px; padding:1px 6px; font-size:{size}px;"
        )
        lbl.setFixedHeight(16)
        return lbl

    @staticmethod
    def _fmt(v):
        if v is None:
            return "0"
        v = float(v)
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if v >= 1_000:
            return f"{v / 1_000:.1f}K"
        return f"{v:.0f}" if v == int(v) else f"{v:.1f}"

    # ── UI construction ──

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left colour accent bar (4 px)
        self._accent = QWidget()
        self._accent.setFixedWidth(4)
        self._accent.setStyleSheet(f"background:{self._color}; border-radius:2px;")
        main_layout.addWidget(self._accent)

        # Content area
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        # Row 0 – name + archetype + war badge + score
        row0 = QHBoxLayout()
        row0.setSpacing(6)
        self._lbl_name = QLabel()
        self._lbl_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        row0.addWidget(self._lbl_name)

        self._badge_archetype = QLabel()
        row0.addWidget(self._badge_archetype)

        row0.addStretch()

        self._badge_war = QLabel()
        row0.addWidget(self._badge_war)

        self._lbl_score = QLabel()
        self._lbl_score.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._lbl_score.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row0.addWidget(self._lbl_score)

        layout.addLayout(row0)

        # Row 1 – leader
        self._lbl_leader = QLabel()
        self._lbl_leader.setFont(QFont("Segoe UI", 10))
        self._lbl_leader.setStyleSheet("color:#bb9af7;")
        layout.addWidget(self._lbl_leader)

        # Row 2 – government + era
        row2 = QHBoxLayout()
        row2.setSpacing(6)
        self._badge_gov = QLabel()
        row2.addWidget(self._badge_gov)
        self._badge_era = QLabel()
        row2.addWidget(self._badge_era)
        self._badge_strategy = QLabel()
        row2.addWidget(self._badge_strategy)
        row2.addStretch()
        layout.addLayout(row2)

        # Row 3 – action
        self._lbl_action = QLabel()
        self._lbl_action.setFont(QFont("Segoe UI", 10, QFont.Style.StyleItalic))
        self._lbl_action.setStyleSheet("color:#565f89;")
        layout.addWidget(self._lbl_action)

        # Row 4-9 – stat bars
        self._stat_pop = StatBar("Pop", "#9ece6a")
        self._stat_tech = StatBar("Tech", "#7aa2f7")
        self._stat_mil = StatBar("Mil", "#f7768e")
        self._stat_treas = StatBar("Gold", "#e0af68")
        self._stat_culture = StatBar("Culture", "#bb9af7")
        self._stat_stability = StatBar("Stab", "#7dcfff")
        for sb in (self._stat_pop, self._stat_tech, self._stat_mil,
                    self._stat_treas, self._stat_culture, self._stat_stability):
            layout.addWidget(sb)

        # Row 10 – sparklines
        spark_row = QHBoxLayout()
        spark_row.setSpacing(4)
        self._spark_pop = SparklineChart("#9ece6a", "Pop")
        self._spark_tech = SparklineChart("#7aa2f7", "Tech")
        self._spark_mil = SparklineChart("#f7768e", "Mil")
        for sp in (self._spark_pop, self._spark_tech, self._spark_mil):
            spark_row.addWidget(sp)
        layout.addLayout(spark_row)

        # Row 11 – religion
        self._lbl_religion = QLabel()
        self._lbl_religion.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self._lbl_religion)

        # Row 12 – wonders
        self._lbl_wonders = QLabel()
        self._lbl_wonders.setFont(QFont("Segoe UI", 9))
        self._lbl_wonders.setStyleSheet("color:#e0af68;")
        self._lbl_wonders.setWordWrap(True)
        layout.addWidget(self._lbl_wonders)

        # Row 13 – diplomacy dots
        self._lbl_diplomacy = QLabel()
        self._lbl_diplomacy.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self._lbl_diplomacy)

        main_layout.addWidget(content)

    # ── update ──

    def update_data(self, d: dict):
        color = d.get("color", self._color)
        self._color = color
        self._accent.setStyleSheet(f"background:{color}; border-radius:2px;")

        # Header name
        self._lbl_name.setText(d.get("name", "?"))
        self._lbl_name.setStyleSheet(f"color:{color}; font-weight:bold; font-size:13px;")

        # Archetype pill
        arch = d.get("archetype_label") or d.get("archetype", "")
        if arch:
            self._badge_archetype.setText(arch)
            self._badge_archetype.setStyleSheet(
                "background:#2f3450; color:#7aa2f7; border-radius:8px; padding:1px 6px; font-size:9px;"
            )
            self._badge_archetype.show()
        else:
            self._badge_archetype.hide()

        # War / peace badge
        at_war = d.get("at_war_with")
        if at_war:
            self._badge_war.setText("\u2694 AT WAR")
            self._badge_war.setStyleSheet(
                "background:#4a1a1a; color:#f7768e; border-radius:8px; padding:1px 6px; font-size:9px; font-weight:bold;"
            )
            self._badge_war.show()
        else:
            self._badge_war.setText("\u2694 Peace")
            self._badge_war.setStyleSheet(
                "background:#1a2a1a; color:#9ece6a; border-radius:8px; padding:1px 6px; font-size:9px;"
            )
            self._badge_war.show()

        # Leader
        leader = d.get("leader_name") or d.get("leader_short_name") or ""
        if leader:
            self._lbl_leader.setText(leader)
            self._lbl_leader.show()
        else:
            self._lbl_leader.hide()

        # Government pill
        gov = d.get("government_label") or d.get("government", "")
        if gov:
            self._badge_gov.setText(gov)
            self._badge_gov.setStyleSheet(
                "background:#1a2a3a; color:#7dcfff; border-radius:8px; padding:1px 6px; font-size:9px;"
            )
            self._badge_gov.show()
        else:
            self._badge_gov.hide()

        # Era pill
        era = d.get("era_name", "")
        if era:
            self._badge_era.setText(era)
            self._badge_era.setStyleSheet(
                "background:#2a2a1a; color:#e0af68; border-radius:8px; padding:1px 6px; font-size:9px;"
            )
            self._badge_era.show()
        else:
            self._badge_era.hide()

        # Strategic state badge
        state_colors = {
            "EXPANSION": "#7aa2f7",
            "CONSOLIDATION": "#565f89",
            "CRISIS": "#f7768e",
            "TOTAL_WAR": "#ff0000",
            "GOLDEN_AGE": "#e0af68",
            "RECOVERY": "#ff9e64",
            "SIEGE": "#db4b4b",
        }
        state = d.get("strategic_state", "")
        if state:
            sc = state_colors.get(state, "#565f89")
            self._badge_strategy.setText(state.replace("_", " ").title())
            self._badge_strategy.setStyleSheet(
                f"background:{sc}22; color:{sc}; border:1px solid {sc}66; border-radius:8px; padding:1px 6px; font-size:9px;"
            )
            self._badge_strategy.show()
        else:
            self._badge_strategy.hide()

        # Action line
        action = d.get("plan_name") or d.get("last_action", "")
        if action:
            self._lbl_action.setText(f"Action: {action}")
            self._lbl_action.show()
        else:
            self._lbl_action.hide()

        # Stat bars
        self._stat_pop.set_value(d.get("population", 0), 100000, self._fmt(d.get("population", 0)))
        self._stat_tech.set_value(d.get("technology", 0), 50, f"{d.get('technology', 0):.1f}")
        self._stat_mil.set_value(d.get("military", 0), 5000, self._fmt(d.get("military", 0)))
        self._stat_treas.set_value(d.get("treasury", 0), 10000, self._fmt(d.get("treasury", 0)))
        self._stat_culture.set_value(d.get("culture", 0), 2000, self._fmt(d.get("culture", 0)))
        self._stat_stability.set_value(d.get("stability", 0), 100, f"{d.get('stability', 0):.1f}")

        # Sparklines
        self._spark_pop.add_point(d.get("population", 0))
        self._spark_tech.add_point(d.get("technology", 0))
        self._spark_mil.add_point(d.get("military", 0))

        # Religion
        rel = d.get("religion", "")
        if rel:
            self._lbl_religion.setText(f'<span style="color:#e0af68;">\u25C6</span> {rel}')
            self._lbl_religion.show()
        else:
            self._lbl_religion.hide()

        # Wonders
        wonders = d.get("wonders", [])
        if wonders:
            if isinstance(wonders, list):
                txt = ", ".join(str(w) for w in wonders)
            else:
                txt = str(wonders)
            self._lbl_wonders.setText(f"\u2726 {txt}")
            self._lbl_wonders.show()
        else:
            self._lbl_wonders.hide()

        # Diplomacy
        dip_parts = []
        allies = d.get("alliances", [])
        if allies:
            dip_parts.append(f'<span style="color:#9ece6a;">\u25CF Allies: {", ".join(allies)}</span>')
        trade = d.get("trade_partners", [])
        if trade:
            dip_parts.append(f'<span style="color:#7dcfff;">\u25CF Trade: {", ".join(trade)}</span>')
        war = d.get("at_war_with", [])
        if war:
            dip_parts.append(f'<span style="color:#f7768e;">\u25CF War: {", ".join(war)}</span>')
        if dip_parts:
            self._lbl_diplomacy.setText(" &nbsp;|&nbsp; ".join(dip_parts))
            self._lbl_diplomacy.show()
        else:
            self._lbl_diplomacy.hide()

        # Score
        score = d.get("score", 0)
        self._lbl_score.setText(self._fmt(score))
        self._lbl_score.setStyleSheet(f"color:{color}; font-size:16px; font-weight:bold;")

        self.update()


# ── 6. MinimapWidget ──────────────────────────────────────────────────

class MinimapWidget(QWidget):
    """Enhanced minimap with click-to-navigate and viewport indicator."""

    navigated = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 150)
        self._terrain_map = None
        self._owner_map = None
        self._civ_colors = {}
        self._explored = None
        self._viewport_rect = None

    def set_viewport_rect(self, rect):
        self._viewport_rect = rect
        self.update()

    def update_data(self, terrain_map, owner_map, civ_colors, explored):
        self._terrain_map = terrain_map
        self._owner_map = owner_map
        self._civ_colors = civ_colors or {}
        self._explored = explored
        self.update()

    def mousePressEvent(self, event):
        if self._terrain_map is None:
            return
        tm = self._terrain_map
        rows, cols = len(tm), len(tm[0]) if tm else 0
        if rows == 0 or cols == 0:
            return
        mx, my = event.position().x(), event.position().y()
        border = 2
        cw = (self.width() - 2 * border) / cols
        ch = (self.height() - 2 * border) / rows
        cx = int((mx - border) / cw)
        cy = int((my - border) / ch)
        cx = max(0, min(cx, cols - 1))
        cy = max(0, min(cy, rows - 1))
        self.navigated.emit(cx, cy)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor("#1a1b26"))

        border = 2
        if self._terrain_map and len(self._terrain_map) > 0:
            rows = len(self._terrain_map)
            cols = len(self._terrain_map[0])
            cw = (w - 2 * border) / cols
            ch = (h - 2 * border) / rows

            for r in range(rows):
                for c in range(cols):
                    # Check explored
                    if self._explored is not None:
                        try:
                            if not self._explored[r][c]:
                                painter.fillRect(QRectF(border + c * cw, border + r * ch, cw + 0.5, ch + 0.5), QColor("#16161e"))
                                continue
                        except (IndexError, TypeError):
                            pass

                    terrain = self._terrain_map[r][c] if c < len(self._terrain_map[r]) else 0
                    base_color = QColor(TERRAIN_COLORS.get(terrain, "#1a1b26"))

                    # Owner tint
                    if self._owner_map and r < len(self._owner_map) and c < len(self._owner_map[r]):
                        owner = self._owner_map[r][c]
                        if owner is not None and owner != -1 and owner in self._civ_colors:
                            civ_c = QColor(self._civ_colors[owner])
                            base_color = QColor(
                                (base_color.red() + civ_c.red()) // 2,
                                (base_color.green() + civ_c.green()) // 2,
                                (base_color.blue() + civ_c.blue()) // 2,
                            )

                    painter.fillRect(
                        QRectF(border + c * cw, border + r * ch, cw + 0.5, ch + 0.5),
                        base_color,
                    )

            # Viewport rectangle
            if self._viewport_rect is not None:
                vr = self._viewport_rect
                rx = border + vr.x() * cw
                ry = border + vr.y() * ch
                rw = vr.width() * cw
                rh = vr.height() * ch
                painter.setPen(QPen(QColor("#ffffff"), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(QRectF(rx, ry, rw, rh))

        # Border
        painter.setPen(QPen(QColor("#3b4261"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, w - 1, h - 1)
        painter.end()


# ── 7. LeaderboardWidget ──────────────────────────────────────────────

class LeaderboardWidget(QTextEdit):
    """Enhanced leaderboard with styled per-row cards."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            "QTextEdit { background-color: #1a1b26; border: 1px solid #3b4261; "
            "border-radius: 4px; color: #a9b1d6; }"
        )

    def update_rankings(self, civs_data):
        sorted_civs = sorted(civs_data, key=lambda c: c.get("score", 0), reverse=True)
        medal_colors = ["#e0af68", "#a9b1d6", "#ff9e64"]
        lines = []
        for i, civ in enumerate(sorted_civs):
            name = civ.get("name", "?")
            score = civ.get("score", 0)
            color = civ.get("color", "#7aa2f7")
            pop = civ.get("population", 0)
            if i < 3:
                medal = f'<span style="color:{medal_colors[i]}; font-size:14px;">\u25C6</span>'
            else:
                medal = f'<span style="color:#565f89; font-size:12px;">  {i + 1}.</span>'
            bar_pct = min(100, (score / max(1, sorted_civs[0].get("score", 1))) * 100)
            bar_html = (
                f'<div style="background:#24283b; border-left:3px solid {color}; '
                f'border-radius:4px; padding:3px 6px; margin:2px 0;">'
                f'{medal} <b style="color:{color};">{name}</b> '
                f'<span style="color:#565f89;">pop {CivCard._fmt(pop)}</span> '
                f'<span style="float:right; color:#c0caf5; font-weight:bold;">{CivCard._fmt(score)}</span>'
                f'<div style="background:#1a1b26; height:3px; border-radius:1px; margin-top:2px;">'
                f'<div style="background:{color}; width:{bar_pct:.1f}%; height:3px; border-radius:1px;"></div>'
                f'</div></div>'
            )
            lines.append(bar_html)
        self.setHtml("<br>".join(lines))


# ── 8. DiplomacyMatrix ────────────────────────────────────────────────

class DiplomacyMatrix(QWidget):
    """Diplomacy relationship matrix with Tokyo Night colours."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._civs_data = []
        self._rel_map = {}

    def update_data(self, civs_data):
        self._civs_data = civs_data
        # Build relationship map: (civ_a, civ_b) -> relation string
        self._rel_map.clear()
        for c in civs_data:
            name = c.get("name", "")
            allies = c.get("alliances", []) or []
            trade = c.get("trade_partners", []) or []
            war = c.get("at_war_with", []) or []
            for a in allies:
                key = tuple(sorted([name, a]))
                if key not in self._rel_map or self._rel_map[key] != "War":
                    self._rel_map[key] = "Allied"
            for t in trade:
                key = tuple(sorted([name, t]))
                if key not in self._rel_map:
                    self._rel_map[key] = "Trade"
            for w in war:
                key = tuple(sorted([name, w]))
                self._rel_map[key] = "War"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        n = len(self._civs_data)
        if n == 0:
            painter.end()
            return

        cell = min(28, (w - 50) // n, (h - 20) // n)
        header = cell + 4
        ox = header
        oy = header

        # Column headers
        painter.setFont(QFont("Segoe UI", 7))
        for i, c in enumerate(self._civs_data):
            x = ox + i * cell + cell // 2
            painter.setPen(QColor(c.get("color", "#c0caf5")))
            painter.save()
            painter.translate(x, 4)
            painter.rotate(45)
            short = c.get("name", "?")[:6]
            painter.drawText(0, 0, short)
            painter.restore()

        # Row headers
        for j, c in enumerate(self._civs_data):
            y = oy + j * cell + cell // 2 + 3
            painter.setPen(QColor(c.get("color", "#c0caf5")))
            painter.drawText(0, int(y), ox - 4, cell, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, c.get("name", "?")[:8])

        # Cells
        rel_colors = {
            "War": QColor("#f7768e"),
            "Allied": QColor("#9ece6a"),
            "Trade": QColor("#7dcfff"),
            "Neutral": QColor("#24283b"),
        }
        for i, ci in enumerate(self._civs_data):
            for j, cj in enumerate(self._civs_data):
                if i == j:
                    col = QColor("#3b4261")
                else:
                    key = tuple(sorted([ci.get("name", ""), cj.get("name", "")]))
                    rel = self._rel_map.get(key, "Neutral")
                    col = rel_colors.get(rel, QColor("#24283b"))
                x = ox + i * cell
                y = oy + j * cell
                painter.fillRect(x, y, cell - 1, cell - 1, col)
                painter.setPen(QPen(QColor("#3b4261"), 1))
                painter.drawRect(x, y, cell - 1, cell - 1)

        painter.end()


# ── 9. NotificationOverlay ────────────────────────────────────────────

class NotificationOverlay(QWidget):
    """Semi-transparent overlay for in-game notifications."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._notifications = deque(maxlen=10)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(200)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.hide()

    def add_notification(self, title, message):
        self._notifications.append({"title": title, "message": message, "alpha": 255})
        self.show()
        self.raise_()
        self.update()

    def _tick(self):
        dirty = False
        new_q = deque(maxlen=10)
        for n in self._notifications:
            n["alpha"] -= 3
            if n["alpha"] > 0:
                new_q.append(n)
            dirty = True
        self._notifications = new_q
        if not self._notifications:
            self.hide()
        if dirty:
            self.update()

    def paintEvent(self, event):
        if not self._notifications:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = 10
        for n in self._notifications:
            alpha = max(0, min(255, n["alpha"]))
            painter.setOpacity(alpha / 255.0)
            text = f"{n['title']}: {n['message']}"
            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(text) + 40
            th = 32
            rect = QRectF(self.width() - tw - 10, y, tw, th)

            # Background gradient
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0, QColor("#2f3450"))
            grad.setColorAt(1, QColor("#24283b"))
            painter.setPen(QPen(QColor("#7aa2f7"), 1))
            painter.setBrush(grad)
            painter.drawRoundedRect(rect, 6, 6)

            # Title + message
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.setPen(QColor("#7aa2f7"))
            painter.drawText(rect.adjusted(8, 2, -8, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, n["title"])
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#a9b1d6"))
            painter.drawText(rect.adjusted(8, 16, -8, -2), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, n["message"])

            y += th + 4
        painter.end()


# ── 10. EventFeed ─────────────────────────────────────────────────────

class EventFeed(QTextEdit):
    """Color-coded scrolling event feed."""

    _COLOR_MAP = {
        "expand": "#9ece6a",
        "attack": "#f7768e",
        "war": "#ff0000",
        "alliance": "#7dcfff",
        "research": "#7aa2f7",
        "wonder": "#e0af68",
        "culture": "#bb9af7",
        "rebel": "#ff9e64",
        "government": "#565f89",
        "leader": "#c0caf5",
        "diplomacy": "#7dcfff",
        "trade": "#9ece6a",
    }
    _ICON_MAP = {
        "expand": "+",
        "attack": "!",
        "war": "!!",
        "alliance": "~",
        "research": "?",
        "wonder": "*",
        "culture": "@",
        "rebel": "#",
        "government": "=",
        "leader": ">",
        "diplomacy": "~",
        "trade": "$",
    }
    _MAX_ENTRIES = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            "QTextEdit { background-color: transparent; border: none; color: #a9b1d6; }"
        )
        self._entry_count = 0

    def add_event(self, event_type: str, text: str, year: int):
        color = self._COLOR_MAP.get(event_type, "#a9b1d6")
        icon = self._ICON_MAP.get(event_type, "-")
        html = (
            f'<span style="color:{color};">[{icon}] '
            f'<b>Year {year}</b> {text}</span>'
        )
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.insertHtml(html + "<br>")
        self._entry_count += 1
        if self._entry_count > self._MAX_ENTRIES:
            cursor2 = self.textCursor()
            cursor2.movePosition(QTextCursor.MoveOperation.End)
            cursor2.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
            cursor2.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)
            cursor2.removeSelectedText()
            self._entry_count -= 1
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_events(self):
        self.clear()
        self._entry_count = 0


# ── 11. GenerationReportPanel ─────────────────────────────────────────

class GenerationReportPanel(QTextEdit):
    """Panel for generation-by-generation AI reports."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            "QTextEdit { background-color: #1a1b26; border: 1px solid #3b4261; "
            "border-radius: 4px; color: #a9b1d6; }"
        )
        self._plain_texts = []

    def add_report(self, html_report, plain_text_report):
        self._plain_texts.append(plain_text_report)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.insertHtml(html_report + "<hr>")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def get_all_plain_text(self):
        return "\n\n---\n\n".join(self._plain_texts)

    def clear_reports(self):
        self.clear()
        self._plain_texts.clear()
# ════════════════════════════════════════════════════════════
# FILE: new_map_view.py  –  Enhanced MapView replacement
# ════════════════════════════════════════════════════════════
"""
Stunning map view with per-tile terrain noise, mountain elevation highlights,
forest canopy texture, subtle territory tinting (30 % civ blend), animated
war-border pulsing, star-shaped capital markers, and enhanced resource /
trade-route rendering.

This module is concatenated after config.py imports, so TERRAIN_COLORS,
TILE_SIZE, SEASON_COLORS, and RESOURCE_TYPES are already in scope.
"""

import math
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QToolTip
from PySide6.QtCore import Qt, QTimer, Signal, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QGraphicsRectItem, QGraphicsLineItem,
    QGraphicsEllipseItem, QGraphicsPathItem,
    QGraphicsPolygonItem, QPolygonF,
    QPainterPath, QCursor,
)


# ════════════════════════════════════════════════════════════
# Helpers (standalone so they work when concatenated)
# ════════════════════════════════════════════════════════════

def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def _qcolor(r, g, b, a=255):
    return QColor(_clamp(r), _clamp(g), _clamp(b), a)


# ════════════════════════════════════════════════════════════
# EnhancedMapView
# ════════════════════════════════════════════════════════════

class EnhancedMapView(QGraphicsView):
    """High-fidelity, animated map view with terrain noise and war pulsing."""

    tile_hovered = Signal(int, int)
    tile_clicked = Signal(int, int)
    zoom_changed = Signal(int)
    viewport_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Scene ─────────────────────────────────────────
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor(26, 27, 38)))

        # ── Overlay toggles ───────────────────────────────
        self.show_fog = True
        self.show_resources = False
        self.show_borders = True
        self.show_trade_routes = True
        self.show_events = True

        # ── Performance caches ────────────────────────────
        self._tile_colors: dict[tuple, QColor] = {}
        self._noised_colors: dict[tuple, QColor] = {}
        self._season_rect: QGraphicsRectItem | None = None
        self._map_W = 0
        self._map_H = 0
        self._no_pen = QPen(Qt.NoPen)
        self._fog_color = QColor(15, 15, 25)

        # ── Tile items (graphics-scene items per tile) ────
        self._tiles: dict[tuple, QGraphicsRectItem] = {}

        # ── Dynamic items (rebuilt on each update / anim) ─
        self._dynamic_items: list = []

        # ── Last-update cache (for refresh_overlays) ──────
        self._last_update_args: dict | None = None

        # ── Pre-computed per-tile noise (0.0 – 1.0) ──────
        self._tile_noise: dict[tuple, float] = {}

        # ── Animation state ───────────────────────────────
        self._water_phase = 0.0
        self._war_pulse = 0.0
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(100)
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start()

        # ── Zoom ──────────────────────────────────────────
        self._zoom = 1.0

    # ────────────────────────────────────────────────────
    # Deterministic tile hash for colour variation
    # ────────────────────────────────────────────────────

    def _tile_hash(self, x: int, y: int) -> float:
        """Deterministic hash for per-tile colour variation. Returns 0.0–1.0."""
        n = x * 374761393 + y * 668265263 + 12345
        n = (n ^ (n >> 13)) * 1274126177
        n = n ^ (n >> 16)
        return (n & 0x7FFFFFFF) / 0x7FFFFFFF

    # ────────────────────────────────────────────────────
    # Noise-varied terrain colour (cached)
    # ────────────────────────────────────────────────────

    def _get_noised_color(self, x: int, y: int, base: QColor) -> QColor:
        """Return *base* with ±8 RGB jitter based on deterministic hash."""
        key = (x, y)
        if key in self._noised_colors:
            return self._noised_colors[key]

        if key not in self._tile_noise:
            self._tile_noise[key] = self._tile_hash(x, y)

        noise = self._tile_noise[key]
        # Convert 0-1 noise to ±8 range
        variation = (noise - 0.5) * 16  # -8 to +8
        r = _clamp(base.red() + variation)
        g = _clamp(base.green() + variation * 0.9)
        b = _clamp(base.blue() + variation * 0.8)
        c = _qcolor(r, g, b)
        self._noised_colors[key] = c
        return c

    def _clear_noise_cache(self):
        self._noised_colors.clear()
        self._tile_noise.clear()

    # ────────────────────────────────────────────────────
    # Star shape helper
    # ────────────────────────────────────────────────────

    def _draw_star(self, painter: QPainter, cx: float, cy: float,
                   r: float, color: QColor):
        """Draw a filled 5-pointed star."""
        path = QPainterPath()
        for i in range(5):
            angle = math.radians(-90 + i * 72)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
            angle2 = math.radians(-90 + i * 72 + 36)
            x2 = cx + r * 0.4 * math.cos(angle2)
            y2 = cy + r * 0.4 * math.sin(angle2)
            path.lineTo(x2, y2)
        path.closeSubpath()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPath(path)

    # ────────────────────────────────────────────────────
    # Mountain elevation highlight
    # ────────────────────────────────────────────────────

    def _draw_mountain_highlight(self, painter: QPainter, px: int, py: int,
                                  ts: int, r: int, g: int, b: int):
        """1-pixel lighter line on top and left edges for elevation effect."""
        highlight = _qcolor(
            min(255, r + 55), min(255, g + 55), min(255, b + 55), 180
        )
        painter.setPen(QPen(highlight, 1))
        painter.drawLine(px, py, px + ts - 1, py)          # top edge
        painter.drawLine(px, py, px, py + ts - 1)          # left edge

        # Subtle dark bottom-right
        shadow = _qcolor(max(0, r - 35), max(0, g - 35), max(0, b - 35), 140)
        painter.setPen(QPen(shadow, 1))
        painter.drawLine(px + ts - 1, py + 1, px + ts - 1, py + ts - 1)  # right
        painter.drawLine(px + 1, py + ts - 1, px + ts - 1, py + ts - 1)  # bottom

    # ────────────────────────────────────────────────────
    # Forest canopy texture
    # ────────────────────────────────────────────────────

    def _draw_forest_dots(self, painter: QPainter, px: int, py: int,
                           ts: int, r: int, g: int, b: int):
        """Tiny darker dots to simulate canopy texture."""
        painter.setPen(Qt.NoPen)
        dot_color = _qcolor(max(0, r - 20), max(0, g - 15), max(0, b - 10), 140)
        painter.setBrush(QBrush(dot_color))
        # Deterministic dot positions based on tile coordinate
        seed = px * 31 + py * 17
        for i in range(3):
            dx = ((seed + i * 37) % max(1, ts - 2)) + 1
            dy = ((seed + i * 53) % max(1, ts - 2)) + 1
            painter.drawEllipse(px + dx, py + dy, 2, 2)

    # ────────────────────────────────────────────────────
    # Visible scene rect (for minimap viewport)
    # ────────────────────────────────────────────────────

    def visible_scene_rect(self) -> QRectF:
        """Return the currently visible scene rectangle."""
        return self.mapToScene(self.viewport().rect()).boundingRect()

    # ────────────────────────────────────────────────────
    # Zoom
    # ────────────────────────────────────────────────────

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self._zoom *= factor
        self._zoom = max(0.2, min(8.0, self._zoom))
        self.scale(factor, factor)
        self.zoom_changed.emit(int(self._zoom * 100))
        self.viewport_changed.emit(self.visible_scene_rect())

    def reset_view(self):
        """Reset zoom and center on the map."""
        self.resetTransform()
        self._zoom = 1.0
        self.zoom_changed.emit(100)
        self.viewport_changed.emit(self.visible_scene_rect())
        if self._map_W and self._map_H:
            self.centerOn(
                self._map_W * TILE_SIZE / 2,
                self._map_H * TILE_SIZE / 2,
            )

    # ────────────────────────────────────────────────────
    # Mouse interaction
    # ────────────────────────────────────────────────────

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.position().toPoint())
        tx = int(scene_pos.x()) // TILE_SIZE
        ty = int(scene_pos.y()) // TILE_SIZE
        self.tile_hovered.emit(tx, ty)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            tx = int(scene_pos.x()) // TILE_SIZE
            ty = int(scene_pos.y()) // TILE_SIZE
            self.tile_clicked.emit(tx, ty)
        super().mousePressEvent(event)

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.viewport_changed.emit(self.visible_scene_rect())

    # ────────────────────────────────────────────────────
    # Clear map
    # ────────────────────────────────────────────────────

    def clear_map(self):
        """Remove all scene items and reset caches."""
        self._scene.clear()
        self._tiles.clear()
        self._dynamic_items.clear()
        self._tile_colors.clear()
        self._noised_colors.clear()
        self._tile_noise.clear()
        self._season_rect = None
        self._last_update_args = None
        self._map_W = 0
        self._map_H = 0

    # ────────────────────────────────────────────────────
    # Animation tick
    # ────────────────────────────────────────────────────

    def _animate(self):
        """Called every 100 ms by _anim_timer. Only animates war borders."""
        self._water_phase += 0.1
        self._war_pulse += 0.15

        # Only re-render dynamic items if we have data and there might be wars
        if self._last_update_args is None:
            return

        # Check if any active events involve wars
        active_events = self._last_update_args.get('active_events', [])
        has_war = any(
            getattr(ev, 'event_type', '') in ('war', 'attack', 'siege')
            or 'war' in str(getattr(ev, 'description', '')).lower()
            for ev in active_events
        )
        if not has_war:
            return

        # Efficient: only rebuild border items with updated pulse
        self._rebuild_borders_only()

    # ────────────────────────────────────────────────────
    # Rebuild only border dynamic items (animation)
    # ────────────────────────────────────────────────────

    def _rebuild_borders_only(self):
        """Remove old border items, re-add with current _war_pulse alpha."""
        args = self._last_update_args
        if not args:
            return

        owner_map = args['owner_map']
        civ_colors = args['civ_colors']
        active_events = args['active_events']
        ts = TILE_SIZE

        # Collect names of civs involved in war-like events
        war_civs: set[str] = set()
        for ev in active_events:
            etype = getattr(ev, 'event_type', '')
            desc = str(getattr(ev, 'description', '')).lower()
            if etype in ('war', 'attack', 'siege') or 'war' in desc:
                src = getattr(ev, 'civ_name', '') or getattr(ev, 'source_civ', '')
                tgt = getattr(ev, 'target_civ', '')
                if src:
                    war_civs.add(src)
                if tgt:
                    war_civs.add(tgt)

        # Remove old border items (tagged with userData)
        to_remove = [it for it in self._dynamic_items
                     if it.data(0) == 'border']
        for it in to_remove:
            self._scene.removeItem(it)
            self._dynamic_items.remove(it)

        # Build set of war pairs (frozenset of two civ names)
        war_pairs: set[frozenset] = set()
        if war_civs:
            # All pairs among war civs are considered at war
            war_list = sorted(war_civs)
            for i in range(len(war_list)):
                for j in range(i + 1, len(war_list)):
                    war_pairs.add(frozenset((war_list[i], war_list[j])))

        # Re-draw borders
        self._draw_borders(owner_map, civ_colors, war_pairs, ts)

    # ────────────────────────────────────────────────────
    # Refresh overlays (re-draw dynamic items from cached args)
    # ────────────────────────────────────────────────────

    def refresh_overlays(self):
        """Rebuild all dynamic overlays from last update_map args."""
        if self._last_update_args is None:
            return
        self.update_map(**self._last_update_args)

    # ────────────────────────────────────────────────────
    # Main update_map
    # ────────────────────────────────────────────────────

    def update_map(self, terrain_map, owner_map, civ_colors, explored,
                   path_data=None, capitals=None, trade_routes=None,
                   active_events=None, resource_map=None, season=0):
        """
        Full map update.  Creates tiles on first call, then incrementally
        updates colours and rebuilds dynamic overlays.

        Parameters
        ----------
        terrain_map  : dict[(x,y)] -> int (Terrain enum value)
        owner_map    : dict[(x,y)] -> str (civ name or None)
        civ_colors   : dict[str]   -> str (civ_name -> hex color)
        explored     : set[(x,y)]  tiles the player has revealed
        path_data    : list[(x,y)] | None  – highlighted path
        capitals     : dict[str] -> (x,y) | None  – capital positions
        trade_routes : list[dict] | None  – trade route segment dicts
        active_events: list | None  – current event objects
        resource_map : dict[(x,y)] -> str | None  – resource type names
        season       : int  – 0-3 season index
        """
        ts = TILE_SIZE

        # Deduce map dimensions
        if terrain_map:
            all_x = set(k[0] for k in terrain_map)
            all_y = set(k[1] for k in terrain_map)
            W = max(all_x) + 1 if all_x else 0
            H = max(all_y) + 1 if all_y else 0
        else:
            W, H = 0, 0

        # Dimension change → full rebuild
        if W != self._map_W or H != self._map_H:
            self.clear_map()
            self._map_W = W
            self._map_H = H
            self._scene.setSceneRect(0, 0, W * ts, H * ts)

        # Defaults
        path_data = path_data or []
        capitals = capitals or {}
        trade_routes = trade_routes or []
        active_events = active_events or []
        resource_map = resource_map or {}

        # ── 1. Create / update base tile rects ──────────
        need_create = len(self._tiles) == 0
        for y in range(H):
            for x in range(W):
                tid = terrain_map.get((x, y), 0)
                base_color = TERRAIN_COLORS.get(tid, QColor(128, 128, 128))
                noised = self._get_noised_color(x, y, base_color)
                key = (x, y)
                is_explored = key in explored if explored else True

                if not is_explored and self.show_fog:
                    display_color = self._fog_color
                elif owner_map and key in owner_map:
                    owner_name = owner_map[key]
                    civ_hex = civ_colors.get(owner_name, '#888888')
                    civ_color = QColor(civ_hex)
                    # 30% civ, 70% terrain blend
                    display_color = _qcolor(
                        int(noised.red() * 0.7 + civ_color.red() * 0.3),
                        int(noised.green() * 0.7 + civ_color.green() * 0.3),
                        int(noised.blue() * 0.7 + civ_color.blue() * 0.3),
                    )
                else:
                    display_color = noised

                # Season tint (skip ocean/coast)
                if 0 <= season < len(SEASON_COLORS) and tid not in (0, 8):
                    sc = SEASON_COLORS[season]
                    # Blend season colour at 15% over the display colour
                    display_color = _qcolor(
                        int(display_color.red() * 0.85 + sc.red() * 0.15),
                        int(display_color.green() * 0.85 + sc.green() * 0.15),
                        int(display_color.blue() * 0.85 + sc.blue() * 0.15),
                    )

                if need_create:
                    item = self._scene.addRect(
                        x * ts, y * ts, ts, ts,
                        self._no_pen, QBrush(display_color)
                    )
                    item.setZValue(1)
                    self._tiles[key] = item

                    # Mountain elevation highlight
                    if tid == 3:  # MOUNTAIN
                        self._add_mountain_scene_items(x, y, ts,
                                                       display_color)
                    # Forest canopy dots
                    if tid in (2, 5):  # FOREST, JUNGLE
                        self._add_forest_scene_items(x, y, ts,
                                                      display_color)
                else:
                    # Dirty check – only update brush if colour changed
                    old = self._tile_colors.get(key)
                    if old != display_color:
                        self._tiles[key].setBrush(QBrush(display_color))

                self._tile_colors[key] = display_color

        # ── 2. Season overlay rect ─────────────────────
        if self._season_rect is None and 0 <= season < len(SEASON_COLORS):
            sc = SEASON_COLORS[season]
            item = self._scene.addRect(
                0, 0, W * ts, H * ts,
                self._no_pen, QBrush(sc)
            )
            item.setZValue(0)
            self._season_rect = item
        elif self._season_rect is not None and 0 <= season < len(SEASON_COLORS):
            sc = SEASON_COLORS[season]
            self._season_rect.setBrush(QBrush(sc))

        # ── 3. Clear dynamic items ─────────────────────
        for item in self._dynamic_items:
            self._scene.removeItem(item)
        self._dynamic_items.clear()

        # ── 4. Borders ─────────────────────────────────
        # Determine war pairs from active_events
        war_civs: set[str] = set()
        for ev in active_events:
            etype = getattr(ev, 'event_type', '')
            desc = str(getattr(ev, 'description', '')).lower()
            if etype in ('war', 'attack', 'siege') or 'war' in desc:
                src = getattr(ev, 'civ_name', '') or getattr(ev, 'source_civ', '')
                tgt = getattr(ev, 'target_civ', '')
                if src:
                    war_civs.add(src)
                if tgt:
                    war_civs.add(tgt)
        war_pairs: set[frozenset] = set()
        if war_civs:
            wl = sorted(war_civs)
            for i in range(len(wl)):
                for j in range(i + 1, len(wl)):
                    war_pairs.add(frozenset((wl[i], wl[j])))

        if self.show_borders:
            self._draw_borders(owner_map, civ_colors, war_pairs, ts)

        # ── 5. Resource markers ────────────────────────
        if self.show_resources and resource_map:
            self._draw_resources(resource_map, ts)

        # ── 6. Event overlays ──────────────────────────
        if self.show_events and active_events:
            self._draw_events(active_events, ts)

        # ── 7. Trade routes ────────────────────────────
        if self.show_trade_routes and trade_routes:
            self._draw_trade_routes(trade_routes, ts)

        # ── 8. Path highlight ──────────────────────────
        if path_data:
            self._draw_path(path_data, ts)

        # ── 9. Capital markers ─────────────────────────
        if capitals:
            self._draw_capitals(capitals, civ_colors, ts)

        # ── Cache args for refresh_overlays / animation ─
        self._last_update_args = {
            'terrain_map': terrain_map,
            'owner_map': owner_map,
            'civ_colors': civ_colors,
            'explored': explored,
            'path_data': path_data,
            'capitals': capitals,
            'trade_routes': trade_routes,
            'active_events': active_events,
            'resource_map': resource_map,
            'season': season,
        }

    # ────────────────────────────────────────────────────
    # Mountain scene items (called once per tile at creation)
    # ────────────────────────────────────────────────────

    def _add_mountain_scene_items(self, x, y, ts, base_color):
        """Add top-left highlight and bottom-right shadow lines."""
        px, py = x * ts, y * ts
        r, g, b = base_color.red(), base_color.green(), base_color.blue()

        # Top edge highlight
        highlight_color = _qcolor(
            min(255, r + 55), min(255, g + 55), min(255, b + 55), 180
        )
        pen = QPen(highlight_color, 1)
        line_top = self._scene.addLine(px, py, px + ts - 1, py, pen)
        line_top.setZValue(2)
        self._tiles[(x, y, 'mt')] = line_top  # store for cleanup

        line_left = self._scene.addLine(px, py, px, py + ts - 1, pen)
        line_left.setZValue(2)
        self._tiles[(x, y, 'ml')] = line_left

        # Bottom-right shadow
        shadow_color = _qcolor(
            max(0, r - 35), max(0, g - 35), max(0, b - 35), 140
        )
        pen2 = QPen(shadow_color, 1)
        line_right = self._scene.addLine(
            px + ts - 1, py + 1, px + ts - 1, py + ts - 1, pen2
        )
        line_right.setZValue(2)
        self._tiles[(x, y, 'mr')] = line_right

        line_bot = self._scene.addLine(
            px + 1, py + ts - 1, px + ts - 1, py + ts - 1, pen2
        )
        line_bot.setZValue(2)
        self._tiles[(x, y, 'mb')] = line_bot

    # ────────────────────────────────────────────────────
    # Forest scene items (called once per tile at creation)
    # ────────────────────────────────────────────────────

    def _add_forest_scene_items(self, x, y, ts, base_color):
        """Add tiny darker dots to simulate canopy texture."""
        px, py = x * ts, y * ts
        r, g, b = base_color.red(), base_color.green(), base_color.blue()
        dot_color = _qcolor(
            max(0, r - 20), max(0, g - 15), max(0, b - 10), 140
        )
        seed = x * 31 + y * 17
        for i in range(3):
            dx = ((seed + i * 37) % max(1, ts - 2)) + 1
            dy = ((seed + i * 53) % max(1, ts - 2)) + 1
            dot = self._scene.addEllipse(
                px + dx, py + dy, 2, 2,
                self._no_pen, QBrush(dot_color)
            )
            dot.setZValue(2)
            self._tiles[(x, y, f'fd{i}')] = dot

    # ────────────────────────────────────────────────────
    # Border drawing
    # ────────────────────────────────────────────────────

    def _draw_borders(self, owner_map, civ_colors, war_pairs, ts):
        """Draw border lines between different owners."""
        W, H = self._map_W, self._map_H

        # Gather border segments: (x1,y1,x2,y2, owner1, owner2)
        drawn = set()
        for y in range(H):
            for x in range(W):
                owner1 = owner_map.get((x, y))
                if not owner1:
                    continue

                # Check right neighbor
                rx, ry = x + 1, y
                if rx < W:
                    owner2 = owner_map.get((rx, ry))
                    if owner2 and owner2 != owner1:
                        seg = ((x, y), (rx, ry))
                        if seg not in drawn:
                            drawn.add(seg)
                            self._add_border_segment(
                                (x + 1) * ts, y * ts,
                                (x + 1) * ts, (y + 1) * ts,
                                owner1, owner2, civ_colors, war_pairs, ts
                            )

                # Check bottom neighbor
                bx, by = x, y + 1
                if by < H:
                    owner2 = owner_map.get((bx, by))
                    if owner2 and owner2 != owner1:
                        seg = ((x, y), (bx, by))
                        if seg not in drawn:
                            drawn.add(seg)
                            self._add_border_segment(
                                x * ts, (y + 1) * ts,
                                (x + 1) * ts, (y + 1) * ts,
                                owner1, owner2, civ_colors, war_pairs, ts
                            )

    def _add_border_segment(self, x1, y1, x2, y2,
                             owner1, owner2, civ_colors, war_pairs, ts):
        """Add a single border line item to the scene."""
        pair = frozenset((owner1, owner2))

        if pair in war_pairs:
            # Pulsing red border
            alpha = int(100 + 155 * (0.5 + 0.5 * math.sin(self._war_pulse)))
            pen = QPen(_qcolor(247, 118, 142, alpha), 1.5)
        else:
            # Regular border – brighter version of owner's colour
            hex1 = civ_colors.get(owner1, '#888888')
            base = QColor(hex1)
            brighter = _qcolor(
                min(255, base.red() + 40),
                min(255, base.green() + 40),
                min(255, base.blue() + 40),
                180,
            )
            pen = QPen(brighter, 1.5)

        line = self._scene.addLine(x1, y1, x2, y2, pen)
        line.setZValue(10)
        line.setData(0, 'border')  # tag for animation cleanup
        self._dynamic_items.append(line)

    # ────────────────────────────────────────────────────
    # Resource markers (enhanced diamonds with white outline)
    # ────────────────────────────────────────────────────

    def _draw_resources(self, resource_map, ts):
        """Draw enhanced diamond-shaped resource markers."""
        for (x, y), res_name in resource_map.items():
            res_color = RESOURCE_TYPES.get(res_name)
            if not res_color:
                continue

            cx = x * ts + ts // 2
            cy = y * ts + ts // 2
            # Diamond shape (slightly larger than original)
            s = max(2, ts // 3)  # half-size of diamond

            diamond = QPolygonF([
                QPointF(cx, cy - s),       # top
                QPointF(cx + s, cy),       # right
                QPointF(cx, cy + s),       # bottom
                QPointF(cx - s, cy),       # left
            ])

            # Filled diamond with resource colour
            item = self._scene.addPolygon(
                diamond, self._no_pen, QBrush(res_color)
            )
            item.setZValue(15)
            self._dynamic_items.append(item)

            # Thin white outline for visibility
            outline_pen = QPen(QColor(255, 255, 255, 160), 0.8)
            outline = self._scene.addPolygon(diamond, outline_pen, QBrush())
            outline.setZValue(16)
            self._dynamic_items.append(outline)

    # ────────────────────────────────────────────────────
    # Event overlays
    # ────────────────────────────────────────────────────

    def _draw_events(self, active_events, ts):
        """Draw event indicators on the map."""
        EVENT_STYLES = {
            "expand":     ("#9ece6a", "+"),
            "attack":     ("#f7768e", "!"),
            "war":        ("#f7768e", "!!"),
            "alliance":   ("#7aa2f7", "~"),
            "research":   ("#7dcfff", "?"),
            "wonder":     ("#e0af68", "*"),
            "culture":    ("#bb9af7", "@"),
            "rebel":      ("#ff9e64", "#"),
            "government": ("#565f89", "="),
            "leader":     ("#565f89", ">"),
            "default":    ("#a9b1d6", "-"),
        }

        for ev in active_events:
            etype = getattr(ev, 'event_type', 'default')
            if isinstance(etype, int):
                etype = 'default'
            color_hex, symbol = EVENT_STYLES.get(
                etype, EVENT_STYLES['default']
            )

            pos = getattr(ev, 'position', None) or getattr(ev, 'tile', None)
            if pos is None:
                continue

            tx, ty = pos
            px = tx * ts + ts // 2
            py = ty * ts + ts // 2

            # Pulsing alpha for event markers
            pulse = 0.6 + 0.4 * math.sin(self._war_pulse * 0.8)
            alpha = int(200 * pulse)

            color = QColor(color_hex)
            color.setAlpha(alpha)

            # Coloured dot
            dot = self._scene.addEllipse(
                px - 3, py - 3, 6, 6,
                self._no_pen, QBrush(color)
            )
            dot.setZValue(20)
            self._dynamic_items.append(dot)

            # Symbol text
            font = QFont("Segoe UI", max(6, ts - 4), QFont.Bold)
            text = self._scene.addText(symbol, font)
            text.setDefaultTextColor(QColor(255, 255, 255, alpha))
            text.setPos(px - ts // 3, py - ts // 3)
            text.setZValue(21)
            self._dynamic_items.append(text)

    # ────────────────────────────────────────────────────
    # Trade routes (golden dash-dot, thicker)
    # ────────────────────────────────────────────────────

    def _draw_trade_routes(self, trade_routes, ts):
        """Draw enhanced trade route lines with golden dash-dot pattern."""
        golden = QColor(224, 175, 104)  # #e0af68
        pen = QPen(golden, 2.5, Qt.DashDotLine)
        pen.setCapStyle(Qt.RoundCap)
        pen.setDashPattern([6, 3, 2, 3])

        for route in trade_routes:
            # Route can be a dict with 'path' key, or a list of (x,y) tuples
            if isinstance(route, dict):
                path = route.get('path', [])
            else:
                path = route

            if not path or len(path) < 2:
                continue

            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                # Centre of each tile
                sx1, sy1 = x1 * ts + ts // 2, y1 * ts + ts // 2
                sx2, sy2 = x2 * ts + ts // 2, y2 * ts + ts // 2
                line = self._scene.addLine(sx1, sy1, sx2, sy2, pen)
                line.setZValue(8)
                self._dynamic_items.append(line)

    # ────────────────────────────────────────────────────
    # Path highlight (yellow dashed)
    # ────────────────────────────────────────────────────

    def _draw_path(self, path_data, ts):
        """Draw a highlighted path (yellow dashed line)."""
        if not path_data or len(path_data) < 2:
            return

        pen = QPen(QColor(255, 255, 100, 200), 2, Qt.DashLine)
        pen.setCapStyle(Qt.RoundCap)

        for i in range(len(path_data) - 1):
            x1, y1 = path_data[i]
            x2, y2 = path_data[i + 1]
            sx1, sy1 = x1 * ts + ts // 2, y1 * ts + ts // 2
            sx2, sy2 = x2 * ts + ts // 2, y2 * ts + ts // 2
            line = self._scene.addLine(sx1, sy1, sx2, sy2, pen)
            line.setZValue(18)
            self._dynamic_items.append(line)

    # ────────────────────────────────────────────────────
    # Capital markers (circle + star + outline ring)
    # ────────────────────────────────────────────────────

    def _draw_capitals(self, capitals, civ_colors, ts):
        """Draw enhanced capital markers: filled circle + white star + ring."""
        for civ_name, (cx, cy) in capitals.items():
            if cx is None or cy is None:
                continue

            civ_hex = civ_colors.get(civ_name, '#ffffff')
            civ_color = QColor(civ_hex)
            px = cx * ts + ts // 2
            py = cy * ts + ts // 2
            radius = TILE_SIZE * 0.6

            # 1. Filled circle in civ colour
            circle = self._scene.addEllipse(
                px - radius, py - radius,
                radius * 2, radius * 2,
                self._no_pen, QBrush(civ_color)
            )
            circle.setZValue(25)
            self._dynamic_items.append(circle)

            # 2. White star on top
            star_r = radius * 0.7
            star_path = QPainterPath()
            for i in range(5):
                angle = math.radians(-90 + i * 72)
                sx = px + star_r * math.cos(angle)
                sy = py + star_r * math.sin(angle)
                if i == 0:
                    star_path.moveTo(sx, sy)
                else:
                    star_path.lineTo(sx, sy)
                angle2 = math.radians(-90 + i * 72 + 36)
                sx2 = px + star_r * 0.4 * math.cos(angle2)
                sy2 = py + star_r * 0.4 * math.sin(angle2)
                star_path.lineTo(sx2, sy2)
            star_path.closeSubpath()

            star_item = self._scene.addPath(
                star_path, self._no_pen, QBrush(QColor(255, 255, 255, 220))
            )
            star_item.setZValue(26)
            self._dynamic_items.append(star_item)

            # 3. White outline ring
            ring_pen = QPen(QColor(255, 255, 255, 200), 1.2)
            ring = self._scene.addEllipse(
                px - radius - 1, py - radius - 1,
                (radius + 1) * 2, (radius + 1) * 2,
                ring_pen, QBrush()
            )
            ring.setZValue(27)
            self._dynamic_items.append(ring)
"""
fixed_main_app.py — API-compatible MainWindow + AppController
that works with the existing SimulationEngine.

All widget classes are imported from new_widgets.py and new_map_view.py.
Engine-specific types (Terrain, SEASON_NAMES, SimulationEngine) are
imported from the engine package.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QScrollArea, QTabWidget, QComboBox, QSlider,
    QTextEdit, QPushButton, QFileDialog, QSizePolicy, QStatusBar,
)
from PyQt6.QtCore import Qt, QSize, QRectF

# ---------------------------------------------------------------------------
# Widget imports (the new widget modules that precede this file)
# ---------------------------------------------------------------------------
from new_widgets import (
    ENHANCED_STYLESHEET,
    TimelineGraph,
    CivCard,
    MinimapWidget,
    LeaderboardWidget,
    DiplomacyMatrix,
    EventFeed,
    GenerationReportPanel,
    NotificationOverlay,
)
from new_map_view import EnhancedMapView

# ---------------------------------------------------------------------------
# Engine imports
# ---------------------------------------------------------------------------
from engine.core import SimulationEngine
from engine.terrain import Terrain, SEASON_NAMES


# ===================================================================
# Helper: SectionFrame
# ===================================================================
class SectionFrame(QFrame):
    """A reusable panel with a coloured header label."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "SectionFrame { border: 1px solid #3b4261; border-radius: 6px; "
            "background-color: #24283b; }"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)
        header = QLabel(title)
        header.setStyleSheet(
            "color: #7aa2f7; font-size: 11px; font-weight: bold; "
            "padding: 2px 6px; background-color: #1a2a3a; border-radius: 3px;"
        )
        lay.addWidget(header)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(4)
        lay.addLayout(self.content_layout)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)


# ===================================================================
# MainWindow
# ===================================================================
class MainWindow(QMainWindow):
    """Top-level window exposing every attribute & method the
    AppController (and engine signals) expect."""

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Civilization Simulator")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(ENHANCED_STYLESHEET)

        # Core widgets --------------------------------------------------
        self.map_view = EnhancedMapView()
        self.minimap = MinimapWidget()
        self.timeline = TimelineGraph()
        self.leaderboard = LeaderboardWidget()
        self.diplomacy_matrix = DiplomacyMatrix()
        self.event_feed = EventFeed()
        self.gen_report_panel = GenerationReportPanel()
        self.notification_overlay = NotificationOverlay(self)

        # Civ cards bookkeeping -----------------------------------------
        self.civ_cards: dict[str, CivCard] = {}

        # Build UI ------------------------------------------------------
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    def _tool_button_style(self, color: str = "#7aa2f7") -> str:
        return (
            f"QPushButton {{ background-color: {color}; color: #1a1b26; "
            f"font-weight: bold; border: none; border-radius: 4px; "
            f"padding: 5px 12px; font-size: 12px; }}"
            f"QPushButton:hover {{ background-color: {color}cc; }}"
            f"QPushButton:pressed {{ background-color: {color}99; }}"
        )

    def _combo_style(self) -> str:
        return (
            "QComboBox { background-color: #1a1b26; color: #c0caf5; "
            "border: 1px solid #3b4261; border-radius: 4px; padding: 4px 8px; "
            "font-size: 11px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView { background-color: #1a1b26; "
            "color: #c0caf5; selection-background-color: #3b4261; }"
        )

    def _slider_style(self) -> str:
        return (
            "QSlider::groove:horizontal { background: #1a1b26; height: 6px; "
            "border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #7aa2f7; width: 14px; "
            "margin: -4px 0; border-radius: 7px; }"
            "QSlider::sub-page:horizontal { background: #3b4261; border-radius: 3px; }"
        )

    def _build_toolbar(self):
        tb = self.addToolBar("Controls")
        tb.setMovable(False)
        tb.setStyleSheet(
            "QToolBar { background: #1a1b26; border-bottom: 1px solid #3b4261; "
            "spacing: 8px; padding: 4px; }"
            "QToolButton { background: transparent; border: none; }"
        )

        # -- Play / Pause
        self.btn_play = QPushButton("  Play  ")
        self.btn_play.setStyleSheet(self._tool_button_style("#9ece6a"))
        self.btn_play.setFixedHeight(28)
        tb.addWidget(self.btn_play)

        # -- Reset view
        self.btn_reset = QPushButton("  Reset View  ")
        self.btn_reset.setStyleSheet(self._tool_button_style("#565f89"))
        self.btn_reset.setFixedHeight(28)
        tb.addWidget(self.btn_reset)

        tb.addSeparator()

        # -- Speed slider
        spd_label = QLabel(" Speed: ")
        spd_label.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        tb.addWidget(spd_label)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 500)
        self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.setStyleSheet(self._slider_style())
        tb.addWidget(self.speed_slider)

        tb.addSeparator()

        # -- Duration combo
        dur_lbl = QLabel(" Duration: ")
        dur_lbl.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        tb.addWidget(dur_lbl)
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["200 years", "500 years", "1000 years", "Endless"])
        self.duration_combo.setStyleSheet(self._combo_style())
        self.duration_combo.setFixedHeight(28)
        tb.addWidget(self.duration_combo)

        tb.addSeparator()

        # -- Civ count combo
        cc_lbl = QLabel(" Civs: ")
        cc_lbl.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        tb.addWidget(cc_lbl)
        self.civ_count_combo = QComboBox()
        self.civ_count_combo.addItems(["3", "4", "5", "6", "7", "8", "10", "12"])
        self.civ_count_combo.setCurrentText("5")
        self.civ_count_combo.setStyleSheet(self._combo_style())
        self.civ_count_combo.setFixedHeight(28)
        tb.addWidget(self.civ_count_combo)

        tb.addSeparator()

        # -- Terrain preset combo
        ter_lbl = QLabel(" Terrain: ")
        ter_lbl.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        tb.addWidget(ter_lbl)
        self.terrain_combo = QComboBox()
        self.terrain_combo.addItems(["continents", "archipelago", "pangaea", "islands"])
        self.terrain_combo.setStyleSheet(self._combo_style())
        self.terrain_combo.setFixedHeight(28)
        tb.addWidget(self.terrain_combo)

        tb.addSeparator()

        # -- Checkbox toggles (as small push-buttons for simplicity)
        self.chk_fog = QPushButton(" Fog ")
        self.chk_fog.setCheckable(True)
        self.chk_fog.setChecked(True)
        self.chk_fog.setStyleSheet(self._tool_button_style("#7aa2f7"))
        self.chk_fog.setFixedHeight(28)
        self.chk_fog.toggled.connect(lambda v: setattr(self.map_view, "show_fog", v))
        tb.addWidget(self.chk_fog)

        self.chk_resources = QPushButton(" Resources ")
        self.chk_resources.setCheckable(True)
        self.chk_resources.setChecked(True)
        self.chk_resources.setStyleSheet(self._tool_button_style("#e0af68"))
        self.chk_resources.setFixedHeight(28)
        self.chk_resources.toggled.connect(lambda v: setattr(self.map_view, "show_resources", v))
        tb.addWidget(self.chk_resources)

        self.chk_borders = QPushButton(" Borders ")
        self.chk_borders.setCheckable(True)
        self.chk_borders.setChecked(True)
        self.chk_borders.setStyleSheet(self._tool_button_style("#9ece6a"))
        self.chk_borders.setFixedHeight(28)
        self.chk_borders.toggled.connect(lambda v: setattr(self.map_view, "show_borders", v))
        tb.addWidget(self.chk_borders)

        self.chk_gen_reports = QPushButton(" Reports ")
        self.chk_gen_reports.setCheckable(True)
        self.chk_gen_reports.setChecked(False)
        self.chk_gen_reports.setStyleSheet(self._tool_button_style("#bb9af7"))
        self.chk_gen_reports.setFixedHeight(28)
        tb.addWidget(self.chk_gen_reports)

        tb.addSeparator()

        # -- Save / Load / New
        self.btn_save = QPushButton(" Save ")
        self.btn_save.setStyleSheet(self._tool_button_style("#565f89"))
        self.btn_save.setFixedHeight(28)
        tb.addWidget(self.btn_save)

        self.btn_load = QPushButton(" Load ")
        self.btn_load.setStyleSheet(self._tool_button_style("#565f89"))
        self.btn_load.setFixedHeight(28)
        tb.addWidget(self.btn_load)

        self.btn_new = QPushButton(" New Game ")
        self.btn_new.setStyleSheet(self._tool_button_style("#f7768e"))
        self.btn_new.setFixedHeight(28)
        tb.addWidget(self.btn_new)

        tb.addSeparator()

        # -- Year display
        self.lbl_year = QLabel("Year: 0  |  Spring  |  Gen: 0")
        self.lbl_year.setStyleSheet(
            "color: #7aa2f7; font-size: 12px; font-weight: bold; "
            "padding: 3px 10px; background-color: #1a2a3a; border-radius: 4px;"
        )
        self.lbl_year.setFixedHeight(28)
        tb.addWidget(self.lbl_year)

    # ------------------------------------------------------------------
    # Central widget
    # ------------------------------------------------------------------
    def _build_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # ---- Left: map view + tile info ----
        left = QVBoxLayout()
        left.setSpacing(4)

        self.map_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.map_view, stretch=1)

        self.tile_info_lbl = QLabel("Hover over a tile for info")
        self.tile_info_lbl.setStyleSheet(
            "color: #a9b1d6; font-size: 11px; padding: 2px 6px; "
            "background-color: #1a1b26; border-radius: 3px;"
        )
        self.tile_info_lbl.setFixedHeight(22)
        left.addWidget(self.tile_info_lbl)

        root.addLayout(left, stretch=3)

        # ---- Right panel ----
        right = QVBoxLayout()
        right.setSpacing(4)

        # 1) Minimap (fixed height ~150px)
        minimap_frame = SectionFrame("Minimap")
        self.minimap.setFixedHeight(145)
        minimap_frame.add_widget(self.minimap)
        right.addWidget(minimap_frame)

        # 2) Event Feed (fixed height ~150px)
        event_frame = SectionFrame("Event Feed")
        self.event_feed.setFixedHeight(145)
        event_frame.add_widget(self.event_feed)
        right.addWidget(event_frame)

        # 3) Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #3b4261; background: #24283b; "
            "border-radius: 4px; }"
            "QTabBar::tab { background: #1a1b26; color: #a9b1d6; padding: 6px 14px; "
            "font-size: 11px; border-top-left-radius: 4px; border-top-right-radius: 4px; "
            "margin-right: 2px; }"
            "QTabBar::tab:selected { background: #24283b; color: #7aa2f7; "
            "border-bottom: 2px solid #7aa2f7; }"
        )

        # Tab: Civilizations (civ cards)
        civ_tab = QWidget()
        civ_tab_lay = QVBoxLayout(civ_tab)
        civ_tab_lay.setContentsMargins(4, 4, 4, 4)
        civ_tab_lay.setSpacing(4)
        self.civ_scroll = QScrollArea()
        self.civ_scroll.setWidgetResizable(True)
        self.civ_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical { background: #1a1b26; width: 8px; border-radius: 4px; }"
            "QScrollBar::handle:vertical { background: #3b4261; border-radius: 4px; min-height: 30px; }"
        )
        civ_scroll_container = QWidget()
        self.civ_layout = QVBoxLayout(civ_scroll_container)
        self.civ_layout.setContentsMargins(2, 2, 2, 2)
        self.civ_layout.setSpacing(4)
        self.civ_layout.addStretch()
        self.civ_scroll.setWidget(civ_scroll_container)
        civ_tab_lay.addWidget(self.civ_scroll)
        self.tabs.addTab(civ_tab, "Civilizations")

        # Tab: Overview (timeline + leaderboard + diplomacy)
        overview_tab = QWidget()
        ov_lay = QVBoxLayout(overview_tab)
        ov_lay.setContentsMargins(4, 4, 4, 4)
        ov_lay.setSpacing(4)

        tl_frame = SectionFrame("Timeline")
        self.timeline.setMinimumHeight(140)
        tl_frame.add_widget(self.timeline)
        ov_lay.addWidget(tl_frame, stretch=1)

        lb_frame = SectionFrame("Leaderboard")
        self.leaderboard.setMinimumHeight(120)
        lb_frame.add_widget(self.leaderboard)
        ov_lay.addWidget(lb_frame, stretch=1)

        dip_frame = SectionFrame("Diplomacy")
        self.diplomacy_matrix.setMinimumHeight(120)
        dip_frame.add_widget(self.diplomacy_matrix)
        ov_lay.addWidget(dip_frame, stretch=1)

        self.tabs.addTab(overview_tab, "Overview")

        # Tab: Log
        log_tab = QWidget()
        log_lay = QVBoxLayout(log_tab)
        log_lay.setContentsMargins(4, 4, 4, 4)
        log_lay.setSpacing(4)

        log_filter_row = QHBoxLayout()
        log_filter_row.setSpacing(6)
        log_filter_lbl = QLabel("Filter:")
        log_filter_lbl.setStyleSheet("color: #a9b1d6; font-size: 11px;")
        log_filter_row.addWidget(log_filter_lbl)
        self.log_filter = QComboBox()
        self.log_filter.addItem("All")
        self.log_filter.setStyleSheet(self._combo_style())
        self.log_filter.setFixedHeight(24)
        self.log_filter.currentTextChanged.connect(self._on_log_filter_changed)
        log_filter_row.addWidget(self.log_filter)
        log_filter_row.addStretch()
        log_lay.addLayout(log_filter_row)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet(
            "QTextEdit { background-color: #1a1b26; color: #c0caf5; "
            "border: 1px solid #3b4261; border-radius: 4px; font-size: 11px; "
            "font-family: 'Consolas', 'Monaco', monospace; }"
        )
        log_lay.addWidget(self.log_view)
        self.tabs.addTab(log_tab, "Log")

        # Tab: Reports
        reports_tab = QWidget()
        rep_lay = QVBoxLayout(reports_tab)
        rep_lay.setContentsMargins(4, 4, 4, 4)
        self.gen_report_panel.setStyleSheet(
            "QTextEdit { background-color: #1a1b26; color: #c0caf5; "
            "border: 1px solid #3b4261; border-radius: 4px; font-size: 11px; }"
        )
        rep_lay.addWidget(self.gen_report_panel)
        self.tabs.addTab(reports_tab, "Reports")

        right.addWidget(self.tabs, stretch=1)

        root.addLayout(right, stretch=2)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.setStyleSheet(
            "QStatusBar { background: #1a1b26; color: #a9b1d6; font-size: 11px; "
            "border-top: 1px solid #3b4261; }"
        )
        self._zoom_lbl = QLabel("Zoom: 100%")
        self._zoom_lbl.setStyleSheet("color: #7aa2f7; padding: 0 8px;")
        sb.addPermanentWidget(self._zoom_lbl)
        self.zoom_lbl = self._zoom_lbl  # alias for backward compat

        self.civ_count_lbl = QLabel("Civs: 5")
        self.civ_count_lbl.setStyleSheet("color: #9ece6a; padding: 0 8px;")
        sb.addPermanentWidget(self.civ_count_lbl)

        self.civ_count_combo.currentTextChanged.connect(
            lambda t: self.civ_count_lbl.setText(f"Civs: {t}")
        )

    # ------------------------------------------------------------------
    # Public API — called by AppController
    # ------------------------------------------------------------------
    def update_stats(self, civs_data: list[dict]):
        """Create / update CivCards, feed timeline, leaderboard, diplomacy."""
        existing_names = set(self.civ_cards.keys())
        new_names = {d["name"] for d in civs_data}

        # Remove cards for civs that no longer exist
        for name in list(existing_names - new_names):
            card = self.civ_cards.pop(name)
            self.civ_layout.removeWidget(card)
            card.deleteLater()

        # Remove the trailing stretch so we can append in order
        stretch_item = self.civ_layout.itemAt(self.civ_layout.count() - 1)
        if stretch_item and stretch_item.spacerItem():
            self.civ_layout.removeItem(stretch_item)

        # Insert new cards at the correct position
        for idx, d in enumerate(civs_data):
            name = d["name"]
            if name in self.civ_cards:
                self.civ_cards[name].update_data(d)
            else:
                card = CivCard(d)
                self.civ_cards[name] = card
                self.civ_layout.insertWidget(min(idx, self.civ_layout.count()), card)

        # Re-add stretch at the end
        self.civ_layout.addStretch()

        # Feed sub-widgets
        self.timeline.update_data(civs_data)
        self.leaderboard.update_rankings(civs_data)
        self.diplomacy_matrix.update_data(civs_data)

    def append_log(self, text: str):
        """Append to log_view and parse into event_feed."""
        parts = text.split(": ", 2)
        if len(parts) == 3:
            year, civ_name, action = parts
            if self.log_filter.currentText() not in ("All", civ_name):
                return
            html = (
                f"<span style='color:#565f89'>{year}:</span> "
                f"<b style='color:#e0af68'>{civ_name}</b> {action}"
            )
            self.log_view.append(html)
            # Feed to event feed
            self._feed_event(year, civ_name, action)
        else:
            self.log_view.append(text)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )

    def add_generation_report(self, html: str, plain: str):
        """Forward to the generation report panel."""
        self.gen_report_panel.add_report(html, plain)

    def show_notification(self, title: str, message: str):
        """Forward to the notification overlay."""
        self.notification_overlay.add_notification(title, message)

    def get_civ_count(self) -> int:
        try:
            return int(self.civ_count_combo.currentText())
        except (ValueError, TypeError):
            return 5

    def get_terrain_preset(self) -> str:
        return self.terrain_combo.currentText()

    def _update_minimap_viewport(self):
        """Sync minimap viewport rectangle with the map view's visible area."""
        try:
            rect = self.map_view.visible_scene_rect()
            self.minimap.set_viewport_rect(rect)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _feed_event(self, year_str: str, civ_name: str, action: str):
        """Parse *action* text and push a typed entry into the EventFeed."""
        action_lower = action.lower()
        type_map = {
            "expand": ("expand", "#9ece6a", "+"),
            "attack": ("attack", "#f7768e", "!"),
            "war": ("war", "#ff0000", "!!"),
            "alliance": ("alliance", "#7dcfff", "~"),
            "research": ("research", "#7aa2f7", "?"),
            "wonder": ("wonder", "#e0af68", "*"),
            "culture": ("culture", "#bb9af7", "@"),
            "rebel": ("rebel", "#ff9e64", "#"),
            "government": ("government", "#565f89", "="),
            "leader": ("leader", "#c0caf5", ">"),
            "trade": ("trade", "#9ece6a", "$"),
            "diplomac": ("diplomacy", "#7dcfff", "~"),
            "fortif": ("fortify", "#7dcfff", "D"),
            "develop": ("develop", "#e0af68", "B"),
        }
        etype, color, icon = "expand", "#9ece6a", "+"
        for key, (t, c, i) in type_map.items():
            if key in action_lower:
                etype, color, icon = t, c, i
                break
        try:
            year_val = int(year_str.replace("Year ", "").strip())
        except Exception:
            year_val = 0
        self.event_feed.add_event(etype, f"{civ_name}: {action}", year_val)

    def _on_log_filter_changed(self, text: str):
        """Re-populate log filter combo with civ names when 'All' is selected."""
        if text == "All":
            return


# ===================================================================
# AppController
# ===================================================================
class AppController:
    """Wires the MainWindow to the SimulationEngine and manages game
    lifecycle (play/pause, save/load, new game)."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.window = MainWindow()
        self.engine = None
        self.playing = False
        self._create_engine()
        self._connect_window_signals()
        self._connect_engine_signals()

    # ------------------------------------------------------------------
    # Engine lifecycle
    # ------------------------------------------------------------------
    def _create_engine(self):
        civ_count = self.window.get_civ_count()
        terrain_preset = self.window.get_terrain_preset()
        self.engine = SimulationEngine(civ_count=civ_count, terrain_preset=terrain_preset)

    def _connect_window_signals(self):
        w = self.window
        w.btn_play.clicked.connect(self.toggle_play)
        w.btn_reset.clicked.connect(w.map_view.reset_view)
        w.speed_slider.valueChanged.connect(self._on_speed_changed)
        w.duration_combo.currentTextChanged.connect(self._set_duration)
        w.map_view.tile_hovered.connect(self._on_tile_hover)
        w.map_view.zoom_changed.connect(self._on_zoom_changed)
        w.btn_save.clicked.connect(self._save_game)
        w.btn_load.clicked.connect(self._load_game)
        w.btn_new.clicked.connect(self._new_game)

    def _connect_engine_signals(self):
        if not self.engine:
            return
        self.engine.update_signal.connect(self._on_update)
        self.engine.log_signal.connect(self.window.append_log)
        self.engine.gen_report_signal.connect(self.window.add_generation_report)
        self.engine.notification_signal.connect(self.window.show_notification)

    def _disconnect_engine_signals(self):
        if not self.engine:
            return
        try:
            self.engine.update_signal.disconnect()
            self.engine.log_signal.disconnect()
            self.engine.gen_report_signal.disconnect()
            self.engine.notification_signal.disconnect()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Window → Engine slots
    # ------------------------------------------------------------------
    def _on_speed_changed(self, v):
        if self.engine:
            self.engine.speed = v

    def _set_duration(self, text: str):
        dur_map = {"200 years": 200, "500 years": 500, "1000 years": 1000, "Endless": 0}
        if self.engine:
            self.engine.max_years = dur_map.get(text, 0)

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.window.btn_play.setText("  Pause  ")
            if self.engine and not self.engine.isRunning():
                self.engine.start()
        else:
            self.window.btn_play.setText("  Play  ")
            if self.engine:
                self.engine.running = False

    def _on_tile_hover(self, tx: int, ty: int):
        if not self.engine:
            return
        t_id = self.engine.terrain_map.get((tx, ty))
        if t_id is not None:
            t_name = Terrain(t_id).name
            owner = self.engine.owner_map.get((tx, ty), "Unclaimed")
            res = self.engine.resource_map.get((tx, ty), "None")
            self.window.tile_info_lbl.setText(
                f"({tx},{ty})  |  Terrain: {t_name}  |  "
                f"Owner: {owner or 'None'}  |  Resource: {res}"
            )

    def _on_zoom_changed(self, zoom_pct: int):
        if hasattr(self.window, "_zoom_lbl"):
            self.window._zoom_lbl.setText(f"Zoom: {zoom_pct}%")
        elif hasattr(self.window, "zoom_lbl"):
            self.window.zoom_lbl.setText(f"Zoom: {zoom_pct}%")

    # ------------------------------------------------------------------
    # Engine → Window slot
    # ------------------------------------------------------------------
    def _on_update(self, data: dict):
        civ_colors = {c.name: c.color for c in data["civs"]}
        season_name = SEASON_NAMES[data["season"]]
        gen = data.get("generation", 0)
        self.window.lbl_year.setText(
            f"Year: {data['year']}  |  {season_name}  |  Gen: {gen}"
        )

        self.window.map_view.update_map(
            data["terrain"],
            data["owners"],
            civ_colors,
            data["explored"],
            data["last_path"],
            data["capitals"],
            data["trade_routes"],
            data["active_events"],
            data["resource_map"],
            data["season"],
        )

        self.window.minimap.update_data(
            data["terrain"], data["owners"], civ_colors, data["explored"]
        )

        # Build UI-friendly dicts from Civ objects
        civs_ui_data = []
        for c in data["civs"]:
            civs_ui_data.append(
                {
                    "name": c.name,
                    "color": c.color,
                    "population": c.population,
                    "pop_delta": 0,
                    "military": c.military,
                    "mil_delta": 0,
                    "technology": c.technology,
                    "tech_delta": 0,
                    "treasury": c.treasury,
                    "treas_delta": 0,
                    "culture": c.culture,
                    "stability": c.stability,
                    "score": c.score,
                    "last_action": c.last_action,
                    "buildings": c.buildings,
                    "wonders": c.wonders,
                    "alliances": c.alliances,
                    "trade_partners": c.trade_partners,
                    "at_war_with": c.at_war_with,
                    "religion": c.religion,
                    "era_name": c.era_name,
                    "archetype": c.archetype,
                    "archetype_label": c.archetype_label,
                    "archetype_desc": c.archetype_desc,
                    "strategic_state": c.strategic_state_name,
                    "plan_name": c.plan_name,
                    "government": c.government,
                    "government_label": c.government_label,
                    "government_desc": c.government_desc,
                    "leader_name": c.leader_name,
                    "leader_short_name": c.leader_short_name,
                }
            )
        self.window.update_stats(civs_ui_data)
        self.window._update_minimap_viewport()

    # ------------------------------------------------------------------
    # Save / Load / New
    # ------------------------------------------------------------------
    def _save_game(self):
        if not self.engine:
            return
        path, _ = QFileDialog.getSaveFileName(
            self.window, "Save Game", "civ_save.json", "JSON Files (*.json)"
        )
        if path:
            was_running = self.engine.running
            self.engine.running = False
            self.engine.save_game(path)
            if was_running:
                self.engine.running = True

    def _load_game(self):
        path, _ = QFileDialog.getOpenFileName(
            self.window, "Load Game", "", "JSON Files (*.json)"
        )
        if path and self.engine:
            was_running = self.engine.running
            self.engine.running = False
            self.engine.load_game(path)
            self.playing = False
            self.window.btn_play.setText("  Play  ")
            for card in self.window.civ_cards.values():
                self.window.civ_layout.removeWidget(card)
                card.deleteLater()
            self.window.civ_cards.clear()
            self.window.map_view.clear_map()

    def _new_game(self):
        if self.engine:
            self.engine.running = False
            self.engine.wait(2000)
            try:
                self.engine.analytics.commit()
            except Exception:
                pass
            self._disconnect_engine_signals()

        self.playing = False
        self.window.btn_play.setText("  Play  ")

        for card in self.window.civ_cards.values():
            self.window.civ_layout.removeWidget(card)
            card.deleteLater()
        self.window.civ_cards.clear()

        self.window.gen_report_panel.clear_reports()
        self.window.log_view.clear()
        if hasattr(self.window, "event_feed"):
            self.window.event_feed.clear_events()
        self.window.map_view.clear_map()

        self._create_engine()
        self._connect_engine_signals()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


# ===================================================================
if __name__ == "__main__":
    controller = AppController()
    controller.run()
