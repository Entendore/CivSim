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
