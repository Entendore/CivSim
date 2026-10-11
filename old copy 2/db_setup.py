"""
db_setup.py
Handles all SQLite database creation, population, and analytics for a
civilization *simulation* — emergent history from rules, not player clicks.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from enum import IntEnum
from typing import Any

from PySide6.QtGui import QColor

DB_PATH = "civ.sqlite"

__all__ = [
    "Terrain", "Relation", "Government", "ResourceCat",
    "GameDefs", "AnalyticsDatabase", "DB_PATH",
]


# ════════════════════════════════════════════════════════════
# Core Enums
# ════════════════════════════════════════════════════════════
class Terrain(IntEnum):
    OCEAN    = 0
    COAST    = 1
    PLAINS   = 2
    GRASSLAND= 3
    FOREST   = 4
    JUNGLE   = 5
    HILLS    = 6
    MOUNTAIN = 7
    DESERT   = 8
    TUNDRA   = 9
    SWAMP    = 10
    RIVER    = 11


class Relation(IntEnum):
    NEUTRAL      = 0
    FRIENDLY     = 1
    ALLIED       = 2
    VASSAL       = 3
    TRIBUTARY    = 4
    HOSTILE      = 5
    AT_WAR       = 6
    COLD_WAR     = 7


class Government(IntEnum):
    TRIBAL       = 0
    CHIEFDOM     = 1
    MONARCHY     = 2
    FEUDALISM    = 3
    THEOCRACY    = 4
    REPUBLIC     = 5
    OLIGARCHY    = 6
    DICTATORSHIP = 7
    DEMOCRACY    = 8
    COMMUNISM    = 9
    FASCISM      = 10
    TECHNOCRACY  = 11


class ResourceCat(IntEnum):
    BONUS      = 0
    STRATEGIC  = 1
    LUXURY     = 2
    FOOD       = 3


# ════════════════════════════════════════════════════════════
# Schema DDL — Definition Tables
# ════════════════════════════════════════════════════════════
_SCHEMA_SQL = """
-- ── Civ identity ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS def_civ_names (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS def_civ_colors (
    id INTEGER PRIMARY KEY,
    r  INTEGER NOT NULL, g INTEGER NOT NULL, b INTEGER NOT NULL
);

-- ── Map / terrain ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS def_terrain (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cr INTEGER, cg INTEGER, cb INTEGER,
    food REAL DEFAULT 0,
    production REAL DEFAULT 0,
    trade REAL DEFAULT 0,
    movement_cost REAL DEFAULT 1,
    defense_bonus REAL DEFAULT 0,
    is_water INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS def_biomes (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    terrain_ids TEXT NOT NULL,
    cr INTEGER, cg INTEGER, cb INTEGER,
    growth_mod  REAL DEFAULT 1.0
);
CREATE TABLE IF NOT EXISTS def_natural_wonders (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    terrain_id INTEGER,
    effect     TEXT,
    bonus      REAL,
    desc_text  TEXT,
    cr INTEGER, cg INTEGER, cb INTEGER
);
CREATE TABLE IF NOT EXISTS def_resources (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    INTEGER NOT NULL,
    terrain_id  INTEGER,
    food_bonus  REAL DEFAULT 0,
    prod_bonus  REAL DEFAULT 0,
    trade_bonus REAL DEFAULT 0,
    cr INTEGER, cg INTEGER, cb INTEGER
);

-- ── Government & politics ────────────────────────────────
CREATE TABLE IF NOT EXISTS def_government_types (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    min_era_id      INTEGER DEFAULT 0,
    stability_mod   REAL DEFAULT 0,
    growth_mod      REAL DEFAULT 0,
    culture_mod     REAL DEFAULT 0,
    mil_mod         REAL DEFAULT 0,
    tech_mod        REAL DEFAULT 0,
    trade_mod       REAL DEFAULT 0,
    faith_mod       REAL DEFAULT 0,
    revolt_chance   REAL DEFAULT 0,
    desc_text       TEXT,
    cr INTEGER, cg INTEGER, cb INTEGER
);
CREATE TABLE IF NOT EXISTS def_policies (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    min_era_id  INTEGER DEFAULT 0,
    min_gov_id  INTEGER,
    effect      TEXT NOT NULL,
    bonus       REAL,
    desc_text   TEXT
);
CREATE TABLE IF NOT EXISTS def_ideologies (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    cr INTEGER, cg INTEGER, cb INTEGER,
    stability_mod REAL DEFAULT 0,
    culture_mod   REAL DEFAULT 0,
    mil_mod       REAL DEFAULT 0,
    desc_text TEXT
);
CREATE TABLE IF NOT EXISTS def_social_classes (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    base_happiness REAL DEFAULT 50.0,
    base_prod_mod  REAL DEFAULT 1.0,
    base_tax_rate  REAL DEFAULT 0.1,
    political_power REAL DEFAULT 0.1,
    desc_text   TEXT
);

-- ── Technology ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS def_technologies (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    era_id      INTEGER NOT NULL,
    cost        REAL NOT NULL,
    category    TEXT NOT NULL,
    prereq_ids  TEXT DEFAULT '',
    effect      TEXT,
    bonus       REAL,
    desc_text   TEXT
);

-- ── Buildings & improvements ─────────────────────────────
CREATE TABLE IF NOT EXISTS def_buildings (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    cost        REAL NOT NULL,
    min_tech_id INTEGER,
    min_era_id  INTEGER DEFAULT 0,
    effect      TEXT NOT NULL,
    bonus       REAL,
    maintenance REAL DEFAULT 0,
    desc_text   TEXT
);
CREATE TABLE IF NOT EXISTS def_improvements (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    terrain_id  INTEGER,
    cost        REAL NOT NULL,
    min_tech_id INTEGER,
    effect      TEXT NOT NULL,
    food_bonus  REAL DEFAULT 0,
    prod_bonus  REAL DEFAULT 0,
    trade_bonus REAL DEFAULT 0,
    desc_text   TEXT
);

-- ── Culture & religion ──────────────────────────────────
CREATE TABLE IF NOT EXISTS def_religions (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    cr INTEGER, cg INTEGER, cb INTEGER,
    tenet     TEXT,
    spread_rate REAL DEFAULT 0.05
);
CREATE TABLE IF NOT EXISTS def_cultural_traits (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    effect      TEXT NOT NULL,
    bonus       REAL,
    desc_text   TEXT
);

-- ── Military ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS def_unit_types (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL,
    era_id       INTEGER NOT NULL,
    cost         REAL NOT NULL,
    attack       REAL NOT NULL,
    defense      REAL NOT NULL,
    hp           REAL DEFAULT 100,
    movement     REAL DEFAULT 2,
    min_tech_id  INTEGER,
    desc_text    TEXT
);

-- ── Diplomacy ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS def_relations (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cr INTEGER, cg INTEGER, cb INTEGER
);
CREATE TABLE IF NOT EXISTS def_treaty_types (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    duration    INTEGER DEFAULT 0,
    effect      TEXT,
    desc_text   TEXT
);

-- ── Great people & works ─────────────────────────────────
CREATE TABLE IF NOT EXISTS def_great_leaders (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    effect    TEXT NOT NULL,
    bonus     REAL,
    desc_text TEXT,
    min_era   TEXT
);
CREATE TABLE IF NOT EXISTS def_great_works (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    category  TEXT NOT NULL,
    culture   REAL DEFAULT 0,
    tourism   REAL DEFAULT 0,
    era_id    INTEGER,
    desc_text TEXT
);

-- ── Wonders ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS def_wonders (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    cost      REAL NOT NULL,
    min_tech  REAL,
    effect    TEXT,
    bonus     REAL,
    desc_text TEXT
);

-- ── Events, Disasters & Diseases ────────────────────────
CREATE TABLE IF NOT EXISTS def_disasters (
    id             INTEGER PRIMARY KEY,
    name           TEXT NOT NULL,
    category       TEXT NOT NULL,
    severity       REAL DEFAULT 1.0,
    pop_kill_pct   REAL DEFAULT 0,
    prod_damage    REAL DEFAULT 0,
    terrain_ids    TEXT,
    min_era_id     INTEGER DEFAULT 0,
    desc_text      TEXT
);
CREATE TABLE IF NOT EXISTS def_diseases (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    spread_rate   REAL DEFAULT 0.1,
    mortality     REAL DEFAULT 0.05,
    duration      INTEGER DEFAULT 10,
    min_era_id    INTEGER DEFAULT 0,
    cure_tech_id  INTEGER,
    desc_text     TEXT
);
CREATE TABLE IF NOT EXISTS def_events (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    probability REAL DEFAULT 0.01,
    min_era_id  INTEGER DEFAULT 0,
    effect      TEXT NOT NULL,
    bonus       REAL,
    desc_text   TEXT
);

-- ── Eras, Espionage, Achievements, Settings ─────────────
CREATE TABLE IF NOT EXISTS def_eras (
    id            INTEGER PRIMARY KEY,
    tech_threshold REAL NOT NULL,
    era_name      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS def_espionage_missions (
    mission_type TEXT PRIMARY KEY,
    cost         REAL NOT NULL,
    success_rate REAL NOT NULL,
    desc_text    TEXT
);
CREATE TABLE IF NOT EXISTS def_achievements (
    achievement_id TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    desc_text     TEXT,
    icon          TEXT
);
CREATE TABLE IF NOT EXISTS def_settings (
    key   TEXT PRIMARY KEY,
    value REAL
);

-- ── Indexes ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_tech_era     ON def_technologies(era_id);
CREATE INDEX IF NOT EXISTS idx_building_cat ON def_buildings(category);
CREATE INDEX IF NOT EXISTS idx_unit_era     ON def_unit_types(era_id);
CREATE INDEX IF NOT EXISTS idx_resource_cat ON def_resources(category);
CREATE INDEX IF NOT EXISTS idx_disaster_cat ON def_disasters(category);
CREATE INDEX IF NOT EXISTS idx_event_cat    ON def_events(category);
"""

# ════════════════════════════════════════════════════════════
# Analytics Schema
# ════════════════════════════════════════════════════════════
_ANALYTICS_SCHEMA_SQL = """
-- ── Game-level ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS games (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time    TEXT,
    end_time      TEXT,
    total_years   INTEGER DEFAULT 0,
    winner_name   TEXT,
    victory_type  TEXT,
    map_seed      INTEGER,
    civ_count     INTEGER DEFAULT 0,
    map_width     INTEGER DEFAULT 0,
    map_height    INTEGER DEFAULT 0
);

-- ── Per-turn snapshots ──────────────────────────────────
CREATE TABLE IF NOT EXISTS turn_snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id     INTEGER NOT NULL,
    year        INTEGER NOT NULL,
    civ_name    TEXT NOT NULL,
    population  INTEGER,
    technology  REAL,
    culture     REAL,
    military    REAL,
    territories INTEGER,
    score       REAL,
    religion    TEXT,
    era         TEXT,
    government  TEXT,
    stability   REAL,
    happiness   REAL,
    treasury    REAL DEFAULT 0,
    food_total  REAL DEFAULT 0,
    prod_total  REAL DEFAULT 0,
    trade_total REAL DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Civ lifetime ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS civ_lifetimes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id           INTEGER NOT NULL,
    civ_name          TEXT NOT NULL,
    starting_culture  TEXT,
    religion          TEXT,
    government        TEXT,
    start_year        INTEGER,
    end_year          INTEGER,
    peak_population   INTEGER DEFAULT 0,
    peak_territory    INTEGER DEFAULT 0,
    cause_of_death    TEXT DEFAULT 'Alive',
    wonder_count      INTEGER DEFAULT 0,
    leader_count      INTEGER DEFAULT 0,
    wars_fought       INTEGER DEFAULT 0,
    wars_won          INTEGER DEFAULT 0,
    golden_age_turns  INTEGER DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── War & treaty history ────────────────────────────────
CREATE TABLE IF NOT EXISTS war_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    attacker      TEXT NOT NULL,
    defender      TEXT NOT NULL,
    start_year    INTEGER NOT NULL,
    end_year      INTEGER,
    attacker_casualties INTEGER DEFAULT 0,
    defender_casualties INTEGER DEFAULT 0,
    winner        TEXT,
    war_cause     TEXT,
    territory_changed INTEGER DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);
CREATE TABLE IF NOT EXISTS treaty_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    civ_a         TEXT NOT NULL,
    civ_b         TEXT NOT NULL,
    treaty_type   TEXT NOT NULL,
    year_signed   INTEGER NOT NULL,
    year_broken   INTEGER,
    broken_by     TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Territory changes ───────────────────────────────────
CREATE TABLE IF NOT EXISTS territory_changes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id     INTEGER NOT NULL,
    year        INTEGER NOT NULL,
    civ_gaining TEXT NOT NULL,
    civ_losing  TEXT,
    tile_x      INTEGER NOT NULL,
    tile_y      INTEGER NOT NULL,
    reason      TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Population & Demographics ───────────────────────────
CREATE TABLE IF NOT EXISTS population_detail (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id     INTEGER NOT NULL,
    year        INTEGER NOT NULL,
    civ_name    TEXT NOT NULL,
    tile_x      INTEGER NOT NULL,
    tile_y      INTEGER NOT NULL,
    population  INTEGER DEFAULT 0,
    growth_rate REAL DEFAULT 0,
    migration_in  INTEGER DEFAULT 0,
    migration_out INTEGER DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);
CREATE TABLE IF NOT EXISTS demographics_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id         INTEGER NOT NULL,
    year            INTEGER NOT NULL,
    civ_name        TEXT NOT NULL,
    class_name      TEXT NOT NULL,
    population_pct  REAL DEFAULT 0,
    happiness       REAL DEFAULT 50.0,
    political_power REAL DEFAULT 0.0,
    wealth_pct      REAL DEFAULT 0.0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Economic Cycles ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS economic_cycle_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    year          INTEGER NOT NULL,
    civ_name      TEXT NOT NULL,
    phase         TEXT NOT NULL,         -- boom / recession / depression / recovery
    gdp           REAL DEFAULT 0,
    inflation     REAL DEFAULT 0,
    unemployment  REAL DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Cultural & religious diffusion ──────────────────────
CREATE TABLE IF NOT EXISTS cultural_diffusion_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id         INTEGER NOT NULL,
    year            INTEGER NOT NULL,
    source_civ      TEXT NOT NULL,
    target_civ      TEXT NOT NULL,
    trait_name      TEXT,
    intensity       REAL DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);
CREATE TABLE IF NOT EXISTS religion_spread_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id         INTEGER NOT NULL,
    year            INTEGER NOT NULL,
    religion        TEXT NOT NULL,
    civ_name        TEXT NOT NULL,
    tile_x          INTEGER,
    tile_y          INTEGER,
    spread_method   TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Technology spread ───────────────────────────────────
CREATE TABLE IF NOT EXISTS tech_discovery_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id     INTEGER NOT NULL,
    year        INTEGER NOT NULL,
    civ_name    TEXT NOT NULL,
    tech_name   TEXT NOT NULL,
    method      TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Disasters & diseases ────────────────────────────────
CREATE TABLE IF NOT EXISTS disaster_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    year          INTEGER NOT NULL,
    disaster_name TEXT NOT NULL,
    civ_name      TEXT,
    tile_x        INTEGER,
    tile_y        INTEGER,
    severity      REAL,
    deaths        INTEGER DEFAULT 0,
    damage        REAL DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);
CREATE TABLE IF NOT EXISTS disease_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    year_start    INTEGER NOT NULL,
    year_end      INTEGER,
    disease_name  TEXT NOT NULL,
    civ_name      TEXT NOT NULL,
    total_deaths  INTEGER DEFAULT 0,
    spread_tiles  INTEGER DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Political events ────────────────────────────────────
CREATE TABLE IF NOT EXISTS political_events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    year          INTEGER NOT NULL,
    civ_name      TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    old_gov       TEXT,
    new_gov       TEXT,
    leader_name   TEXT,
    desc_text     TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Leader tenures ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS leader_tenures (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    civ_name      TEXT NOT NULL,
    leader_name   TEXT NOT NULL,
    start_year    INTEGER NOT NULL,
    end_year      INTEGER,
    end_cause     TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Trade routes ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trade_route_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id       INTEGER NOT NULL,
    year          INTEGER NOT NULL,
    civ_a         TEXT NOT NULL,
    civ_b         TEXT NOT NULL,
    route_type    TEXT,
    volume        REAL DEFAULT 0,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Achievements ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS achievements (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id        INTEGER NOT NULL,
    civ_name       TEXT NOT NULL,
    achievement_id TEXT NOT NULL,
    year           INTEGER NOT NULL,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

-- ── Analytics indexes ───────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_snap_game_year   ON turn_snapshots(game_id, year);
CREATE INDEX IF NOT EXISTS idx_snap_civ         ON turn_snapshots(game_id, civ_name);
CREATE INDEX IF NOT EXISTS idx_war_game         ON war_history(game_id);
CREATE INDEX IF NOT EXISTS idx_treaty_game      ON treaty_history(game_id);
CREATE INDEX IF NOT EXISTS idx_terr_change_game ON territory_changes(game_id, year);
CREATE INDEX IF NOT EXISTS idx_pop_game_year    ON population_detail(game_id, year);
CREATE INDEX IF NOT EXISTS idx_demo_game_year   ON demographics_log(game_id, year);
CREATE INDEX IF NOT EXISTS idx_econ_game_year   ON economic_cycle_log(game_id, year);
CREATE INDEX IF NOT EXISTS idx_cultdiff_game    ON cultural_diffusion_log(game_id);
CREATE INDEX IF NOT EXISTS idx_relgsp_game      ON religion_spread_log(game_id);
CREATE INDEX IF NOT EXISTS idx_techdisc_game    ON tech_discovery_log(game_id);
CREATE INDEX IF NOT EXISTS idx_disaster_game    ON disaster_log(game_id);
CREATE INDEX IF NOT EXISTS idx_political_game   ON political_events(game_id);
CREATE INDEX IF NOT EXISTS idx_leader_game      ON leader_tenures(game_id);
"""

# ════════════════════════════════════════════════════════════
# Default Data
# ════════════════════════════════════════════════════════════

_DEFAULT_CIV_NAMES = [
    "Aethoria", "Byzantia", "Celestia", "Drakonia", "Elysium",
    "Ferrum", "Glacialis", "Heliopolis", "Ithaca", "Jadea",
    "Krakentia", "Lumina", "Mythoria", "Nyxium", "Olympia",
    "Pyrathia", "Quasaria", "Riven", "Solara", "Tempestia",
    "Umbra", "Valoria", "Wyrmitis", "Xanthia", "Zephyria",
    "Ashgard", "Borealis", "Cinderfall", "Duskhold", "Everpeak",
    "Frostmere", "Goldreach", "Hearthfire", "Ironveil", "Jasperia",
    "Kindlemark", "Lornvale", "Mistral", "Northspire", "Oakhaven",
]

_DEFAULT_CIV_COLORS = [
    (215, 55, 55),  (55,105,215), (55,175, 55), (215,175, 30), (165, 55,215),
    (55,195,195),   (215,125,30), (195, 55,125), (135,195, 55), (175,125, 55),
    (100,155,215),  (215,100,100), (80,200,160), (200, 80,180), (160,140, 80),
    (80,120,200),   (200,160, 60), (120, 60,160), (60,180,140), (180,100, 60),
]

_DEFAULT_TERRAIN = [
    #  id, name,        cr,  cg,  cb,  food, prod, trade, move, def, is_water
    ( 0, "Ocean",        22,  50, 115, 0.0, 0.0, 0.0, 99, 0.0, 1),
    ( 1, "Coast",        50, 100, 170, 1.0, 0.0, 1.0,  3, 0.0, 1),
    ( 2, "Plains",      125, 182,  82, 2.0, 1.0, 1.0,  1, 0.0, 0),
    ( 3, "Grassland",   140, 200,  90, 3.0, 0.5, 0.5,  1, 0.0, 0),
    ( 4, "Forest",       42, 122,  42, 1.0, 2.0, 0.5,  2, 0.15,0),
    ( 5, "Jungle",       30, 140,  30, 2.0, 0.5, 0.5,  3, 0.10,0),
    ( 6, "Hills",       155, 142, 102, 1.0, 2.0, 0.5,  2, 0.20,0),
    ( 7, "Mountain",    142, 132, 122, 0.0, 3.0, 0.0,  4, 0.35,0),
    ( 8, "Desert",      208, 182, 102, 0.0, 0.5, 1.0,  2, 0.0, 0),
    ( 9, "Tundra",      198, 212, 222, 0.5, 0.5, 0.0,  2, 0.05,0),
    (10, "Swamp",        60, 100,  50, 1.5, 0.0, 0.0,  3, 0.10,0),
    (11, "River",        70, 140, 200, 2.0, 1.0, 2.0,  1, 0.05,0),
]

_DEFAULT_BIOMES = [
    (0, "Temperate",     "2,3,4,6,11",     130, 180, 100, 1.0),
    (1, "Tropical",      "4,5,10",          40, 150,  60, 1.2),
    (2, "Arid",          "8",              210, 185, 110, 0.6),
    (3, "Boreal",        "4,9",            160, 190, 200, 0.5),
    (4, "Coastal",       "1,11",            70, 150, 200, 1.1),
    (5, "Highland",      "6,7",            150, 135, 115, 0.7),
]

_DEFAULT_NATURAL_WONDERS = [
    (0, "Mount Olympus",    7, "military",   0.10, "+10% Military",       200,180,255),
    (1, "Fountain of Youth",4, "growth",     0.10, "+10% Growth",         100,255,200),
    (2, "Grand Canyon",     8, "culture",    3.0,  "+3 Culture/turn",     255,130, 80),
    (3, "Crystal Caves",    7, "tech",       0.2,  "+0.2 Tech",           180,120,255),
    (4, "Sacred Oasis",     8, "faith",      0.15, "+0.15 Faith",         255,220,100),
    (5, "Ancient Grove",    4, "stability",  5.0,  "+5 Stability",         60,200, 60),
    (6, "Frozen Falls",     9, "trade",      0.15, "+15% Trade",          180,220,255),
    (7, "Volcanic Springs", 7, "resources",  3.0,  "+3 Res/turn",         255, 80, 40),
    (8, "Coral Reef",       1, "naval",      0.20, "+20% Naval",           60,220,200),
    (9, "Whispering Dunes", 8, "espionage",  0.20, "+20% Espionage",      230,200,120),
]

_DEFAULT_RESOURCES = [
    (0,  "Wheat",         3,   3,       2.0,  0.0,  0.0,  220, 200, 80),
    (1,  "Rice",          3,   5,       2.0,  0.0,  0.0,  180, 220, 80),
    (2,  "Cattle",        3,   3,       1.5,  1.0,  0.0,  180, 120, 80),
    (3,  "Fish",          3,   1,       2.0,  0.0,  0.5,  120, 160, 220),
    (4,  "Iron",          1,   6,       0.0,  3.0,  0.0,  160, 160, 170),
    (5,  "Copper",        1,   6,       0.0,  2.0,  1.0,  200, 140, 80),
    (6,  "Horses",        1,   2,       0.0,  1.0,  0.0,  180, 140, 100),
    (7,  "Coal",          1,   6,       0.0,  4.0,  0.0,   80,  80,  80),
    (8,  "Oil",           1,   8,       0.0,  3.0,  2.0,   60,  60,  60),
    (9,  "Uranium",       1,   7,       0.0,  5.0,  0.0,   80, 220,  80),
    (10, "Gold",          2,   6,       0.0,  0.0,  4.0,  255, 220, 50),
    (11, "Silver",        2,   7,       0.0,  0.0,  3.0,  210, 210, 220),
    (12, "Gems",          2,   7,       0.0,  0.0,  5.0,  220,  80, 200),
    (13, "Incense",       2,   8,       0.0,  0.0,  2.0,  220, 200, 160),
    (14, "Silk",          2,   4,       0.0,  0.0,  3.0,  240, 230, 200),
    (15, "Spices",        2,   5,       0.0,  0.0,  3.0,  200, 100, 50),
    (16, "Marble",        0,   6,       0.0,  2.0,  1.0,  230, 230, 240),
    (17, "Stone",         0,   7,       0.0,  2.0,  0.0,  190, 185, 180),
    (18, "Wood",          0,   4,       0.0,  2.0,  0.5,  140, 100, 60),
    (19, "Salt",          0,   8,       0.0,  0.0,  1.0,  240, 240, 240),
]

_DEFAULT_GOVERNMENTS = [
    # id, name,         min_era, stab, grow,  cult,  mil,   tech,  trade, faith, revolt, desc,                             cr,  cg,  cb
    (0,  "Tribal",      0,      -2,    0.0,   -0.5,  0.0,  -0.3,  -0.3,   0.2,  0.15, "Loose kinship bands",            160, 140, 100),
    (1,  "Chiefdom",    0,       0,    0.05,   0.0,   0.1,  -0.1,   0.0,   0.1,  0.10, "Centralized tribal rule",        180, 150, 110),
    (2,  "Monarchy",    1,       2,    0.0,    0.1,   0.1,   0.0,   0.0,   0.1,  0.05, "Divine right to rule",           200, 170,  50),
    (3,  "Feudalism",   2,       1,   -0.05,   0.0,   0.2,  -0.1,  -0.1,   0.1,  0.08, "Decentralized land ownership",   150, 120,  80),
    (4,  "Theocracy",   1,       3,   -0.05,   0.3,  -0.1,  -0.2,   0.0,   0.5,  0.02, "Rule by religious clergy",       220, 200, 100),
    (5,  "Republic",    2,       1,    0.05,   0.2,  -0.1,   0.1,   0.2,  -0.1,  0.04, "Representative citizen rule",    100, 150, 220),
    (6,  "Oligarchy",   1,      -1,    0.0,    0.0,   0.0,   0.1,   0.3,  -0.1,  0.07, "Rule by wealthy elite",          120, 120, 140),
    (7,  "Dictatorship",3,      -3,    0.0,   -0.2,   0.4,  -0.2,  -0.2,  -0.2,  0.12, "Absolute authoritarian control", 180,  50,  50),
    (8,  "Democracy",   4,       2,    0.1,    0.3,  -0.2,   0.2,   0.2,  -0.1,  0.01, "Universal suffrage and rights",  80,  180, 220),
    (9,  "Communism",   5,       1,    0.05,   0.1,   0.2,   0.1,  -0.3,  -0.3,  0.06, "Stateless classless society",    200,  50,  50),
    (10, "Fascism",     5,      -2,    0.0,   -0.1,   0.5,   0.0,  -0.1,   0.0,  0.10, "Ultranationalist autocracy",     60,  60,   60),
    (11, "Technocracy", 5,       3,    0.0,    0.1,   0.0,   0.5,   0.2,  -0.2,  0.03, "Rule by technical experts",      100, 220, 220),
]

_DEFAULT_POLICIES = [
    (0, "Agrarian Reform",  "economic",  1, None, "growth",   0.10, "Redistributes land to boost growth"),
    (1, "Conscription",     "military",  2, None, "military", 0.15, "Forced military service"),
    (2, "Emancipation",     "social",    3, None, "happiness",5.0,  "Outlaws slavery, improves happiness"),
    (3, "Free Market",      "economic",  4, 5,  "trade",    0.20, "Deregulated trade"),
    (4, "State Religion",   "diplomatic",1, 4,  "faith",    0.20, "Official religion boosts faith"),
    (5, "Secularism",       "social",    4, 5,  "tech",     0.15, "Separation of church and state"),
    (6, "Militarism",       "military",  3, 7,  "mil_mod",  0.20, "Society geared for war"),
    (7, "Welfare State",    "economic",  5, 8,  "stability",5.0,  "Social safety nets"),
]

_DEFAULT_IDEOLOGIES = [
    (0, "Traditionalism",  150, 100, 50,  2.0, -0.1, -0.1, "Preservation of ancient ways"),
    (1, "Liberalism",      100, 150, 220, 0.0,  0.1, -0.1, "Individual rights and freedom"),
    (2, "Socialism",       200, 50,  50,  1.0,  0.1,  0.0, "Collective ownership"),
    (3, "Nationalism",     60,  60,  120,-1.0,  0.0,  0.2, "Supremacy of the nation-state"),
]

_DEFAULT_SOCIAL_CLASSES = [
    (0, "Rulers",      70.0, 1.0, 0.0,  0.50, "The governing elite"),
    (1, "Nobility",    65.0, 1.0, 0.05, 0.25, "Aristocratic lords"),
    (2, "Clergy",      60.0, 1.0, 0.05, 0.15, "Religious leaders"),
    (3, "Burghers",    55.0, 1.2, 0.10, 0.05, "Wealthy merchants"),
    (4, "Artisans",    50.0, 1.5, 0.08, 0.02, "Skilled craftsmen"),
    (5, "Peasants",    40.0, 1.0, 0.15, 0.02, "Agricultural workers"),
    (6, "Slaves",      20.0, 0.5, 0.00, 0.00, "Bound servants"),
]

_DEFAULT_TECHNOLOGIES = [
    # id, name,            era, cost, cat,       prereq, effect,       bonus, desc
    (0,  "Pottery",        0,   5,    "economic", "",     "growth",     0.05,  "Food storage"),
    (1,  "Masonry",        0,   8,    "economic", "",     "production", 0.10,  "Stone working"),
    (2,  "Bronze Working", 0,  12,    "military", "",     "military",   0.10,  "Bronze weapons"),
    (3,  "Writing",        0,  15,    "cultural", "",     "tech",       0.15,  "Record keeping"),
    (4,  "Iron Working",   1,  25,    "military", "2",    "military",   0.20,  "Iron weapons"),
    (5,  "Mathematics",    1,  30,    "cultural", "3",    "tech",       0.20,  "Abstract reasoning"),
    (6,  "Currency",       1,  20,    "economic", "3",    "trade",      0.20,  "Standardized trade"),
    (7,  "Construction",   1,  22,    "economic", "1",    "production", 0.15,  "Major buildings"),
    (8,  "Feudalism",      2,  40,    "civic",    "7",    "stability",  5.0,   "Social hierarchy"),
    (9,  "Machinery",      2,  45,    "economic", "5,7",  "production", 0.25,  "Mechanical power"),
    (10, "Gunpowder",      3,  60,    "military", "4,9",  "military",   0.30,  "Explosive weapons"),
    (11, "Printing Press", 3,  55,    "cultural", "3,9",  "culture",    0.30,  "Mass communication"),
    (12, "Banking",        3,  50,    "economic", "6",    "trade",      0.30,  "Financial systems"),
    (13, "Industrialization",4, 80,   "economic", "9,12", "production", 0.50,  "Mass production"),
    (14, "Rifling",        4,  85,    "military", "10",   "military",   0.40,  "Modern firearms"),
    (15, "Electricity",    4,  90,    "economic", "13",   "tech",       0.40,  "Electrical power"),
    (16, "Computers",      5,  120,   "economic", "15",   "tech",       0.60,  "Digital revolution"),
    (17, "Nuclear Fission",5,  130,   "military", "15",   "military",   0.80,  "Atomic power"),
]

_DEFAULT_BUILDINGS = [
    # id, name,         cat,         cost, tech, era, effect,      bonus, maint, desc
    (0,  "Granary",     "infrastructure",10,  0,   0, "growth",    0.10,  0, "Stores food"),
    (1,  "Monument",    "cultural",      15, -1,   0, "culture",   2.0,   0, "Cultural identity"),
    (2,  "Barracks",    "military",      25,  2,   0, "military",  0.10,  1, "Trains soldiers"),
    (3,  "Library",     "cultural",      40,  3,   0, "tech",      0.10,  1, "Stores knowledge"),
    (4,  "Market",      "economic",      30,  6,   1, "trade",     0.15,  1, "Trade hub"),
    (5,  "Workshop",    "economic",      35,  7,   1, "production",0.15,  1, "Manufacturing"),
    (6,  "Temple",      "religious",     30, -1,   0, "faith",     0.10,  1, "Religious site"),
    (7,  "Castle",      "military",      60,  8,   2, "defense",   0.25,  2, "Fortification"),
    (8,  "University",  "cultural",      80,  5,   2, "tech",      0.20,  2, "Higher learning"),
    (9,  "Bank",        "economic",      70, 12,   3, "trade",     0.30,  2, "Financial center"),
    (10, "Factory",     "economic",     100, 13,   4, "production",0.40,  3, "Industrial plant"),
    (11, "Hospital",    "infrastructure",90, 15,   4, "growth",    0.20,  2, "Healthcare"),
    (12, "Research Lab","cultural",     120, 16,   5, "tech",      0.40,  3, "Cutting-edge science"),
]

_DEFAULT_IMPROVEMENTS = [
    # id, name,         terrain, cost, tech, effect,       food, prod, trade, desc
    (0, "Farm",         3,       5,    0,    "food_bonus", 2.0, 0.0, 0.0, "Cultivates crops"),
    (1, "Mine",         6,       8,    1,    "prod_bonus", 0.0, 3.0, 0.0, "Extracts minerals"),
    (2, "Lumber Mill",  4,       6,    0,    "prod_bonus", 0.0, 2.0, 0.0, "Harvests wood"),
    (3, "Pasture",      2,       5,    0,    "food_bonus", 1.0, 1.0, 0.0, "Grazes livestock"),
    (4, "Plantation",   5,       7,    0,    "trade_bonus",0.0, 0.0, 3.0, "Grows luxury crops"),
    (5, "Quarry",       7,      10,    1,    "prod_bonus", 0.0, 4.0, 0.0, "Cuts stone"),
    (6, "Fishing Boats",1,       6,    0,    "food_bonus", 2.0, 0.0, 1.0, "Harvests the sea"),
    (7, "Trading Post", 2,      12,    6,    "trade_bonus",0.0, 0.0, 4.0, "Facilitates commerce"),
]

_DEFAULT_RELIGIONS = [
    (0, "Solarism",  255,200, 50, "Sun Worship",    0.06),
    (1, "Lunarism",  150,180,255, "Moon Shadows",   0.05),
    (2, "Animism",    80,200, 80, "Spirit Veneration",0.07),
    (3, "Mysticism", 180,100,255, "Esoteric Truths", 0.04),
    (4, "Druidism",   50,160, 80, "Nature Harmony",  0.06),
    (5, "Shamanism", 220,140, 60, "Ancestor Spirits",0.08),
]

_DEFAULT_CULTURAL_TRAITS = [
    (0, "Warlike",      "martial",     "mil_mod",      0.15, "Fierce combat traditions"),
    (1, "Philosophical","philosophical","tech_mod",     0.15, "Pursuit of wisdom"),
    (2, "Mercantile",   "mercantile",  "trade_mod",    0.15, "Acumen for trade"),
    (3, "Agrarian",     "agrarian",    "growth_mod",   0.15, "Farming expertise"),
    (4, "Seafaring",    "naval",       "naval_mod",    0.20, "Mastery of the seas"),
    (5, "Isolationist", "diplomatic",  "trade_mod",   -0.10, "Distrust of outsiders"),
]

_DEFAULT_UNIT_TYPES = [
    # id, name,         cat,       era, cost, atk, def, hp,  mov, tech, desc
    (0,  "Warrior",      "infantry",0,  10,  2,  2, 100, 2, -1,   "Basic tribal fighter"),
    (1,  "Archer",       "ranged",  0,  15,  4,  1,  80, 2,  0,   "Primitive ranged"),
    (2,  "Spearman",     "infantry",0,  15,  3,  4, 100, 2,  0,   "Anti-cavalry"),
    (3,  "Swordsman",    "infantry",1,  25,  5,  4, 120, 2,  4,   "Bronze/iron melee"),
    (4,  "Horseman",     "cavalry", 1,  30,  5,  2, 100, 3,  4,   "Mounted flanking"),
    (5,  "Catapult",     "siege",   1,  35,  8,  1,  60, 2,  5,   "City breaker"),
    (6,  "Knight",       "cavalry", 2,  50,  8,  6, 150, 3,  8,   "Heavily armored"),
    (7,  "Crossbowman",  "ranged",  2,  40,  7,  3,  90, 2,  9,   "Advanced ranged"),
    (8,  "Musketman",    "infantry",3,  60,  10, 7, 140, 2, 10,   "Gunpowder infantry"),
    (9,  "Cannon",       "siege",   3,  70,  14, 3,  80, 2, 10,   "Artillery"),
    (10, "Rifleman",     "infantry",4,  80,  15, 12, 160, 2, 14,  "Modern firearms"),
    (11, "Cavalry",      "cavalry", 4,  90,  14, 8, 140, 3, 14,  "Fast modern horses"),
    (12, "Tank",         "armor",   5,  120, 25, 18, 200, 3, 17,  "Armored vehicle"),
    (13, "Infantry",     "infantry",5,  100, 20, 20, 200, 2, 16,  "Modern squad"),
    (14, "Artillery",    "siege",   5,  110, 30, 5,  100, 2, 16,  "Long-range bombardment"),
]

_DEFAULT_RELATIONS = [
    (0, "Neutral",   170,170,170),
    (1, "Friendly",   90,195, 90),
    (2, "Allied",     55,155,250),
    (3, "Vassal",    180,140,220),
    (4, "Tributary", 200,180,100),
    (5, "Hostile",   215,155, 55),
    (6, "At War",    215, 55, 55),
    (7, "Cold War",  140,140,180),
]

_DEFAULT_TREATIES = [
    (0, "Peace Treaty",   20, "ends_war",    "Formal end to conflict"),
    (1, "Trade Pact",      0, "trade_bonus", "Mutual economic benefit"),
    (2, "Alliance",        0, "defense_pact","Mutual defense agreement"),
    (3, "Vassalage",       0, "suzerainty",  "Subservient relationship"),
]

_DEFAULT_GREAT_LEADERS = [
    (0, "Alexander",    "military",  0.20, "+20% Military Power", "Ancient"),
    (1, "Confucius",    "culture",   5.0,  "+5 Culture/turn",      "Ancient"),
    (2, "Da Vinci",     "tech",      0.3,  "+0.3 Tech/turn",       "Medieval"),
    (3, "Cleopatra",    "trade",     0.30, "+30% Trade income",    "Ancient"),
    (4, "Genghis Khan", "conquest",  0.25, "+25% Capture rate",    "Classical"),
    (5, "Newton",       "tech",      0.5,  "+0.5 Tech/turn",       "Renaissance"),
    (6, "Sun Tzu",      "defense",   0.20, "+20% Defense",         "Ancient"),
    (7, "Hammurabi",    "stability", 8.0,  "+8 Stability/turn",    "Ancient"),
    (8, "Magellan",     "naval",     0.30, "+30% Naval power",     "Renaissance"),
    (9, "Moses",        "faith",     0.20, "+20% Faith growth",    "Ancient"),
    (10,"Tesla",        "tech",      0.6,  "+0.6 Tech/turn",       "Industrial"),
    (11,"Boudica",      "rebellion", 0.30, "-30% Rebellion chance","Classical"),
]

_DEFAULT_GREAT_WORKS = [
    (0, "The Iliad",         "literature", 3.0, 1.0, 0, "Epic poem of heroes"),
    (1, "Venus de Milo",     "art",        4.0, 2.0, 1, "Ancient sculpture"),
    (2, "The Republic",      "philosophy", 5.0, 1.5, 0, "Philosophical treatise"),
    (3, "Mona Lisa",         "art",        6.0, 4.0, 3, "Renaissance portrait"),
    (4, "Symphony No. 9",    "music",      5.0, 3.0, 3, "Choral masterpiece"),
    (5, "On the Origin of Species", "literature", 5.0, 2.0, 4, "Scientific revolution"),
]

_DEFAULT_WONDERS = [
    (0, "Great Library",    60, 2.0, "tech",      0.4,   "+0.4 Tech growth"),
    (1, "Grand Temple",     50, 1.5, "culture",   4.0,   "+4 Culture/turn"),
    (2, "Iron Forge",       55, 2.5, "military",  0.15,  "+15% Military"),
    (3, "Silk Road",        45, 2.0, "trade",     0.25,  "+25% Trade income"),
    (4, "Colossal Statue",  70, 3.0, "stability", 12.0,  "+12 Stability"),
    (5, "Sacred Garden",    40, 1.0, "growth",    0.15,  "+15% Pop growth"),
    (6, "Obsidian Tower",   80, 4.0, "espionage", 0.25,  "+25% Espionage"),
    (7, "Crystal Palace",   90, 5.0, "golden",    0.015, "+1.5% Golden age"),
    (8, "Harbor of Kings",  65, 3.5, "naval",     0.20,  "+20% Naval power"),
    (9, "Grand Academy",    75, 4.5, "leader",    0.02,  "+2% Leader spawn"),
]

_DEFAULT_DISASTERS = [
    (0, "Earthquake",  "geological",      1.5, 0.10, 20.0, "6,7",    0, "Tectonic shift"),
    (1, "Flood",       "meteorological",  1.2, 0.05, 10.0, "2,3,11", 0, "River overflow"),
    (2, "Volcanic Eruption","geological", 2.0, 0.20, 40.0, "7",      0, "Mountain eruption"),
    (3, "Hurricane",   "meteorological",  1.8, 0.05, 15.0, "1,2",    0, "Coastal storm"),
    (4, "Famine",      "biological",      2.5, 0.15, 0.0,  "8,9",    1, "Crop failure"),
    (5, "Plague Rats", "biological",      1.0, 0.10, 0.0,  "2,3",    2, "Vermin infestation"),
]

_DEFAULT_DISEASES = [
    (0, "Bubonic Plague",   0.15, 0.20, 15, 1, 8,  "Black death"),
    (1, "Smallpox",         0.10, 0.15, 20, 0, 11, "Speckled monster"),
    (2, "Cholera",          0.12, 0.10, 10, 3, 13, "Waterborne illness"),
    (3, "Influenza",        0.20, 0.05,  5, 4, 15, "Flu pandemic"),
]

_DEFAULT_EVENTS = [
    (0, "Golden Age",      "cultural",   0.005, 2, "all",      0.10, "Society flourishes"),
    (1, "Peasant Revolt",  "political",  0.015, 1, "stability",-10.0, "Uprising of the poor"),
    (2, "Schism",          "religious",  0.010, 1, "faith",    -0.10, "Religious division"),
    (3, "Migration Wave",  "social",     0.020, 0, "growth",    5.0,  "Influx of people"),
    (4, "Cultural Flowering","cultural", 0.008, 2, "culture",   5.0,  "Artistic boom"),
    (5, "Economic Boom",   "economic",   0.015, 3, "trade",     0.15, "Trade explosion"),
    (6, "Dark Age",        "cultural",   0.005, 1, "all",      -0.10, "Society declines"),
]

_DEFAULT_ERAS = [
    (0, 0.0, "Ancient"),
    (1, 1.5, "Classical"),
    (2, 3.0, "Medieval"),
    (3, 5.0, "Renaissance"),
    (4, 7.0, "Industrial"),
    (5, 9.0, "Modern"),
]

_DEFAULT_ESPIONAGE = [
    ("steal_tech",    30, 0.35, "Steal Technology"),
    ("sabotage",      25, 0.40, "Sabotage Resources"),
    ("incite_revolt", 40, 0.25, "Incite Revolt"),
    ("spy",           15, 0.60, "Gather Intelligence"),
    ("assassinate",   50, 0.15, "Assassinate Leader"),
]

_DEFAULT_ACHIEVEMENTS = [
    ("first_blood",    "First Blood",     "Win your first battle",            "⚔️"),
    ("empire_builder", "Empire Builder",  "Own 100+ territories",             "🏰"),
    ("tech_pioneer",   "Tech Pioneer",    "Reach the Modern era",             "🔬"),
    ("holy_crusade",   "Holy Crusade",    "Win a holy war",                   "✝️"),
    ("trade_mogul",    "Trade Mogul",     "Earn 10+ trade income per turn",   "💰"),
    ("wonder_builder", "Wonder Builder",  "Build 3 wonders",                  "🏛️"),
    ("survivor",       "Survivor",        "Survive 500 years",                "⏳"),
    ("conqueror",      "Conqueror",       "Conquer another civ's capital",    "👑"),
    ("golden_age",     "Golden Age",      "Enter a golden age",               "✨"),
    ("renaissance",    "Renaissance",     "Have 3 great leaders at once",     "🎨"),
    ("naval_supremacy","Naval Supremacy", "Own 20+ coastal tiles",            "⚓"),
    ("faith_spread",   "Faith Spread",    "Convert 50+ tiles to your religion","🙏"),
    ("plague_survivor","Plague Survivor", "Survive a major pandemic",         "💉"),
    ("revolution",     "Revolution",      "Overthrow your own government",    "✊"),
]

_DEFAULT_SETTINGS = [
    ("river_bonus", 1),
    ("sim_speed", 1.0),
    ("ai_aggressiveness", 0.5),
]


# ════════════════════════════════════════════════════════════
# Game Definitions Loader
# ════════════════════════════════════════════════════════════
class GameDefs:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._cur = self._conn.cursor()
        self._create_tables()
        self._ensure_populated()
        self._load_all()

    def __enter__(self) -> GameDefs:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _create_tables(self) -> None:
        self._cur.executescript(_SCHEMA_SQL)
        self._conn.commit()

    def _ensure_populated(self) -> None:
        self._cur.execute("SELECT COUNT(*) FROM def_civ_names")
        if self._cur.fetchone()[0] > 0:
            return
        self._populate_defaults()

    def _populate_defaults(self) -> None:
        c = self._cur
        c.executemany("INSERT INTO def_civ_names VALUES (?,?)", enumerate(_DEFAULT_CIV_NAMES))
        c.executemany("INSERT INTO def_civ_colors VALUES (?,?,?,?)", [(i, r, g, b) for i, (r, g, b) in enumerate(_DEFAULT_CIV_COLORS)])
        c.executemany("INSERT INTO def_terrain VALUES (?,?,?,?,?,?,?,?,?,?,?)", _DEFAULT_TERRAIN)
        c.executemany("INSERT INTO def_biomes VALUES (?,?,?,?,?,?,?)", _DEFAULT_BIOMES)
        c.executemany("INSERT INTO def_natural_wonders VALUES (?,?,?,?,?,?,?,?,?)", _DEFAULT_NATURAL_WONDERS)
        c.executemany("INSERT INTO def_resources VALUES (?,?,?,?,?,?,?,?,?,?)", _DEFAULT_RESOURCES)
        c.executemany("INSERT INTO def_government_types VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", _DEFAULT_GOVERNMENTS)
        c.executemany("INSERT INTO def_policies VALUES (?,?,?,?,?,?,?,?)", _DEFAULT_POLICIES)
        c.executemany("INSERT INTO def_ideologies VALUES (?,?,?,?,?,?,?,?)", _DEFAULT_IDEOLOGIES)
        c.executemany("INSERT INTO def_social_classes VALUES (?,?,?,?,?,?)", _DEFAULT_SOCIAL_CLASSES)
        c.executemany("INSERT INTO def_technologies VALUES (?,?,?,?,?,?,?,?,?)", _DEFAULT_TECHNOLOGIES)
        c.executemany("INSERT INTO def_buildings VALUES (?,?,?,?,?,?,?,?,?,?)", _DEFAULT_BUILDINGS)
        c.executemany("INSERT INTO def_improvements VALUES (?,?,?,?,?,?,?,?,?,?)", _DEFAULT_IMPROVEMENTS)
        c.executemany("INSERT INTO def_religions VALUES (?,?,?,?,?,?)", _DEFAULT_RELIGIONS)
        c.executemany("INSERT INTO def_cultural_traits VALUES (?,?,?,?,?,?)", _DEFAULT_CULTURAL_TRAITS)
        c.executemany("INSERT INTO def_unit_types VALUES (?,?,?,?,?,?,?,?,?,?,?)", _DEFAULT_UNIT_TYPES)
        c.executemany("INSERT INTO def_relations VALUES (?,?,?,?,?)", _DEFAULT_RELATIONS)
        c.executemany("INSERT INTO def_treaty_types VALUES (?,?,?,?,?)", _DEFAULT_TREATIES)
        c.executemany("INSERT INTO def_great_leaders VALUES (?,?,?,?,?,?)", _DEFAULT_GREAT_LEADERS)
        c.executemany("INSERT INTO def_great_works VALUES (?,?,?,?,?,?)", _DEFAULT_GREAT_WORKS)
        c.executemany("INSERT INTO def_wonders VALUES (?,?,?,?,?,?,?)", _DEFAULT_WONDERS)
        c.executemany("INSERT INTO def_disasters VALUES (?,?,?,?,?,?,?,?,?)", _DEFAULT_DISASTERS)
        c.executemany("INSERT INTO def_diseases VALUES (?,?,?,?,?,?,?)", _DEFAULT_DISEASES)
        c.executemany("INSERT INTO def_events VALUES (?,?,?,?,?,?,?,?)", _DEFAULT_EVENTS)
        c.executemany("INSERT INTO def_eras VALUES (?,?,?)", _DEFAULT_ERAS)
        c.executemany("INSERT INTO def_espionage_missions VALUES (?,?,?,?)", _DEFAULT_ESPIONAGE)
        c.executemany("INSERT INTO def_achievements VALUES (?,?,?,?)", _DEFAULT_ACHIEVEMENTS)
        c.executemany("INSERT INTO def_settings VALUES (?,?)", _DEFAULT_SETTINGS)
        self._conn.commit()

    def _load_all(self) -> None:
        cur = self._cur
        
        cur.execute("SELECT name FROM def_civ_names ORDER BY id")
        self.civ_names: list[str] = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT r,g,b FROM def_civ_colors ORDER BY id")
        self.civ_colors: list[QColor] = [QColor(r, g, b) for r, g, b in cur.fetchall()]

        cur.execute("SELECT id,name,cr,cg,cb,food,production,trade,movement_cost,defense_bonus,is_water FROM def_terrain ORDER BY id")
        self.terrain_colors: dict[Terrain, QColor] = {}
        self.terrain_names:  dict[Terrain, str]    = {}
        self.terrain_stats:  dict[Terrain, dict]   = {}
        for tid, name, cr, cg, cb, food, prod, trade, move, defense, is_water in cur.fetchall():
            t = Terrain(tid)
            self.terrain_colors[t] = QColor(cr, cg, cb)
            self.terrain_names[t]  = name
            self.terrain_stats[t]  = {"food": food, "prod": prod, "trade": trade, "move": move, "def": defense, "is_water": bool(is_water)}

        cur.execute("SELECT key,value FROM def_settings")
        self.settings: dict[str, float] = dict(cur.fetchall())
        self.river_bonus: int = int(self.settings.get("river_bonus", 1))

        cur.execute("SELECT id,name,terrain_id,effect,bonus,desc_text,cr,cg,cb FROM def_natural_wonders ORDER BY id")
        self.natural_wonder_defs: list[dict] = []
        for _, name, tid, effect, bonus, desc, cr, cg, cb in cur.fetchall():
            self.natural_wonder_defs.append({
                "name": name, "terrain": Terrain(tid), "effect": effect,
                "bonus": bonus, "desc": desc, "color": QColor(cr, cg, cb),
            })

        cur.execute("SELECT id,name,category,terrain_id,food_bonus,prod_bonus,trade_bonus,cr,cg,cb FROM def_resources ORDER BY id")
        self.resource_defs: list[dict] = []
        for rid, name, cat, tid, food, prod, trade, cr, cg, cb in cur.fetchall():
            self.resource_defs.append({
                "id": rid, "name": name, "category": ResourceCat(cat), "terrain": Terrain(tid) if tid is not None else None,
                "food": food, "prod": prod, "trade": trade, "color": QColor(cr, cg, cb)
            })

        cur.execute("SELECT id,name,min_era_id,stability_mod,growth_mod,culture_mod,mil_mod,tech_mod,trade_mod,faith_mod,revolt_chance,desc_text,cr,cg,cb FROM def_government_types ORDER BY id")
        self.government_defs: dict[Government, dict] = {}
        for gid, name, min_era, stab, grow, cult, mil, tech, trade, faith, revolt, desc, cr, cg, cb in cur.fetchall():
            self.government_defs[Government(gid)] = {
                "name": name, "min_era": min_era, "stability": stab, "growth": grow, "culture": cult,
                "military": mil, "tech": tech, "trade": trade, "faith": faith, "revolt": revolt,
                "desc": desc, "color": QColor(cr, cg, cb)
            }

        cur.execute("SELECT id,name,category,min_era_id,min_gov_id,effect,bonus,desc_text FROM def_technologies ORDER BY id")
        self.tech_defs: list[dict] = [
            {"id": t[0], "name": t[1], "category": t[2], "era": t[3], "min_gov": t[4], "effect": t[5], "bonus": t[6], "desc": t[7]}
            for t in cur.fetchall()
        ]

        cur.execute("SELECT id,name,category,cost,min_tech_id,min_era_id,effect,bonus,maintenance,desc_text FROM def_buildings ORDER BY id")
        self.building_defs: list[dict] = [
            {"id": b[0], "name": b[1], "category": b[2], "cost": b[3], "min_tech": b[4], "min_era": b[5], "effect": b[6], "bonus": b[7], "maint": b[8], "desc": b[9]}
            for b in cur.fetchall()
        ]

        cur.execute("SELECT id,name,category,era_id,cost,attack,defense,hp,movement,min_tech_id,desc_text FROM def_unit_types ORDER BY id")
        self.unit_defs: list[dict] = [
            {"id": u[0], "name": u[1], "category": u[2], "era": u[3], "cost": u[4], "atk": u[5], "def": u[6], "hp": u[7], "mov": u[8], "min_tech": u[9], "desc": u[10]}
            for u in cur.fetchall()
        ]

        cur.execute("SELECT id,name,cr,cg,cb,tenet,spread_rate FROM def_religions ORDER BY id")
        self.religions: list[str]    = []
        self.religion_colors: list[QColor] = []
        self.religion_stats: list[dict] = []
        for _, name, cr, cg, cb, tenet, spread in cur.fetchall():
            self.religions.append(name)
            self.religion_colors.append(QColor(cr, cg, cb))
            self.religion_stats.append({"tenet": tenet, "spread": spread})

        cur.execute("SELECT id,name,cr,cg,cb FROM def_relations ORDER BY id")
        self.relation_names:  dict[Relation, str]   = {}
        self.relation_colors: dict[Relation, QColor] = {}
        for rid, name, cr, cg, cb in cur.fetchall():
            r = Relation(rid)
            self.relation_names[r]  = name
            self.relation_colors[r] = QColor(cr, cg, cb)

        cur.execute("SELECT tech_threshold,era_name FROM def_eras ORDER BY id")
        self.era_thresholds: list[tuple[float, str]] = [(t, n) for t, n in cur.fetchall()]

        cur.execute("SELECT name,cost,min_tech,effect,bonus,desc_text FROM def_wonders ORDER BY id")
        self.wonder_defs: list[dict] = [
            {"name": n, "cost": c, "min_tech": mt, "effect": e, "bonus": b, "desc": d}
            for n, c, mt, e, b, d in cur.fetchall()
        ]
        self.wonder_defs_by_name: dict[str, dict] = {
            wd["name"]: wd for wd in self.wonder_defs
        }

        cur.execute("SELECT name,effect,bonus,desc_text,min_era FROM def_great_leaders ORDER BY id")
        self.great_leader_defs: list[dict] = [
            {"name": n, "effect": e, "bonus": b, "desc": d, "min_era": me}
            for n, e, b, d, me in cur.fetchall()
        ]

        cur.execute("SELECT mission_type,cost,success_rate,desc_text FROM def_espionage_missions")
        self.espionage_missions: dict[str, dict] = {
            mt: {"cost": c, "success": s, "desc": d}
            for mt, c, s, d in cur.fetchall()
        }

        cur.execute("SELECT achievement_id,name,desc_text,icon FROM def_achievements")
        self.achievement_defs: dict[str, dict] = {
            aid: {"name": n, "desc": d, "icon": ic}
            for aid, n, d, ic in cur.fetchall()
        }

        cur.execute("SELECT id,name,base_happiness,base_prod_mod,base_tax_rate,political_power,desc_text FROM def_social_classes ORDER BY id")
        self.social_classes: list[dict] = [
            {"id": s[0], "name": s[1], "happiness": s[2], "prod_mod": s[3], "tax": s[4], "power": s[5], "desc": s[6]}
            for s in cur.fetchall()
        ]

        cur.execute("SELECT id,name,category,severity,pop_kill_pct,prod_damage,terrain_ids,min_era_id,desc_text FROM def_disasters ORDER BY id")
        self.disaster_defs: list[dict] = [
            {"id": d[0], "name": d[1], "category": d[2], "severity": d[3], "kill_pct": d[4], "prod_dmg": d[5], "terrains": d[6], "min_era": d[7], "desc": d[8]}
            for d in cur.fetchall()
        ]

        cur.execute("SELECT id,name,spread_rate,mortality,duration,min_era_id,cure_tech_id,desc_text FROM def_diseases ORDER BY id")
        self.disease_defs: list[dict] = [
            {"id": d[0], "name": d[1], "spread": d[2], "mortality": d[3], "duration": d[4], "min_era": d[5], "cure_tech": d[6], "desc": d[7]}
            for d in cur.fetchall()
        ]

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


# ════════════════════════════════════════════════════════════
# Analytics Database
# ════════════════════════════════════════════════════════════
class AnalyticsDatabase:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._cur = self._conn.cursor()
        self._cur.executescript(_ANALYTICS_SCHEMA_SQL)
        self._conn.commit()
        self.current_game_id: int | None = None

    def __enter__(self) -> AnalyticsDatabase:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def start_new_game(self, map_seed: int = 0, civ_count: int = 0, width: int = 0, height: int = 0) -> None:
        self._cur.execute(
            "INSERT INTO games (start_time, total_years, map_seed, civ_count, map_width, map_height) VALUES (?, 0, ?, ?, ?, ?)",
            (datetime.now().isoformat(), map_seed, civ_count, width, height),
        )
        self._conn.commit()
        self.current_game_id = self._cur.lastrowid

    def end_game(self, total_years: int, winner_name: str, victory_type: str) -> None:
        if self.current_game_id is None:
            return
        self._cur.execute(
            "UPDATE games SET end_time=?, total_years=?, winner_name=?, victory_type=? WHERE id=?",
            (datetime.now().isoformat(), total_years, winner_name, victory_type, self.current_game_id),
        )
        self._conn.commit()
        self.current_game_id = None

    def register_civ_birth(self, civ_name: str, religion: str, start_year: int, starting_culture: str = "", government: str = "Tribal") -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO civ_lifetimes (game_id,civ_name,starting_culture,religion,government,start_year) VALUES (?,?,?,?,?,?)",
            (self.current_game_id, civ_name, starting_culture, religion, government, start_year),
        )
        self._conn.commit()

    def register_civ_death(self, civ_name: str, end_year: int,
                           peak_pop: int, peak_terr: int, cause: str,
                           wonder_count: int, leader_count: int = 0, 
                           wars_fought: int = 0, wars_won: int = 0, golden_age_turns: int = 0) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "UPDATE civ_lifetimes SET end_year=?, peak_population=?, peak_territory=?, cause_of_death=?, wonder_count=?, leader_count=?, wars_fought=?, wars_won=?, golden_age_turns=? WHERE game_id=? AND civ_name=? AND end_year IS NULL",
            (end_year, peak_pop, peak_terr, cause, wonder_count, leader_count, wars_fought, wars_won, golden_age_turns, self.current_game_id, civ_name),
        )
        self._conn.commit()

    def log_turn_snapshots(self, year: int, civilizations: list) -> None:
        if self.current_game_id is None: return
        gid = self.current_game_id
        rows = [
            (gid, year, c.name, c.population, c.technology, c.culture, c.military_power, len(c.territories), c.score, c.religion, c.era, c.government, c.stability, c.happiness, c.treasury, c.food, c.production, c.trade)
            for c in civilizations if c.alive
        ]
        self._cur.executemany(
            "INSERT INTO turn_snapshots (game_id,year,civ_name,population,technology,culture,military,territories,score,religion,era,government,stability,happiness,treasury,food_total,prod_total,trade_total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            rows,
        )
        self._cur.execute("UPDATE games SET total_years=? WHERE id=?", (year, gid))
        self._conn.commit()

    def log_war(self, attacker: str, defender: str, start_year: int, war_cause: str = "") -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO war_history (game_id,attacker,defender,start_year,war_cause) VALUES (?,?,?,?,?)",
            (self.current_game_id, attacker, defender, start_year, war_cause),
        )
        self._conn.commit()

    def end_war(self, attacker: str, defender: str, end_year: int, winner: str, att_cas: int, def_cas: int, terr_changed: int) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "UPDATE war_history SET end_year=?, winner=?, attacker_casualties=?, defender_casualties=?, territory_changed=? WHERE game_id=? AND attacker=? AND defender=? AND end_year IS NULL",
            (end_year, winner, att_cas, def_cas, terr_changed, self.current_game_id, attacker, defender),
        )
        self._conn.commit()

    def log_treaty(self, civ_a: str, civ_b: str, treaty_type: str, year_signed: int) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO treaty_history (game_id,civ_a,civ_b,treaty_type,year_signed) VALUES (?,?,?,?,?)",
            (self.current_game_id, civ_a, civ_b, treaty_type, year_signed),
        )
        self._conn.commit()

    def log_territory_change(self, year: int, civ_gaining: str, civ_losing: str, x: int, y: int, reason: str) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO territory_changes (game_id,year,civ_gaining,civ_losing,tile_x,tile_y,reason) VALUES (?,?,?,?,?,?,?)",
            (self.current_game_id, year, civ_gaining, civ_losing, x, y, reason),
        )
        self._conn.commit()

    def log_demographics(self, year: int, civ_name: str, class_name: str, pop_pct: float, happiness: float, power: float, wealth: float) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO demographics_log (game_id,year,civ_name,class_name,population_pct,happiness,political_power,wealth_pct) VALUES (?,?,?,?,?,?,?,?)",
            (self.current_game_id, year, civ_name, class_name, pop_pct, happiness, power, wealth),
        )
        self._conn.commit()

    def log_economic_cycle(self, year: int, civ_name: str, phase: str, gdp: float, inflation: float, unemployment: float) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO economic_cycle_log (game_id,year,civ_name,phase,gdp,inflation,unemployment) VALUES (?,?,?,?,?,?,?)",
            (self.current_game_id, year, civ_name, phase, gdp, inflation, unemployment),
        )
        self._conn.commit()

    def log_cultural_diffusion(self, year: int, source: str, target: str, trait: str, intensity: float) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO cultural_diffusion_log (game_id,year,source_civ,target_civ,trait_name,intensity) VALUES (?,?,?,?,?,?)",
            (self.current_game_id, year, source, target, trait, intensity),
        )
        self._conn.commit()

    def log_religion_spread(self, year: int, religion: str, civ_name: str, x: int, y: int, method: str) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO religion_spread_log (game_id,year,religion,civ_name,tile_x,tile_y,spread_method) VALUES (?,?,?,?,?,?,?)",
            (self.current_game_id, year, religion, civ_name, x, y, method),
        )
        self._conn.commit()

    def log_tech_discovery(self, year: int, civ_name: str, tech_name: str, method: str) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO tech_discovery_log (game_id,year,civ_name,tech_name,method) VALUES (?,?,?,?,?)",
            (self.current_game_id, year, civ_name, tech_name, method),
        )
        self._conn.commit()

    def log_disaster(self, year: int, disaster_name: str, civ_name: str, x: int, y: int, severity: float, deaths: int, damage: float) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO disaster_log (game_id,year,disaster_name,civ_name,tile_x,tile_y,severity,deaths,damage) VALUES (?,?,?,?,?,?,?,?,?)",
            (self.current_game_id, year, disaster_name, civ_name, x, y, severity, deaths, damage),
        )
        self._conn.commit()

    def log_disease_start(self, year_start: int, disease_name: str, civ_name: str) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO disease_log (game_id,year_start,disease_name,civ_name) VALUES (?,?,?,?)",
            (self.current_game_id, year_start, disease_name, civ_name),
        )
        self._conn.commit()

    def log_disease_end(self, year_end: int, disease_name: str, civ_name: str, total_deaths: int, spread_tiles: int) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "UPDATE disease_log SET year_end=?, total_deaths=?, spread_tiles=? WHERE game_id=? AND disease_name=? AND civ_name=? AND year_end IS NULL",
            (year_end, total_deaths, spread_tiles, self.current_game_id, disease_name, civ_name),
        )
        self._conn.commit()

    def log_political_event(self, year: int, civ_name: str, event_type: str, old_gov: str, new_gov: str, leader_name: str, desc: str) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO political_events (game_id,year,civ_name,event_type,old_gov,new_gov,leader_name,desc_text) VALUES (?,?,?,?,?,?,?,?)",
            (self.current_game_id, year, civ_name, event_type, old_gov, new_gov, leader_name, desc),
        )
        self._conn.commit()

    def log_leader_tenure_start(self, civ_name: str, leader_name: str, start_year: int) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO leader_tenures (game_id,civ_name,leader_name,start_year) VALUES (?,?,?,?)",
            (self.current_game_id, civ_name, leader_name, start_year),
        )
        self._conn.commit()

    def log_leader_tenure_end(self, civ_name: str, leader_name: str, end_year: int, end_cause: str) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "UPDATE leader_tenures SET end_year=?, end_cause=? WHERE game_id=? AND civ_name=? AND leader_name=? AND end_year IS NULL",
            (end_year, end_cause, self.current_game_id, civ_name, leader_name),
        )
        self._conn.commit()

    def log_achievement(self, civ_name: str, achievement_id: str, year: int) -> None:
        if self.current_game_id is None: return
        self._cur.execute(
            "INSERT INTO achievements (game_id,civ_name,achievement_id,year) VALUES (?,?,?,?)",
            (self.current_game_id, civ_name, achievement_id, year),
        )
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


if __name__ == "__main__":
    import os
    print("Initializing simulation database...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    defs = GameDefs()
    analytics = AnalyticsDatabase()
    print(f"Successfully created and populated {DB_PATH}!")
    print(f" - Loaded {len(defs.civ_names)} civilizations")
    print(f" - Loaded {len(defs.terrain_stats)} terrain types")
    print(f" - Loaded {len(defs.government_defs)} governments")
    print(f" - Loaded {len(defs.tech_defs)} technologies")
    print(f" - Loaded {len(defs.building_defs)} buildings")
    print(f" - Loaded {len(defs.unit_defs)} unit types")
    print(f" - Loaded {len(defs.disaster_defs)} disasters")
    print(f" - Loaded {len(defs.disease_defs)} diseases")
    print(f" - Loaded {len(defs.social_classes)} social classes")
    defs.close()
    analytics.close()