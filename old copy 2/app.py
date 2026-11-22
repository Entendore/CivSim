"""
app.py — Civilization Simulation
Complete implementation with continuous time-frame limit, map rendering, and UI.
"""

from __future__ import annotations

import sys
import random
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QTextEdit, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QComboBox, QSplitter,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from db_setup import GameDefs, AnalyticsDatabase, DB_PATH, Terrain, Relation

__all__ = ["MainWindow", "SimulationEngine", "Civilization"]

# ════════════════════════════════════════════════════════════
# Core Constants
# ════════════════════════════════════════════════════════════
GRID_W, GRID_H = 80, 50
CELL_SIZE = 11
NUM_INITIAL_CIVS = 8
MAX_EVENTS = 800
SEASONS_PER_YEAR = 4
SEASON_NAMES = ("Spring", "Summer", "Autumn", "Winter")

# Removed traditional victory conditions - Sim runs continuously until this year
MAX_YEARS = 2000


# ════════════════════════════════════════════════════════════
# Enums
# ════════════════════════════════════════════════════════════
class EventCategory(str, Enum):
    DIPLOMACY   = "diplomacy"
    WAR         = "war"
    CULTURE     = "culture"
    TECH        = "tech"
    DISASTER    = "disaster"
    GROWTH      = "growth"
    COLLAPSE    = "collapse"
    GOLDEN      = "golden"
    WONDER      = "wonder"
    RELIGION    = "religion"
    TRADE       = "trade"
    REBELLION   = "rebellion"
    BARBARIAN   = "barbarian"
    SEASON      = "season"
    ACHIEVEMENT = "achievement"
    TIME_UP     = "time_up"


class OverlayMode(str, Enum):
    POLITICAL = "Political"
    TERRAIN   = "Terrain"
    RELIGION  = "Religion"


EVENT_CAT_COLORS = {
    EventCategory.DIPLOMACY: "#5599ff", EventCategory.WAR: "#ff4444",
    EventCategory.CULTURE: "#bb55ff", EventCategory.TECH: "#00ccdd",
    EventCategory.DISASTER: "#ff8800", EventCategory.GROWTH: "#44cc44",
    EventCategory.COLLAPSE: "#aa2222", EventCategory.GOLDEN: "#ffcc00",
    EventCategory.WONDER: "#ff9944", EventCategory.RELIGION: "#dd66aa",
    EventCategory.TRADE: "#55ccaa", EventCategory.REBELLION: "#cc6600",
    EventCategory.BARBARIAN: "#885533", EventCategory.SEASON: "#aaddff",
    EventCategory.ACHIEVEMENT: "#44ffaa", EventCategory.TIME_UP: "#ffffff",
}


@dataclass(frozen=True, slots=True)
class SeasonModifier:
    growth: float
    military: float
    trade: float
    stability: float

SEASON_MODIFIERS = (
    SeasonModifier(1.10, 1.00, 1.00, 1.00),
    SeasonModifier(1.15, 1.05, 1.10, 1.05),
    SeasonModifier(1.00, 1.00, 1.15, 1.00),
    SeasonModifier(0.80, 0.90, 0.70, 0.90),
)


@dataclass(frozen=True, slots=True)
class GameEvent:
    year: int
    season: int
    message: str
    category: EventCategory
    civ_name: str | None = None

    def __str__(self) -> str:
        sn = SEASON_NAMES[self.season] if 0 <= self.season < 4 else "?"
        return f"Y{self.year} {sn}: {self.message}"


@dataclass
class BarbarianCamp:
    x: int
    y: int
    spawn_year: int
    power: float = field(default_factory=lambda: random.uniform(10, 40))

    def tick(self) -> None:
        self.power = min(self.power + random.uniform(0.5, 2.0), 80.0)


class EventLog:
    def __init__(self, max_events: int = MAX_EVENTS) -> None:
        self._all: deque[GameEvent] = deque(maxlen=max_events)

    def log(self, event: GameEvent) -> None:
        self._all.append(event)

    @property
    def all_events(self) -> deque[GameEvent]:
        return self._all

    def clear(self) -> None:
        self._all.clear()


# ════════════════════════════════════════════════════════════
# SpatialHelper
# ════════════════════════════════════════════════════════════
class SpatialHelper:
    __slots__ = ("H", "W")

    def __init__(self, H: int, W: int) -> None:
        self.H, self.W = H, W

    def _propagate_mask(self, src: np.ndarray) -> np.ndarray:
        H, W = self.H, self.W
        out = np.zeros((H, W), dtype=bool)
        out[:, 1:]  |= src[:, :-1]
        out[:, :-1] |= src[:, 1:]
        out[1:, :]  |= src[:-1, :]
        out[:-1, :] |= src[1:, :]
        return out

    def find_frontier(self, ownership: np.ndarray, terrain: np.ndarray, civ_id: int) -> np.ndarray:
        owned = (ownership == civ_id)
        unclaimed = (ownership == -1) & (terrain != int(Terrain.OCEAN))
        return unclaimed & self._propagate_mask(owned)

    def find_capturable(self, ownership: np.ndarray, attacker_id: int, defender_id: int) -> np.ndarray:
        atk = (ownership == attacker_id)
        def_ = (ownership == defender_id)
        return def_ & self._propagate_mask(atk)

    def find_coastal(self, ownership: np.ndarray, terrain: np.ndarray, civ_id: int) -> np.ndarray:
        owned = (ownership == civ_id)
        ocean_adj = self._propagate_mask(terrain == int(Terrain.OCEAN))
        return owned & ocean_adj

    def compute_adjacency(self, ownership: np.ndarray) -> dict[int, set[int]]:
        adj: dict[int, set[int]] = defaultdict(set)
        pairs: set[tuple[int, int]] = set()
        left, right = ownership[:, :-1], ownership[:, 1:]
        mask = (left != right) & (left >= 0) & (right >= 0)
        if np.any(mask):
            for a, b in zip(left[mask].tolist(), right[mask].tolist()):
                pairs.add((min(a, b), max(a, b)))
        top, bottom = ownership[:-1, :], ownership[1:, :]
        mask = (top != bottom) & (top >= 0) & (bottom >= 0)
        if np.any(mask):
            for a, b in zip(top[mask].tolist(), bottom[mask].tolist()):
                pairs.add((min(a, b), max(a, b)))
        for a, b in pairs:
            adj[a].add(b)
            adj[b].add(a)
        return dict(adj)


# ════════════════════════════════════════════════════════════
# Terrain Generation
# ════════════════════════════════════════════════════════════
def _smooth_noise_numpy(noise: np.ndarray, iterations: int = 5) -> np.ndarray:
    H, W = noise.shape
    for _ in range(iterations):
        padded = np.pad(noise, 2, mode="reflect")
        total = np.zeros((H, W), dtype=np.float64)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                total += padded[2 + dy:2 + dy + H, 2 + dx:2 + dx + W]
        noise = total / 25.0
    return noise

def generate_terrain(defs: GameDefs) -> tuple[np.ndarray, np.ndarray]:
    noise = np.random.random((GRID_H, GRID_W))
    noise = _smooth_noise_numpy(noise, 5)

    yc = np.arange(GRID_H).reshape(-1, 1)
    xc = np.arange(GRID_W).reshape(1, -1)
    dist = np.sqrt(((yc - GRID_H / 2) / (GRID_H / 2)) ** 2 + ((xc - GRID_W / 2) / (GRID_W / 2)) ** 2)
    noise = noise * np.clip(1.0 - (dist - 0.55) * 1.1, 0.0, 1.0)

    mn, mx = noise.min(), noise.max()
    noise = (noise - mn) / max(mx - mn, 1e-9)

    lat = np.abs(yc - GRID_H / 2) / (GRID_H / 2)
    t = np.full((GRID_H, GRID_W), Terrain.PLAINS, dtype=np.int32)
    t[noise < 0.32] = Terrain.OCEAN
    t[(noise >= 0.32) & (lat > 0.83)] = Terrain.TUNDRA
    t[(noise >= 0.32) & (noise < 0.42) & (lat <= 0.83)] = Terrain.PLAINS
    t[(noise >= 0.42) & (noise < 0.54) & (lat < 0.55)] = Terrain.FOREST
    t[(noise >= 0.54) & (noise < 0.66)] = Terrain.PLAINS
    t[(noise >= 0.66) & (noise < 0.76)] = Terrain.MOUNTAIN
    t[(noise >= 0.76) & (lat < 0.35)] = Terrain.DESERT

    rivers = np.zeros((GRID_H, GRID_W), dtype=bool)
    # Simplified river gen
    mtns = np.argwhere(t == int(Terrain.MOUNTAIN))
    if len(mtns) > 0:
        for sy, sx in mtns[:random.randint(5, 10)]:
            x, y = int(sx), int(sy)
            for _ in range(50):
                rivers[y, x] = True
                if t[y, x] == int(Terrain.OCEAN): break
                best_h, best_pos = 999, None
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                        if t[ny, nx] < best_h:
                            best_h = t[ny, nx]
                            best_pos = (nx, ny)
                if best_pos is None: break
                x, y = best_pos

    return t, rivers


# ════════════════════════════════════════════════════════════
# Civilization
# ════════════════════════════════════════════════════════════
class Civilization:
    def __init__(self, civ_id: int, name: str, color: QColor, capital_pos: tuple[int, int], start_year: int, religion: str | None, defs: GameDefs) -> None:
        self.id = civ_id
        self.name = name
        self.color = color
        self.capital = capital_pos
        self.start_year = start_year
        self._defs = defs

        self.population = random.randint(800, 2000)
        self.technology = random.uniform(0.5, 2.0)
        self.military_power = random.uniform(20, 60)
        self.resources = random.uniform(30, 70)
        self.culture = random.uniform(5, 15)
        self.stability = random.uniform(70, 100)
        self.war_weariness = 0.0
        self.golden_age = False
        self.age = 0
        self.alive = True

        self.territories: set[tuple[int, int]] = {capital_pos}
        self.peak_population = self.population
        self.peak_territory = 1

        self.population_history: list[int] = [self.population]
        self.territory_history: list[int] = [1]

        # FIX: Proper religion precedence and fallback
        if religion:
            self.religion = religion
        elif defs.religions:
            self.religion = random.choice(defs.religions)
        else:
            self.religion = "Solarism"
            
        self.faith = random.uniform(5, 20)
        self.religion_converts = 0
        self.wonders: list[str] = []
        self.leaders: list[dict] = []
        self.relations: dict[int, Relation] = {}
        self.trade_partners: set[int] = set()
        self.trade_income = 0.0
        self.coastal_tiles = 0
        self.score = 0.0
        self.kills = 0
        self.capitals_conquered = 0
        self.achievements_earned: set[str] = set()

    @property
    def era(self) -> str:
        era = self._defs.era_thresholds[0][1] if self._defs.era_thresholds else "Ancient"
        for threshold, name in self._defs.era_thresholds:
            if self.technology >= threshold:
                era = name
        return era

    @property
    def all_bonuses(self) -> dict[str, float]:
        combined: dict[str, float] = defaultdict(float)
        for w_name in self.wonders:
            wd = self._defs.wonder_defs_by_name.get(w_name)
            if wd:
                combined[wd["effect"]] += wd["bonus"]
        for leader in self.leaders:
            if leader.get("alive", False):
                combined[leader["effect"]] += leader["bonus"]
        return dict(combined)

    def add_territory(self, pos: tuple[int, int]) -> None:
        self.territories.add(pos)
        self.peak_territory = max(self.peak_territory, len(self.territories))

    def remove_territory(self, pos: tuple[int, int]) -> None:
        self.territories.discard(pos)

    def compute_score(self) -> float:
        self.score = (
            len(self.territories) * 2 + self.population * 0.01 +
            self.technology * 15 + self.culture * 0.5 + self.military_power * 0.3 +
            len(self.wonders) * 25 + self.faith * 0.2 + self.kills * 50 +
            self.coastal_tiles * 0.5 + len(self.achievements_earned) * 10
        )
        return self.score


# ════════════════════════════════════════════════════════════
# Simulation Engine
# ════════════════════════════════════════════════════════════
class SimulationEngine:
    def __init__(self, db: AnalyticsDatabase, defs: GameDefs) -> None:
        self.db = db
        self.defs = defs
        self.terrain = np.zeros((GRID_H, GRID_W), dtype=np.int32)
        self.rivers = np.zeros((GRID_H, GRID_W), dtype=bool)
        self.ownership = np.full((GRID_H, GRID_W), -1, dtype=np.int32)
        self.religion_map = np.full((GRID_H, GRID_W), -1, dtype=np.int32)
        
        self.civilizations: dict[int, Civilization] = {}
        self.barbarian_camps: list[BarbarianCamp] = []
        self._next_civ_id = 0

        self.year = 0
        self.season = 0
        self.event_log = EventLog(MAX_EVENTS)
        self.used_names: set[str] = set()
        self.built_wonders: set[str] = set()
        
        # Replaced Victory Civ with Time-Up state
        self.time_up = False 
        self.winner_by_time: Civilization | None = None
        
        self._spatial = SpatialHelper(GRID_H, GRID_W)
        self._adjacency: dict[int, set[int]] = {}
        self._adjacency_dirty = True

        self._init_world()

    def _create_civilization(self, name: str, color: QColor, capital_pos: tuple[int, int], start_year: int = 0, religion: str | None = None) -> Civilization:
        self._next_civ_id += 1
        return Civilization(self._next_civ_id, name, color, capital_pos, start_year, religion, self.defs)

    def _init_world(self) -> None:
        self.terrain, self.rivers = generate_terrain(self.defs)
        self.ownership[:] = -1
        self.religion_map[:] = -1

        self.civilizations.clear()
        self.barbarian_camps.clear()
        self._next_civ_id = 0
        self.year = 0
        self.season = 0
        self.time_up = False
        self.winner_by_time = None
        self.event_log.clear()
        self.used_names.clear()
        self.built_wonders.clear()
        self._adjacency.clear()
        self._adjacency_dirty = True

        self._place_initial_civilizations()
        self._rebuild_adjacency()
        self._spawn_barbarian_camps()

        self.db.start_new_game()
        for civ in self.civilizations.values():
            self.db.register_civ_birth(civ.name, civ.religion, 0)

    def reset(self) -> None:
        if self.db.current_game_id is not None:
            for civ in self.civilizations.values():
                if civ.alive:
                    self.db.register_civ_death(civ.name, self.year, civ.peak_population, civ.peak_territory, "Reset", len(civ.wonders))
            # Time limit is the only "victory" type
            self.db.end_game(self.year, self.winner_by_time.name if self.winner_by_time else "None", "Time Limit" if self.time_up else "Abandoned")
        self._init_world()

    def _place_initial_civilizations(self) -> None:
        names = list(self.defs.civ_names)
        random.shuffle(names)
        placed = 0
        attempts = 0
        while placed < NUM_INITIAL_CIVS and attempts < 3000:
            attempts += 1
            x = random.randint(5, GRID_W - 6)
            y = random.randint(5, GRID_H - 6)
            if self.terrain[y, x] == Terrain.OCEAN: continue
            if any(abs(c.capital[0] - x) + abs(c.capital[1] - y) < 12 for c in self.civilizations.values()): continue

            civ = self._create_civilization(names[placed], self.defs.civ_colors[placed % len(self.defs.civ_colors)], (x, y), 0)
            self.civilizations[civ.id] = civ
            self._set_cell_owner(x, y, civ.id, initial=True)
            
            # FIX: Safe religion index mapping
            if civ.religion in self.defs.religions:
                self.religion_map[y, x] = self.defs.religions.index(civ.religion)
            self.used_names.add(names[placed])

            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < GRID_W and 0 <= ny < GRID_H and self.terrain[ny, nx] != Terrain.OCEAN and self.ownership[ny, nx] == -1 and random.random() < 0.6):
                        self._set_cell_owner(nx, ny, civ.id, initial=True)
                        if civ.religion in self.defs.religions:
                            self.religion_map[ny, nx] = self.defs.religions.index(civ.religion)
            
            # FIX: Initialize relations with other civs
            for other in self.civilizations.values():
                if other.id != civ.id:
                    civ.relations[other.id] = Relation.NEUTRAL
                    other.relations[civ.id] = Relation.NEUTRAL

            self._log(f"{civ.name} is founded at ({x}, {y})", EventCategory.DIPLOMACY, civ.name)
            placed += 1

    def _set_cell_owner(self, x: int, y: int, new_owner: int, *, initial: bool = False) -> None:
        old_owner = int(self.ownership[y, x])
        if old_owner == new_owner: return
        self.ownership[y, x] = new_owner
        if old_owner >= 0 and old_owner in self.civilizations:
            self.civilizations[old_owner].remove_territory((x, y))
        if new_owner >= 0 and new_owner in self.civilizations:
            self.civilizations[new_owner].add_territory((x, y))
        if not initial:
            self._adjacency_dirty = True

    def _rebuild_adjacency(self) -> None:
        self._adjacency = self._spatial.compute_adjacency(self.ownership)
        self._adjacency_dirty = False

    def _ensure_adjacency(self) -> None:
        if self._adjacency_dirty:
            self._rebuild_adjacency()

    def _log(self, message: str, category: EventCategory = EventCategory.GROWTH, civ_name: str | None = None) -> None:
        event = GameEvent(year=self.year, season=self.season, message=message, category=category, civ_name=civ_name)
        self.event_log.log(event)

    def _spawn_barbarian_camps(self) -> None:
        self.barbarian_camps.clear()
        for _ in range(random.randint(3, 7)):
            for _ in range(100):
                x, y = random.randint(3, GRID_W - 4), random.randint(3, GRID_H - 4)
                if (self.terrain[y, x] != Terrain.OCEAN and self.ownership[y, x] == -1 and all(abs(c.capital[0] - x) + abs(c.capital[1] - y) > 8 for c in self.civilizations.values() if c.alive)):
                    self.barbarian_camps.append(BarbarianCamp(x, y, 0))
                    break

    # ════════════════════════════════════════════════════════
    # Core Simulation Loop (FIX: Implemented missing tick)
    # ════════════════════════════════════════════════════════
    def tick(self) -> None:
        if self.time_up:
            return

        self.year += 1
        self.season = (self.season + 1) % SEASONS_PER_YEAR
        
        if self.season == 0:
            self._log(f"Year {self.year} begins.", EventCategory.SEASON)

        mod = SEASON_MODIFIERS[self.season]
        self._ensure_adjacency()

        alive_civs = [c for c in self.civilizations.values() if c.alive]

        # 1. Update Civ Stats & Expansion
        for civ in alive_civs:
            bonuses = civ.all_bonuses
            growth_mult = 1.0 + bonuses.get("growth", 0.0)
            civ.population = int(civ.population * (1.0 + 0.02 * mod.growth * growth_mult))
            civ.technology += 0.02 * mod.trade + bonuses.get("tech", 0.0)
            civ.culture += 0.1 + bonuses.get("culture", 0.0)
            civ.military_power += 0.5 * mod.military * (1.0 + bonuses.get("military", 0.0))
            civ.faith += 0.05 + bonuses.get("faith", 0.0)
            civ.trade_income = len(civ.trade_partners) * 2.0 * mod.trade * (1.0 + bonuses.get("trade", 0.0))
            civ.resources += civ.trade_income

            # Coastal update
            civ.coastal_tiles = int(np.sum(self._spatial.find_coastal(self.ownership, self.terrain, civ.id)))

            # Expansion
            frontier = self._spatial.find_frontier(self.ownership, self.terrain, civ.id)
            frontier_coords = np.argwhere(frontier)
            if len(frontier_coords) > 0 and random.random() < 0.3:
                idx = random.randint(0, len(frontier_coords) - 1)
                fy, fx = frontier_coords[idx]
                self._set_cell_owner(int(fx), int(fy), civ.id)
                if civ.religion in self.defs.religions:
                    self.religion_map[fy, fx] = self.defs.religions.index(civ.religion)

            civ.age += 1
            civ.compute_score()

            # History tracking
            if self.year % 10 == 0:
                civ.population_history.append(civ.population)
                civ.territory_history.append(len(civ.territories))

        # 2. Diplomacy & War
        for civ in alive_civs:
            neighbors = self._adjacency.get(civ.id, set())
            for nid in list(neighbors):
                if nid not in self.civilizations or not self.civilizations[nid].alive: continue
                rel = civ.relations.get(nid, Relation.NEUTRAL)
                
                # Random war declaration
                if rel != Relation.AT_WAR and rel != Relation.ALLIED and random.random() < 0.005:
                    civ.relations[nid] = Relation.AT_WAR
                    self.civilizations[nid].relations[civ.id] = Relation.AT_WAR
                    if nid in civ.trade_partners: civ.trade_partners.discard(nid)
                    if civ.id in self.civilizations[nid].trade_partners: self.civilizations[nid].trade_partners.discard(civ.id)
                    self._log(f"{civ.name} declares war on {self.civilizations[nid].name}!", EventCategory.WAR, civ.name)
                
                # Random peace
                elif rel == Relation.AT_WAR and random.random() < 0.01:
                    civ.relations[nid] = Relation.NEUTRAL
                    self.civilizations[nid].relations[civ.id] = Relation.NEUTRAL
                    self._log(f"{civ.name} signs peace with {self.civilizations[nid].name}.", EventCategory.DIPLOMACY, civ.name)

                # Random trade
                elif rel in (Relation.NEUTRAL, Relation.FRIENDLY) and nid not in civ.trade_partners and random.random() < 0.02:
                    civ.trade_partners.add(nid)
                    self.civilizations[nid].trade_partners.add(civ.id)
                    self._log(f"{civ.name} establishes trade with {self.civilizations[nid].name}.", EventCategory.TRADE, civ.name)

        # 3. War Resolution
        for civ in alive_civs:
            at_war_with = [nid for nid, r in civ.relations.items() if r == Relation.AT_WAR and nid in self.civilizations and self.civilizations[nid].alive]
            for nid in at_war_with:
                enemy = self.civilizations[nid]
                capturable = self._spatial.find_capturable(self.ownership, civ.id, nid)
                coords = np.argwhere(capturable)
                if len(coords) > 0 and civ.military_power > enemy.military_power * 0.8:
                    if random.random() < 0.2:
                        idx = random.randint(0, len(coords) - 1)
                        cy, cx = coords[idx]
                        self._set_cell_owner(int(cx), int(cy), civ.id)
                        if (int(cx), int(cy)) == enemy.capital:
                            civ.capitals_conquered += 1
                            civ.kills += 1
                            enemy.alive = False
                            enemy_territories = list(enemy.territories)
                            for tx, ty in enemy_territories:
                                self._set_cell_owner(tx, ty, civ.id)
                            self._log(f"{civ.name} has conquered {enemy.name}!", EventCategory.WAR, civ.name)
                            self.db.register_civ_death(enemy.name, self.year, enemy.peak_population, enemy.peak_territory, "Conquered", len(enemy.wonders))
                            break 

        # 4. Barbarians
        self._process_barbarians()

        # 5. Disasters
        if random.random() < 0.02:
            civ = random.choice(alive_civs)
            loss = int(civ.population * random.uniform(0.05, 0.15))
            civ.population = max(1, civ.population - loss)
            self._log(f"A disaster strikes {civ.name}! Lost {loss} people.", EventCategory.DISASTER, civ.name)

        # 6. Achievements
        for civ in alive_civs:
            self._check_achievements(civ)

        # 7. End Check - Continuous Sim until Time Limit
        if self.year >= MAX_YEARS:
            self.time_up = True
            alive_civs.sort(key=lambda c: c.score, reverse=True)
            self.winner_by_time = alive_civs[0] if alive_civs else None
            winner_name = self.winner_by_time.name if self.winner_by_time else "None"
            self._log(f"Time limit reached! {winner_name} is the dominant civilization!", EventCategory.TIME_UP)
            self.db.end_game(self.year, winner_name, "Time Limit")

        # Log DB snapshot periodically
        if self.year % 25 == 0:
            self.db.log_turn_snapshots(self.year, list(self.civilizations.values()))

    def _process_barbarians(self) -> None:
        surviving = []
        for camp in self.barbarian_camps:
            camp.tick()
            if random.random() < 0.02 and camp.power > 20:
                best_civ, best_dist = None, 999
                for civ in self.civilizations.values():
                    if not civ.alive: continue
                    for tx, ty in list(civ.territories)[:20]:
                        d = abs(tx - camp.x) + abs(ty - camp.y)
                        if d < best_dist:
                            best_dist = d
                            best_civ = civ
                if best_civ and best_dist < 15:
                    loss = int(best_civ.population * random.uniform(0.01, 0.04))
                    best_civ.population = max(1, best_civ.population - loss)
                    self._log(f"Barbarian raid on {best_civ.name}! Lost {loss} people.", EventCategory.BARBARIAN, best_civ.name)
                    camp.power = max(5.0, camp.power - random.uniform(2, 8))

            if self.ownership[camp.y, camp.x] >= 0:
                continue
            if camp.power < 3.0:
                continue
            surviving.append(camp)
        self.barbarian_camps = surviving

    def _check_achievements(self, civ: Civilization) -> None:
        checks = {
            "empire_builder": len(civ.territories) >= 100,
            "trade_mogul": civ.trade_income >= 10,
            "survivor": civ.age >= 500,
        }
        for ach_id, condition in checks.items():
            if ach_id not in civ.achievements_earned and condition:
                civ.achievements_earned.add(ach_id)
                ach_def = self.defs.achievement_defs.get(ach_id, {})
                self._log(f"🏆 {civ.name}: {ach_def.get('name', ach_id)}", EventCategory.ACHIEVEMENT, civ.name)
                self.db.log_achievement(civ.name, ach_id, self.year)


# ════════════════════════════════════════════════════════════
# Main Window & Map Renderer (FIX: Fully Implemented)
# ════════════════════════════════════════════════════════════
class MapWidget(QWidget):
    def __init__(self, sim: SimulationEngine, parent=None):
        super().__init__(parent)
        self.sim = sim
        self.overlay = OverlayMode.POLITICAL
        self.setMinimumSize(GRID_W * CELL_SIZE, GRID_H * CELL_SIZE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        sim = self.sim

        for y in range(GRID_H):
            for x in range(GRID_W):
                rect_x = x * CELL_SIZE
                rect_y = y * CELL_SIZE
                
                # Base Color
                if self.overlay == OverlayMode.TERRAIN:
                    t = Terrain(sim.terrain[y, x])
                    color = sim.defs.terrain_colors.get(t, QColor(0, 0, 0))
                elif self.overlay == OverlayMode.RELIGION:
                    rid = sim.religion_map[y, x]
                    if rid >= 0 and rid < len(sim.defs.religion_colors):
                        color = sim.defs.religion_colors[rid]
                    else:
                        t = Terrain(sim.terrain[y, x])
                        color = sim.defs.terrain_colors.get(t, QColor(0,0,0)).darker(150)
                else: # POLITICAL
                    owner_id = sim.ownership[y, x]
                    if owner_id >= 0 and owner_id in sim.civilizations:
                        civ = sim.civilizations[owner_id]
                        color = civ.color
                        # Darken borders slightly
                        if (x == 0 or sim.ownership[y, x-1] != owner_id or 
                            y == 0 or sim.ownership[y-1, x] != owner_id):
                            color = color.darker(120)
                    else:
                        t = Terrain(sim.terrain[y, x])
                        color = sim.defs.terrain_colors.get(t, QColor(0,0,0)).lighter(80)

                # River overlay
                if sim.rivers[y, x]:
                    color = color.lighter(110)
                    painter.setPen(QPen(QColor(50, 100, 200), 1))
                    painter.setBrush(color)
                    painter.drawRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
                    painter.drawLine(rect_x + CELL_SIZE//2, rect_y, rect_x + CELL_SIZE//2, rect_y + CELL_SIZE)
                else:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(color)
                    painter.drawRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)

        # Draw Capitals
        for civ in sim.civilizations.values():
            if civ.alive:
                cx, cy = civ.capital
                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(QPen(QColor(0,0,0), 1))
                painter.drawRect(cx * CELL_SIZE - 1, cy * CELL_SIZE - 1, CELL_SIZE + 2, CELL_SIZE + 2)
        
        # Draw Barbarian Camps
        painter.setBrush(QColor(255, 0, 0, 150))
        painter.setPen(Qt.NoPen)
        for camp in sim.barbarian_camps:
            painter.drawEllipse(camp.x * CELL_SIZE, camp.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        painter.end()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Civilization Simulation - Time Limit Mode")
        self.resize(1280, 800)

        self.defs = GameDefs()
        self.db = AnalyticsDatabase()
        self.sim = SimulationEngine(self.db, self.defs)

        self.is_running = False
        self.speed = 100  # ms per tick

        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step_simulation)

    def init_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left: Map
        self.map_widget = MapWidget(self.sim)
        
        # Right: Controls & Info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Controls
        ctrl_group = QGroupBox("Simulation Controls")
        ctrl_layout = QHBoxLayout(ctrl_group)
        
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.clicked.connect(self.toggle_play)
        
        self.btn_step = QPushButton("⏭ Step")
        self.btn_step.clicked.connect(self.step_simulation)
        
        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.clicked.connect(self.reset_sim)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 500)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.setInvertedAppearance(True)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.btn_step)
        ctrl_layout.addWidget(self.btn_reset)
        ctrl_layout.addWidget(QLabel("Speed:"))
        ctrl_layout.addWidget(self.speed_slider)
        
        right_layout.addWidget(ctrl_group)

        # Overlay
        overlay_group = QGroupBox("Map Overlay")
        overlay_layout = QHBoxLayout(overlay_group)
        self.combo_overlay = QComboBox()
        self.combo_overlay.addItems([m.value for m in OverlayMode])
        self.combo_overlay.currentTextChanged.connect(self.change_overlay)
        overlay_layout.addWidget(self.combo_overlay)
        right_layout.addWidget(overlay_group)

        # Status
        self.lbl_status = QLabel(f"Year: 0 | Season: Spring | Time Limit: {MAX_YEARS} Years")
        self.lbl_status.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(self.lbl_status)

        # Civ Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Civ", "Pop", "Tech", "Era", "Terr", "Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right_layout.addWidget(self.table)

        # Event Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        right_layout.addWidget(self.log_box)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.map_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 500])
        main_layout.addWidget(splitter)

    def toggle_play(self):
        if self.is_running:
            self.timer.stop()
            self.btn_play.setText("▶ Play")
        else:
            self.timer.start(self.speed)
            self.btn_play.setText("⏸ Pause")
        self.is_running = not self.is_running

    def update_speed(self, val):
        self.speed = val
        if self.timer.isActive():
            self.timer.setInterval(val)

    def change_overlay(self, text):
        self.map_widget.overlay = OverlayMode(text)
        self.map_widget.update()

    def reset_sim(self):
        was_running = self.is_running
        if was_running:
            self.toggle_play()
        self.sim.reset()
        self.log_box.clear()
        self.update_ui()

    def step_simulation(self):
        self.sim.tick()
        self.update_ui()

    def update_ui(self):
        self.map_widget.update()
        
        sn = SEASON_NAMES[self.sim.season]
        status = f"Year: {self.sim.year} | Season: {sn} | Time Limit: {MAX_YEARS} Years"
        if self.sim.time_up:
            winner = self.sim.winner_by_time.name if self.sim.winner_by_time else "None"
            status += f" | 🏆 TIME UP! Winner: {winner}"
            if self.is_running:
                self.toggle_play() # Auto pause
        self.lbl_status.setText(status)

        # Table
        alive_civs = [c for c in self.sim.civilizations.values() if c.alive]
        self.table.setRowCount(len(alive_civs))
        for i, c in enumerate(sorted(alive_civs, key=lambda x: x.score, reverse=True)):
            self.table.setItem(i, 0, QTableWidgetItem(c.name))
            self.table.setItem(i, 1, QTableWidgetItem(f"{c.population:,}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{c.technology:.1f}"))
            self.table.setItem(i, 3, QTableWidgetItem(c.era))
            self.table.setItem(i, 4, QTableWidgetItem(str(len(c.territories))))
            self.table.setItem(i, 5, QTableWidgetItem(f"{c.score:.0f}"))
            
            color = c.color
            for col in range(6):
                item = self.table.item(i, col)
                item.setBackground(color)
                # Basic text contrast
                item.setForeground(QColor(0,0,0) if color.lightness() > 128 else QColor(255,255,255))

        # Event Log
        events = list(self.sim.event_log.all_events)[-20:]
        self.log_box.clear()
        for ev in reversed(events):
            color = EVENT_CAT_COLORS.get(ev.category, "#ffffff")
            self.log_box.append(f"<span style='color:{color}'>{ev}</span>")
        
        # Auto scroll
        cursor = self.log_box.textCursor()
        cursor.movePosition(cursor.Start)
        self.log_box.setTextCursor(cursor)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()