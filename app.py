# ════════════════════════════════════════════════════════════
# AUTONOMOUS CIVILIZATION SIMULATION - SINGLE FILE EDITION
# In-Memory Data Architecture - No SQLite Dependency
# ════════════════════════════════════════════════════════════
from __future__ import annotations

import sys
import os
import math
import json
import random
import heapq
from enum import IntEnum
from collections import deque
from typing import Optional, Callable

from PySide6.QtCore import (
    Qt, QRectF, Signal, QTimer, QThread, QPointF, QPoint, QSize,
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QLinearGradient, QPen, QBrush, QFont,
    QPolygonF, QCursor, QShortcut, QKeySequence,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QScrollArea, QTabWidget, QComboBox, QSlider,
    QTextEdit, QPushButton, QFileDialog, QSizePolicy, QStatusBar,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGridLayout,
    QSplitter,
)

# ════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════
DB_PATH = "civ_simulation.sqlite"  # Kept for legacy compatibility, unused
TILE_SIZE = 14

class Terrain(IntEnum):
    OCEAN = 0; PLAINS = 1; FOREST = 2; MOUNTAIN = 3; DESERT = 4
    JUNGLE = 5; HILLS = 6; TUNDRA = 7; COAST = 8; GRASSLAND = 9

class Relation(IntEnum):
    NEUTRAL = 0; FRIENDLY = 1; ALLIED = 2; HOSTILE = 3; AT_WAR = 4

class TerrainPreset:
    CONTINENT = "Continent"
    ARCHIPELAGO = "Archipelago"
    PANGAEA = "Pangaea"
    ISLANDS = "Islands"
    HIGHLANDS = "Highlands"
    RIVER_VALLEY = "River Valley"
    CRATER = "Crater Lake"
    MEDITERRANEAN = "Mediterranean"

TERRAIN_COLORS = {
    0: QColor(22, 50, 115),  1: QColor(125, 182, 82),  2: QColor(42, 122, 42),
    3: QColor(142, 132, 122),4: QColor(208, 182, 102),5: QColor(34, 139, 34),
    6: QColor(139, 119, 101),7: QColor(180, 210, 230),8: QColor(72, 145, 220),
    9: QColor(100, 200, 100),
}
TERRAIN_NAMES = {
    0: "Ocean", 1: "Plains", 2: "Forest", 3: "Mountain", 4: "Desert",
    5: "Jungle", 6: "Hills", 7: "Tundra", 8: "Coast", 9: "Grassland",
}

RESOURCE_TYPES = {
    "iron":     QColor(160, 160, 170),
    "wheat":    QColor(240, 220, 130),
    "gold_ore": QColor(255, 215, 0),
    "horses":   QColor(139, 90, 43),
    "stone":    QColor(180, 180, 180),
    "fish":     QColor(100, 180, 255),
}

RELIGIONS = [
    {"name": "Sun Worship",  "color": "#FFD700", "bonus_type": "growth",   "bonus_val": 0.05},
    {"name": "War Cult",     "color": "#FF4500", "bonus_type": "military", "bonus_val": 0.05},
    {"name": "Mystic Order", "color": "#9370DB", "bonus_type": "culture",  "bonus_val": 0.08},
    {"name": "Trade Creed",  "color": "#37AFAF", "bonus_type": "trade",    "bonus_val": 0.06},
]

WONDERS = [
    {"name": "Great Lighthouse",    "effect": "trade",    "bonus": 0.30, "cost": 200},
    {"name": "Colossus",            "effect": "military", "bonus": 0.20, "cost": 150},
    {"name": "Hanging Gardens",     "effect": "growth",   "bonus": 0.25, "cost": 180},
    {"name": "Great Library",       "effect": "tech",     "bonus": 0.30, "cost": 200},
    {"name": "Temple of Artemis",   "effect": "culture",  "bonus": 0.20, "cost": 170},
    {"name": "Pyramids",            "effect": "growth",   "bonus": 0.15, "cost": 160},
]

SEASON_NAMES = ["Spring", "Summer", "Autumn", "Winter"]
FOOD_MULTIPLIERS = [1.0, 1.3, 0.9, 0.5]
SEASON_COLORS = [
    QColor(100, 200, 100, 35),
    QColor(255, 200, 50, 35),
    QColor(200, 120, 50, 35),
    QColor(150, 200, 255, 35),
]

REBEL_NAMES = ["Free State", "Independents", "Rebels", "Liberators", "Uprising"]

GOVERNMENTS = {
    "chiefdom":    {"label": "Chiefdom",     "succession": "hereditary", "leader_term_min": 20, "leader_term_max": 40, "stability_mod": 0.3,  "gold_mod": 0.8,  "science_mod": 0.7, "military_mod": 1.0, "culture_mod": 0.8,  "war_threshold_mod": -5,  "diplo_bonus": 0.00, "rebel_chance": 0.010, "allowed_govts": ["monarchy", "republic", "theocracy"],         "description": "A tribal society ruled by a hereditary chief.",                              "era_min": 0},
    "monarchy":    {"label": "Monarchy",     "succession": "hereditary", "leader_term_min": 25, "leader_term_max": 50, "stability_mod": 0.5,  "gold_mod": 1.0,  "science_mod": 0.9, "military_mod": 1.1, "culture_mod": 1.0,  "war_threshold_mod":  0,  "diplo_bonus": 0.05, "rebel_chance": 0.008, "allowed_govts": ["republic", "theocracy", "dictatorship", "oligarchy"], "description": "A hereditary kingdom where rulers reign for life.",                         "era_min": 1},
    "republic":    {"label": "Republic",     "succession": "election",   "leader_term_min":  8, "leader_term_max": 16, "stability_mod": 0.2,  "gold_mod": 1.2,  "science_mod": 1.2, "military_mod": 0.9, "culture_mod": 1.1,  "war_threshold_mod": 10,  "diplo_bonus": 0.15, "rebel_chance": 0.004, "allowed_govts": ["democracy", "oligarchy", "dictatorship", "monarchy"], "description": "Elected leaders govern for fixed terms.",                                  "era_min": 2},
    "theocracy":   {"label": "Theocracy",   "succession": "theocratic", "leader_term_min": 15, "leader_term_max": 35, "stability_mod": 0.7,  "gold_mod": 0.9,  "science_mod": 0.7, "military_mod": 1.0, "culture_mod": 1.5,  "war_threshold_mod": -3,  "diplo_bonus": 0.10, "rebel_chance": 0.005, "allowed_govts": ["monarchy", "republic", "dictatorship"],             "description": "Divine rule where religious leaders guide the state.",                     "era_min": 1},
    "dictatorship":{"label": "Dictatorship", "succession": "coup",        "leader_term_min": 10, "leader_term_max": 30, "stability_mod": -0.2, "gold_mod": 1.1,  "science_mod": 0.8, "military_mod": 1.3, "culture_mod": 0.6,  "war_threshold_mod": -15, "diplo_bonus": -0.10, "rebel_chance": 0.020, "allowed_govts": ["monarchy", "republic", "oligarchy"],                  "description": "Iron-fisted rule by a strongman.",                                         "era_min": 2},
    "oligarchy":   {"label": "Oligarchy",   "succession": "election",   "leader_term_min": 12, "leader_term_max": 24, "stability_mod": 0.1,  "gold_mod": 1.4,  "science_mod": 1.0, "military_mod": 0.8, "culture_mod": 0.9,  "war_threshold_mod":  5,  "diplo_bonus": 0.20, "rebel_chance": 0.006, "allowed_govts": ["republic", "dictatorship", "monarchy"],                   "description": "A small elite rules for profit.",                                          "era_min": 2},
    "democracy":   {"label": "Democracy",   "succession": "election",   "leader_term_min":  6, "leader_term_max": 12, "stability_mod": 0.4,  "gold_mod": 1.1,  "science_mod": 1.3, "military_mod": 0.8, "culture_mod": 1.3,  "war_threshold_mod": 15,  "diplo_bonus": 0.25, "rebel_chance": 0.002, "allowed_govts": ["republic", "oligarchy"],                              "description": "Full representative democracy.",                                           "era_min": 3},
}

LEADER_FIRST_NAMES = ["Aldric","Berenice","Caius","Darius","Elena","Felix","Gaius","Helena","Ivan","Julia","Kaspar","Livia","Magnus","Nadia","Octavia","Publius","Quintus","Rufina","Severus","Tatiana","Ursus","Valeria","Wolfram","Xanthippe","Yevgeny","Zeno","Alaric","Brunhilde","Cyrus","Demetria","Erik","Freya","Gundahar","Hrotsvitha","Iskandar","Jahanara","Khosrow","Lysistrata","Mithridates","Nefertari","Ozymandias","Priam","Rhadamanthus","Semiramis","Themistocles","Vercingetorix","Xerxes","Zenobia","Ashoka","Boudicca"]
LEADER_TITLES = {"chiefdom":["Chieftain","Headman","Elder","Matriarch","Patriarch"],"monarchy":["King","Queen","Emperor","Empress","Sovereign","High King"],"republic":["Consul","Chancellor","Premier","Tribune","Magistrate"],"theocracy":["High Priest","Prophet","Pontiff","Oracle","Hierophant"],"dictatorship":["Generalissimo","Supreme Leader","Commandant","Autarch","Protector"],"oligarchy":["Director","Chairman","Patrician","Archon","Syndic"],"democracy":["President","Prime Minister","Premier","Speaker","Minister"]}
LEADER_EPITHETS = ["the Bold","the Wise","the Cruel","the Just","the Great","the Unready","the Conqueror","the Peacemaker","the Mad","the Pious","the Terrible","the Enlightened","the Iron","the Golden","the Fierce","the Patient","the Venerable","the Proud","the Cunning","the Merciful","the Stubborn","the Young","the Old","the Silent","the Storm"]

PERSONALITY_ARCHETYPES = {
    "warlord":    {"label":"Warlord",          "war_threshold":25, "alliance_eagerness":0.3, "trade_eagerness":0.4, "expansion_greed":1.4, "wonder_hunger":0.6, "stability_resilience":0.8, "tolerance":10, "starting_bonus":{"military":50},   "weights":{"expansion":1.4,"military":1.6,"tech":0.6,"culture":0.5,"economy":0.7,"trade":0.4,"diplomacy":0.3,"wonder":0.2}},
    "philosopher":{"label":"Philosopher",      "war_threshold":80, "alliance_eagerness":0.8, "trade_eagerness":0.9, "expansion_greed":0.7, "wonder_hunger":0.7, "stability_resilience":1.2, "tolerance":60, "starting_bonus":{"technology":3.0},"weights":{"expansion":0.6,"military":0.5,"tech":1.8,"culture":1.2,"economy":1.0,"trade":1.0,"diplomacy":1.2,"wonder":0.8}},
    "merchant":   {"label":"Merchant Republic","war_threshold":60, "alliance_eagerness":1.0, "trade_eagerness":1.5, "expansion_greed":0.8, "wonder_hunger":0.5, "stability_resilience":1.0, "tolerance":40, "starting_bonus":{"treasury":300},  "weights":{"expansion":0.7,"military":0.6,"tech":1.0,"culture":0.8,"economy":1.6,"trade":1.8,"diplomacy":1.1,"wonder":1.0}},
    "zealot":     {"label":"Zealot",           "war_threshold":40, "alliance_eagerness":0.6, "trade_eagerness":0.5, "expansion_greed":1.0, "wonder_hunger":0.8, "stability_resilience":1.4, "tolerance":15, "starting_bonus":{"culture":100},   "weights":{"expansion":0.9,"military":1.0,"tech":0.8,"culture":1.8,"economy":0.8,"trade":0.5,"diplomacy":0.7,"wonder":1.2}},
    "builder":    {"label":"Builder",          "war_threshold":70, "alliance_eagerness":0.7, "trade_eagerness":0.8, "expansion_greed":0.6, "wonder_hunger":0.3, "stability_resilience":2.0, "tolerance":50, "starting_bonus":{"treasury":200},  "weights":{"expansion":0.5,"military":0.7,"tech":1.1,"culture":0.9,"economy":1.5,"trade":1.0,"diplomacy":0.9,"wonder":1.6}},
    "diplomat":   {"label":"Diplomat",         "war_threshold":90, "alliance_eagerness":1.5, "trade_eagerness":1.3, "expansion_greed":0.7, "wonder_hunger":0.6, "stability_resilience":1.3, "tolerance":70, "starting_bonus":{"culture":50},    "weights":{"expansion":0.6,"military":0.4,"tech":1.0,"culture":1.2,"economy":1.0,"trade":1.3,"diplomacy":2.0,"wonder":0.7}},
    "raider":     {"label":"Raider",           "war_threshold":30, "alliance_eagerness":0.2, "trade_eagerness":0.3, "expansion_greed":1.8, "wonder_hunger":0.9, "stability_resilience":0.6, "tolerance": 8, "starting_bonus":{"military":30,"treasury":-100},"weights":{"expansion":1.7,"military":1.5,"tech":0.7,"culture":0.4,"economy":0.5,"trade":0.3,"diplomacy":0.2,"wonder":0.1}},
    "survivor":   {"label":"Survivor",         "war_threshold":55, "alliance_eagerness":0.8, "trade_eagerness":0.7, "expansion_greed":0.8, "wonder_hunger":0.5, "stability_resilience":2.5, "tolerance":45, "starting_bonus":{"population":200,"stability":10},"weights":{"expansion":0.8,"military":0.8,"tech":1.0,"culture":0.9,"economy":1.2,"trade":0.9,"diplomacy":1.0,"wonder":0.6}},
}

CIV_TEMPLATES = [
    {"name":"Aethoria",  "color":"#D73737", "archetype":"warlord",     "government":"chiefdom"},
    {"name":"Byzantia",  "color":"#3769D7", "archetype":"diplomat",    "government":"republic"},
    {"name":"Celestia",  "color":"#37AF37", "archetype":"zealot",      "government":"theocracy"},
    {"name":"Drakonia",  "color":"#D7AF1E", "archetype":"raider",      "government":"chiefdom"},
    {"name":"Solaria",   "color":"#FF8C00", "archetype":"philosopher", "government":"republic"},
    {"name":"Ironhold",  "color":"#8B8B8B", "archetype":"warlord",     "government":"monarchy"},
    {"name":"Verdania",  "color":"#2E8B57", "archetype":"builder",     "government":"monarchy"},
    {"name":"Crimsonia", "color":"#DC143C", "archetype":"merchant",    "government":"oligarchy"},
    {"name":"Thornwall", "color":"#6B4C9A", "archetype":"survivor",    "government":"chiefdom"},
    {"name":"Ashford",   "color":"#C8A951", "archetype":"merchant",    "government":"oligarchy"},
]

DEFAULT_MAP_WIDTH  = 80
DEFAULT_MAP_HEIGHT = 60
SEASON_LENGTH = 25
AUTO_SAVE_INTERVAL = 100

BIRTH_RATE = 0.005
DEATH_RATE = 0.003
FAMINE_THRESHOLD = 1.10
FAMINE_DEATH_RATE = 0.05
STABILITY_BIRTH_MULT = 0.5
STABILITY_DEATH_MULT = 0.5
POP_HARD_CAP_MULT = 1.5

TECH_DIFFUSION_RATE = 0.005
TECH_DIFFUSION_MIN_GAP = 2.0
BORDER_FRICTION_BASE = 0.05
BORDER_FRICTION_RELIGION_MULT = 2.0

REBEL_TECH_INHERIT = 0.6
REBEL_CULTURE_INHERIT = 0.3
REBEL_POP_INHERIT = 0.2
REBEL_MILITARY_INHERIT = 0.15

# ─── Dark theme stylesheet ─────────────────────────────────
ENHANCED_STYLESHEET = """
QMainWindow, QWidget { background-color: #1a1b26; color: #c0caf5;
    font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif; font-size: 12px; }
QGraphicsView { border: 1px solid #3b4261; background-color: #1a1b26; border-radius: 2px; }
QToolBar { background-color: #24283b; border-bottom: 1px solid #1a1a2a; spacing: 5px; padding: 4px 8px; }
QPushButton { background-color: #2f3450; color: #c0caf5; border: 1px solid #3b4261;
    border-radius: 4px; padding: 5px 12px; font-size: 11px; }
QPushButton:hover { background-color: #3b4261; border-color: #7aa2f7; }
QPushButton:pressed { background-color: #1a1b26; }
QPushButton:checked { background-color: #7aa2f7; color: #1a1b26; font-weight: bold; }
QSlider::groove:horizontal { background: #24283b; height: 4px; border-radius: 2px; }
QSlider::handle:horizontal { background: #7aa2f7; width: 14px; margin: -5px 0; border-radius: 7px; }
QSlider::handle:horizontal:hover { background: #89b4fa; }
QTextEdit { border: 1px solid #3b4261; background-color: #1a1b26; border-radius: 4px; color: #a9b1d6; }
QScrollBar:vertical { background: transparent; width: 8px; }
QScrollBar::handle:vertical { background: #3b4261; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #565f89; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: transparent; height: 8px; }
QScrollBar::handle:horizontal { background: #3b4261; border-radius: 4px; min-width: 20px; }
QComboBox { background-color: #2f3450; border: 1px solid #3b4261; border-radius: 4px;
    padding: 3px 8px; color: #c0caf5; font-size: 11px; }
QComboBox:hover { border-color: #7aa2f7; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background-color: #24283b; color: #c0caf5;
    selection-background-color: #7aa2f7; border: 1px solid #3b4261; }
QTabWidget::pane { border: 1px solid #3b4261; background-color: #1a1b26; border-radius: 4px; }
QTabBar::tab { background: #1a1b26; color: #a9b1d6; padding: 6px 14px; font-size: 11px;
    border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
QTabBar::tab:selected { background: #24283b; color: #7aa2f7; border-bottom: 2px solid #7aa2f7; }
QStatusBar { background-color: #24283b; border-top: 1px solid #3b4261; color: #a9b1d6; }
QStatusBar QLabel { padding: 0 8px; }
QToolTip { background-color: #24283b; color: #c0caf5; border: 1px solid #7aa2f7;
    padding: 6px 10px; border-radius: 4px; font-size: 11px; }
QFrame[frameShape="6"] { color: #3b4261; }
"""

# ════════════════════════════════════════════════════════════
# IN-MEMORY DATA STORES (Replaces SQLite)
# ════════════════════════════════════════════════════════════
class GameDefinitions:
    """Loads and caches game definition data in-memory."""
    def __init__(self):
        self.terrain_stats = {
            0: {"food": 0.0, "prod": 0.0, "trade": 0.0, "move": 99, "is_water": True},
            1: {"food": 2.0, "prod": 1.0, "trade": 1.0, "move": 1, "is_water": False},
            2: {"food": 1.0, "prod": 2.0, "trade": 0.5, "move": 2, "is_water": False},
            3: {"food": 0.0, "prod": 3.0, "trade": 0.0, "move": 4, "is_water": False},
            4: {"food": 0.0, "prod": 0.5, "trade": 1.0, "move": 2, "is_water": False},
            5: {"food": 1.0, "prod": 0.5, "trade": 0.5, "move": 3, "is_water": False},
            6: {"food": 1.0, "prod": 2.0, "trade": 0.5, "move": 2, "is_water": False},
            7: {"food": 0.5, "prod": 0.0, "trade": 0.0, "move": 2, "is_water": False},
            8: {"food": 1.0, "prod": 0.0, "trade": 2.0, "move": 2, "is_water": True},
            9: {"food": 2.5, "prod": 0.5, "trade": 0.5, "move": 1, "is_water": False},
        }
        self.buildings = [
            {"id": 0, "name": "Granary", "category": "economic", "cost": 10, "min_era_id": 0, "effect": "growth", "bonus": 0.10, "maintenance": 0},
            {"id": 1, "name": "Barracks", "category": "military", "cost": 25, "min_era_id": 0, "effect": "military", "bonus": 0.10, "maintenance": 1},
            {"id": 2, "name": "Library", "category": "tech", "cost": 40, "min_era_id": 0, "effect": "tech", "bonus": 0.15, "maintenance": 1},
            {"id": 3, "name": "Market", "category": "trade", "cost": 30, "min_era_id": 1, "effect": "trade", "bonus": 0.15, "maintenance": 1},
            {"id": 4, "name": "Theater", "category": "culture", "cost": 35, "min_era_id": 1, "effect": "culture", "bonus": 0.20, "maintenance": 1},
            {"id": 5, "name": "Temple", "category": "religion", "cost": 50, "min_era_id": 1, "effect": "culture", "bonus": 0.25, "maintenance": 2},
            {"id": 6, "name": "Walls", "category": "military", "cost": 35, "min_era_id": 0, "effect": "military", "bonus": 0.08, "maintenance": 1},
            {"id": 7, "name": "Harbor", "category": "trade", "cost": 45, "min_era_id": 1, "effect": "trade", "bonus": 0.20, "maintenance": 2},
            {"id": 8, "name": "University", "category": "tech", "cost": 60, "min_era_id": 2, "effect": "tech", "bonus": 0.25, "maintenance": 2},
            {"id": 9, "name": "Cathedral", "category": "culture", "cost": 70, "min_era_id": 2, "effect": "culture", "bonus": 0.30, "maintenance": 3},
        ]
        self.techs = [
            {"id": 0, "name": "Pottery", "era_id": 0, "cost": 5, "category": "economic", "effect": "growth", "bonus": 0.05},
            {"id": 1, "name": "Bronze Working", "era_id": 0, "cost": 12, "category": "military", "effect": "military", "bonus": 0.10},
            {"id": 2, "name": "Writing", "era_id": 0, "cost": 15, "category": "tech", "effect": "tech", "bonus": 0.15},
            {"id": 3, "name": "Masonry", "era_id": 0, "cost": 10, "category": "economic", "effect": "growth", "bonus": 0.08},
            {"id": 4, "name": "Diplomacy", "era_id": 1, "cost": 25, "category": "culture", "effect": "culture", "bonus": 0.20},
            {"id": 5, "name": "Theology", "era_id": 1, "cost": 30, "category": "religion", "effect": "culture", "bonus": 0.25},
            {"id": 6, "name": "Mathematics", "era_id": 1, "cost": 28, "category": "tech", "effect": "tech", "bonus": 0.20},
            {"id": 7, "name": "Feudalism", "era_id": 2, "cost": 45, "category": "culture", "effect": "military", "bonus": 0.15},
            {"id": 8, "name": "Engineering", "era_id": 2, "cost": 50, "category": "tech", "effect": "growth", "bonus": 0.20},
            {"id": 9, "name": "Chivalry", "era_id": 2, "cost": 55, "category": "military", "effect": "military", "bonus": 0.25},
        ]
        self.eras = [
            {"id": 0, "tech_threshold": 0.0, "era_name": "Ancient"},
            {"id": 1, "tech_threshold": 15.0, "era_name": "Classical"},
            {"id": 2, "tech_threshold": 40.0, "era_name": "Medieval"},
            {"id": 3, "tech_threshold": 70.0, "era_name": "Renaissance"},
        ]
        self.buildings_by_name = {b["name"]: b for b in self.buildings}
        self.techs_by_name = {t["name"]: t for t in self.techs}


class AnalyticsStore:
    """In-memory analytics storage for timeline graphs and post-game analysis."""
    def __init__(self):
        self.snapshots: list[dict] = []

    def log_snapshot(self, year, civ_name, pop, tech, mil, terr, score, action):
        self.snapshots.append({
            "year": year, "civ_name": civ_name, "population": pop,
            "technology": tech, "military": mil, "territory": terr,
            "score": score, "action": action
        })

    def commit(self):
        """No-op for compatibility. Data is already in memory."""
        pass

    def get_civ_history(self, civ_name, limit=500):
        hist = [s for s in self.snapshots if s["civ_name"] == civ_name]
        return hist[-limit:] if limit else hist


# ════════════════════════════════════════════════════════════
# AI — D* Lite pathfinding + Utility AI
# ════════════════════════════════════════════════════════════
class DStarLite:
    """Incremental D* Lite pathfinder. terrain_stats_coords maps (x,y) -> dict."""
    def __init__(self, width: int, height: int):
        self.W, self.H = width, height
        self.g: dict[tuple, float] = {}
        self.rhs: dict[tuple, float] = {}
        self.U: list = []
        self.U_set: set = set()
        self.km = 0.0
        self.start = self.goal = None
        self.cost_map: dict[tuple, float] = {}
        self._neighbors_cache: dict[tuple, list[tuple]] = {}
        for y in range(height):
            for x in range(width):
                self._neighbors_cache[(x, y)] = [
                    (nx, ny) for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                    if 0 <= nx < width and 0 <= ny < height]

    def _h(self, a, b) -> float:
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def _key(self, s):
        g = self.g.get(s, float('inf'))
        rhs = self.rhs.get(s, float('inf'))
        return (min(g, rhs) + self._h(self.start, s) + self.km, min(g, rhs))

    def _neighbors(self, s):
        return self._neighbors_cache.get(s, [])

    def init(self, start, goal, terrain_stats_coords: dict) -> None:
        self.start, self.goal = start, goal
        self.g.clear(); self.rhs.clear()
        self.U.clear(); self.U_set.clear()
        self.cost_map.clear(); self.km = 0.0
        inf = float('inf')
        for s in self._neighbors_cache:
            self.g[s] = inf; self.rhs[s] = inf
        for s in self._neighbors_cache:
            t_data = terrain_stats_coords.get(s)
            t_cost = (t_data['move'] if t_data and not t_data['is_water'] else 999) if t_data else 999
            for n in self._neighbors_cache[s]:
                self.cost_map[(s, n)] = t_cost
        self.rhs[self.goal] = 0
        heapq.heappush(self.U, (self._key(self.goal), self.goal))
        self.U_set.add(self.goal)

    def _update_vertex(self, u) -> None:
        if u != self.goal:
            self.rhs[u] = min(
                (self.cost_map.get((u, n), 1) + self.g.get(n, float('inf'))
                 for n in self._neighbors(u)),
                default=float('inf'))
        if u in self.U_set:
            self.U = [(k, n) for k, n in self.U if n != u]
            self.U_set.discard(u)
            heapq.heapify(self.U)
        if self.g.get(u, float('inf')) != self.rhs.get(u, float('inf')):
            heapq.heappush(self.U, (self._key(u), u))
            self.U_set.add(u)

    def compute_shortest_path(self) -> None:
        while self.U and (
                self.U[0][0] < self._key(self.start)
                or self.rhs.get(self.start, float('inf')) != self.g.get(self.start, float('inf'))):
            k_old, u = heapq.heappop(self.U)
            self.U_set.discard(u)
            k_new = self._key(u)
            if k_old < k_new:
                heapq.heappush(self.U, (k_new, u))
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

    def get_path(self, max_len: int = 20) -> list[tuple]:
        path, cur, visited = [], self.start, set()
        while cur != self.goal and len(path) < max_len:
            path.append(cur); visited.add(cur)
            nbrs = self._neighbors(cur)
            if not nbrs: break
            cur = min(nbrs, key=lambda n: self.cost_map.get((cur, n), 1) + self.g.get(n, float('inf')))
            if cur in visited: break
        if cur == self.goal:
            path.append(self.goal)
        return path


class StrategicState(IntEnum):
    EXPANSION = 0; CONSOLIDATION = 1; CRISIS = 2; TOTAL_WAR = 3
    GOLDEN_AGE = 4; RECOVERY = 5; SIEGE = 6


STATE_WEIGHT_MODIFIERS = {
    StrategicState.EXPANSION:     {"expansion":1.4,"military":0.9,"economy":1.1,"tech":0.9,"culture":0.6,"diplomacy":0.7,"trade":0.8,"wonder":0.3},
    StrategicState.CONSOLIDATION: {"expansion":0.5,"military":0.8,"economy":1.5,"tech":1.3,"culture":1.2,"diplomacy":1.0,"trade":1.2,"wonder":0.8},
    StrategicState.CRISIS:        {"expansion":0.3,"military":1.5,"economy":1.0,"tech":0.5,"culture":0.3,"diplomacy":1.3,"trade":0.6,"wonder":0.1},
    StrategicState.TOTAL_WAR:    {"expansion":1.2,"military":2.0,"economy":0.6,"tech":0.7,"culture":0.2,"diplomacy":0.3,"trade":0.2,"wonder":0.1},
    StrategicState.GOLDEN_AGE:    {"expansion":0.7,"military":0.6,"economy":1.2,"tech":1.3,"culture":1.6,"diplomacy":1.1,"trade":1.1,"wonder":1.8},
    StrategicState.RECOVERY:     {"expansion":0.4,"military":0.7,"economy":1.4,"tech":1.0,"culture":0.8,"diplomacy":1.2,"trade":1.0,"wonder":0.4},
    StrategicState.SIEGE:        {"expansion":0.6,"military":1.6,"economy":1.0,"tech":1.1,"culture":0.4,"diplomacy":0.6,"trade":0.4,"wonder":0.1},
}


class ActionType:
    EXPAND="Expand"; DEVELOP="Develop"; RESEARCH="Research"; FORTIFY="Fortify"
    ATTACK="Attack"; CULTURE="Culture"; DIPLOMACY="Diplomacy"; TRADE="Trade"; WONDER="Build Wonder"
    ALL=[EXPAND,DEVELOP,RESEARCH,FORTIFY,ATTACK,CULTURE,DIPLOMACY,TRADE,WONDER]
    WEIGHT_KEY={EXPAND:"expansion",FORTIFY:"military",DEVELOP:"economy",RESEARCH:"tech",
                ATTACK:"military",CULTURE:"culture",DIPLOMACY:"diplomacy",TRADE:"trade",WONDER:"wonder"}


class ResponseCurve:
    @staticmethod
    def linear(x, slope=1.0, intercept=0.0):
        return max(0.0, min(1.0, slope * x + intercept))
    @staticmethod
    def logistic(x, midpoint=0.5, steepness=10.0):
        e = -steepness * (x - midpoint)
        if e > 500:  return 0.0
        if e < -500: return 1.0
        return 1.0 / (1.0 + math.exp(e))
    @staticmethod
    def inverse(x, scale=1.0, offset=0.0):
        if x <= 0.001: return 1.0
        return max(0.0, min(1.0, scale / (x + offset)))
    @staticmethod
    def bell(x, center=0.5, width=0.3):
        d = abs(x - center)
        if d > width * 3: return 0.0
        return max(0.0, min(1.0, math.exp(-(d*d) / (2*width*width))))
    @staticmethod
    def step(x, threshold=0.5, below=0.0, above=1.0):
        return above if x >= threshold else below


class Consideration:
    __slots__ = ('name', 'curve', 'params', 'invert')
    def __init__(self, name: str, curve, invert: bool = False, **params):
        self.name, self.curve, self.params, self.invert = name, curve, params, invert
    def score(self, context: dict) -> float:
        val = self.curve(context.get(self.name, 0.0), **self.params)
        return 1.0 - val if self.invert else val


class UtilityAction:
    __slots__ = ('action_type', 'considerations', 'weight', 'score', 'compensation')
    def __init__(self, action_type: str, considerations, weight: float = 1.0, compensation: float = 0.02):
        self.action_type = action_type
        self.considerations = considerations
        self.weight = weight
        self.compensation = compensation
        self.score = 0.0
    def evaluate(self, context: dict) -> None:
        total = 1.0
        for c in self.considerations:
            total *= c.score(context)
            if total < 0.0001:
                total = 0.0; break
        self.score = (total + self.compensation) * self.weight


class ThreatAssessment:
    @staticmethod
    def assess(our_mil: float, our_tech: float, neighbors: list[dict]) -> dict[str, float]:
        threats = {}
        our_mil = max(1.0, our_mil)
        our_tech = max(1.0, our_tech)
        for n in neighbors:
            n_mil = max(1.0, n.get("military", 100))
            n_tech = max(1.0, n.get("technology", 1))
            mil_threat = min(1.0, (n_mil / our_mil) / 3.0)
            tech_threat = min(1.0, (n_tech / our_tech) / 3.0)
            grievance_threat = min(1.0, n.get("grievance_vs_us", 0) / 100.0)
            war_threat = 1.0 if n.get("at_war") else 0.0
            alliance_mod = 0.2 if n.get("allied") else 1.0
            total = (mil_threat*0.35 + tech_threat*0.15 + grievance_threat*0.20
                     + war_threat*0.25 + 0.1*0.05) * alliance_mod
            threats[n.get("name","")] = max(0.0, min(1.0, total))
        return threats

    @staticmethod
    def highest(threats: dict[str, float]) -> tuple[str, float]:
        if not threats: return ("", 0.0)
        name = max(threats, key=threats.get)
        return (name, threats[name])


class ActionMemory:
    def __init__(self, capacity: int = 20):
        self.history: deque = deque(maxlen=capacity)
        self.outcomes: dict[str, deque] = {}
    def record(self, action_type: str, success: bool = True) -> None:
        self.history.append(action_type)
        if action_type not in self.outcomes:
            self.outcomes[action_type] = deque(maxlen=10)
        self.outcomes[action_type].append(success)
    def get_fatigue(self, action_type: str, window: int = 5) -> float:
        if not self.history: return 0.0
        recent = list(self.history)[-window:]
        if not recent: return 0.0
        return sum(1 for a in recent if a == action_type) / len(recent)
    def get_success_rate(self, action_type: str) -> float:
        if action_type not in self.outcomes or not self.outcomes[action_type]:
            return 0.5
        outs = list(self.outcomes[action_type])
        return sum(1 for o in outs if o) / len(outs)
    def get_novelty(self, action_type: str) -> float:
        if not self.history: return 1.0
        recent = list(self.history)[-20:]
        if not recent: return 1.0
        return 1.0 - (sum(1 for a in recent if a == action_type) / len(recent))


class CivAgent:
    def __init__(self, personality: dict, archetype: str = "survivor"):
        self.personality_weights = {
            "expansion": personality.get("expansion", 1.0),
            "military":  personality.get("military", 1.0),
            "economy":   personality.get("economy", 1.0),
            "tech":      personality.get("tech", 1.0),
            "culture":   personality.get("culture", 1.0),
            "diplomacy": personality.get("diplomacy", 0.8),
            "trade":     personality.get("trade", 0.9),
            "wonder":    personality.get("wonder", 0.4),
        }
        self.archetype = archetype
        self.strategic_state = StrategicState.CONSOLIDATION
        self.memory = ActionMemory()
        self.last_decision_explanation: dict = {}
        self._build_actions()

    def _build_actions(self):
        p = self.personality_weights
        self.actions = [
            UtilityAction(ActionType.EXPAND, [
                Consideration("can_expand", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("pop_pressure", ResponseCurve.logistic, midpoint=0.55, steepness=10),
                Consideration("mil_strength", ResponseCurve.logistic, midpoint=0.05, steepness=12),
                Consideration("territory_ratio", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.35, steepness=8),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["expansion"]),
            UtilityAction(ActionType.FORTIFY, [
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.35, steepness=12),
                Consideration("stability_norm", ResponseCurve.inverse, scale=0.7, offset=0.1),
                Consideration("mil_strength", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.3, above=0.8),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["military"]),
            UtilityAction(ActionType.DEVELOP, [
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.05, steepness=20),
                Consideration("building_ratio", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("pop_pressure", ResponseCurve.linear, slope=-1.2, intercept=0.8),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.4, steepness=6),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["economy"]),
            UtilityAction(ActionType.RESEARCH, [
                Consideration("tech_deficit", ResponseCurve.logistic, midpoint=0.2, steepness=8),
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.05, steepness=20),
                Consideration("tech_level", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["tech"]),
            UtilityAction(ActionType.ATTACK, [
                Consideration("available_attack_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.5, steepness=10),
                Consideration("mil_strength", ResponseCurve.logistic, midpoint=0.45, steepness=8),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.2, above=0.7),
                Consideration("stability_norm", ResponseCurve.linear, slope=1.0, intercept=-0.1),
                Consideration("target_weakness", ResponseCurve.linear, slope=1.5, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["military"]),
            UtilityAction(ActionType.CULTURE, [
                Consideration("treasury", ResponseCurve.linear, slope=1.0, intercept=0.0),
                Consideration("pop_pressure", ResponseCurve.bell, center=0.4, width=0.3),
                Consideration("culture_level", ResponseCurve.inverse, scale=0.4, offset=0.1),
                Consideration("game_phase", ResponseCurve.linear, slope=1.5, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["culture"]),
            UtilityAction(ActionType.DIPLOMACY, [
                Consideration("available_diplomacy_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("threat_level", ResponseCurve.logistic, midpoint=0.55, steepness=8),
                Consideration("alliance_count_norm", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("stability_norm", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.3, above=0.6),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["diplomacy"]),
            UtilityAction(ActionType.TRADE, [
                Consideration("available_trade_targets", ResponseCurve.step, threshold=0.5, below=0.0, above=1.0),
                Consideration("treasury", ResponseCurve.inverse, scale=0.6, offset=0.1),
                Consideration("at_war", ResponseCurve.step, threshold=0.5, below=0.7, above=0.2),
                Consideration("trade_partner_norm", ResponseCurve.inverse, scale=0.5, offset=0.1),
                Consideration("pop_pressure", ResponseCurve.linear, slope=0.8, intercept=0.1),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["trade"]),
            UtilityAction(ActionType.WONDER, [
                Consideration("treasury", ResponseCurve.logistic, midpoint=0.7, steepness=10),
                Consideration("stability_norm", ResponseCurve.logistic, midpoint=0.6, steepness=8),
                Consideration("game_phase", ResponseCurve.linear, slope=2.0, intercept=-0.3),
                Consideration("mil_strength", ResponseCurve.linear, slope=1.0, intercept=-0.2),
                Consideration("action_fatigue", ResponseCurve.inverse, scale=0.8, offset=0.1),
            ], weight=p["wonder"]),
        ]

    def set_archetype(self, new_archetype: str) -> None:
        if new_archetype == self.archetype: return
        self.archetype = new_archetype
        old_state = self.strategic_state
        old_mem = self.memory
        self._build_actions()
        self.strategic_state = old_state
        self.memory = old_mem

    def _build_context(self, raw: dict) -> dict:
        pop = raw["population"]; pop_cap = max(1, raw.get("pop_cap", 1))
        mil = raw["military"]; tre = raw["treasury"]
        tec = raw["technology"]; cul = raw.get("culture", 0)
        sta = raw.get("stability", 50)
        ter = raw.get("territory_count", 1)
        total_land = max(1, raw.get("total_land", 1000))
        return {
            "pop_pressure": min(1.0, pop / max(1, pop_cap)),
            "mil_strength": min(1.0, mil / 5000.0),
            "treasury": min(1.0, tre / 10000.0),
            "tech_deficit": min(1.0, max(0.0, (raw.get("avg_enemy_tech", tec) - tec) / 20.0)),
            "tech_level": min(1.0, tec / 100.0),
            "culture_level": min(1.0, cul / 5000.0),
            "stability_norm": min(1.0, max(0.0, sta / 100.0)),
            "territory_ratio": min(1.0, ter / total_land),
            "building_ratio": min(1.0, raw.get("building_count", 0) / max(1, ter * 2)),
            "threat_level": min(1.0, raw.get("hostile_neighbors", 0) / 5.0),
            "at_war": 1.0 if raw.get("at_war", False) else 0.0,
            "war_count": raw.get("war_count", 0),
            "alliance_count_norm": min(1.0, raw.get("alliance_count", 0) / max(1, raw.get("total_civs", 4) - 1)),
            "trade_partner_norm": min(1.0, raw.get("trade_partner_count", 0) / max(1, raw.get("total_civs", 4) - 1)),
            "max_threat": raw.get("max_threat", 0.0),
            "target_weakness": raw.get("target_weakness", 0.0),
            "game_phase": min(1.0, max(0.0, (raw.get("year", -3000) + 3000) / 3000.0)),
            "action_fatigue": 0.0,
            "can_expand": 1.0 if raw.get("can_expand", True) else 0.0,
            "available_trade_targets": float(raw.get("available_trade_targets", 0)),
            "available_diplomacy_targets": float(raw.get("available_diplomacy_targets", 0)),
            "available_attack_targets": float(raw.get("available_attack_targets", 0)),
        }

    def _evaluate_state(self, ctx: dict) -> StrategicState:
        stab = ctx.get("stability_norm", 0.5)
        at_war = ctx.get("at_war", False)
        war_count = ctx.get("war_count", 0)
        tre = ctx.get("treasury", 0.0)
        mil = ctx.get("mil_strength", 0.0)
        tr = ctx.get("territory_ratio", 0.0)
        pp = ctx.get("pop_pressure", 0.0)
        threat = ctx.get("max_threat", 0.0)
        can_attack = at_war and mil > 0.3 and threat < 0.85
        if stab < 0.2 and (war_count > 0 or tre < 0.1): return StrategicState.CRISIS
        if at_war and can_attack: return StrategicState.TOTAL_WAR
        if at_war and not can_attack: return StrategicState.SIEGE
        if war_count >= 2 and mil < 0.25: return StrategicState.CRISIS
        if 0.2 <= stab < 0.35 and not at_war: return StrategicState.RECOVERY
        if stab > 0.75 and tre > 0.5 and not at_war and mil > 0.3: return StrategicState.GOLDEN_AGE
        if pp > 0.5 and stab > 0.4 and tr < 0.3: return StrategicState.EXPANSION
        return StrategicState.CONSOLIDATION

    def decide(self, raw: dict) -> str:
        ctx = self._build_context(raw)
        self.strategic_state = self._evaluate_state(ctx)
        mods = STATE_WEIGHT_MODIFIERS.get(self.strategic_state, {})
        best, best_score = ActionType.FORTIFY, -1.0
        for a in self.actions:
            wkey = ActionType.WEIGHT_KEY.get(a.action_type, "")
            base = self.personality_weights.get(wkey, 1.0)
            smod = mods.get(wkey, 1.0)
            fat = self.memory.get_fatigue(a.action_type, 5)
            ctx["action_fatigue"] = fat
            succ = self.memory.get_success_rate(a.action_type)
            succ_mod = 0.2 + 0.8 * succ
            novelty = self.memory.get_novelty(a.action_type)
            expl = 1.0 + (0.0 if self.strategic_state in (StrategicState.CRISIS, StrategicState.TOTAL_WAR, StrategicState.SIEGE) else 0.25 * novelty)
            a.weight = base * smod * succ_mod * expl
            a.evaluate(ctx)
            if a.score > best_score:
                best_score = a.score; best = a.action_type
        self.memory.record(best, True)
        self.last_decision_explanation = {
            "action": best, "state": self.strategic_state.name, "score": best_score,
        }
        return best

    def record_outcome(self, action_type: str, success: bool) -> None:
        if self.memory.history and self.memory.history[-1] == action_type:
            if action_type in self.memory.outcomes and self.memory.outcomes[action_type]:
                self.memory.outcomes[action_type][-1] = success

    @property
    def state_name(self) -> str: return self.strategic_state.name
    @property
    def plan_name(self) -> Optional[str]: return None


# ════════════════════════════════════════════════════════════
# MODELS
# ════════════════════════════════════════════════════════════
class Leader:
    def __init__(self, name: str, title: str, epithet: str, archetype: str, government: str):
        self.name = name; self.title = title; self.epithet = epithet
        self.archetype = archetype; self.government = government
        self.tenure = 0
        self.accomplishments: list[str] = []

    @property
    def full_name(self) -> str:
        parts = [self.title, self.name]
        if self.epithet: parts.append(self.epithet)
        return " ".join(parts)

    @property
    def short_name(self) -> str:
        parts = [self.name]
        if self.epithet: parts.append(self.epithet)
        return " ".join(parts)

    @classmethod
    def generate(cls, government: str, archetype: Optional[str] = None) -> "Leader":
        first = random.choice(LEADER_FIRST_NAMES)
        title = random.choice(LEADER_TITLES.get(government, ["Leader"]))
        epithet = ""
        if government in ("monarchy", "chiefdom") or random.random() < 0.6:
            epithet = random.choice(LEADER_EPITHETS)
        if archetype is None:
            archetype = cls._pick_archetype_for_government(government)
        return cls(first, title, epithet, archetype, government)

    @staticmethod
    def _pick_archetype_for_government(government: str) -> str:
        weights = {
            "chiefdom":    {"warlord":3,"raider":2,"survivor":2,"builder":1},
            "monarchy":    {"warlord":2,"builder":2,"philosopher":1,"diplomat":1,"survivor":1},
            "republic":    {"diplomat":3,"philosopher":2,"merchant":2,"builder":1},
            "theocracy":   {"zealot":4,"builder":1,"diplomat":1},
            "dictatorship":{"warlord":3,"raider":2,"merchant":1,"survivor":1},
            "oligarchy":   {"merchant":4,"builder":2,"diplomat":1,"philosopher":1},
            "democracy":   {"diplomat":3,"philosopher":3,"merchant":1,"builder":1},
        }.get(government, {"survivor":1})
        return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]

    def to_dict(self) -> dict:
        return {"name":self.name, "title":self.title, "epithet":self.epithet,
                "archetype":self.archetype, "government":self.government,
                "tenure":self.tenure, "accomplishments":self.accomplishments}

    @classmethod
    def from_dict(cls, d: dict) -> "Leader":
        l = cls(d["name"], d["title"], d.get("epithet",""), d["archetype"], d["government"])
        l.tenure = d.get("tenure", 0)
        l.accomplishments = d.get("accomplishments", [])
        return l


class WorldEvent:
    def __init__(self, name: str, desc: str, effect_fn: Callable, duration: int,
                 visual_color: str, target_civ: str, position: Optional[tuple] = None,
                 event_type: str = "default"):
        self.name = name; self.desc = desc; self.effect_fn = effect_fn
        self.duration = duration; self.remaining = duration
        self.visual_color = visual_color; self.target_civ = target_civ
        self.position = position
        self.event_type = event_type


class Civ:
    def __init__(self, name: str, color: str, x: int, y: int,
                 personality: Optional[dict] = None, archetype: str = "survivor",
                 government: str = "chiefdom"):
        self.name = name; self.color = color
        self.capital: tuple[int, int] = (x, y)
        self.territory: set[tuple[int, int]] = {(x, y)}
        self._base_archetype = archetype
        self.population = 1000.0; self.military = 100.0
        self.technology = 1.0; self.treasury = 500.0
        self.culture = 10.0; self.stability = 100.0
        self.score = 0.0; self.pop_cap = 1000.0
        self.last_action = "None"
        self.buildings: list[dict] = []
        self.wonders: list[str] = []
        self.techs_researched: list[str] = []
        self.grievances: dict[str, float] = {}
        self.at_war_with: set[str] = set()
        self.alliances: set[str] = set()
        self.trade_partners: set[str] = set()
        self.religion: Optional[str] = None
        self.era_id = 0; self.era_name = "Ancient"
        self.government = government
        self.gov_tenure = 0
        self.leader: Optional[Leader] = None
        self.previous_leaders: list[Leader] = []
        self.leader_history_count = 0
        if personality is None:
            personality = {}
        self.agent = CivAgent(personality, archetype)

    @property
    def archetype(self) -> str:
        return self.leader.archetype if self.leader and self.leader.archetype else self._base_archetype

    @property
    def archetype_label(self) -> str:
        return PERSONALITY_ARCHETYPES.get(self.archetype, {}).get("label", self.archetype.title())

    @property
    def strategic_state_name(self) -> str: return self.agent.state_name
    @property
    def plan_name(self) -> Optional[str]: return self.agent.plan_name
    @property
    def government_label(self) -> str:
        return GOVERNMENTS.get(self.government, {}).get("label", self.government.title())
    @property
    def leader_name(self) -> str: return self.leader.full_name if self.leader else "No Leader"
    @property
    def leader_short_name(self) -> str: return self.leader.short_name if self.leader else "?"

    @classmethod
    def from_template(cls, template: dict, x: int, y: int) -> "Civ":
        return cls(template["name"], template["color"], x, y,
                   PERSONALITY_ARCHETYPES.get(template.get("archetype","survivor"), {}).get("weights", {}),
                   template.get("archetype","survivor"),
                   template.get("government","chiefdom"))

    def to_dict(self) -> dict:
        return {
            "name":self.name, "color":self.color,
            "capital":list(self.capital),
            "territory":[list(t) for t in self.territory],
            "population":self.population, "military":self.military,
            "technology":self.technology, "treasury":self.treasury,
            "culture":self.culture, "stability":self.stability,
            "score":self.score, "pop_cap":self.pop_cap,
            "last_action":self.last_action,
            "buildings":self.buildings, "wonders":self.wonders,
            "techs_researched":self.techs_researched, "grievances":self.grievances,
            "at_war_with":list(self.at_war_with),
            "alliances":list(self.alliances),
            "trade_partners":list(self.trade_partners),
            "religion":self.religion, "era_id":self.era_id, "era_name":self.era_name,
            "personality":self.agent.personality_weights,
            "archetype":self._base_archetype,
            "government":self.government, "gov_tenure":self.gov_tenure,
            "leader":self.leader.to_dict() if self.leader else None,
            "previous_leaders":[l.to_dict() for l in self.previous_leaders[-5:]],
            "leader_history_count":self.leader_history_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Civ":
        cap = d["capital"]
        civ = cls(d["name"], d["color"], cap[0], cap[1],
                  d.get("personality", {}), d.get("archetype","survivor"),
                  d.get("government","chiefdom"))
        civ.territory = {tuple(t) for t in d["territory"]}
        for k in ["population","military","technology","treasury","culture","stability",
                  "score","pop_cap","last_action"]:
            setattr(civ, k, d.get(k, 0))
        civ.buildings = d.get("buildings", [])
        civ.wonders = d.get("wonders", [])
        civ.techs_researched = d.get("techs_researched", [])
        civ.grievances = d.get("grievances", {})
        civ.at_war_with = set(d.get("at_war_with", []))
        civ.alliances = set(d.get("alliances", []))
        civ.trade_partners = set(d.get("trade_partners", []))
        civ.religion = d.get("religion")
        civ.era_id = d.get("era_id", 0)
        civ.era_name = d.get("era_name", "Ancient")
        civ.gov_tenure = d.get("gov_tenure", 0)
        civ.leader_history_count = d.get("leader_history_count", 0)
        if d.get("leader"):
            civ.leader = Leader.from_dict(d["leader"])
        civ.previous_leaders = [Leader.from_dict(l) for l in d.get("previous_leaders", [])]
        return civ


# ════════════════════════════════════════════════════════════
# MAP GENERATOR
# ════════════════════════════════════════════════════════════
class MapGenerator:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H

    def generate(self, preset: str) -> dict[tuple, int]:
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

    def _empty_ocean(self) -> dict[tuple, int]:
        return {(x, y): Terrain.OCEAN for y in range(self.H) for x in range(self.W)}

    def _in_bounds(self, x, y) -> bool:
        return 0 <= x < self.W and 0 <= y < self.H

    def _set_circle(self, tmap, cx, cy, radius, tid, falloff=True):
        ri = int(radius) + 2
        cx_i, cy_i = int(cx), int(cy)
        for dy in range(-ri, ri + 1):
            y = cy_i + dy
            if y < 0 or y >= self.H: continue
            for dx in range(-ri, ri + 1):
                x = cx_i + dx
                if x < 0 or x >= self.W: continue
                dist = math.sqrt(dx*dx + dy*dy)
                if falloff:
                    if dist < radius * 0.7: tmap[(x, y)] = tid
                    elif dist < radius and random.random() < (radius - dist) / (radius * 0.3):
                        tmap[(x, y)] = tid
                else:
                    if dist < radius: tmap[(x, y)] = tid

    def _set_ellipse(self, tmap, cx, cy, rx, ry, tid):
        cx_i, cy_i = int(cx), int(cy)
        rx_safe = max(rx, 0.1); ry_safe = max(ry, 0.1)
        for dy in range(-int(ry)-2, int(ry)+3):
            y = cy_i + dy
            if y < 0 or y >= self.H: continue
            for dx in range(-int(rx)-2, int(rx)+3):
                x = cx_i + dx
                if x < 0 or x >= self.W: continue
                d = math.sqrt((dx/rx_safe)**2 + (dy/ry_safe)**2)
                if d < 0.7: tmap[(x, y)] = tid
                elif d < 1.0 and random.random() < (1.0 - d) / 0.3: tmap[(x, y)] = tid

    def _add_coast(self, tmap):
        coast = set()
        W, H = self.W, self.H
        for y in range(H):
            for x in range(W):
                if tmap[(x, y)] == Terrain.OCEAN:
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < W and 0 <= ny < H and tmap.get((nx, ny)) != Terrain.OCEAN:
                            coast.add((x, y)); break
        for x, y in coast: tmap[(x, y)] = Terrain.COAST

    def _assign_biomes(self, tmap, style="mixed"):
        for y in range(self.H):
            for x in range(self.W):
                if tmap[(x, y)] not in (Terrain.OCEAN, Terrain.COAST):
                    tmap[(x, y)] = self._pick_biome(x, y, style)

    def _pick_biome(self, x, y, style):
        lat = y / self.H
        r = random.random()
        if style == "highlands":
            if r < 0.25: return Terrain.MOUNTAIN
            if r < 0.50: return Terrain.HILLS
            if r < 0.70: return Terrain.FOREST
            if r < 0.85: return Terrain.PLAINS
            return Terrain.GRASSLAND
        if lat < 0.12 or lat > 0.88:
            if r < 0.50: return Terrain.TUNDRA
            if r < 0.75: return Terrain.HILLS
            return Terrain.MOUNTAIN
        if lat < 0.25 or lat > 0.75:
            if r < 0.25: return Terrain.FOREST
            if r < 0.45: return Terrain.PLAINS
            if r < 0.60: return Terrain.GRASSLAND
            if r < 0.75: return Terrain.HILLS
            if r < 0.88: return Terrain.DESERT
            return Terrain.MOUNTAIN
        if r < 0.20: return Terrain.JUNGLE
        if r < 0.40: return Terrain.FOREST
        if r < 0.55: return Terrain.GRASSLAND
        if r < 0.70: return Terrain.PLAINS
        if r < 0.82: return Terrain.DESERT
        if r < 0.92: return Terrain.HILLS
        return Terrain.MOUNTAIN

    def _add_rivers(self, tmap, count=3):
        for _ in range(count):
            cand = [(x, y) for y in range(self.H) for x in range(self.W)
                    if tmap[(x, y)] in (Terrain.MOUNTAIN, Terrain.HILLS)]
            if not cand: continue
            sx, sy = random.choice(cand)
            for _ in range(60):
                tmap[(sx, sy)] = Terrain.COAST
                nbrs = [(nx, ny) for nx, ny in [(sx+1,sy),(sx-1,sy),(sx,sy+1),(sx,sy-1)]
                        if self._in_bounds(nx, ny)]
                if not nbrs: break
                water = [n for n in nbrs if tmap[n] in (Terrain.OCEAN, Terrain.COAST)]
                if water: break
                order = {Terrain.MOUNTAIN:9, Terrain.HILLS:6, Terrain.TUNDRA:5,
                         Terrain.FOREST:4, Terrain.JUNGLE:4, Terrain.GRASSLAND:3,
                         Terrain.PLAINS:3, Terrain.DESERT:3, Terrain.COAST:1, Terrain.OCEAN:0}
                sx, sy = min(nbrs, key=lambda n: order.get(tmap[n], 3))

    def _gen_continent(self):
        tmap = self._empty_ocean()
        n = random.randint(2, 3)
        for i in range(n):
            cx = self.W * 0.2 + (self.W * 0.6) * ((i + 0.5) / n) + random.uniform(-5, 5)
            cy = self.H * 0.5 + random.uniform(-self.H * 0.2, self.H * 0.2)
            self._set_ellipse(tmap, cx, cy, random.uniform(self.W * 0.18, self.W * 0.28),
                              random.uniform(self.H * 0.25, self.H * 0.40), Terrain.GRASSLAND)
            for _ in range(random.randint(2, 5)):
                self._set_circle(tmap, cx + random.uniform(-15, 15), cy + random.uniform(-10, 10),
                                 random.uniform(5, 12), Terrain.PLAINS)
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed"); self._add_rivers(tmap, random.randint(2, 4))
        return tmap

    def _gen_archipelago(self):
        tmap = self._empty_ocean()
        for _ in range(random.randint(8, 15)):
            cx = random.uniform(self.W * 0.1, self.W * 0.9)
            cy = random.uniform(self.H * 0.1, self.H * 0.9)
            self._set_circle(tmap, cx, cy, random.uniform(4, 10), Terrain.GRASSLAND)
            for _ in range(random.randint(1, 3)):
                self._set_circle(tmap, cx + random.uniform(-8, 8), cy + random.uniform(-8, 8),
                                 random.uniform(2, 5), Terrain.PLAINS)
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed"); self._add_rivers(tmap, random.randint(1, 2))
        return tmap

    def _gen_pangaea(self):
        tmap = self._empty_ocean()
        cx, cy = self.W * 0.5, self.H * 0.5
        self._set_ellipse(tmap, cx, cy, self.W * 0.38, self.H * 0.38, Terrain.GRASSLAND)
        for _ in range(random.randint(6, 12)):
            ang = random.uniform(0, 2 * math.pi)
            d = random.uniform(0.5, 0.9)
            self._set_circle(tmap, cx + math.cos(ang) * self.W * 0.38 * d,
                             cy + math.sin(ang) * self.H * 0.38 * d,
                             random.uniform(5, 15), Terrain.PLAINS)
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed"); self._add_rivers(tmap, random.randint(3, 6))
        return tmap

    def _gen_islands(self):
        tmap = self._empty_ocean()
        for _ in range(random.randint(20, 35)):
            self._set_circle(tmap, random.uniform(self.W * 0.05, self.W * 0.95),
                             random.uniform(self.H * 0.05, self.H * 0.95),
                             random.uniform(2, 6), Terrain.PLAINS)
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed")
        return tmap

    def _gen_highlands(self):
        tmap = {(x, y): Terrain.HILLS for y in range(self.H) for x in range(self.W)}
        for _ in range(random.randint(3, 6)):
            ang = random.uniform(0, math.pi); off = random.uniform(0, self.W)
            for y in range(self.H):
                for x in range(self.W):
                    d = abs((x - off) * math.cos(ang) + (y - self.H/2) * math.sin(ang))
                    if d < 4 and random.random() < 0.7: tmap[(x, y)] = Terrain.MOUNTAIN
                    elif d < 8 and random.random() < 0.3: tmap[(x, y)] = Terrain.MOUNTAIN
        for _ in range(random.randint(2, 5)):
            self._set_circle(tmap, random.randint(0, self.W-1), random.randint(0, self.H-1),
                             random.uniform(3, 6), Terrain.OCEAN, falloff=False)
        self._add_coast(tmap); self._assign_biomes(tmap, "highlands"); self._add_rivers(tmap, random.randint(1, 3))
        return tmap

    def _gen_river_valley(self):
        tmap = self._empty_ocean()
        bw = max(5, self.W // 6)
        for y in range(self.H):
            for x in range(self.W):
                if x < bw or x > self.W - bw: tmap[(x, y)] = Terrain.MOUNTAIN
                elif x < bw + 4 or x > self.W - bw - 4: tmap[(x, y)] = Terrain.HILLS
                else: tmap[(x, y)] = Terrain.PLAINS
        rx = self.W // 2
        for y in range(self.H):
            rx += random.randint(-1, 1)
            rx = max(bw + 5, min(self.W - bw - 5, rx))
            for dx in range(-1, 2):
                if self._in_bounds(rx + dx, y): tmap[(rx + dx, y)] = Terrain.COAST
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed")
        return tmap

    def _gen_crater(self):
        tmap = self._empty_ocean()
        cx, cy = self.W / 2, self.H / 2
        outer = min(self.W, self.H) * 0.42
        inner = outer * 0.35
        for y in range(self.H):
            for x in range(self.W):
                d = math.sqrt((x - cx)**2 + (y - cy)**2)
                if inner < d < outer:
                    if d < inner + (outer - inner) * 0.2: tmap[(x, y)] = Terrain.MOUNTAIN
                    elif d > outer - (outer - inner) * 0.15: tmap[(x, y)] = Terrain.HILLS
                    else: tmap[(x, y)] = Terrain.PLAINS
                if d < inner * 0.9: tmap[(x, y)] = Terrain.OCEAN
                elif d < inner: tmap[(x, y)] = Terrain.COAST
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed"); self._add_rivers(tmap, random.randint(1, 2))
        return tmap

    def _gen_mediterranean(self):
        tmap = self._empty_ocean()
        self._set_ellipse(tmap, self.W * 0.5, self.H * 0.5, self.W * 0.3, self.H * 0.25, Terrain.OCEAN)
        for y in range(self.H):
            for x in range(self.W):
                dx = abs(x - self.W / 2) / (self.W / 2)
                dy = abs(y - self.H / 2) / (self.H / 2)
                if dx > 0.6 or dy > 0.6:
                    if tmap[(x, y)] == Terrain.OCEAN: tmap[(x, y)] = Terrain.GRASSLAND
        for _ in range(random.randint(2, 4)):
            ang = random.uniform(0, 2 * math.pi)
            self._set_circle(tmap, self.W / 2 + math.cos(ang) * self.W * 0.3 * 0.7 + math.cos(ang) * 15,
                             self.H / 2 + math.sin(ang) * self.H * 0.25 * 0.7 + math.sin(ang) * 15,
                             random.uniform(5, 10), Terrain.PLAINS)
        for _ in range(random.randint(2, 5)):
            self._set_circle(tmap, self.W * 0.5 + random.uniform(-self.W * 0.15, self.W * 0.15),
                             self.H * 0.5 + random.uniform(-self.H * 0.12, self.H * 0.12),
                             random.uniform(2, 4), Terrain.PLAINS)
        self._add_coast(tmap); self._assign_biomes(tmap, "mixed"); self._add_rivers(tmap, random.randint(2, 3))
        return tmap


# ════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ════════════════════════════════════════════════════════════
class SimulationEngine(QThread):
    update_signal = Signal(dict)
    log_signal = Signal(str)
    notification_signal = Signal(str, str)

    def __init__(self, map_width: int = DEFAULT_MAP_WIDTH, map_height: int = DEFAULT_MAP_HEIGHT,
                 civ_count: int = 4, terrain_preset: str = TerrainPreset.CONTINENT):
        super().__init__()
        self.running = False
        self.paused = False
        self.speed = 150
        self.year = -3000
        self.generation = 0
        self.W, self.H = map_width, map_height
        self.civ_count = civ_count
        self.terrain_preset = terrain_preset
        self.defs = GameDefinitions()
        self.analytics = AnalyticsStore()
        self.terrain_map: dict[tuple, int] = {}
        self.owner_map: dict[tuple, Optional[str]] = {}
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
        self._civ_by_name: dict[str, Civ] = {}
        self._civ_archetype: dict[str, dict] = {}
        self._is_water_cache: dict[int, bool] = {int(t): s['is_water'] for t, s in self.defs.terrain_stats.items()}
        self._terrain_stats_by_id: dict[int, dict] = {int(t): s for t, s in self.defs.terrain_stats.items()}
        self._terrain_stats_coords: dict[tuple, dict] = {}
        self._wonders_by_name = {w['name']: w for w in WONDERS}
        self._religions_by_name = {r['name']: r for r in RELIGIONS}
        self._generate_world()

    # ── World generation ──────────────────────────────────────
    def _generate_world(self) -> None:
        self.terrain_map = MapGenerator(self.W, self.H).generate(self.terrain_preset)
        self._terrain_stats_coords = {(x, y): self._terrain_stats_by_id.get(tid)
                                      for (x, y), tid in self.terrain_map.items()}
        self.owner_map = {}
        self.resource_map = {}
        self.total_land_tiles = 0
        is_water = self._is_water_cache
        tmap = self.terrain_map
        for y in range(self.H):
            for x in range(self.W):
                self.owner_map[(x, y)] = None
                tid = tmap[(x, y)]
                if not is_water.get(tid, True):
                    self.total_land_tiles += 1
                    if random.random() < 0.04:
                        if tid == Terrain.HILLS:    self.resource_map[(x, y)] = random.choice(["iron", "stone"])
                        elif tid == Terrain.MOUNTAIN: self.resource_map[(x, y)] = random.choice(["iron", "gold_ore", "stone"])
                        elif tid in (Terrain.PLAINS, Terrain.GRASSLAND):
                            self.resource_map[(x, y)] = random.choice(["wheat", "horses"])
                        elif tid == Terrain.FOREST: self.resource_map[(x, y)] = random.choice(["wheat", "stone"])
                        else: self.resource_map[(x, y)] = random.choice(list(RESOURCE_TYPES.keys()))
                elif tid == Terrain.COAST and random.random() < 0.06:
                    self.resource_map[(x, y)] = "fish"
        self._place_civilizations(CIV_TEMPLATES[:self.civ_count])

    def _place_civilizations(self, templates: list[dict]) -> None:
        placed = []
        min_d = max(10, min(self.W, self.H) // 5)
        for template in templates:
            best, best_score = None, -1
            for _ in range(2000):
                x = random.randint(0, self.W - 1)
                y = random.randint(0, self.H - 1)
                if self._is_water_cache.get(self.terrain_map[(x, y)], True): continue
                if self.owner_map[(x, y)] is not None: continue
                tid = self.terrain_map[(x, y)]
                tscore = {Terrain.PLAINS:10, Terrain.GRASSLAND:10, Terrain.FOREST:7,
                          Terrain.HILLS:5, Terrain.JUNGLE:4, Terrain.DESERT:2,
                          Terrain.TUNDRA:2, Terrain.MOUNTAIN:1}.get(tid, 3)
                if placed:
                    d = min(abs(x-px)+abs(y-py) for px, py in placed)
                    dscore = min(d / min_d, 2.0)
                else: dscore = 2.0
                coast_bonus = 3 if any(self.terrain_map.get((x+dx, y+dy)) in (Terrain.COAST, Terrain.OCEAN)
                                       for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]
                                       if 0 <= x+dx < self.W and 0 <= y+dy < self.H) else 0
                total = tscore + dscore * 5 + coast_bonus
                if total > best_score: best_score, best = total, (x, y)
            if best:
                civ = Civ.from_template(template, best[0], best[1])
                self.civs.append(civ)
                self.owner_map[best] = civ.name
                placed.append(best)
                self._civ_by_name[civ.name] = civ
                arch = PERSONALITY_ARCHETYPES.get(template.get("archetype", "survivor"), {})
                self._civ_archetype[civ.name] = arch
                civ.government = template.get("government", "chiefdom")
                civ.leader = Leader.generate(civ.government, template.get("archetype", "survivor"))
                civ.leader_history_count = 1
                for stat, bonus in arch.get("starting_bonus", {}).items():
                    setattr(civ, stat, getattr(civ, stat, 0) + bonus)

    def _in_bounds(self, x, y) -> bool:
        return 0 <= x < self.W and 0 <= y < self.H

    # ── Main loop ─────────────────────────────────────────────
    def run(self) -> None:
        self.running = True
        while self.running:
            if not self.finished and not self.paused:
                self.process_turn()
            self.msleep(self.speed)

    def _get_ranks(self) -> dict[str, int]:
        sc = sorted(self.civs, key=lambda c: c.score, reverse=True)
        return {c.name: i + 1 for i, c in enumerate(sc)}

    def process_turn(self) -> None:
        if self.max_years > 0 and self.year - (-3000) >= self.max_years:
            self.finished = True
            self.log_signal.emit(f"SIMULATION COMPLETE at Year {self.year}")
            self._end_game()
            return

        self.year += 1
        self.generation += 1
        self.last_path = []
        self.turn_events_log = []
        self.season_timer += 1
        if self.season_timer >= SEASON_LENGTH:
            self.season = (self.season + 1) % 4
            self.season_timer = 0
        food_mult = FOOD_MULTIPLIERS[self.season]

        for civ in self.civs:
            self._process_economy(civ, food_mult)
            self._process_diplomacy(civ)
            self._process_leadership(civ)

        self._process_tech_diffusion()
        self._process_border_friction()
        self._process_events()

        for civ in self.civs:
            if civ.territory:
                self._process_civ_turn(civ)
            civ.score = (civ.population * 0.1 + civ.technology * 10
                         + len(civ.territory) * 50 + len(civ.buildings) * 100 + civ.culture)
            self.analytics.log_snapshot(self.year, civ.name, civ.population, civ.technology,
                                        civ.military, len(civ.territory), civ.score, civ.last_action)
            old_era = civ.era_name
            for era in self.defs.eras[::-1]:
                if civ.technology >= era['tech_threshold'] and civ.era_id < era['id']:
                    civ.era_id = era['id']
                    civ.era_name = era['era_name']
                    break
            if civ.era_name != old_era:
                self.log_signal.emit(f"{self.year}: {civ.name} entered the {civ.era_name} Era!")
                self.turn_events_log.append(f"{civ.name} entered the {civ.era_name} Era!")
                self.notification_signal.emit("Era Advance", f"{civ.name} entered the {civ.era_name} Era!")

        self._update_explored_incremental()
        self.update_signal.emit(self._build_data())

        if self.generation % AUTO_SAVE_INTERVAL == 0:
            self._auto_save()

    def _update_explored_incremental(self) -> None:
        W, H = self.W, self.H
        exp = self.explored
        add = exp.add
        for civ in self.civs:
            for x, y in civ.territory:
                for dx in range(-3, 4):
                    nx = x + dx
                    if nx < 0 or nx >= W: continue
                    for dy in range(-3, 4):
                        ny = y + dy
                        if ny < 0 or ny >= H: continue
                        add((nx, ny))
        if self.generation % 100 == 0:
            self._rebuild_explored()

    def _rebuild_explored(self) -> None:
        W, H = self.W, self.H
        new_exp = set()
        for civ in self.civs:
            for x, y in civ.territory:
                for dx in range(-3, 4):
                    nx = x + dx
                    if nx < 0 or nx >= W: continue
                    for dy in range(-3, 4):
                        ny = y + dy
                        if ny < 0 or ny >= H: continue
                        new_exp.add((nx, ny))
        self.explored = new_exp

    # ── Economy ───────────────────────────────────────────────
    def _process_economy(self, civ: Civ, food_mult: float) -> None:
        civ.pop_cap = len(civ.territory) * 100.0 + sum(b['bonus'] * 500 for b in civ.buildings if b['effect'] == 'growth') + sum(w['bonus'] * 1000 for w in WONDERS if w['name'] in civ.wonders and w['effect'] == 'growth')
        govt = GOVERNMENTS.get(civ.government, {})
        gold_mod = govt.get("gold_mod", 1.0)
        sci_mod = govt.get("science_mod", 1.0)
        mil_mod = govt.get("military_mod", 1.0)
        cult_mod = govt.get("culture_mod", 1.0)
        tmap = self.terrain_map
        tstats = self._terrain_stats_by_id
        rmap = self.resource_map
        for x, y in civ.territory:
            s = tstats.get(tmap[(x, y)])
            if not s: continue
            gf = min(1.0, civ.pop_cap / max(1.0, civ.population)) if civ.population > civ.pop_cap else 1.0
            civ.population += s['food'] * 5 * food_mult * gf
            civ.treasury += s['trade'] * 5 * gold_mod
            res = rmap.get((x, y))
            if res:
                if res == "iron":      civ.military += 2 * mil_mod
                elif res == "wheat":   civ.population += 5 * food_mult * gf
                elif res == "gold_ore":civ.treasury += 8 * gold_mod
                elif res == "horses":  civ.military += 1 * mil_mod
                elif res == "stone":   civ.treasury += 3 * gold_mod
                elif res == "fish":    civ.population += 3 * food_mult * gf
        for b in civ.buildings:
            eff = b['effect']; bon = b['bonus']
            if eff == 'growth':    civ.population += bon * 100 * food_mult
            elif eff == 'trade':   civ.treasury += bon * 50 * gold_mod
            elif eff == 'tech':    civ.technology += bon * 0.5 * sci_mod
            elif eff == 'military':civ.military += bon * 10 * mil_mod
            elif eff == 'culture':civ.culture += bon * 20 * cult_mod
        for wn in civ.wonders:
            w = self._wonders_by_name.get(wn)
            if not w: continue
            eff = w['effect']; bon = w['bonus']
            if eff == 'growth':    civ.population += bon * 50
            elif eff == 'trade':   civ.treasury += bon * 25
            elif eff == 'military':civ.military += bon * 5
            elif eff == 'tech':    civ.technology += bon * 0.2
            elif eff == 'culture':civ.culture += bon * 30
        if civ.religion:
            r = self._religions_by_name.get(civ.religion)
            if r:
                bt = r['bonus_type']; bv = r['bonus_val']
                if bt == 'growth':    civ.population += civ.culture * bv
                elif bt == 'military':civ.military += civ.culture * bv
                elif bt == 'culture':civ.culture += civ.population * bv * 0.1
                elif bt == 'trade':   civ.treasury += civ.population * bv * 0.1
        civ.culture += civ.population / 500.0
        stab_norm = max(0.0, min(1.0, civ.stability / 100.0))
        bm = 1.0 - STABILITY_BIRTH_MULT * (1.0 - stab_norm)
        dm = 1.0 + STABILITY_DEATH_MULT * (1.0 - stab_norm)
        civ.population = max(1.0, civ.population + civ.population * BIRTH_RATE * bm - civ.population * DEATH_RATE * dm)
        if civ.population > civ.pop_cap * FAMINE_THRESHOLD:
            over = (civ.population / max(1.0, civ.pop_cap)) - 1.0
            deaths = civ.population * FAMINE_DEATH_RATE * over
            civ.population = max(1.0, civ.population - deaths)
            civ.stability -= 0.5 * over
            if over > 0.15 and random.random() < 0.3:
                self.turn_events_log.append(f"{civ.name} suffers famine! (-{int(deaths)} pop)")
        civ.treasury -= civ.military * 0.02
        if civ.treasury < 0:
            desert = int(abs(civ.treasury) / 10)
            civ.military = max(10, civ.military - desert)
            civ.stability -= 1.0
            if desert > 0:
                self.turn_events_log.append(f"{civ.name} troops deserting! (-{desert})")
        hard_cap = civ.pop_cap * POP_HARD_CAP_MULT
        if civ.population > hard_cap:
            civ.population = hard_cap

    # ── Cross-civ dynamics ───────────────────────────────────
    def _process_tech_diffusion(self) -> None:
        if len(self.civs) < 2: return
        pairs = set()
        om = self.owner_map
        for civ in self.civs:
            cn = civ.name
            for x, y in civ.territory:
                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    no = om.get((nx, ny))
                    if no and no != cn:
                        pairs.add(tuple(sorted((cn, no))))
        for a, b in pairs:
            ca = self._civ_by_name.get(a); cb = self._civ_by_name.get(b)
            if not ca or not cb: continue
            if ca.technology > cb.technology + TECH_DIFFUSION_MIN_GAP:
                gain = TECH_DIFFUSION_RATE * (ca.technology - cb.technology)
                cb.technology += gain; cb.culture += gain * 5.0
            elif cb.technology > ca.technology + TECH_DIFFUSION_MIN_GAP:
                gain = TECH_DIFFUSION_RATE * (cb.technology - ca.technology)
                ca.technology += gain; ca.culture += gain * 5.0

    def _process_border_friction(self) -> None:
        if len(self.civs) < 2: return
        pairs = set()
        om = self.owner_map
        for civ in self.civs:
            cn = civ.name
            for x, y in civ.territory:
                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    no = om.get((nx, ny))
                    if no and no != cn:
                        pairs.add(tuple(sorted((cn, no))))
        for a, b in pairs:
            ca = self._civ_by_name.get(a); cb = self._civ_by_name.get(b)
            if not ca or not cb: continue
            if a in cb.at_war_with: continue
            if a in cb.alliances: continue
            fric = BORDER_FRICTION_BASE
            if ca.religion and cb.religion and ca.religion != cb.religion:
                fric *= BORDER_FRICTION_RELIGION_MULT
            ca.grievances[b] = ca.grievances.get(b, 0) + fric
            cb.grievances[a] = cb.grievances.get(a, 0) + fric

    # ── Diplomacy ────────────────────────────────────────────
    def _process_diplomacy(self, civ: Civ) -> None:
        arch = self._civ_archetype.get(civ.name, {})
        civ_by_name = self._civ_by_name.get
        govt = GOVERNMENTS.get(civ.government, {})
        for p in list(civ.trade_partners):
            pn = civ_by_name(p)
            if pn and pn.name not in civ.at_war_with:
                civ.treasury += 15
            else:
                civ.trade_partners.discard(p)
        for o in list(civ.grievances.keys()):
            civ.grievances[o] = max(0, civ.grievances[o] - 0.5)
            war_thr = arch.get("war_threshold", 50) + govt.get("war_threshold_mod", 0)
            if civ.grievances[o] < war_thr * 0.3 and o in civ.at_war_with:
                civ.at_war_with.discard(o)
                on = civ_by_name(o)
                if on:
                    on.at_war_with.discard(civ.name)
                    self.log_signal.emit(f"{self.year}: {civ.name} made peace with {o}")
                    self.turn_events_log.append(f"{civ.name} made peace with {o}")
                    self.notification_signal.emit("Peace Treaty", f"{civ.name} made peace with {o}")
        self._process_religion(civ, arch.get("tolerance", 30))
        self._process_stability(civ, arch.get("stability_resilience", 1.0))

    def _process_religion(self, civ: Civ, tolerance: float = 30) -> None:
        if not civ.religion and civ.culture > 500:
            civ.religion = random.choice(RELIGIONS)['name']
            self.log_signal.emit(f"{self.year}: {civ.name} founded {civ.religion}!")
            self.turn_events_log.append(f"{civ.name} founded {civ.religion}")
            self.notification_signal.emit("New Religion", f"{civ.name} founded {civ.religion}!")
        if civ.religion:
            om = self.owner_map
            cn = civ.name
            nbrs = set()
            for x, y in civ.territory:
                for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                    no = om.get((nx, ny))
                    if no and no != cn: nbrs.add(no)
            amt = 0.2 * (30 / max(tolerance, 5))
            for n in nbrs:
                nc = self._civ_by_name.get(n)
                if nc and nc.religion and nc.religion != civ.religion:
                    nc.grievances[civ.name] = nc.grievances.get(civ.name, 0) + amt
                    civ.grievances[nc.name] = civ.grievances.get(nc.name, 0) + amt

    def _process_stability(self, civ: Civ, resilience: float = 1.0) -> None:
        if civ.at_war_with:
            civ.stability -= len(civ.at_war_with) * 1.5
        if len(civ.territory) > civ.military / 10:
            civ.stability -= 1.0
        om = self.owner_map
        cn = civ.name; cc = civ.culture
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                no = om.get((nx, ny))
                if no and no != cn:
                    en = self._civ_by_name.get(no)
                    if en and en.culture > cc * 1.5:
                        civ.stability -= 0.1
        govt = GOVERNMENTS.get(civ.government, {})
        civ.stability += 1.5 * resilience + govt.get("stability_mod", 0.0)
        civ.stability = max(0, min(100, civ.stability))
        if civ.stability < 20 and len(civ.territory) > 5 and random.random() < 0.05:
            self._spawn_rebellion(civ)

    def _spawn_rebellion(self, civ: Civ) -> None:
        if not civ.territory: return
        ft = sorted(civ.territory, key=lambda t: abs(t[0]-civ.capital[0]) + abs(t[1]-civ.capital[1]), reverse=True)
        rc = ft[0]; rt = {rc}
        for x, y in ft[1:]:
            if abs(x-rc[0]) + abs(y-rc[1]) <= 4 and random.random() < 0.6:
                rt.add((x, y))
        if len(rt) < 3: return
        first_word = civ.name.split()[0] if civ.name else "Unknown"
        nn = f"{random.choice(REBEL_NAMES)} of {first_word}"
        nc = Civ(nn, QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)).name(),
                 rc[0], rc[1], archetype="raider", government="chiefdom")
        nc.population = civ.population * REBEL_POP_INHERIT
        nc.military = civ.military * REBEL_MILITARY_INHERIT
        nc.culture = civ.culture * REBEL_CULTURE_INHERIT
        nc.technology = civ.technology * REBEL_TECH_INHERIT
        nc.stability = 70
        nc.techs_researched = list(civ.techs_researched)
        nc.buildings = list(civ.buildings)[:max(1, len(civ.buildings) // 4)]
        for t in rt:
            civ.territory.discard(t)
            self.owner_map[t] = nn
            nc.territory.add(t)
        civ.population *= 0.8; civ.military *= 0.85; civ.stability = 50
        civ.at_war_with.add(nn); nc.at_war_with.add(civ.name)
        civ.grievances[nn] = 100; nc.grievances[civ.name] = 100
        self.civs.append(nc)
        self._civ_by_name[nc.name] = nc
        self._civ_archetype[nc.name] = PERSONALITY_ARCHETYPES.get("raider", {})
        self.log_signal.emit(f"{self.year}: REBELLION! {nn} broke from {civ.name}!")
        self.turn_events_log.append(f"REBELLION! {nn} broke from {civ.name}")
        self.notification_signal.emit("Rebellion!", f"{nn} broke from {civ.name}!")

    # ── Events ───────────────────────────────────────────────
    def _process_events(self) -> None:
        if random.random() < 0.03 and self.civs:
            tc = random.choice(self.civs)
            evts = [
                ("Plague", "A plague sweeps {}", lambda c: setattr(c, 'population', c.population * 0.85), 5, "#8B0000", "plague"),
                ("Earthquake", "Earthquake strikes {}!", lambda c: setattr(c, 'stability', max(0, c.stability - 20)), 0, "#A0522D", "disaster"),
                ("Golden Age", "{} enters a Golden Age!", lambda c: setattr(c, 'culture', c.culture + 100), 20, "#FFD700", "golden"),
                ("Drought", "Drought ravages {}!", lambda c: setattr(c, 'stability', max(0, c.stability - 15)), 15, "#CD853F", "disaster"),
                ("Barbarians", "Barbarians raid {}!", lambda c: setattr(c, 'military', max(10, c.military - 80)), 0, "#FF4500", "war"),
                ("Comet", "A comet is seen over {}!", lambda c: setattr(c, 'culture', c.culture + 50), 10, "#9370DB", "omen"),
                ("Renaissance", "A renaissance blooms in {}!", lambda c: (setattr(c, 'culture', c.culture + 200), setattr(c, 'technology', c.technology + 2)), 15, "#FF69B4", "golden"),
                ("Boom", "Economic boom enriches {}!", lambda c: setattr(c, 'treasury', c.treasury + 300), 10, "#32CD32", "boom"),
            ]
            n, d, f, du, col, etype = random.choice(evts)
            f(tc)
            cap = tc.capital
            ev = WorldEvent(n, d.format(tc.name), f, du, col, tc.name, position=cap, event_type=etype)
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
                    if ev.name == "Drought":      c.population *= 0.998; c.stability = max(0, c.stability - 1)
                    elif ev.name == "Golden Age": c.treasury += 30; c.culture += 10
                    elif ev.name == "Plague":     c.population *= 0.997
                    elif ev.name == "Comet":      c.culture += 5
                    elif ev.name == "Renaissance":c.culture += 15; c.technology += 0.05
                    elif ev.name == "Boom":       c.treasury += 25

    # ── Leadership ───────────────────────────────────────────
    def _process_leadership(self, civ: Civ) -> None:
        if not civ.leader:
            civ.leader = Leader.generate(civ.government, civ.archetype)
            civ.leader_history_count += 1
            return
        civ.leader.tenure += 1
        civ.gov_tenure += 1
        govt = GOVERNMENTS.get(civ.government, {})
        term_max = govt.get("leader_term_max", 40)
        term_min = govt.get("leader_term_min", 20)
        succ = govt.get("succession", "hereditary")
        must = civ.leader.tenure >= term_max
        early = False
        if civ.leader.tenure >= term_min:
            over = civ.leader.tenure - term_min
            base = 0.02 + over * 0.01
            if succ == "election": base = 0.08 + over * 0.03
            elif succ == "coup":
                if civ.stability < 40: base = 0.10 + over * 0.04
            elif succ == "theocratic": base = 0.01 + over * 0.005
            early = random.random() < base
        if must or early:
            self._succeed_leader(civ, succ)
        self._process_government_reform(civ, govt)

    def _succeed_leader(self, civ: Civ, succ: str) -> None:
        old = civ.leader
        old_arch = civ.archetype
        if old:
            if civ.stability > 70: old.accomplishments.append("Stable reign")
            if len(civ.territory) > 20: old.accomplishments.append("Expanded borders")
            if civ.technology > 10: old.accomplishments.append("Advanced learning")
            civ.previous_leaders.append(old)
            if len(civ.previous_leaders) > 5:
                civ.previous_leaders = civ.previous_leaders[-5:]
        if succ == "hereditary":
            new_arch = old_arch if random.random() < 0.6 else Leader._pick_archetype_for_government(civ.government)
        elif succ == "election":
            new_arch = Leader._pick_archetype_for_government(civ.government)
        elif succ == "coup":
            new_arch = random.choices(["warlord","raider","survivor","merchant"], weights=[5,3,1,1])[0]
        elif succ == "theocratic":
            new_arch = random.choices(["zealot","builder","diplomat","survivor"], weights=[5,2,1,1])[0]
        else:
            new_arch = old_arch
        new_leader = Leader.generate(civ.government, new_arch)
        civ.leader = new_leader
        civ.leader_history_count += 1
        self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(new_arch, {})
        if new_arch != old_arch:
            civ.agent.set_archetype(new_arch)
        flavor = {"hereditary":"has died. Long live","election":"has been voted out. Elected:",
                  "coup":"has been overthrown! Seizing power:","theocratic":"has passed to the divine. Anointed:"}
        old_name = old.short_name if old else "Previous ruler"
        self.log_signal.emit(f"{self.year}: {civ.name}: {old_name} {flavor.get(succ, 'is replaced by')} {new_leader.full_name}")
        self.turn_events_log.append(f"{civ.name}: {old_name} -> {new_leader.full_name}")
        self.notification_signal.emit("New Leader", f"{civ.name}: {new_leader.full_name} takes power!")
        if new_arch != old_arch:
            self.log_signal.emit(f"{self.year}: {civ.name} shifts from {PERSONALITY_ARCHETYPES.get(old_arch,{}).get('label',old_arch)} to {PERSONALITY_ARCHETYPES.get(new_arch,{}).get('label',new_arch)}")
        if succ == "coup": civ.stability = max(0, civ.stability - 20)
        elif succ == "hereditary": civ.stability = max(0, civ.stability - 5)
        elif succ == "election": civ.stability = min(100, civ.stability + 5)
        elif succ == "theocratic": civ.stability = min(100, civ.stability + 3)

    def _process_government_reform(self, civ: Civ, govt: dict) -> None:
        allowed = govt.get("allowed_govts", [])
        rc = govt.get("rebel_chance", 0.01)
        if civ.stability < 20 and random.random() < rc * 3:
            self._change_government(civ, allowed, "revolution"); return
        if civ.stability < 40 and random.random() < rc:
            self._change_government(civ, allowed, "uprising"); return
        if random.random() < 0.005:
            elig = [g for g in allowed if civ.era_id >= GOVERNMENTS.get(g, {}).get("era_min", 0) and g != civ.government]
            if elig:
                self._change_government(civ, [random.choice(elig)], "reform")

    def _change_government(self, civ: Civ, allowed: list[str], reason: str) -> None:
        elig = [g for g in allowed if civ.era_id >= GOVERNMENTS.get(g, {}).get("era_min", 0)]
        if not elig: return
        old_g = civ.government
        new_g = random.choice(elig)
        civ.government = new_g
        civ.gov_tenure = 0
        new_arch = Leader._pick_archetype_for_government(new_g)
        new_leader = Leader.generate(new_g, new_arch)
        if civ.leader:
            civ.previous_leaders.append(civ.leader)
            if len(civ.previous_leaders) > 5:
                civ.previous_leaders = civ.previous_leaders[-5:]
        civ.leader = new_leader
        civ.leader_history_count += 1
        self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(new_arch, {})
        civ.agent.set_archetype(new_arch)
        if reason == "revolution": civ.stability = max(0, civ.stability - 30)
        elif reason == "uprising":  civ.stability = max(0, civ.stability - 15)
        elif reason == "reform":    civ.stability = min(100, civ.stability + 5)
        self.log_signal.emit(f"{self.year}: {civ.name} {reason}: {GOVERNMENTS.get(old_g,{}).get('label',old_g)} -> {GOVERNMENTS.get(new_g,{}).get('label',new_g)} under {new_leader.full_name}")
        self.turn_events_log.append(f"{civ.name} gov't: {old_g} -> {new_g} ({reason})")
        self.notification_signal.emit("Government Change", f"{civ.name}: {GOVERNMENTS.get(old_g,{}).get('label',old_g)} -> {GOVERNMENTS.get(new_g,{}).get('label',new_g)}")

    # ── AI turn ───────────────────────────────────────────────
    def _get_neighbors(self, civ: Civ) -> list[Civ]:
        seen = set()
        om = self.owner_map
        cn = civ.name
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                no = om.get((nx, ny))
                if no and no != cn and no not in seen:
                    seen.add(no)
        return [self._civ_by_name[n] for n in seen if n in self._civ_by_name]

    def _build_ai_context(self, civ: Civ, arch: dict) -> dict:
        om = self.owner_map
        tm = self.terrain_map
        is_water = self._is_water_cache
        cn = civ.name
        hc = 0
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                no = om.get((nx, ny))
                if no and no != cn: hc += 1
        neighbors = self._get_neighbors(civ)
        threats = ThreatAssessment.assess(civ.military, civ.technology, [
            {"name": n.name, "military": n.military, "technology": n.technology,
             "grievance_vs_us": n.grievances.get(civ.name, 0),
             "at_war": n.name in civ.at_war_with, "allied": n.name in civ.alliances}
            for n in neighbors])
        _, max_threat = ThreatAssessment.highest(threats)
        war_targets = [c for c in self.civs if c.name in civ.at_war_with and c.territory]
        target_weakness = 0.0
        if war_targets:
            weakest = min(war_targets, key=lambda t: t.military)
            target_weakness = max(0.0, min(1.0, 1.0 - weakest.military / max(1, civ.military)))
        can_expand = False
        att = 0; adt = 0; aat = len(war_targets)
        W, H = self.W, self.H
        for x, y in civ.territory:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if not (0 <= nx < W and 0 <= ny < H): continue
                if is_water.get(tm[(nx, ny)], True): continue
                if om.get((nx, ny)) != cn:
                    can_expand = True
        for n in neighbors:
            if n.name in civ.at_war_with: continue
            if n.name not in civ.trade_partners: att += 1
            if n.name not in civ.alliances: adt += 1
        return {
            "population": civ.population, "pop_cap": civ.pop_cap,
            "military": civ.military, "technology": civ.technology,
            "treasury": civ.treasury, "culture": civ.culture, "stability": civ.stability,
            "territory_count": len(civ.territory), "total_land": self.total_land_tiles,
            "building_count": len(civ.buildings), "hostile_neighbors": hc,
            "at_war": len(civ.at_war_with) > 0, "war_count": len(civ.at_war_with),
            "alliance_count": len(civ.alliances), "trade_partner_count": len(civ.trade_partners),
            "total_civs": len(self.civs),
            "avg_enemy_tech": sum(c.technology for c in self.civs if c != civ) / max(1, len(self.civs) - 1),
            "year": self.year, "era_id": civ.era_id, "has_religion": civ.religion is not None,
            "max_threat": max_threat, "target_weakness": target_weakness,
            "can_expand": can_expand, "available_trade_targets": att,
            "available_diplomacy_targets": adt, "available_attack_targets": aat,
        }

    def _process_civ_turn(self, civ: Civ) -> None:
        arch = self._civ_archetype.get(civ.name, {})
        rs = self._build_ai_context(civ, arch)
        at = civ.agent.decide(rs)
        civ.last_action = at
        success = False
        if   at == ActionType.EXPAND:   success = self._exec_expand(civ, arch)
        elif at == ActionType.FORTIFY:   success = self._exec_fortify(civ, arch)
        elif at == ActionType.DEVELOP:   success = self._exec_develop(civ, arch)
        elif at == ActionType.RESEARCH:  success = self._exec_research(civ, arch)
        elif at == ActionType.ATTACK:    success = self._exec_attack(civ, arch)
        elif at == ActionType.CULTURE:   success = self._exec_culture(civ, arch)
        elif at == ActionType.DIPLOMACY:  success = self._exec_diplo(civ, arch)
        elif at == ActionType.TRADE:     success = self._exec_trade(civ, arch)
        elif at == ActionType.WONDER:    success = self._exec_wonder(civ, arch)
        civ.agent.record_outcome(at, success)

    # ── Action execution ─────────────────────────────────────
    def _exec_expand(self, civ: Civ, arch: dict) -> bool:
        om = self.owner_map; tm = self.terrain_map
        is_water = self._is_water_cache
        cn = civ.name
        W, H = self.W, self.H
        borders = [(nx, ny) for x, y in civ.territory
                   for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                   if 0 <= nx < W and 0 <= ny < H
                   and om.get((nx, ny)) != cn
                   and not is_water.get(tm[(nx, ny)], True)]
        if not borders or civ.military <= 20: return False
        cap = civ.capital
        def val(t):
            s = self._terrain_stats_by_id.get(tm[t], {})
            v = s.get('food', 0) * 3 + s.get('trade', 0) * 2 + s.get('prod', 0)
            if t in self.resource_map: v += 5
            v += max(0, 3 - (abs(t[0]-cap[0]) + abs(t[1]-cap[1])) * 0.05)
            v += sum(1 for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]
                     if om.get((t[0]+dx, t[1]+dy)) == cn) * 2
            co = om.get(t)
            if co:
                en = self._civ_by_name.get(co)
                if en and en.military > civ.military * 2 and en.name not in civ.at_war_with:
                    v -= 10
            return v
        bt = max(borders, key=val)
        co = om.get(bt)
        if co:
            en = self._civ_by_name.get(co)
            if en:
                war_thr = arch.get("war_threshold", 50)
                en.grievances[cn] = en.grievances.get(cn, 0) + 30
                if en.grievances[cn] > war_thr:
                    en.at_war_with.add(cn); civ.at_war_with.add(en.name)
                    self.log_signal.emit(f"{self.year}: {cn} & {en.name} went to WAR!")
                    self.turn_events_log.append(f"{cn} & {en.name} went to WAR!")
                    self.notification_signal.emit("War Declared!", f"{cn} & {en.name} went to WAR!")
        self.pathfinder.init(civ.capital, bt, self._terrain_stats_coords)
        self.pathfinder.compute_shortest_path()
        path = self.pathfinder.get_path(max_len=8)
        if path and len(path) > 1:
            civ.territory.add(bt); om[bt] = cn; civ.military -= 15
            self.last_path = path
            self.log_signal.emit(f"{self.year}: {cn} expanded to {bt}")
            self.turn_events_log.append(f"{cn} expanded to new tile")
            return True
        return False

    def _exec_fortify(self, civ: Civ, arch: dict) -> bool:
        if civ.treasury < 10:
            civ.military += 20; return True
        base = 50 + len(civ.buildings) * 5
        lbl = arch.get("label", "")
        if lbl == "Warlord": base = int(base * 1.3)
        elif lbl == "Raider": base = int(base * 1.2)
        elif lbl == "Builder": civ.stability = min(100, civ.stability + 2)
        civ.military += base; civ.treasury -= 30
        if civ.agent.strategic_state == StrategicState.TOTAL_WAR:
            extra = min(civ.treasury * 0.3, 100)
            civ.military += int(extra); civ.treasury -= extra
        return True

    def _exec_develop(self, civ: Civ, arch: dict) -> bool:
        owned = {b['name'] for b in civ.buildings}
        av = [b for b in self.defs.buildings if b['cost'] <= civ.treasury
              and b['min_era_id'] <= civ.era_id and b['name'] not in owned]
        if not av: return False
        def pri(b):
            s = b['bonus']
            if b['effect'] == 'growth' and civ.population < civ.pop_cap * 0.6: s *= 2
            elif b['effect'] == 'military' and civ.military < 200: s *= 2.5
            elif b['effect'] == 'tech' and civ.technology < 10: s *= 2
            elif b['effect'] == 'trade' and civ.treasury < 300: s *= 1.8
            lbl = arch.get("label", "")
            if lbl == "Builder" and b['effect'] in ('growth', 'trade'): s *= 1.3
            elif lbl == "Warlord" and b['effect'] == 'military': s *= 1.5
            elif lbl == "Philosopher" and b['effect'] == 'tech': s *= 1.5
            elif lbl == "Merchant Republic" and b['effect'] == 'trade': s *= 1.5
            elif lbl == "Zealot" and b['effect'] == 'culture': s *= 1.4
            if civ.treasury < 100: s *= (1.0 / max(1, b['cost'])) * 20
            return s
        b = max(av, key=pri)
        civ.treasury -= b['cost']; civ.buildings.append(b)
        self.log_signal.emit(f"{self.year}: {civ.name} built {b['name']}")
        self.turn_events_log.append(f"{civ.name} built {b['name']}")
        return True

    def _exec_research(self, civ: Civ, arch: dict) -> bool:
        res = set(civ.techs_researched)
        av = [t for t in self.defs.techs if t['cost'] <= civ.treasury
              and t['era_id'] <= civ.era_id and t['name'] not in res]
        if not av: return False
        def pri(t):
            s = t['bonus']
            if t['effect'] == 'military' and civ.military < 200: s *= 2
            elif t['effect'] == 'growth' and civ.population < civ.pop_cap * 0.5: s *= 2
            elif t['effect'] == 'tech' and civ.technology < 10: s *= 1.8
            lbl = arch.get("label", "")
            if lbl == "Philosopher" and t['effect'] == 'tech': s *= 2
            elif lbl == "Warlord" and t['effect'] == 'military': s *= 1.8
            elif lbl == "Zealot" and t['effect'] == 'culture': s *= 1.6
            if civ.treasury < 50: s *= (1.0 / max(1, t['cost'])) * 10
            return s
        t = max(av, key=pri)
        civ.technology += t['bonus']; civ.treasury -= t['cost']
        civ.techs_researched.append(t['name'])
        self.log_signal.emit(f"{self.year}: {civ.name} researched {t['name']}")
        self.turn_events_log.append(f"{civ.name} researched {t['name']}")
        return True

    def _exec_attack(self, civ: Civ, arch: dict) -> bool:
        wt = [c for c in self.civs if c.name in civ.at_war_with and c.territory]
        if not wt or civ.military < 150:
            civ.last_action = ActionType.FORTIFY; civ.military += 30; return False
        wt.sort(key=lambda t: (t.military, -len(t.territory)))
        max_targets = max(1, min(3, int(civ.military / 500)))
        if arch.get("label", "") == "Raider": max_targets += 1
        any_ok = False
        for tc in wt[:max_targets]:
            if civ.military < 100: break
            any_ok = any_ok or self._attack_one(civ, arch, tc)
        return any_ok

    def _attack_one(self, civ: Civ, arch: dict, tc: Civ) -> bool:
        om = self.owner_map
        cn = civ.name; tn = tc.name
        borders = [(nx, ny) for x, y in civ.territory
                   for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
                   if 0 <= nx < self.W and 0 <= ny < self.H and om.get((nx, ny)) == tn]
        if not borders: return False
        def val(t):
            v = 1.0
            if t in self.resource_map: v += 3
            v += max(0, 5 - (abs(t[0]-tc.capital[0]) + abs(t[1]-tc.capital[1])) * 0.1)
            s = self._terrain_stats_by_id.get(self.terrain_map[t], {})
            if s.get('food', 0) > 1.5: v += 1
            if s.get('trade', 0) > 1.0: v += 1
            return v
        tt = max(borders, key=val)
        greed = arch.get("expansion_greed", 1.0)
        bonus = 1.0 + (greed - 1.0) * 0.3
        lbl = arch.get("label", "")
        if lbl == "Warlord": bonus *= 1.15
        elif lbl == "Raider": bonus *= 1.1
        ally_bonus = 1.0
        for an in civ.alliances:
            ac = self._civ_by_name.get(an)
            if ac and tn in ac.at_war_with: ally_bonus += 0.1
        ap = civ.military * random.uniform(0.9, 1.3) * bonus * ally_bonus
        dp = tc.military * random.uniform(0.7, 1.1)
        civ.military -= 40
        if ap > dp:
            if tt in tc.territory:
                tc.territory.discard(tt); tc.military -= 50
                civ.territory.add(tt); om[tt] = cn
                if lbl == "Raider" and tc.treasury > 0:
                    stolen = min(tc.treasury * 0.1, 50)
                    civ.treasury += stolen; tc.treasury -= stolen
                self.log_signal.emit(f"{self.year}: {cn} conquered tile from {tn}!")
                self.turn_events_log.append(f"{cn} conquered tile from {tn}")
            else:
                self.turn_events_log.append(f"{cn} attack on {tn} - tile already lost")
        else:
            self.turn_events_log.append(f"{cn} failed to attack {tn}")
            if random.random() < 0.3 and tc.military > 200:
                civ.military -= 20
        for an in tc.alliances:
            ac = self._civ_by_name.get(an)
            if ac and cn not in ac.at_war_with:
                ac.at_war_with.add(cn); civ.at_war_with.add(ac.name)
                self.log_signal.emit(f"{self.year}: {ac.name} joins war defending {tn}!")
                self.turn_events_log.append(f"{ac.name} joins war defending {tn}")
        return ap > dp

    def _exec_culture(self, civ: Civ, arch: dict) -> bool:
        if civ.treasury < 10: return False
        base = 50
        inv = min(40, civ.treasury)
        lbl = arch.get("label", "")
        if lbl == "Zealot": base = int(base * 1.4)
        elif lbl == "Philosopher": civ.technology += 0.3
        elif lbl == "Diplomat":
            for n in self._get_neighbors(civ):
                n.grievances[civ.name] = max(0, n.grievances.get(civ.name, 0) - 5)
                civ.grievances[n.name] = max(0, civ.grievances.get(n.name, 0) - 5)
        civ.culture += base; civ.treasury -= inv
        if civ.agent.strategic_state == StrategicState.GOLDEN_AGE:
            civ.culture += 30
        return True

    def _exec_diplo(self, civ: Civ, arch: dict) -> bool:
        eagerness = arch.get("alliance_eagerness", 0.8)
        ns = self._get_neighbors(civ)
        war_thr = arch.get("war_threshold", 50)
        if len(civ.at_war_with) >= 2 and civ.military < 300:
            for en_name in list(civ.at_war_with):
                en = self._civ_by_name.get(en_name)
                if en and civ.grievances.get(en_name, 0) < war_thr * 0.5:
                    civ.at_war_with.discard(en_name); en.at_war_with.discard(civ.name)
                    civ.grievances[en_name] = max(0, civ.grievances.get(en_name, 0) - 20)
                    en.grievances[civ.name] = max(0, en.grievances.get(civ.name, 0) - 20)
                    self.log_signal.emit(f"{self.year}: {civ.name} made peace with {en_name}")
                    self.turn_events_log.append(f"{civ.name} made peace with {en_name}")
                    self.notification_signal.emit("Peace Treaty", f"{civ.name} made peace with {en_name}")
                    return True
        cs = [n for n in ns if n.name not in civ.at_war_with and n.name not in civ.alliances
              and civ.grievances.get(n.name, 0) < war_thr * 0.4]
        if cs:
            def val(n):
                v = -civ.grievances.get(n.name, 0)
                v += len(civ.at_war_with & n.at_war_with) * 20
                v += n.military * 0.01
                return v
            t = max(cs, key=val)
            if t.grievances.get(civ.name, 0) < war_thr * 0.4 and random.random() < 0.3 * eagerness:
                civ.alliances.add(t.name); t.alliances.add(civ.name)
                self.log_signal.emit(f"{self.year}: {civ.name} allied with {t.name}!")
                self.turn_events_log.append(f"{civ.name} allied with {t.name}")
                self.notification_signal.emit("Alliance Formed", f"{civ.name} allied with {t.name}!")
                return True
            for n in cs:
                n.grievances[civ.name] = max(0, n.grievances.get(civ.name, 0) - 10)
                civ.grievances[n.name] = max(0, civ.grievances.get(n.name, 0) - 10)
            return True
        return False

    def _exec_trade(self, civ: Civ, arch: dict) -> bool:
        eagerness = arch.get("trade_eagerness", 0.9)
        war_thr = arch.get("war_threshold", 50)
        ns = self._get_neighbors(civ)
        cs = [n for n in ns if n.name not in civ.at_war_with and n.name not in civ.trade_partners]
        if not cs: return False
        def val(n):
            v = 50 if n.name in civ.alliances else 0
            v -= civ.grievances.get(n.name, 0)
            v -= n.grievances.get(civ.name, 0)
            v += n.treasury * 0.001
            return v
        cs.sort(key=val, reverse=True)
        t = cs[0]
        if t.grievances.get(civ.name, 0) < war_thr * 0.6 and random.random() < 0.4 * eagerness:
            civ.trade_partners.add(t.name); t.trade_partners.add(civ.name)
            lbl = arch.get("label", "")
            if lbl == "Merchant Republic":
                civ.treasury += 10; t.treasury += 5
            elif lbl == "Diplomat":
                civ.grievances[t.name] = max(0, civ.grievances.get(t.name, 0) - 3)
                t.grievances[civ.name] = max(0, t.grievances.get(civ.name, 0) - 3)
            self.log_signal.emit(f"{self.year}: {civ.name} traded with {t.name}")
            self.turn_events_log.append(f"{civ.name} traded with {t.name}")
            return True
        return False

    def _exec_wonder(self, civ: Civ, arch: dict) -> bool:
        built = set(self.wonders_built)
        av = [w for w in WONDERS if w['name'] not in built and w['cost'] <= civ.treasury]
        if not av or civ.treasury <= 10000 * arch.get("wonder_hunger", 0.5): return False
        def val(w):
            v = w['bonus']
            if w['effect'] == 'military' and civ.military < 300: v *= 1.5
            elif w['effect'] == 'tech' and civ.technology < 15: v *= 1.5
            elif w['effect'] == 'growth' and civ.population < civ.pop_cap * 0.5: v *= 1.5
            lbl = arch.get("label", "")
            if lbl == "Builder": v *= 1.3
            elif lbl == "Philosopher" and w['effect'] == 'tech': v *= 1.6
            elif lbl == "Warlord" and w['effect'] == 'military': v *= 1.5
            elif lbl == "Merchant Republic" and w['effect'] == 'trade': v *= 1.6
            elif lbl == "Zealot" and w['effect'] == 'culture': v *= 1.5
            return v
        w = max(av, key=val)
        civ.treasury -= w['cost']; civ.wonders.append(w['name'])
        self.wonders_built.append(w['name'])
        self.log_signal.emit(f"{self.year}: {civ.name} built the {w['name']}!")
        self.turn_events_log.append(f"{civ.name} built the {w['name']}")
        self.notification_signal.emit("Wonder Built", f"{civ.name} built the {w['name']}!")
        return True

    # ── End game / data ───────────────────────────────────────
    def _end_game(self) -> None:
        self.analytics.commit()
        self.update_signal.emit(self._build_data())
        for i, c in enumerate(sorted(self.civs, key=lambda x: x.score, reverse=True)):
            self.log_signal.emit(f"  #{i+1} {c.name} - Score: {int(c.score)} | Pop: {int(c.population)} | Terr: {len(c.territory)}")

    def _build_data(self) -> dict:
        tr = []
        seen = set()
        for c in self.civs:
            for t in c.trade_partners:
                p = tuple(sorted((c.name, t)))
                if p not in seen:
                    seen.add(p); tr.append(p)
        at_war = set()
        for c in self.civs:
            for enemy in c.at_war_with:
                at_war.add(tuple(sorted((c.name, enemy))))
        return {
            'terrain': self.terrain_map, 'owners': self.owner_map,
            'civs': self.civs, 'year': self.year, 'generation': self.generation,
            'last_path': self.last_path,
            'capitals': {c.name: c.capital for c in self.civs},
            'explored': self.explored, 'trade_routes': tr,
            'active_events': self.active_events,
            'resource_map': self.resource_map, 'season': self.season,
            'at_war_pairs': at_war,
        }

    # ── Save / Load ─────────────────────────────────────────
    def save_game(self, filepath: str) -> None:
        state = {
            "year": self.year, "generation": self.generation,
            "season": self.season, "season_timer": self.season_timer,
            "max_years": self.max_years, "terrain_preset": self.terrain_preset,
            "W": self.W, "H": self.H,
            "terrain_map": {f"{k[0]},{k[1]}": v for k, v in self.terrain_map.items()},
            "owner_map":   {f"{k[0]},{k[1]}": v for k, v in self.owner_map.items()},
            "resource_map":{f"{k[0]},{k[1]}": v for k, v in self.resource_map.items()},
            "wonders_built": self.wonders_built,
            "civs": [c.to_dict() for c in self.civs],
            "analytics": self.analytics.snapshots,
        }
        with open(filepath, 'w') as f:
            json.dump(state, f)
        self.log_signal.emit(f"Game saved to {filepath}")

    def load_game(self, filepath: str) -> None:
        with open(filepath, 'r') as f:
            state = json.load(f)
        self.year = state["year"]; self.generation = state["generation"]
        self.season = state["season"]; self.season_timer = state["season_timer"]
        self.max_years = state.get("max_years", 0)
        self.terrain_preset = state.get("terrain_preset", TerrainPreset.CONTINENT)
        self.W = state["W"]; self.H = state["H"]
        self.wonders_built = state.get("wonders_built", [])
        self.finished = False
        self.terrain_map = {tuple(map(int, k.split(','))): v for k, v in state["terrain_map"].items()}
        self.owner_map   = {tuple(map(int, k.split(','))): v for k, v in state["owner_map"].items()}
        self.resource_map= {tuple(map(int, k.split(','))): v for k, v in state["resource_map"].items()}
        self.civs = [Civ.from_dict(cd) for cd in state["civs"]]
        self.pathfinder = DStarLite(self.W, self.H)
        self._terrain_stats_coords = {(x, y): self._terrain_stats_by_id.get(tid)
                                      for (x, y), tid in self.terrain_map.items()}
        self.last_path = []; self.active_events = []
        self._civ_by_name.clear(); self._civ_archetype.clear()
        for civ in self.civs:
            self._civ_by_name[civ.name] = civ
            self._civ_archetype[civ.name] = PERSONALITY_ARCHETYPES.get(civ.archetype, {})
        self.analytics.snapshots = state.get("analytics", [])
        self._rebuild_explored()
        self.log_signal.emit(f"Game loaded from {filepath}")
        self.update_signal.emit(self._build_data())

    def _auto_save(self) -> None:
        saves_dir = os.path.join(os.path.expanduser("~"), ".civsim", "saves")
        try:
            os.makedirs(saves_dir, exist_ok=True)
            path = os.path.join(saves_dir, f"autosave_gen{self.generation}.json")
        except OSError:
            path = f"autosave_gen{self.generation}.json"
        self.save_game(path)


# ════════════════════════════════════════════════════════════
# WIDGETS
# ════════════════════════════════════════════════════════════
def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


class SparklineChart(QWidget):
    def __init__(self, color="#7aa2f7", parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._data: list[float] = []
        self.setFixedHeight(40); self.setMinimumWidth(50)

    def add_point(self, v: float):
        self._data.append(float(v))
        if len(self._data) > 80: self._data = self._data[-80:]
        self.update()

    def clear_data(self):
        self._data.clear(); self.update()

    def paintEvent(self, ev):
        if not self._data: return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        dmin, dmax = min(self._data), max(self._data)
        drange = dmax - dmin if dmax != dmin else 1.0
        path = QPainterPath()
        for i, v in enumerate(self._data):
            x = (i / max(len(self._data) - 1, 1)) * (w - 16)
            y = 2 + (h - 4) - ((v - dmin) / drange) * (h - 4)
            if i == 0: path.moveTo(x, y)
            else: path.lineTo(x, y)
        p.setPen(QPen(self._color, 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()


class StatBar(QWidget):
    def __init__(self, label="", color="#7aa2f7", parent=None):
        super().__init__(parent)
        self._label = label
        self._color = QColor(color)
        self._value = 0.0; self._max_value = 1.0
        self._display = ""
        self.setFixedHeight(18)

    @staticmethod
    def _fmt(v):
        v = float(v)
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000: return f"{v/1_000:.1f}K"
        return f"{v:.0f}" if v == int(v) else f"{v:.1f}"

    def set_value(self, v, max_v=None, display=""):
        self._value = float(v)
        if max_v is not None: self._max_value = float(max_v)
        self._display = display
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor("#a9b1d6"))
        p.drawText(0, 0, 42, h, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._label)
        txt = self._display or self._fmt(self._value)
        p.setPen(QColor("#c0caf5"))
        f = p.font(); f.setBold(True); p.setFont(f)
        p.drawText(w - 56, 0, 56, h, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, txt)
        bx = 46; bw = w - 46 - 58
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#1a1b26"))
        p.drawRoundedRect(QRectF(bx, 3, bw, h - 6), 3, 3)
        ratio = min(self._value / self._max_value, 1.0) if self._max_value else 0
        if ratio > 0:
            grad = QLinearGradient(bx, 0, bx + bw * ratio, 0)
            grad.setColorAt(0, self._color.darker(150))
            grad.setColorAt(1, self._color)
            p.setBrush(grad)
            p.drawRoundedRect(QRectF(bx, 3, bw * ratio, h - 6), 3, 3)
        p.end()


class TimelineGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: list[list[dict]] = []
        self.setMinimumSize(280, 130)
        self.setMaximumHeight(180)

    def update_data(self, civs_data):
        snap = [{"name": d.get("name","?"), "color": d.get("color","#7aa2f7"), "score": d.get("score",0)} for d in civs_data]
        self._history.append(snap)
        if len(self._history) > 200: self._history = self._history[-200:]
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor("#1a1b26"))
        p.setPen(QPen(QColor("#3b4261"), 1)); p.drawRect(0, 0, w - 1, h - 1)
        if len(self._history) < 2:
            p.setPen(QColor("#565f89"))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Waiting for data…")
            return
        ml, mr, mt, mb = 40, 10, 20, 20
        pw, ph = w - ml - mr, h - mt - mb
        all_s = [s for snap in self._history for s in (c["score"] for c in snap)]
        if not all_s: return
        ymin, ymax = min(all_s), max(all_s)
        yrange = ymax - ymin if ymax != ymin else 1
        ng = len(self._history)
        def xy(gi, sc):
            return ml + (gi / max(ng - 1, 1)) * pw, mt + ph - ((sc - ymin) / yrange) * ph
        p.setPen(QPen(QColor("#2f3450"), 1, Qt.PenStyle.DotLine))
        p.setFont(QFont("Segoe UI", 7))
        for i in range(6):
            yv = ymin + (yrange * i / 5)
            _, gy = xy(0, yv)
            p.drawLine(int(ml), int(gy), int(w - mr), int(gy))
            p.setPen(QColor("#565f89"))
            p.drawText(2, int(gy) - 6, ml - 4, 12,
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{yv:.0f}")
            p.setPen(QPen(QColor("#2f3450"), 1, Qt.PenStyle.DotLine))
        civ_info = {c["name"]: c["color"] for c in self._history[-1]}
        for cn, cc in civ_info.items():
            points = [(gi, c["score"]) for gi, snap in enumerate(self._history) for c in snap if c["name"] == cn]
            if len(points) < 2: continue
            col = QColor(cc)
            path = QPainterPath()
            for idx, (gi, sc) in enumerate(points):
                x, y = xy(gi, sc)
                if idx == 0: path.moveTo(x, y)
                else: path.lineTo(x, y)
            p.setPen(QPen(col, 1.5)); p.setBrush(Qt.BrushStyle.NoBrush); p.drawPath(path)
        p.end()


class CivCard(QFrame):
    def __init__(self, data: dict):
        super().__init__()
        self.setObjectName("CivCard")
        self.setStyleSheet("CivCard { background: #24283b; border: 1px solid #3b4261; border-radius: 6px; }")
        self._color = data.get("color", "#7aa2f7")
        self._build_ui()
        self.update_data(data)

    @staticmethod
    def _fmt(v):
        if v is None: return "0"
        v = float(v)
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000: return f"{v/1_000:.1f}K"
        return f"{v:.0f}" if v == int(v) else f"{v:.1f}"

    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        self._accent = QWidget(); self._accent.setFixedWidth(4)
        self._accent.setStyleSheet(f"background:{self._color}; border-radius:2px;")
        lay.addWidget(self._accent)
        content = QWidget()
        v = QVBoxLayout(content)
        v.setContentsMargins(8, 6, 8, 6); v.setSpacing(3)
        r0 = QHBoxLayout(); r0.setSpacing(6)
        self._lbl_name = QLabel()
        self._lbl_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        r0.addWidget(self._lbl_name)
        self._badge_arch = QLabel(); r0.addWidget(self._badge_arch)
        r0.addStretch()
        self._badge_war = QLabel(); r0.addWidget(self._badge_war)
        self._lbl_score = QLabel()
        self._lbl_score.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._lbl_score.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        r0.addWidget(self._lbl_score)
        v.addLayout(r0)
        self._lbl_leader = QLabel()
        self._lbl_leader.setFont(QFont("Segoe UI", 9))
        self._lbl_leader.setStyleSheet("color:#bb9af7;")
        v.addWidget(self._lbl_leader)
        r2 = QHBoxLayout(); r2.setSpacing(4)
        self._badge_gov = QLabel(); r2.addWidget(self._badge_gov)
        self._badge_era = QLabel(); r2.addWidget(self._badge_era)
        self._badge_strat = QLabel(); r2.addWidget(self._badge_strat)
        r2.addStretch(); v.addLayout(r2)
        self._lbl_action = QLabel()
        self._lbl_action.setFont(QFont("Segoe UI", 9))
        self._lbl_action.setStyleSheet("color:#565f89;")
        v.addWidget(self._lbl_action)
        self._stat_pop = StatBar("Pop", "#9ece6a")
        self._stat_tech = StatBar("Tech", "#7aa2f7")
        self._stat_mil = StatBar("Mil", "#f7768e")
        self._stat_treas = StatBar("Gold", "#e0af68")
        self._stat_cult = StatBar("Cult", "#bb9af7")
        self._stat_stab = StatBar("Stab", "#7dcfff")
        for s in (self._stat_pop, self._stat_tech, self._stat_mil,
                  self._stat_treas, self._stat_cult, self._stat_stab):
            v.addWidget(s)
        sr = QHBoxLayout(); sr.setSpacing(4)
        self._spark_pop = SparklineChart("#9ece6a")
        self._spark_tech = SparklineChart("#7aa2f7")
        self._spark_mil = SparklineChart("#f7768e")
        for s in (self._spark_pop, self._spark_tech, self._spark_mil):
            sr.addWidget(s)
        v.addLayout(sr)
        self._lbl_diplo = QLabel()
        self._lbl_diplo.setFont(QFont("Segoe UI", 8))
        self._lbl_diplo.setWordWrap(True)
        v.addWidget(self._lbl_diplo)
        lay.addWidget(content)

    def _pill(self, lbl, txt, bg, fg):
        lbl.setText(txt)
        lbl.setStyleSheet(f"background:{bg}; color:{fg}; border-radius:8px; padding:1px 6px; font-size:9px;")
        lbl.show()

    def update_data(self, d: dict):
        color = d.get("color", self._color)
        self._color = color
        self._accent.setStyleSheet(f"background:{color}; border-radius:2px;")
        self._lbl_name.setText(d.get("name","?"))
        self._lbl_name.setStyleSheet(f"color:{color}; font-weight:bold; font-size:12px;")
        arch = d.get("archetype_label") or d.get("archetype","")
        if arch:
            self._pill(self._badge_arch, arch, "#2f3450", "#7aa2f7")
        else: self._badge_arch.hide()
        war = d.get("at_war_with", [])
        if war:
            self._pill(self._badge_war, f"⚔ AT WAR ({len(war)})", "#4a1a1a", "#f7768e")
        else:
            self._pill(self._badge_war, "⚔ Peace", "#1a2a1a", "#9ece6a")
        leader = d.get("leader_name","")
        if leader: self._lbl_leader.setText(leader); self._lbl_leader.show()
        else: self._lbl_leader.hide()
        gov = d.get("government_label","")
        if gov: self._pill(self._badge_gov, gov, "#1a2a3a", "#7dcfff")
        else: self._badge_gov.hide()
        era = d.get("era_name","")
        if era: self._pill(self._badge_era, era, "#2a2a1a", "#e0af68")
        else: self._badge_era.hide()
        state_colors = {"EXPANSION":"#7aa2f7","CONSOLIDATION":"#565f89","CRISIS":"#f7768e",
                        "TOTAL_WAR":"#ff0000","GOLDEN_AGE":"#e0af68","RECOVERY":"#ff9e64","SIEGE":"#db4b4b"}
        st = d.get("strategic_state","")
        if st:
            sc = state_colors.get(st, "#565f89")
            self._badge_strat.setText(st.replace("_"," ").title())
            self._badge_strat.setStyleSheet(f"background:{sc}22; color:{sc}; border:1px solid {sc}66; border-radius:8px; padding:1px 6px; font-size:9px;")
            self._badge_strat.show()
        else: self._badge_strat.hide()
        act = d.get("plan_name") or d.get("last_action","")
        if act:
            self._lbl_action.setText(f"⟶ {act}")
            self._lbl_action.show()
        else: self._lbl_action.hide()
        self._stat_pop.set_value(d.get("population",0), 100000, self._fmt(d.get("population",0)))
        self._stat_tech.set_value(d.get("technology",0), 50, f"{d.get('technology',0):.1f}")
        self._stat_mil.set_value(d.get("military",0), 5000, self._fmt(d.get("military",0)))
        self._stat_treas.set_value(d.get("treasury",0), 10000, self._fmt(d.get("treasury",0)))
        self._stat_cult.set_value(d.get("culture",0), 2000, self._fmt(d.get("culture",0)))
        self._stat_stab.set_value(d.get("stability",0), 100, f"{d.get('stability',0):.0f}")
        self._spark_pop.add_point(d.get("population",0))
        self._spark_tech.add_point(d.get("technology",0))
        self._spark_mil.add_point(d.get("military",0))
        parts = []
        allies = d.get("alliances",[])
        if allies: parts.append(f'<span style="color:#9ece6a;">● Allies: {", ".join(allies)}</span>')
        trade = d.get("trade_partners",[])
        if trade: parts.append(f'<span style="color:#7dcfff;">● Trade: {", ".join(trade)}</span>')
        if war: parts.append(f'<span style="color:#f7768e;">● War: {", ".join(war)}</span>')
        rel = d.get("religion","")
        if rel: parts.append(f'<span style="color:#bb9af7;">◆ {rel}</span>')
        wonders = d.get("wonders",[])
        if wonders: parts.append(f'<span style="color:#e0af68;">★ {", ".join(wonders)}</span>')
        if parts:
            self._lbl_diplo.setText(" | ".join(parts)); self._lbl_diplo.show()
        else: self._lbl_diplo.hide()
        self._lbl_score.setText(self._fmt(d.get("score",0)))
        self._lbl_score.setStyleSheet(f"color:{color}; font-size:14px; font-weight:bold;")
        self.update()


class MinimapWidget(QWidget):
    navigated = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 130)
        self._terrain_map: dict = {}
        self._owner_map: dict = {}
        self._civ_colors: dict = {}
        self._explored: set = set()
        self._viewport: Optional[QRectF] = None
        self._W = 0; self._H = 0

    def set_viewport(self, r: QRectF):
        self._viewport = r; self.update()

    def update_data(self, terrain_map, owner_map, civ_colors, explored):
        self._terrain_map = terrain_map or {}
        self._owner_map = owner_map or {}
        self._civ_colors = civ_colors or {}
        self._explored = explored or set()
        if self._terrain_map:
            self._W = max(k[0] for k in self._terrain_map) + 1
            self._H = max(k[1] for k in self._terrain_map) + 1
        self.update()

    def mousePressEvent(self, ev):
        if not self._terrain_map: return
        mx, my = ev.position().x(), ev.position().y()
        cw = (self.width() - 4) / max(1, self._W)
        ch = (self.height() - 4) / max(1, self._H)
        cx = max(0, min(self._W - 1, int((mx - 2) / cw)))
        cy = max(0, min(self._H - 1, int((my - 2) / ch)))
        self.navigated.emit(cx, cy)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#1a1b26"))
        if not self._terrain_map: return
        W, H = self._W, self._H
        cw = (self.width() - 4) / W; ch = (self.height() - 4) / H
        for y in range(H):
            for x in range(W):
                if (x, y) not in self._explored:
                    p.fillRect(QRectF(2 + x*cw, 2 + y*ch, cw + 0.5, ch + 0.5), QColor("#16161e"))
                    continue
                tid = self._terrain_map.get((x, y), 0)
                base = QColor(TERRAIN_COLORS.get(tid, QColor(40, 40, 50)))
                owner = self._owner_map.get((x, y))
                if owner and owner in self._civ_colors:
                    cc = QColor(self._civ_colors[owner])
                    base = QColor((base.red() + cc.red()) // 2,
                                  (base.green() + cc.green()) // 2,
                                  (base.blue() + cc.blue()) // 2)
                p.fillRect(QRectF(2 + x*cw, 2 + y*ch, cw + 0.5, ch + 0.5), base)
        if self._viewport:
            vr = self._viewport
            rx = 2 + vr.x() * cw; ry = 2 + vr.y() * ch
            p.setPen(QPen(QColor("#ffffff"), 1)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(QRectF(rx, ry, vr.width() * cw, vr.height() * ch))
        p.setPen(QPen(QColor("#3b4261"), 2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()


class LeaderboardWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 10))

    def update_rankings(self, civs_data):
        sc = sorted(civs_data, key=lambda c: c.get("score", 0), reverse=True)
        medals = ["#e0af68", "#a9b1d6", "#ff9e64"]
        lines = []
        for i, civ in enumerate(sc):
            name = civ.get("name","?"); score = civ.get("score",0)
            color = civ.get("color","#7aa2f7"); pop = civ.get("population",0)
            if i < 3: medal = f'<span style="color:{medals[i]}; font-size:14px;">◆</span>'
            else: medal = f'<span style="color:#565f89; font-size:11px;">{i+1}.</span>'
            pct = min(100, (score / max(1, sc[0].get("score", 1))) * 100)
            lines.append(
                f'<div style="background:#24283b; border-left:3px solid {color}; border-radius:4px; padding:3px 6px; margin:2px 0;">'
                f'{medal} <b style="color:{color};">{name}</b> '
                f'<span style="color:#565f89;">pop {CivCard._fmt(pop)}</span> '
                f'<span style="float:right; color:#c0caf5; font-weight:bold;">{CivCard._fmt(score)}</span>'
                f'<div style="background:#1a1b26; height:3px; border-radius:1px; margin-top:2px;">'
                f'<div style="background:{color}; width:{pct:.1f}%; height:3px; border-radius:1px;"></div></div></div>')
        self.setHtml("<br>".join(lines))


class DiplomacyMatrix(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._civs = []
        self._rel: dict[tuple, str] = {}
        self.setMinimumHeight(120)

    def update_data(self, civs_data):
        self._civs = civs_data
        self._rel.clear()
        for c in civs_data:
            name = c.get("name","")
            for a in (c.get("alliances") or []):
                k = tuple(sorted([name, a]))
                if self._rel.get(k) != "War": self._rel[k] = "Allied"
            for t in (c.get("trade_partners") or []):
                k = tuple(sorted([name, t]))
                if k not in self._rel: self._rel[k] = "Trade"
            for w in (c.get("at_war_with") or []):
                k = tuple(sorted([name, w]))
                self._rel[k] = "War"
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#1a1b26"))
        n = len(self._civs)
        if n == 0: return
        cell = min(24, max(8, (self.width() - 50) // max(1, n)))
        head = cell + 4
        p.setFont(QFont("Segoe UI", 7))
        for i, c in enumerate(self._civs):
            x = head + i * cell + cell // 2
            p.setPen(QColor(c.get("color", "#c0caf5")))
            p.save(); p.translate(x, 4); p.rotate(45)
            p.drawText(0, 0, c.get("name","?")[:6]); p.restore()
        for j, c in enumerate(self._civs):
            y = head + j * cell + cell // 2 + 3
            p.setPen(QColor(c.get("color", "#c0caf5")))
            p.drawText(0, int(y), head - 4, cell,
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                       c.get("name","?")[:8])
        rel_colors = {"War": QColor("#f7768e"), "Allied": QColor("#9ece6a"),
                      "Trade": QColor("#7dcfff"), "Neutral": QColor("#24283b")}
        for i, ci in enumerate(self._civs):
            for j, cj in enumerate(self._civs):
                if i == j: col = QColor("#3b4261")
                else:
                    k = tuple(sorted([ci.get("name",""), cj.get("name","")]))
                    col = rel_colors.get(self._rel.get(k, "Neutral"), QColor("#24283b"))
                p.fillRect(head + i*cell, head + j*cell, cell - 1, cell - 1, col)
                p.setPen(QPen(QColor("#3b4261"), 1))
                p.drawRect(head + i*cell, head + j*cell, cell - 1, cell - 1)
        p.end()


class EventFeed(QTextEdit):
    _COLORS = {
        "expand":"#9ece6a","attack":"#f7768e","war":"#ff0000","alliance":"#7dcfff",
        "research":"#7aa2f7","wonder":"#e0af68","culture":"#bb9af7",
        "rebel":"#ff9e64","government":"#565f89","leader":"#c0caf5",
        "diplomacy":"#7dcfff","trade":"#9ece6a","default":"#a9b1d6",
    }
    _ICONS = {"expand":"+","attack":"!","war":"⚔","alliance":"~","research":"?","wonder":"★",
              "culture":"@","rebel":"#","government":"=","leader":"→","diplomacy":"~","trade":"$","default":"-"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 9))
        self.document().setMaximumBlockCount(200)

    def add_event(self, etype: str, text: str, year: int):
        col = self._COLORS.get(etype, self._COLORS["default"])
        icon = self._ICONS.get(etype, self._ICONS["default"])
        self.append(f'<span style="color:{col};">[{icon}] <b>Yr {year}</b> {text}</span>')

    def clear_events(self): self.clear()


class NotificationOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue = deque(maxlen=8)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(200)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hide()

    def add_notification(self, title, msg):
        self._queue.append({"title": title, "msg": msg, "alpha": 255})
        self.show(); self.raise_(); self.update()

    def _tick(self):
        if not self._queue: return
        new_q = deque(maxlen=8)
        for n in self._queue:
            n["alpha"] -= 4
            if n["alpha"] > 0: new_q.append(n)
        self._queue = new_q
        if not self._queue: self.hide()
        else: self.update()

    def paintEvent(self, ev):
        if not self._queue: return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = 10
        for n in self._queue:
            alpha = max(0, min(255, n["alpha"]))
            p.setOpacity(alpha / 255.0)
            rect = QRectF(self.width() - 260, y, 250, 36)
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0, QColor("#2f3450")); grad.setColorAt(1, QColor("#24283b"))
            p.setPen(QPen(QColor("#7aa2f7"), 1)); p.setBrush(grad)
            p.drawRoundedRect(rect, 6, 6)
            p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            p.setPen(QColor("#7aa2f7"))
            p.drawText(rect.adjusted(8, 2, -8, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, n["title"])
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(QColor("#a9b1d6"))
            p.drawText(rect.adjusted(8, 18, -8, -2), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, n["msg"])
            y += 40
        p.end()


class SectionFrame(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("SectionFrame { border: 1px solid #3b4261; border-radius: 6px; background-color: #24283b; }")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6); lay.setSpacing(4)
        h = QLabel(title)
        h.setStyleSheet("color: #7aa2f7; font-size: 11px; font-weight: bold; padding: 2px 6px; background-color: #1a2a3a; border-radius: 3px;")
        lay.addWidget(h)
        self.content = QVBoxLayout()
        self.content.setSpacing(4)
        lay.addLayout(self.content)

    def add_widget(self, w):
        self.content.addWidget(w)


# ════════════════════════════════════════════════════════════
# MAP VIEW
# ════════════════════════════════════════════════════════════
class EnhancedMapView(QGraphicsView):
    tile_hovered = Signal(int, int)
    tile_clicked = Signal(int, int)
    zoom_changed = Signal(int)
    viewport_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor(26, 27, 38)))
        self.show_fog = True
        self.show_resources = True
        self.show_borders = True
        self.show_trade_routes = True
        self._tiles: dict[tuple, QGraphicsRectItem] = {}
        self._dynamic = []
        self._tile_colors: dict[tuple, QColor] = {}
        self._noised: dict[tuple, QColor] = {}
        self._noise: dict[tuple, float] = {}
        self._map_W = 0; self._map_H = 0
        self._no_pen = QPen(Qt.PenStyle.NoPen)
        self._fog = QColor(15, 15, 25)
        self._war_pulse = 0.0
        self._zoom = 1.0
        self._last_args = None
        self._anim = QTimer(self)
        self._anim.setInterval(100)
        self._anim.timeout.connect(self._tick)
        self._anim.start()

    def _hash(self, x, y):
        n = x * 374761393 + y * 668265263 + 12345
        n = (n ^ (n >> 13)) * 1274126177
        n = n ^ (n >> 16)
        return (n & 0x7FFFFFFF) / 0x7FFFFFFF

    def _noised_color(self, x, y, base: QColor) -> QColor:
        k = (x, y)
        if k in self._noised: return self._noised[k]
        if k not in self._noise: self._noise[k] = self._hash(x, y)
        v = (self._noise[k] - 0.5) * 16
        c = QColor(_clamp(base.red() + v), _clamp(base.green() + v * 0.9), _clamp(base.blue() + v * 0.8))
        self._noised[k] = c
        return c

    def visible_scene_rect(self) -> QRectF:
        return self.mapToScene(self.viewport().rect()).boundingRect()

    def wheelEvent(self, ev):
        f = 1.15 if ev.angleDelta().y() > 0 else 1.0 / 1.15
        self._zoom = max(0.2, min(8.0, self._zoom * f))
        self.scale(f, f)
        self.zoom_changed.emit(int(self._zoom * 100))
        self.viewport_changed.emit(self.visible_scene_rect())

    def reset_view(self):
        self.resetTransform(); self._zoom = 1.0
        self.zoom_changed.emit(100)
        self.viewport_changed.emit(self.visible_scene_rect())
        if self._map_W and self._map_H:
            self.centerOn(self._map_W * TILE_SIZE / 2, self._map_H * TILE_SIZE / 2)

    def mouseMoveEvent(self, ev):
        super().mouseMoveEvent(ev)
        sp = self.mapToScene(ev.position().toPoint())
        self.tile_hovered.emit(int(sp.x()) // TILE_SIZE, int(sp.y()) // TILE_SIZE)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            sp = self.mapToScene(ev.position().toPoint())
            self.tile_clicked.emit(int(sp.x()) // TILE_SIZE, int(sp.y()) // TILE_SIZE)
        super().mousePressEvent(ev)

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.viewport_changed.emit(self.visible_scene_rect())

    def clear_map(self):
        self._scene.clear()
        self._tiles.clear(); self._dynamic.clear()
        self._tile_colors.clear(); self._noised.clear(); self._noise.clear()
        self._map_W = 0; self._map_H = 0
        self._last_args = None

    def _tick(self):
        self._war_pulse += 0.15
        if self._last_args:
            self._rebuild_dynamic()

    def update_map(self, terrain_map, owner_map, civ_colors, explored,
                   path_data=None, capitals=None, trade_routes=None,
                   active_events=None, resource_map=None, season=0, at_war_pairs=None):
        ts = TILE_SIZE
        W = max(k[0] for k in terrain_map) + 1 if terrain_map else 0
        H = max(k[1] for k in terrain_map) + 1 if terrain_map else 0
        if W != self._map_W or H != self._map_H:
            self.clear_map()
            self._map_W, self._map_H = W, H
            self._scene.setSceneRect(0, 0, W * ts, H * ts)
        path_data = path_data or []
        capitals = capitals or {}
        trade_routes = trade_routes or []
        active_events = active_events or []
        resource_map = resource_map or {}
        need_create = len(self._tiles) == 0
        for y in range(H):
            for x in range(W):
                tid = terrain_map.get((x, y), 0)
                base = TERRAIN_COLORS.get(tid, QColor(128, 128, 128))
                noised = self._noised_color(x, y, base)
                k = (x, y)
                explored_k = k in explored if explored else True
                if not explored_k and self.show_fog:
                    disp = self._fog
                elif owner_map and k in owner_map and owner_map[k]:
                    owner = owner_map[k]
                    cc = QColor(civ_colors.get(owner, "#888888"))
                    disp = QColor(
                        _clamp(int(noised.red() * 0.7 + cc.red() * 0.3)),
                        _clamp(int(noised.green() * 0.7 + cc.green() * 0.3)),
                        _clamp(int(noised.blue() * 0.7 + cc.blue() * 0.3)))
                else:
                    disp = noised
                if 0 <= season < len(SEASON_COLORS) and tid not in (0, 8):
                    sc = SEASON_COLORS[season]
                    disp = QColor(
                        _clamp(int(disp.red() * 0.85 + sc.red() * 0.15)),
                        _clamp(int(disp.green() * 0.85 + sc.green() * 0.15)),
                        _clamp(int(disp.blue() * 0.85 + sc.blue() * 0.15)))
                if need_create:
                    item = self._scene.addRect(x * ts, y * ts, ts, ts, self._no_pen, QBrush(disp))
                    item.setZValue(1)
                    self._tiles[k] = item
                    if tid == 3:
                        hl = QColor(_clamp(base.red() + 55), _clamp(base.green() + 55), _clamp(base.blue() + 55), 180)
                        self._scene.addLine(x*ts, y*ts, x*ts + ts - 1, y*ts, QPen(hl, 1)).setZValue(2)
                        self._scene.addLine(x*ts, y*ts, x*ts, y*ts + ts - 1, QPen(hl, 1)).setZValue(2)
                        sh = QColor(max(0, base.red() - 35), max(0, base.green() - 35), max(0, base.blue() - 35), 140)
                        self._scene.addLine(x*ts + ts - 1, y*ts + 1, x*ts + ts - 1, y*ts + ts - 1, QPen(sh, 1)).setZValue(2)
                        self._scene.addLine(x*ts + 1, y*ts + ts - 1, x*ts + ts - 1, y*ts + ts - 1, QPen(sh, 1)).setZValue(2)
                    if tid in (2, 5):
                        dot_c = QColor(max(0, base.red() - 20), max(0, base.green() - 15), max(0, base.blue() - 10), 140)
                        seed = x * 31 + y * 17
                        for i in range(3):
                            dx = ((seed + i * 37) % max(1, ts - 2)) + 1
                            dy = ((seed + i * 53) % max(1, ts - 2)) + 1
                            d = self._scene.addEllipse(x*ts + dx, y*ts + dy, 2, 2, self._no_pen, QBrush(dot_c))
                            d.setZValue(2)
                else:
                    if self._tile_colors.get(k) != disp:
                        self._tiles[k].setBrush(QBrush(disp))
                self._tile_colors[k] = disp
        self._last_args = {
            'terrain_map': terrain_map, 'owner_map': owner_map, 'civ_colors': civ_colors,
            'explored': explored, 'path_data': path_data, 'capitals': capitals,
            'trade_routes': trade_routes, 'active_events': active_events,
            'resource_map': resource_map, 'season': season,
            'at_war_pairs': at_war_pairs or set(),
        }
        self._rebuild_dynamic()

    def _rebuild_dynamic(self):
        if not self._last_args: return
        for it in self._dynamic:
            self._scene.removeItem(it)
        self._dynamic.clear()
        ts = TILE_SIZE
        args = self._last_args
        om = args['owner_map']; cc = args['civ_colors']
        ae = args['active_events']; tr = args['trade_routes']
        pd = args['path_data']; caps = args['capitals']
        rm = args['resource_map']
        war_pairs = args.get('at_war_pairs', set())
        if self.show_borders:
            self._draw_borders(om, cc, war_pairs, ts)
        if self.show_resources and rm:
            self._draw_resources(rm, ts)
        if ae:
            self._draw_events(ae, ts)
        if self.show_trade_routes and tr:
            self._draw_trade_routes(tr, ts, caps)
        if pd:
            self._draw_path(pd, ts)
        if caps:
            self._draw_capitals(caps, cc, ts)

    def _draw_borders(self, om, cc, war_pairs, ts):
        W, H = self._map_W, self._map_H
        for y in range(H):
            for x in range(W):
                o1 = om.get((x, y))
                if not o1: continue
                if x + 1 < W:
                    o2 = om.get((x+1, y))
                    if o2 and o2 != o1:
                        war = tuple(sorted((o1, o2))) in war_pairs
                        if war:
                            a = int(100 + 155 * (0.5 + 0.5 * math.sin(self._war_pulse)))
                            pen = QPen(QColor(247, 118, 142, a), 1.5)
                        else:
                            base = QColor(cc.get(o1, "#888888"))
                            pen = QPen(QColor(min(255, base.red() + 40), min(255, base.green() + 40), min(255, base.blue() + 40), 180), 1.5)
                        ln = self._scene.addLine((x+1)*ts, y*ts, (x+1)*ts, (y+1)*ts, pen)
                        ln.setZValue(10); self._dynamic.append(ln)
                if y + 1 < H:
                    o2 = om.get((x, y+1))
                    if o2 and o2 != o1:
                        war = tuple(sorted((o1, o2))) in war_pairs
                        if war:
                            a = int(100 + 155 * (0.5 + 0.5 * math.sin(self._war_pulse)))
                            pen = QPen(QColor(247, 118, 142, a), 1.5)
                        else:
                            base = QColor(cc.get(o1, "#888888"))
                            pen = QPen(QColor(min(255, base.red() + 40), min(255, base.green() + 40), min(255, base.blue() + 40), 180), 1.5)
                        ln = self._scene.addLine(x*ts, (y+1)*ts, (x+1)*ts, (y+1)*ts, pen)
                        ln.setZValue(10); self._dynamic.append(ln)

    def _draw_resources(self, rm, ts):
        for (x, y), res in rm.items():
            rc = RESOURCE_TYPES.get(res)
            if not rc: continue
            cx = x * ts + ts // 2; cy = y * ts + ts // 2
            s = max(2, ts // 3)
            diamond = QPolygonF([QPointF(cx, cy - s), QPointF(cx + s, cy),
                                 QPointF(cx, cy + s), QPointF(cx - s, cy)])
            it = self._scene.addPolygon(diamond, self._no_pen, QBrush(rc))
            it.setZValue(15); self._dynamic.append(it)
            ol = self._scene.addPolygon(diamond, QPen(QColor(255, 255, 255, 160), 0.8), QBrush())
            ol.setZValue(16); self._dynamic.append(ol)

    def _draw_events(self, ae, ts):
        for ev in ae:
            pos = getattr(ev, 'position', None)
            if not pos: continue
            tx, ty = pos
            px = tx * ts + ts // 2; py = ty * ts + ts // 2
            pulse = 0.6 + 0.4 * math.sin(self._war_pulse * 0.8)
            alpha = int(200 * pulse)
            col = QColor(getattr(ev, 'visual_color', '#a9b1d6'))
            col.setAlpha(alpha)
            dot = self._scene.addEllipse(px - 4, py - 4, 8, 8, self._no_pen, QBrush(col))
            dot.setZValue(20); self._dynamic.append(dot)

    def _draw_trade_routes(self, tr, ts, caps):
        pen = QPen(QColor(224, 175, 104), 2, Qt.PenStyle.DashDotLine)
        for route in tr:
            if not isinstance(route, (tuple, list)) or len(route) != 2: continue
            c1, c2 = route
            cap1 = caps.get(c1); cap2 = caps.get(c2)
            if not cap1 or not cap2: continue
            ln = self._scene.addLine(cap1[0]*ts + ts//2, cap1[1]*ts + ts//2,
                                     cap2[0]*ts + ts//2, cap2[1]*ts + ts//2, pen)
            ln.setZValue(8); self._dynamic.append(ln)

    def _draw_path(self, pd, ts):
        if len(pd) < 2: return
        pen = QPen(QColor(255, 255, 100, 200), 2, Qt.PenStyle.DashLine)
        for i in range(len(pd) - 1):
            x1, y1 = pd[i]; x2, y2 = pd[i+1]
            ln = self._scene.addLine(x1*ts + ts//2, y1*ts + ts//2,
                                     x2*ts + ts//2, y2*ts + ts//2, pen)
            ln.setZValue(18); self._dynamic.append(ln)

    def _draw_capitals(self, caps, cc, ts):
        for cn, (cx, cy) in caps.items():
            col = QColor(cc.get(cn, "#ffffff"))
            px = cx * ts + ts // 2; py = cy * ts + ts // 2
            r = TILE_SIZE * 0.6
            circ = self._scene.addEllipse(px - r, py - r, r * 2, r * 2, self._no_pen, QBrush(col))
            circ.setZValue(25); self._dynamic.append(circ)
            path = QPainterPath()
            for i in range(5):
                a1 = math.radians(-90 + i * 72)
                a2 = math.radians(-90 + i * 72 + 36)
                if i == 0:
                    path.moveTo(px + r * 0.7 * math.cos(a1), py + r * 0.7 * math.sin(a1))
                else:
                    path.lineTo(px + r * 0.7 * math.cos(a1), py + r * 0.7 * math.sin(a1))
                path.lineTo(px + r * 0.7 * 0.4 * math.cos(a2), py + r * 0.7 * 0.4 * math.sin(a2))
            path.closeSubpath()
            star = self._scene.addPath(path, self._no_pen, QBrush(QColor(255, 255, 255, 220)))
            star.setZValue(26); self._dynamic.append(star)
            ring = self._scene.addEllipse(px - r - 1, py - r - 1, (r+1)*2, (r+1)*2,
                                          QPen(QColor(255, 255, 255, 200), 1.2), QBrush())
            ring.setZValue(27); self._dynamic.append(ring)


# ════════════════════════════════════════════════════════════
# MAIN WINDOW + CONTROLLER
# ════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Civilization Simulator")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(ENHANCED_STYLESHEET)
        self.map_view = EnhancedMapView()
        self.minimap = MinimapWidget()
        self.timeline = TimelineGraph()
        self.leaderboard = LeaderboardWidget()
        self.diplomacy_matrix = DiplomacyMatrix()
        self.event_feed = EventFeed()
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.notification_overlay = NotificationOverlay(self)
        self.civ_cards: dict[str, CivCard] = {}
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()
        self._setup_shortcuts()
        self.minimap.navigated.connect(self._on_minimap_nav)
        self.map_view.viewport_changed.connect(self._on_viewport_changed)

    def _tool_btn_style(self, color: str = "#7aa2f7") -> str:
        return (f"QPushButton {{ background-color: {color}; color: #1a1b26; font-weight: bold;"
                f" border: none; border-radius: 4px; padding: 5px 12px; font-size: 12px; }}"
                f" QPushButton:hover {{ background-color: {color}cc; }}"
                f" QPushButton:pressed {{ background-color: {color}99; }}"
                f" QPushButton:checked {{ background-color: {color}; }}")

    def _build_toolbar(self):
        tb = self.addToolBar("Controls")
        tb.setMovable(False)
        self.btn_play = QPushButton("  ▶ Play  ")
        self.btn_play.setStyleSheet(self._tool_btn_style("#9ece6a"))
        self.btn_play.setFixedHeight(28); tb.addWidget(self.btn_play)
        self.btn_reset = QPushButton("  Reset View  ")
        self.btn_reset.setStyleSheet(self._tool_btn_style("#565f89"))
        self.btn_reset.setFixedHeight(28); tb.addWidget(self.btn_reset)
        tb.addSeparator()
        tb.addWidget(QLabel(" Speed: "))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(10, 500); self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(120); tb.addWidget(self.speed_slider)
        tb.addSeparator()
        tb.addWidget(QLabel(" Duration: "))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["200 years", "500 years", "1000 years", "Endless"])
        self.duration_combo.setFixedHeight(28); tb.addWidget(self.duration_combo)
        tb.addSeparator()
        tb.addWidget(QLabel(" Civs: "))
        self.civ_count_combo = QComboBox()
        self.civ_count_combo.addItems(["3", "4", "5", "6", "7", "8", "10", "12"])
        self.civ_count_combo.setCurrentText("5")
        self.civ_count_combo.setFixedHeight(28); tb.addWidget(self.civ_count_combo)
        tb.addSeparator()
        tb.addWidget(QLabel(" Terrain: "))
        self.terrain_combo = QComboBox()
        self.terrain_combo.addItems(["Continent", "Archipelago", "Pangaea", "Islands",
                                     "Highlands", "River Valley", "Crater Lake", "Mediterranean"])
        self.terrain_combo.setFixedHeight(28); tb.addWidget(self.terrain_combo)
        tb.addSeparator()
        self.chk_fog = QPushButton(" Fog ")
        self.chk_fog.setCheckable(True); self.chk_fog.setChecked(True)
        self.chk_fog.setStyleSheet(self._tool_btn_style("#7aa2f7"))
        self.chk_fog.setFixedHeight(28)
        self.chk_fog.toggled.connect(lambda v: setattr(self.map_view, "show_fog", v))
        tb.addWidget(self.chk_fog)
        self.chk_res = QPushButton(" Resources ")
        self.chk_res.setCheckable(True); self.chk_res.setChecked(True)
        self.chk_res.setStyleSheet(self._tool_btn_style("#e0af68"))
        self.chk_res.setFixedHeight(28)
        self.chk_res.toggled.connect(lambda v: setattr(self.map_view, "show_resources", v))
        tb.addWidget(self.chk_res)
        self.chk_borders = QPushButton(" Borders ")
        self.chk_borders.setCheckable(True); self.chk_borders.setChecked(True)
        self.chk_borders.setStyleSheet(self._tool_btn_style("#9ece6a"))
        self.chk_borders.setFixedHeight(28)
        self.chk_borders.toggled.connect(lambda v: setattr(self.map_view, "show_borders", v))
        tb.addWidget(self.chk_borders)
        tb.addSeparator()
        self.btn_save = QPushButton(" Save ")
        self.btn_save.setStyleSheet(self._tool_btn_style("#565f89"))
        self.btn_save.setFixedHeight(28); tb.addWidget(self.btn_save)
        self.btn_load = QPushButton(" Load ")
        self.btn_load.setStyleSheet(self._tool_btn_style("#565f89"))
        self.btn_load.setFixedHeight(28); tb.addWidget(self.btn_load)
        self.btn_new = QPushButton(" New Game ")
        self.btn_new.setStyleSheet(self._tool_btn_style("#f7768e"))
        self.btn_new.setFixedHeight(28); tb.addWidget(self.btn_new)
        tb.addSeparator()
        self.lbl_year = QLabel("Year: -3000  |  Spring  |  Gen: 0")
        self.lbl_year.setStyleSheet("color: #7aa2f7; font-size: 12px; font-weight: bold;"
                                    " padding: 3px 10px; background-color: #1a2a3a; border-radius: 4px;")
        self.lbl_year.setFixedHeight(28); tb.addWidget(self.lbl_year)

    def _build_central(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(4, 4, 4, 4); root.setSpacing(4)
        # Left: map + info
        left = QVBoxLayout(); left.setSpacing(4)
        self.map_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left.addWidget(self.map_view, stretch=1)
        self.tile_info_lbl = QLabel("Hover over a tile for info")
        self.tile_info_lbl.setStyleSheet("color: #a9b1d6; font-size: 11px; padding: 2px 6px;"
                                         " background-color: #1a1b26; border-radius: 3px;")
        self.tile_info_lbl.setFixedHeight(22)
        left.addWidget(self.tile_info_lbl)
        root.addLayout(left, stretch=3)
        # Right: panels + tabs
        right = QVBoxLayout(); right.setSpacing(4)
        mm = SectionFrame("Minimap")
        self.minimap.setFixedHeight(135)
        mm.add_widget(self.minimap)
        right.addWidget(mm)
        ev = SectionFrame("Event Feed")
        self.event_feed.setFixedHeight(135)
        ev.add_widget(self.event_feed)
        right.addWidget(ev)
        self.tabs = QTabWidget()
        civ_tab = QWidget(); cl = QVBoxLayout(civ_tab); cl.setContentsMargins(4, 4, 4, 4)
        self.civ_scroll = QScrollArea(); self.civ_scroll.setWidgetResizable(True)
        csc = QWidget(); self.civ_layout = QVBoxLayout(csc)
        self.civ_layout.setContentsMargins(2, 2, 2, 2); self.civ_layout.setSpacing(4)
        self.civ_layout.addStretch()
        self.civ_scroll.setWidget(csc); cl.addWidget(self.civ_scroll)
        self.tabs.addTab(civ_tab, "Civilizations")
        ov = QWidget(); ol = QVBoxLayout(ov); ol.setContentsMargins(4, 4, 4, 4); ol.setSpacing(4)
        tlf = SectionFrame("Timeline"); tlf.add_widget(self.timeline); ol.addWidget(tlf, stretch=1)
        lbf = SectionFrame("Leaderboard"); lbf.add_widget(self.leaderboard); ol.addWidget(lbf, stretch=1)
        dpf = SectionFrame("Diplomacy"); dpf.add_widget(self.diplomacy_matrix); ol.addWidget(dpf, stretch=1)
        self.tabs.addTab(ov, "Overview")
        lt = QWidget(); ll = QVBoxLayout(lt); ll.setContentsMargins(4, 4, 4, 4)
        ll.addWidget(self.log_view)
        self.tabs.addTab(lt, "Log")
        right.addWidget(self.tabs, stretch=1)
        root.addLayout(right, stretch=2)

    def _build_statusbar(self):
        sb = QStatusBar(); self.setStatusBar(sb)
        self.zoom_lbl = QLabel("Zoom: 100%")
        self.zoom_lbl.setStyleSheet("color: #7aa2f7; padding: 0 8px;")
        sb.addPermanentWidget(self.zoom_lbl)
        self.civ_count_lbl = QLabel("Civs: 5")
        self.civ_count_lbl.setStyleSheet("color: #9ece6a; padding: 0 8px;")
        sb.addPermanentWidget(self.civ_count_lbl)
        self.civ_count_combo.currentTextChanged.connect(
            lambda t: self.civ_count_lbl.setText(f"Civs: {t}"))

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Space"), self, activated=self._toggle_play_shortcut)
        QShortcut(QKeySequence("R"), self, activated=self.map_view.reset_view)
        QShortcut(QKeySequence("F"), self, activated=lambda: self.chk_fog.toggle())
        QShortcut(QKeySequence("G"), self, activated=lambda: self.chk_res.toggle())
        QShortcut(QKeySequence("B"), self, activated=lambda: self.chk_borders.toggle())
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.btn_save.click)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.btn_load.click)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.btn_new.click)
        QShortcut(QKeySequence("+"), self, activated=lambda: self._change_speed(+20))
        QShortcut(QKeySequence("-"), self, activated=lambda: self._change_speed(-20))

    def _change_speed(self, delta):
        v = max(10, min(500, self.speed_slider.value() + delta))
        self.speed_slider.setValue(v)

    def _toggle_play_shortcut(self):
        self.btn_play.click()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.notification_overlay.setGeometry(self.rect())

    def _on_minimap_nav(self, cx, cy):
        self.map_view.centerOn(cx * TILE_SIZE, cy * TILE_SIZE)

    def _on_viewport_changed(self, rect):
        if isinstance(rect, QRectF):
            self.minimap.set_viewport(rect)

    def update_stats(self, civs_data):
        existing = set(self.civ_cards.keys())
        new = {d["name"] for d in civs_data}
        for n in list(existing - new):
            card = self.civ_cards.pop(n)
            self.civ_layout.removeWidget(card)
            card.deleteLater()
        stretch = self.civ_layout.itemAt(self.civ_layout.count() - 1)
        if stretch and stretch.spacerItem():
            self.civ_layout.removeItem(stretch)
        for idx, d in enumerate(civs_data):
            name = d["name"]
            if name in self.civ_cards:
                self.civ_cards[name].update_data(d)
            else:
                card = CivCard(d)
                self.civ_cards[name] = card
                self.civ_layout.insertWidget(min(idx, self.civ_layout.count()), card)
        self.civ_layout.addStretch()
        self.timeline.update_data(civs_data)
        self.leaderboard.update_rankings(civs_data)
        self.diplomacy_matrix.update_data(civs_data)

    def append_log(self, text: str):
        parts = text.split(": ", 2)
        if len(parts) == 3:
            yr, cn, act = parts
            self.log_view.append(f"<span style='color:#565f89'>{yr}:</span> <b style='color:#e0af68'>{cn}</b> {act}")
            self._feed_event(yr, cn, act)
        else:
            self.log_view.append(text)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    def _feed_event(self, yr_str, cn, act):
        al = act.lower()
        type_map = {"expand":("expand","+"),"attack":("attack","!"),"war":("war","⚔"),
                    "alliance":("alliance","~"),"research":("research","?"),"wonder":("wonder","★"),
                    "culture":("culture","@"),"rebel":("rebel","#"),"government":("government","="),
                    "leader":("leader","→"),"trade":("trade","$"),"diplomac":("diplomacy","~"),
                    "peace":("diplomacy","~"),"founded":("culture","◆"),"era":("research","↑"),
                    "plague":("attack","☠"),"earthquake":("attack","☠"),"barbarian":("war","⚔")}
        et, ic = "default", "-"
        for k, (t, i) in type_map.items():
            if k in al: et, ic = t, i; break
        try: yv = int(yr_str.replace("Year ", "").strip())
        except: yv = 0
        self.event_feed.add_event(et, f"{cn}: {act}", yv)

    def show_notification(self, title, msg):
        self.notification_overlay.add_notification(title, msg)

    def get_civ_count(self) -> int:
        try: return int(self.civ_count_combo.currentText())
        except: return 5

    def get_terrain_preset(self) -> str:
        return self.terrain_combo.currentText()


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.window = MainWindow()
        self.engine: Optional[SimulationEngine] = None
        self.playing = False
        self._create_engine()
        self._connect_window()
        self._connect_engine()

    def _create_engine(self):
        self.engine = SimulationEngine(
            civ_count=self.window.get_civ_count(),
            terrain_preset=self.window.get_terrain_preset())

    def _connect_window(self):
        w = self.window
        w.btn_play.clicked.connect(self.toggle_play)
        w.btn_reset.clicked.connect(w.map_view.reset_view)
        w.speed_slider.valueChanged.connect(self._on_speed)
        w.duration_combo.currentTextChanged.connect(self._set_duration)
        w.map_view.tile_hovered.connect(self._on_tile_hover)
        w.map_view.zoom_changed.connect(self._on_zoom)
        w.btn_save.clicked.connect(self._save)
        w.btn_load.clicked.connect(self._load)
        w.btn_new.clicked.connect(self._new_game)

    def _connect_engine(self):
        if not self.engine: return
        self.engine.update_signal.connect(self._on_update)
        self.engine.log_signal.connect(self.window.append_log)
        self.engine.notification_signal.connect(self.window.show_notification)

    def _disconnect_engine(self):
        if not self.engine: return
        try:
            self.engine.update_signal.disconnect()
            self.engine.log_signal.disconnect()
            self.engine.notification_signal.disconnect()
        except: pass

    def _on_speed(self, v):
        if self.engine: self.engine.speed = v

    def _set_duration(self, text):
        m = {"200 years":200, "500 years":500, "1000 years":1000, "Endless":0}
        if self.engine: self.engine.max_years = m.get(text, 0)

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.window.btn_play.setText("  ⏸ Pause  ")
            if self.engine:
                self.engine.paused = False
                if not self.engine.isRunning(): self.engine.start()
        else:
            self.window.btn_play.setText("  ▶ Play  ")
            if self.engine: self.engine.paused = True

    def _on_tile_hover(self, tx, ty):
        if not self.engine: return
        if not (0 <= tx < self.engine.W and 0 <= ty < self.engine.H):
            self.window.tile_info_lbl.setText(f"({tx},{ty})  |  Out of bounds")
            return
        tid = self.engine.terrain_map.get((tx, ty), 0)
        t_name = TERRAIN_NAMES.get(tid, "Unknown")
        owner = self.engine.owner_map.get((tx, ty)) or "Unclaimed"
        res = self.engine.resource_map.get((tx, ty), "None")
        if res != "None": res = res.title().replace('_', ' ')
        self.window.tile_info_lbl.setText(
            f"({tx},{ty})  |  Terrain: {t_name}  |  Owner: {owner}  |  Resource: {res}")

    def _on_zoom(self, pct):
        self.window.zoom_lbl.setText(f"Zoom: {pct}%")

    def _on_update(self, data: dict):
        civ_colors = {c.name: c.color for c in data["civs"]}
        season_name = SEASON_NAMES[data["season"]]
        gen = data.get("generation", 0)
        self.window.lbl_year.setText(f"Year: {data['year']}  |  {season_name}  |  Gen: {gen}")
        self.window.map_view.update_map(
            data["terrain"], data["owners"], civ_colors, data["explored"],
            data["last_path"], data["capitals"], data["trade_routes"],
            data["active_events"], data["resource_map"], data["season"],
            data.get("at_war_pairs", set()))
        self.window.minimap.update_data(data["terrain"], data["owners"], civ_colors, data["explored"])
        ui_data = []
        for c in data["civs"]:
            ui_data.append({
                "name": c.name, "color": c.color, "population": c.population,
                "military": c.military, "technology": c.technology, "treasury": c.treasury,
                "culture": c.culture, "stability": c.stability, "score": c.score,
                "last_action": c.last_action, "buildings": c.buildings, "wonders": c.wonders,
                "alliances": list(c.alliances), "trade_partners": list(c.trade_partners),
                "at_war_with": list(c.at_war_with), "religion": c.religion,
                "era_name": c.era_name, "archetype": c.archetype,
                "archetype_label": c.archetype_label,
                "strategic_state": c.strategic_state_name, "plan_name": c.plan_name,
                "government": c.government, "government_label": c.government_label,
                "leader_name": c.leader_name, "leader_short_name": c.leader_short_name,
            })
        self.window.update_stats(ui_data)

    def _save(self):
        if not self.engine: return
        path, _ = QFileDialog.getSaveFileName(self.window, "Save Game", "civ_save.json", "JSON Files (*.json)")
        if path:
            was = self.engine.running
            self.engine.paused = True
            self.engine.save_game(path)
            if was: self.engine.paused = False

    def _load(self):
        path, _ = QFileDialog.getOpenFileName(self.window, "Load Game", "", "JSON Files (*.json)")
        if path and self.engine:
            self.engine.paused = True
            self.engine.load_game(path)
            self.playing = False
            self.window.btn_play.setText("  ▶ Play  ")
            for card in list(self.window.civ_cards.values()):
                self.window.civ_layout.removeWidget(card); card.deleteLater()
            self.window.civ_cards.clear()
            self.window.map_view.clear_map()

    def _new_game(self):
        if self.engine:
            self.engine.running = False
            self.engine.paused = True
            try: self.engine.wait(2000)
            except: pass
            try: self.engine.analytics.commit()
            except: pass
            self._disconnect_engine()
        self.playing = False
        self.window.btn_play.setText("  ▶ Play  ")
        for card in list(self.window.civ_cards.values()):
            self.window.civ_layout.removeWidget(card); card.deleteLater()
        self.window.civ_cards.clear()
        self.window.log_view.clear()
        self.window.event_feed.clear_events()
        self.window.map_view.clear_map()
        self._create_engine()
        self._connect_engine()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


# ════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    controller = AppController()
    controller.run()