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
from CivSim.config import DB_PATH, Terrain


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
