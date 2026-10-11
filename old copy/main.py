#!/usr/bin/env python3
"""
Civilization Simulation — Optimized Data Structures & Algorithms Edition

Key algorithmic improvements:
  - SpatialHelper: O(H*W) vectorized NumPy spatial queries (shifted-array technique)
  - Adjacency graph: O(E) diplomacy instead of O(A²) all-pairs checking
  - Centralized _set_cell_owner(): single source of truth for territory sync
  - collections.deque: O(1) event log rotation
  - Cached terrain base image: avoids recomputing static terrain colors every frame
  - Pre-computed terrain resource map: vectorized resource income
  - Island-shaped terrain: radial gradient mask for natural continents
"""

import sys
import random
import math
from enum import IntEnum
from collections import defaultdict, deque
import numpy as np

# --- Hardware Acceleration Imports with Fallbacks ---
try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

try:
    import cupy as cp
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QTextEdit, QGroupBox,
    QProgressBar, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal, QPointF, QRect
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QPainterPath, QPolygonF, QImage,
)

# ════════════════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════════════════
GRID_W, GRID_H = 80, 50
CELL_SIZE = 11
NUM_INITIAL_CIVS = 8
MAX_CIVS = 12
MAX_EVENTS = 600

CIV_NAMES = [
    "Aethoria", "Byzantia", "Celestia", "Drakonia", "Elysium",
    "Ferrum", "Glacialis", "Heliopolis", "Ithaca", "Jadea",
    "Krakentia", "Lumina", "Mythoria", "Nyxium", "Olympia",
    "Pyrathia", "Quasaria", "Riven", "Solara", "Tempestia",
    "Umbra", "Valoria", "Wyrmitis", "Xanthia", "Zephyria",
]

CIV_COLORS = [
    QColor(215, 55, 55),  QColor(55, 105, 215), QColor(55, 175, 55),
    QColor(215, 175, 30), QColor(165, 55, 215),  QColor(55, 195, 195),
    QColor(215, 125, 30), QColor(195, 55, 125),  QColor(135, 195, 55),
    QColor(175, 125, 55), QColor(100, 155, 215), QColor(215, 100, 100),
]


class Terrain(IntEnum):
    OCEAN = 0; PLAINS = 1; FOREST = 2; MOUNTAIN = 3; DESERT = 4; TUNDRA = 5


TERRAIN_COLORS = {
    Terrain.OCEAN:    QColor(22, 50, 115),
    Terrain.PLAINS:   QColor(125, 182, 82),
    Terrain.FOREST:   QColor(42, 122, 42),
    Terrain.MOUNTAIN: QColor(142, 132, 122),
    Terrain.DESERT:   QColor(208, 182, 102),
    Terrain.TUNDRA:   QColor(198, 212, 222),
}

TERRAIN_NAMES = {
    Terrain.OCEAN: "Ocean",    Terrain.PLAINS: "Plains",
    Terrain.FOREST: "Forest",  Terrain.MOUNTAIN: "Mountain",
    Terrain.DESERT: "Desert",  Terrain.TUNDRA: "Tundra",
}

TERRAIN_RESOURCES = {
    Terrain.OCEAN: 0,  Terrain.PLAINS: 3,
    Terrain.FOREST: 2, Terrain.MOUNTAIN: 2,
    Terrain.DESERT: 1, Terrain.TUNDRA: 1,
}


class Relation(IntEnum):
    NEUTRAL = 0; FRIENDLY = 1; ALLIED = 2; HOSTILE = 3; AT_WAR = 4


RELATION_NAMES = {
    Relation.NEUTRAL: "Neutral",  Relation.FRIENDLY: "Friendly",
    Relation.ALLIED: "Allied",    Relation.HOSTILE: "Hostile",
    Relation.AT_WAR: "At War",
}

RELATION_COLORS = {
    Relation.NEUTRAL:  QColor(170, 170, 170),
    Relation.FRIENDLY: QColor(90, 195, 90),
    Relation.ALLIED:   QColor(55, 155, 250),
    Relation.HOSTILE:  QColor(215, 155, 55),
    Relation.AT_WAR:   QColor(215, 55, 55),
}


# ════════════════════════════════════════════════════════════
# Numba JIT Acceleration Kernels
# ════════════════════════════════════════════════════════════
if HAS_NUMBA:
    @numba.njit
    def _nb_smooth_noise(noise, iterations, H, W):
        out = noise.copy()
        for _ in range(iterations):
            temp = np.zeros((H, W), dtype=numba.float64)
            for y in range(H):
                for x in range(W):
                    total = 0.0; count = 0
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < H and 0 <= nx < W:
                                total += out[ny, nx]; count += 1
                    temp[y, x] = total / count
            out = temp
        return out

    @numba.njit
    def _nb_classify_terrain(noise, H, W):
        terrain = np.empty((H, W), dtype=numba.int32)
        for y in range(H):
            for x in range(W):
                v = noise[y, x]; lat = abs(y - H / 2) / (H / 2)
                if v < 0.32:       terrain[y, x] = 0
                elif lat > 0.83:   terrain[y, x] = 5
                elif v < 0.42:     terrain[y, x] = 1
                elif v < 0.54:     terrain[y, x] = 2 if lat < 0.55 else 1
                elif v < 0.66:     terrain[y, x] = 1
                elif v < 0.76:     terrain[y, x] = 3
                elif lat < 0.35:   terrain[y, x] = 4
                else:              terrain[y, x] = 1
        return terrain

    @numba.njit
    def _nb_compute_resource_income(terrain, ownership, civ_id):
        total = 0.0
        for y in range(terrain.shape[0]):
            for x in range(terrain.shape[1]):
                if ownership[y, x] == civ_id:
                    t = terrain[y, x]
                    if   t == 1: total += 3
                    elif t == 2: total += 2
                    elif t == 3: total += 2
                    elif t == 4: total += 1
                    elif t == 5: total += 1
        return total

    @numba.njit
    def _nb_compute_adjacency(ownership, H, W):
        """Build a boolean adjacency matrix between civ IDs.
        Only checks right and down neighbors to avoid double-counting."""
        max_id = 0
        for y in range(H):
            for x in range(W):
                if ownership[y, x] > max_id:
                    max_id = ownership[y, x]
        adj = np.zeros((max_id + 1, max_id + 1), dtype=numba.boolean)
        for y in range(H):
            for x in range(W):
                cid = ownership[y, x]
                if cid >= 0:
                    if x + 1 < W:
                        nid = ownership[y, x + 1]
                        if nid >= 0 and nid != cid:
                            a, b = (cid, nid) if cid < nid else (nid, cid)
                            adj[a, b] = True
                    if y + 1 < H:
                        nid = ownership[y + 1, x]
                        if nid >= 0 and nid != cid:
                            a, b = (cid, nid) if cid < nid else (nid, cid)
                            adj[a, b] = True
        return adj, max_id


# ════════════════════════════════════════════════════════════
# SpatialHelper — Vectorized NumPy Spatial Queries
#
# Uses the shifted-array technique: instead of iterating each cell
# and checking its 4 neighbours in Python (O(H·W) slow iterations),
# we compare offset slices of the whole array at once.
# Each direction is a single vectorized comparison over the entire grid.
# ════════════════════════════════════════════════════════════
class SpatialHelper:
    """Pre-computes spatial relationships on the grid using numpy."""

    _DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def __init__(self, H: int, W: int):
        self.H, self.W = H, W

    # ── helpers: 4-directional "has neighbour of type" via slicing ──

    def _propagate_mask(self, src: np.ndarray) -> np.ndarray:
        """For every cell, True if any of the 4 cardinal neighbours is True in *src*."""
        H, W = self.H, self.W
        out = np.zeros((H, W), dtype=bool)
        out[:, 1:]  |= src[:, :-1]   # left  neighbour
        out[:, :-1] |= src[:, 1:]    # right neighbour
        out[1:, :]  |= src[:-1, :]   # up    neighbour
        out[:-1, :] |= src[1:, :]    # down  neighbour
        return out

    # ── public API ──

    def find_borders(self, ownership: np.ndarray, civ_id: int) -> np.ndarray:
        """Boolean mask: civ territory cells adjacent to a non-civ or OOB cell."""
        owned = (ownership == civ_id)
        has_foreign = self._propagate_mask(~owned)
        # Edge cells that are owned are always border (OOB = foreign)
        has_foreign[0, :]  |= owned[0, :]
        has_foreign[-1, :] |= owned[-1, :]
        has_foreign[:, 0]  |= owned[:, 0]
        has_foreign[:, -1] |= owned[:, -1]
        return owned & has_foreign

    def find_frontier(self, ownership: np.ndarray, terrain: np.ndarray,
                      civ_id: int) -> np.ndarray:
        """Boolean mask: unclaimed non-ocean cells adjacent to civ territory."""
        owned = (ownership == civ_id)
        unclaimed = (ownership == -1) & (terrain != int(Terrain.OCEAN))
        return unclaimed & self._propagate_mask(owned)

    def find_capturable(self, ownership: np.ndarray,
                        attacker_id: int, defender_id: int) -> np.ndarray:
        """Boolean mask: defender cells with at least one attacker neighbour."""
        atk = (ownership == attacker_id)
        def_ = (ownership == defender_id)
        return def_ & self._propagate_mask(atk)

    def compute_adjacency(self, ownership: np.ndarray) -> dict:
        """Return {civ_id: set(neighbouring_civ_ids)} using shifted-array comparison.

        Horizontal and vertical neighbour pairs are extracted via array slicing,
        then deduplicated with a Python set over the (small) boundary-pair list.
        """
        adj: dict[int, set[int]] = defaultdict(set)
        pairs: set[tuple[int, int]] = set()

        # Horizontal
        left, right = ownership[:, :-1], ownership[:, 1:]
        mask = (left != right) & (left >= 0) & (right >= 0)
        if np.any(mask):
            la, ra = left[mask].tolist(), right[mask].tolist()
            for a, b in zip(la, ra):
                pairs.add((min(a, b), max(a, b)))

        # Vertical
        top, bottom = ownership[:-1, :], ownership[1:, :]
        mask = (top != bottom) & (top >= 0) & (bottom >= 0)
        if np.any(mask):
            ta, ba = top[mask].tolist(), bottom[mask].tolist()
            for a, b in zip(ta, ba):
                pairs.add((min(a, b), max(a, b)))

        for a, b in pairs:
            adj[a].add(b); adj[b].add(a)
        return dict(adj)


# ════════════════════════════════════════════════════════════
# Terrain Generation
# ════════════════════════════════════════════════════════════
def _smooth_noise_numpy(noise: np.ndarray, iterations: int = 5) -> np.ndarray:
    """Vectorised box-blur smoothing (replaces O(H·W·25·iter) Python loop)."""
    H, W = noise.shape
    for _ in range(iterations):
        padded = np.pad(noise, 2, mode='reflect')
        total = np.zeros((H, W), dtype=np.float64)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                total += padded[2 + dy: 2 + dy + H, 2 + dx: 2 + dx + W]
        noise = total / 25.0
    return noise


def generate_terrain() -> np.ndarray:
    if HAS_CUPY:
        noise = cp.asnumpy(cp.random.random((GRID_H, GRID_W)))
    else:
        noise = np.random.random((GRID_H, GRID_W))

    if HAS_NUMBA:
        noise = _nb_smooth_noise(noise, 5, GRID_H, GRID_W)
    else:
        noise = _smooth_noise_numpy(noise, 5)

    # Island shaping — push ocean toward map edges
    yc = np.arange(GRID_H).reshape(-1, 1)
    xc = np.arange(GRID_W).reshape(1, -1)
    dist = np.sqrt(((yc - GRID_H / 2) / (GRID_H / 2)) ** 2 +
                   ((xc - GRID_W / 2) / (GRID_W / 2)) ** 2)
    noise = noise * np.clip(1.0 - (dist - 0.55) * 1.1, 0.0, 1.0)

    mn, mx = noise.min(), noise.max()
    noise = (noise - mn) / max(mx - mn, 1e-9)

    if HAS_NUMBA:
        return _nb_classify_terrain(noise, GRID_H, GRID_W)

    lat = np.abs(yc - GRID_H / 2) / (GRID_H / 2)
    t = np.full((GRID_H, GRID_W), Terrain.PLAINS, dtype=np.int32)
    t[noise < 0.32]                                                  = Terrain.OCEAN
    t[(noise >= 0.32) & (lat > 0.83)]                                = Terrain.TUNDRA
    t[(noise >= 0.32) & (noise < 0.42) & (lat <= 0.83)]             = Terrain.PLAINS
    t[(noise >= 0.42) & (noise < 0.54) & (lat < 0.55)]              = Terrain.FOREST
    t[(noise >= 0.42) & (noise < 0.54) & (lat >= 0.55)]             = Terrain.PLAINS
    t[(noise >= 0.54) & (noise < 0.66)]                              = Terrain.PLAINS
    t[(noise >= 0.66) & (noise < 0.76)]                              = Terrain.MOUNTAIN
    t[(noise >= 0.76) & (lat < 0.35)]                                = Terrain.DESERT
    return t


# ════════════════════════════════════════════════════════════
# Civilization
# ════════════════════════════════════════════════════════════
class Civilization:
    _id_counter = 0

    def __init__(self, name, color, capital_pos, start_year=0):
        Civilization._id_counter += 1
        self.id = Civilization._id_counter
        self.name = name
        self.color = color
        self.capital = capital_pos
        self.territories: set[tuple[int, int]] = {capital_pos}
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
        self.relations: dict[int, Relation] = {}
        self.population_history: list[int] = [self.population]
        self.territory_history: list[int] = [1]
        self.start_year = start_year

    def add_territory(self, pos):
        self.territories.add(pos)

    def remove_territory(self, pos):
        self.territories.discard(pos)


# ════════════════════════════════════════════════════════════
# Simulation Engine
# ════════════════════════════════════════════════════════════
class SimulationEngine:
    def __init__(self):
        self.terrain = np.zeros((GRID_H, GRID_W), dtype=np.int32)
        self.ownership = np.full((GRID_H, GRID_W), -1, dtype=np.int32)
        self.terrain_resource_map = np.zeros((GRID_H, GRID_W), dtype=np.float64)
        self.civilizations: dict[int, Civilization] = {}
        self.year = 0
        self.events: deque = deque(maxlen=MAX_EVENTS)
        self.used_names: set[str] = set()
        self._spatial = SpatialHelper(GRID_H, GRID_W)
        self._adjacency: dict[int, set[int]] = {}
        self._init_world()

    # ────────────── world setup ──────────────

    def _rebuild_resource_map(self):
        self.terrain_resource_map = np.zeros((GRID_H, GRID_W), dtype=np.float64)
        for t, r in TERRAIN_RESOURCES.items():
            self.terrain_resource_map[self.terrain == int(t)] = r

    def _init_world(self):
        self.terrain = generate_terrain()
        self.ownership = np.full((GRID_H, GRID_W), -1, dtype=np.int32)
        self._rebuild_resource_map()
        self.civilizations.clear()
        self.year = 0
        self.events.clear()
        self.used_names.clear()
        Civilization._id_counter = 0
        self._adjacency.clear()
        self._place_initial_civilizations()
        self._rebuild_adjacency()

    def reset(self):
        self._init_world()

    def _place_initial_civilizations(self):
        names = list(CIV_NAMES)
        random.shuffle(names)
        placed = attempts = 0
        while placed < NUM_INITIAL_CIVS and attempts < 3000:
            attempts += 1
            x = random.randint(5, GRID_W - 6)
            y = random.randint(5, GRID_H - 6)
            if self.terrain[y, x] == Terrain.OCEAN:
                continue
            if any(abs(c.capital[0] - x) + abs(c.capital[1] - y) < 12
                   for c in self.civilizations.values()):
                continue
            color = CIV_COLORS[placed % len(CIV_COLORS)]
            civ = Civilization(names[placed], color, (x, y), 0)
            self.civilizations[civ.id] = civ
            self._set_cell_owner(x, y, civ.id, initial=True)
            self.used_names.add(names[placed])
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < GRID_W and 0 <= ny < GRID_H
                            and self.terrain[ny, nx] != Terrain.OCEAN
                            and self.ownership[ny, nx] == -1
                            and random.random() < 0.6):
                        self._set_cell_owner(nx, ny, civ.id, initial=True)
                        civ.add_territory((nx, ny))
            self._log(f"{civ.name} is founded at ({x}, {y})")
            placed += 1

    # ────────────── centralized cell ownership ──────────────

    def _set_cell_owner(self, x: int, y: int, new_owner: int, *,
                        initial: bool = False):
        """Single source of truth for changing cell ownership.

        Updates the ownership array, territory sets, and marks adjacency
        as stale.  All territory mutations must go through this method.
        """
        old_owner = int(self.ownership[y, x])
        if old_owner == new_owner:
            return
        self.ownership[y, x] = new_owner
        if old_owner >= 0 and old_owner in self.civilizations:
            self.civilizations[old_owner].remove_territory((x, y))
        if new_owner >= 0 and new_owner in self.civilizations:
            self.civilizations[new_owner].add_territory((x, y))
        if not initial:
            self._adjacency_dirty = True

    # ────────────── adjacency graph ──────────────

    def _rebuild_adjacency(self):
        """Recompute the civ-civ adjacency graph from the ownership array."""
        if HAS_NUMBA:
            adj_matrix, max_id = _nb_compute_adjacency(
                self.ownership, GRID_H, GRID_W)
            self._adjacency = defaultdict(set)
            for i in range(max_id + 1):
                for j in range(i + 1, max_id + 1):
                    if adj_matrix[i, j]:
                        self._adjacency[i].add(j)
                        self._adjacency[j].add(i)
        else:
            self._adjacency = self._spatial.compute_adjacency(self.ownership)
        self._adjacency_dirty = False

    # ────────────── logging ──────────────

    def _log(self, msg: str):
        self.events.append(f"Year {self.year}: {msg}")

    # ────────────── main step ──────────────

    def step(self):
        self.year += 1
        self._adjacency_dirty = False

        for civ in list(self.civilizations.values()):
            if civ.alive:
                self._update_civilization(civ)

        # Rebuild adjacency once after all expansions
        if self._adjacency_dirty:
            self._rebuild_adjacency()

        # Interact only bordering pairs — O(E) instead of O(A²)
        seen_pairs: set[tuple[int, int]] = set()
        for civ_id, neighbours in self._adjacency.items():
            civ = self.civilizations.get(civ_id)
            if not civ or not civ.alive:
                continue
            for other_id in neighbours:
                other = self.civilizations.get(other_id)
                if not other or not other.alive:
                    continue
                pair = (min(civ_id, other_id), max(civ_id, other_id))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                self._interact(civ, other)

        for civ in list(self.civilizations.values()):
            if civ.alive and (civ.stability <= 0 or civ.population < 10):
                self._collapse(civ)

        alive_count = sum(1 for c in self.civilizations.values() if c.alive)
        if random.random() < 0.012 and alive_count < MAX_CIVS:
            self._try_spawn()

        for civ in self.civilizations.values():
            if civ.alive:
                civ.population_history.append(civ.population)
                civ.territory_history.append(len(civ.territories))
                civ.age += 1

    # ────────────── per-civ update ──────────────

    def _update_civilization(self, civ: Civilization):
        # Resource income — vectorized
        if HAS_NUMBA:
            res_income = _nb_compute_resource_income(
                self.terrain, self.ownership, civ.id) * 0.1
        else:
            civ_mask = (self.ownership == civ.id)
            res_income = float(np.sum(self.terrain_resource_map[civ_mask])) * 0.1
        civ.resources = min(civ.resources + res_income, 300)

        # Population
        capacity = len(civ.territories) * 500
        gr = 0.02 * (1 - civ.population / max(capacity, 1))
        gr *= civ.stability / 100
        gr *= (0.5 + civ.technology / 10)
        if civ.golden_age:
            gr *= 1.5
        civ.population = max(1, int(civ.population * (1 + gr)))

        # Technology
        tc = 0.03 * (civ.culture / 20) * (civ.stability / 100)
        tc *= math.log10(max(civ.population, 10)) / 3
        if random.random() < tc:
            civ.technology = min(10.0, civ.technology + random.uniform(0.05, 0.25))

        # Culture
        cg = 0.02 * (1 + civ.technology / 5) * (civ.stability / 100)
        if civ.golden_age:
            cg *= 2
        civ.culture += cg

        # Military
        civ.military_power = (
            (civ.population * 0.01 + civ.resources * 0.15)
            * (1 + civ.technology / 5)
        )

        # Stability
        sc = 0.5
        if civ.population > capacity * 0.85:
            sc -= 1.5
        if civ.resources < 15:
            sc -= 2
        sc -= civ.war_weariness * 0.4
        if civ.golden_age:
            sc += 2
        sc += min(civ.culture / 100, 0.5)
        civ.stability = max(0, min(100, civ.stability + sc))
        civ.war_weariness = max(0, civ.war_weariness - 0.3)

        # Golden age
        if (not civ.golden_age and civ.stability > 80
                and civ.technology > 3 and random.random() < 0.005):
            civ.golden_age = True
            self._log(f"✨ {civ.name} enters a Golden Age!")
        if civ.golden_age and (civ.stability < 50 or random.random() < 0.015):
            civ.golden_age = False
            self._log(f"{civ.name}'s Golden Age ends")

        self._try_expand(civ)
        self._random_events(civ)

    # ────────────── expansion ──────────────

    def _try_expand(self, civ: Civilization):
        if civ.resources < 3 or civ.stability < 25:
            return

        # Vectorized frontier detection
        frontier_mask = self._spatial.find_frontier(
            self.ownership, self.terrain, civ.id)
        frontier_coords = np.argwhere(frontier_mask)  # [[y,x], ...]
        if len(frontier_coords) == 0:
            return

        prob = min(
            0.6,
            0.12 * (civ.military_power / 100)
            * (civ.stability / 100)
            * (1 + civ.technology / 10),
        )

        # Shuffle to avoid directional bias
        indices = np.random.permutation(len(frontier_coords))
        for idx in indices:
            y, x = int(frontier_coords[idx, 0]), int(frontier_coords[idx, 1])
            res_val = TERRAIN_RESOURCES.get(Terrain(self.terrain[y, x]), 1)
            effective_prob = prob * (0.5 + res_val / 6.0)
            if random.random() < effective_prob and civ.resources >= 2:
                self._set_cell_owner(x, y, civ.id)
                civ.resources -= 2

    # ────────────── diplomacy ──────────────

    def _interact(self, c1: Civilization, c2: Civilization):
        if c2.id not in c1.relations:
            c1.relations[c2.id] = Relation.NEUTRAL
        if c1.id not in c2.relations:
            c2.relations[c1.id] = Relation.NEUTRAL
        r1, r2 = c1.relations[c2.id], c2.relations[c1.id]

        # Culture flip
        if r1 != Relation.AT_WAR and r2 != Relation.AT_WAR:
            if (c1.culture > c2.culture * 1.8
                    and c1.stability > 60 and random.random() < 0.03):
                self._culture_flip(c1, c2)
            elif (c2.culture > c1.culture * 1.8
                  and c2.stability > 60 and random.random() < 0.03):
                self._culture_flip(c2, c1)

        # War
        if r1 == Relation.AT_WAR or r2 == Relation.AT_WAR:
            self._conduct_war(c1, c2)
            if ((c1.war_weariness > 4 or c2.war_weariness > 4)
                    and random.random() < 0.08):
                c1.relations[c2.id] = c2.relations[c1.id] = Relation.HOSTILE
                self._log(f"🕊️ {c1.name} and {c2.name} sign a peace treaty")
            return

        # Allied / Friendly bonuses
        if r1 in (Relation.FRIENDLY, Relation.ALLIED):
            bonus = min(c1.resources, c2.resources) * 0.015
            c1.resources += bonus; c2.resources += bonus
            c1.culture += 0.003;  c2.culture += 0.003
            if r1 == Relation.ALLIED and random.random() < 0.02:
                lo, hi = (c1, c2) if c1.technology < c2.technology else (c2, c1)
                diff = hi.technology - lo.technology
                if diff > 0.3:
                    lo.technology = min(10, lo.technology + diff * 0.05)

        # Diplomatic drift
        if r1 == Relation.NEUTRAL:
            if (c1.culture > 15 and c2.culture > 15
                    and random.random() < 0.015):
                c1.relations[c2.id] = c2.relations[c1.id] = Relation.FRIENDLY
                self._log(f"🤝 {c1.name} and {c2.name} establish friendly relations")
            elif random.random() < 0.008:
                c1.relations[c2.id] = c2.relations[c1.id] = Relation.HOSTILE
                self._log(f"⚡ Tensions rise between {c1.name} and {c2.name}")
        elif r1 == Relation.FRIENDLY and random.random() < 0.008:
            c1.relations[c2.id] = c2.relations[c1.id] = Relation.ALLIED
            self._log(f"🏰 {c1.name} and {c2.name} form an alliance!")
        elif r1 == Relation.HOSTILE:
            wp = 0.025 * (1 - min(c1.stability, c2.stability) / 150)
            if random.random() < wp:
                c1.relations[c2.id] = c2.relations[c1.id] = Relation.AT_WAR
                self._log(f"⚔️ {c1.name} declares war on {c2.name}!")

    def _culture_flip(self, influencer: Civilization, target: Civilization):
        capturable = self._get_capturable(influencer, target)
        if capturable:
            y, x = random.choice(capturable)
            self._set_cell_owner(x, y, influencer.id)
            self._log(
                f"🎭 {influencer.name}'s culture assimilates territory from {target.name}")

    # ────────────── warfare ──────────────

    def _conduct_war(self, c1: Civilization, c2: Civilization):
        p1 = c1.military_power * random.uniform(0.7, 1.3)
        p2 = c2.military_power * random.uniform(0.7, 1.3)
        winner, loser = (c1, c2) if p1 > p2 else (c2, c1)

        battle_types = [
            "border skirmish", "pitched battle", "siege",
            "naval engagement", "guerrilla raid",
        ]
        intensity = abs(p1 - p2) / max(p1, p2, 1)
        loser_loss  = random.uniform(0.01, 0.04) * (1 + intensity)
        winner_loss = random.uniform(0.005, 0.02) * (1 - intensity * 0.5)

        loser.population  = max(1, int(loser.population * (1 - loser_loss)))
        winner.population = max(1, int(winner.population * (1 - winner_loss)))
        l_cas = int(loser.population * loser_loss)
        w_cas = int(winner.population * winner_loss)
        if l_cas > 30 or w_cas > 30:
            self._log(
                f"⚔️ {random.choice(battle_types).title()}: "
                f"{winner.name} beats {loser.name} "
                f"({w_cas:,} vs {l_cas:,} lost)")

        if p1 > p2 * 1.15:
            self._capture(c1, c2)
        elif p2 > p1 * 1.15:
            self._capture(c2, c1)

        c1.war_weariness += 0.4; c2.war_weariness += 0.4
        loser.stability  = max(0, loser.stability - random.uniform(1, 3))
        winner.stability = max(0, winner.stability - random.uniform(0.3, 1))
        c1.resources = max(0, c1.resources - random.uniform(1, 4))
        c2.resources = max(0, c2.resources - random.uniform(1, 4))

    def _get_capturable(self, attacker: Civilization,
                        defender: Civilization) -> list[tuple[int, int]]:
        """Return list of (y, x) defender cells adjacent to attacker territory."""
        mask = self._spatial.find_capturable(
            self.ownership, attacker.id, defender.id)
        coords = np.argwhere(mask)  # [[y,x], ...]
        return [(int(r[0]), int(r[1])) for r in coords]

    def _capture(self, attacker: Civilization, defender: Civilization):
        capturable = self._get_capturable(attacker, defender)
        if not capturable:
            return
        n = min(len(capturable), random.randint(1, max(1, len(capturable) // 3)))
        for y, x in random.sample(capturable, n):
            self._set_cell_owner(x, y, attacker.id)
            if (x, y) == defender.capital:
                if defender.territories:
                    defender.capital = random.choice(list(defender.territories))
                defender.stability = max(0, defender.stability - 20)
                self._log(f"🏰 {attacker.name} captures {defender.name}'s capital!")

    # ────────────── collapse ──────────────

    def _collapse(self, civ: Civilization):
        civ.alive = False
        # Neighbors can seize territory
        positions = list(civ.territories)
        for x, y in positions:
            neighbours = []
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    owner = int(self.ownership[ny, nx])
                    if (owner >= 0 and owner != civ.id
                            and owner in self.civilizations
                            and self.civilizations[owner].alive):
                        neighbours.append(owner)
            if neighbours and random.random() < 0.35:
                self._set_cell_owner(x, y, random.choice(neighbours))
            else:
                self._set_cell_owner(x, y, -1)
        civ.territories.clear()
        self._log(f"💀 {civ.name} has collapsed into ruin…")

    # ────────────── new civ spawning ──────────────

    def _try_spawn(self):
        candidates = []
        for y in range(3, GRID_H - 3):
            for x in range(3, GRID_W - 3):
                if (self.terrain[y, x] != Terrain.OCEAN
                        and self.ownership[y, x] == -1):
                    if not any(
                        abs(c.capital[0] - x) + abs(c.capital[1] - y) < 10
                        for c in self.civilizations.values() if c.alive
                    ):
                        candidates.append((x, y))
        if not candidates:
            return
        avail = [n for n in CIV_NAMES if n not in self.used_names]
        if not avail:
            return
        pos = random.choice(candidates)
        name = avail[0]
        color = CIV_COLORS[len(self.civilizations) % len(CIV_COLORS)]
        civ = Civilization(name, color, pos, self.year)
        self.civilizations[civ.id] = civ
        self._set_cell_owner(pos[0], pos[1], civ.id)
        self.used_names.add(name)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = pos[0] + dx, pos[1] + dy
                if (0 <= nx < GRID_W and 0 <= ny < GRID_H
                        and self.terrain[ny, nx] != Terrain.OCEAN
                        and self.ownership[ny, nx] == -1
                        and random.random() < 0.5):
                    self._set_cell_owner(nx, ny, civ.id)
        self._log(f"🌱 A new civilization, {name}, rises!")

    # ────────────── random events ──────────────

    def _random_events(self, civ: Civilization):
        if random.random() < 0.004:
            loss = int(civ.population * random.uniform(0.05, 0.15))
            civ.population = max(1, civ.population - loss)
            civ.stability = max(0, civ.stability - random.uniform(5, 15))
            self._log(f"🦠 Plague strikes {civ.name}! {loss:,} perish")

        if random.random() < 0.003:
            civ.resources = max(0, civ.resources - random.uniform(15, 40))
            civ.stability = max(0, civ.stability - random.uniform(3, 8))
            self._log(f"🌾 Famine sweeps through {civ.name}")

        if random.random() < 0.002:
            loss = int(civ.population * random.uniform(0.02, 0.08))
            civ.population = max(1, civ.population - loss)
            civ.stability = max(0, civ.stability - random.uniform(3, 10))
            self._log(f"🌋 Natural disaster devastates {civ.name}")

        if random.random() < 0.003:
            civ.resources = min(300, civ.resources + random.uniform(15, 50))
            self._log(f"⛏️ {civ.name} discovers rich resource deposits")

        if random.random() < 0.003:
            civ.culture += random.uniform(3, 10)
            civ.stability = min(100, civ.stability + 5)
            self._log(f"🎨 Cultural renaissance in {civ.name}")

        if random.random() < 0.002:
            civ.technology = min(10, civ.technology + random.uniform(0.2, 0.5))
            self._log(f"🔬 {civ.name} makes a technological breakthrough!")

        if random.random() < 0.002:
            gain = int(civ.population * random.uniform(0.03, 0.08))
            civ.population += gain
            civ.culture += random.uniform(1, 4)
            self._log(f"👥 A great migration swells {civ.name}'s population (+{gain:,})")

        if random.random() < 0.002:
            civ.resources = min(300, civ.resources + random.uniform(20, 45))
            civ.culture += random.uniform(2, 6)
            self._log(f"🏛️ {civ.name} builds a grand monument!")

        if (civ.stability < 20 and len(civ.territories) > 5
                and random.random() < 0.04):
            lost = random.sample(list(civ.territories), len(civ.territories) // 4)
            for pos in lost:
                self._set_cell_owner(pos[0], pos[1], -1)
            civ.population = max(1, int(civ.population * 0.8))
            civ.stability = max(0, civ.stability - 10)
            self._log(f"🔥 Civil war tears {civ.name} apart!")


# ════════════════════════════════════════════════════════════
# Map Widget
# ════════════════════════════════════════════════════════════
class MapWidget(QWidget):
    civ_clicked = Signal(int)

    def __init__(self, engine: SimulationEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.selected_civ_id = None
        self.hover_cell = None
        self.setFixedSize(GRID_W * CELL_SIZE, GRID_H * CELL_SIZE)
        self.setMouseTracking(True)
        self._border_cache: dict[int, np.ndarray] = {}
        self._cache_year = -1
        self._terrain_base: np.ndarray | None = None
        self._build_terrain_base()

    def _build_terrain_base(self):
        """Pre-compute the static terrain colour image (only changes on reset)."""
        H, W = GRID_H, GRID_W
        img = np.zeros((H, W, 4), dtype=np.uint8)
        for t_val, color in TERRAIN_COLORS.items():
            mask = (self.engine.terrain == int(t_val))
            img[mask] = [color.red(), color.green(), color.blue(), 255]
        self._terrain_base = img

    def invalidate_terrain_cache(self):
        self._build_terrain_base()
        self._cache_year = -1

    def _rebuild_border_cache(self):
        if self._cache_year == self.engine.year:
            return
        self._cache_year = self.engine.year
        self._border_cache.clear()
        sp = self.engine._spatial
        for civ in self.engine.civilizations.values():
            if civ.alive:
                self._border_cache[civ.id] = sp.find_borders(
                    self.engine.ownership, civ.id)

    def paintEvent(self, event):
        p = QPainter(self)
        engine = self.engine
        H, W = GRID_H, GRID_W

        # ── 1. Render base image ──
        if HAS_CUPY:
            terrain_gpu = cp.asarray(engine.terrain)
            ownership_gpu = cp.asarray(engine.ownership)
            img_gpu = cp.zeros((H, W, 4), dtype=cp.uint8)
            for t_val, color in TERRAIN_COLORS.items():
                mask = (terrain_gpu == int(t_val))
                img_gpu[mask] = cp.array(
                    [color.red(), color.green(), color.blue(), 255], dtype=cp.uint8)
            for civ in engine.civilizations.values():
                if civ.alive:
                    mask = (ownership_gpu == int(civ.id))
                    if cp.any(mask):
                        c = QColor(civ.color)
                        if self.selected_civ_id == civ.id:
                            c = c.lighter(140)
                        elif civ.golden_age:
                            c = c.lighter(115)
                        img_gpu[mask] = cp.array(
                            [c.red(), c.green(), c.blue(), 255], dtype=cp.uint8)
            img_cpu = cp.asnumpy(img_gpu)
        else:
            # Start from cached terrain base, overlay ownership
            img_cpu = self._terrain_base.copy()
            for civ in engine.civilizations.values():
                if civ.alive:
                    mask = (engine.ownership == int(civ.id))
                    if np.any(mask):
                        c = QColor(civ.color)
                        if self.selected_civ_id == civ.id:
                            c = c.lighter(140)
                        elif civ.golden_age:
                            c = c.lighter(115)
                        img_cpu[mask] = [c.red(), c.green(), c.blue(), 255]

        h, w = img_cpu.shape[:2]
        qimg = QImage(
            img_cpu.tobytes(), w, h, 4 * w,
            QImage.Format_RGBA8888).copy()
        p.setRenderHint(QPainter.SmoothPixmapTransform, False)
        p.drawImage(QRect(0, 0, W * CELL_SIZE, H * CELL_SIZE), qimg)

        # ── 2. Border overlays ──
        self._rebuild_border_cache()
        for civ in engine.civilizations.values():
            if not civ.alive:
                continue
            borders = self._border_cache.get(civ.id)
            if borders is None:
                continue
            if self.selected_civ_id == civ.id:
                p.setPen(QPen(Qt.white, 2))
            else:
                p.setPen(QPen(QColor(civ.color).darker(150), 1))
            p.setBrush(Qt.NoBrush)
            ys, xs = np.where(borders)
            for x, y in zip(xs.tolist(), ys.tolist()):
                p.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # ── 3. Capital markers ──
        for civ in engine.civilizations.values():
            if not civ.alive:
                continue
            cx, cy = civ.capital
            px = cx * CELL_SIZE + CELL_SIZE // 2
            py = cy * CELL_SIZE + CELL_SIZE // 2
            p.setPen(QPen(Qt.white, 1.5))
            p.setBrush(QColor(255, 255, 200))
            s = max(3, CELL_SIZE // 3)
            p.drawPolygon(QPolygonF([
                QPointF(px, py - s), QPointF(px + s, py),
                QPointF(px, py + s), QPointF(px - s, py)]))

        # ── 4. Diplomatic routes ──
        drawn: set[tuple[int, int]] = set()
        for civ in engine.civilizations.values():
            if not civ.alive:
                continue
            for other_id, rel in civ.relations.items():
                if other_id not in engine.civilizations:
                    continue
                other = engine.civilizations[other_id]
                if not other.alive:
                    continue
                route_key = (min(civ.id, other_id), max(civ.id, other_id))
                if route_key in drawn:
                    continue
                drawn.add(route_key)
                if rel == Relation.ALLIED:
                    p.setPen(QPen(QColor(255, 215, 0, 80), 1.5, Qt.DashLine))
                elif rel == Relation.AT_WAR:
                    p.setPen(QPen(QColor(255, 50, 50, 100), 2, Qt.DashLine))
                elif rel == Relation.HOSTILE:
                    p.setPen(QPen(QColor(255, 165, 0, 60), 1, Qt.DotLine))
                else:
                    continue
                x1 = civ.capital[0] * CELL_SIZE + CELL_SIZE // 2
                y1 = civ.capital[1] * CELL_SIZE + CELL_SIZE // 2
                x2 = other.capital[0] * CELL_SIZE + CELL_SIZE // 2
                y2 = other.capital[1] * CELL_SIZE + CELL_SIZE // 2
                p.drawLine(x1, y1, x2, y2)

        # ── 5. Hover ──
        if self.hover_cell:
            hx, hy = self.hover_cell
            p.setPen(QPen(QColor(255, 255, 255, 160), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRect(hx * CELL_SIZE, hy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        p.end()

    def mouseMoveEvent(self, event):
        x = int(event.position().x() // CELL_SIZE)
        y = int(event.position().y() // CELL_SIZE)
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            self.hover_cell = (x, y)
            owner = self.engine.ownership[y, x]
            t_name = TERRAIN_NAMES[Terrain(self.engine.terrain[y, x])]
            res = TERRAIN_RESOURCES.get(Terrain(self.engine.terrain[y, x]), 0)
            if owner != -1 and owner in self.engine.civilizations:
                civ = self.engine.civilizations[owner]
                self.setToolTip(
                    f"{t_name} — {civ.name}\n"
                    f"Pop: {civ.population:,}  |  Res yield: {res}")
            else:
                self.setToolTip(f"{t_name} — Unclaimed\nRes yield: {res}")
        else:
            self.hover_cell = None
        self.update()

    def leaveEvent(self, event):
        self.hover_cell = None
        self.update()

    def mousePressEvent(self, event):
        x = int(event.position().x() // CELL_SIZE)
        y = int(event.position().y() // CELL_SIZE)
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            owner = self.engine.ownership[y, x]
            if owner != -1 and owner in self.engine.civilizations:
                self.selected_civ_id = owner
                self.civ_clicked.emit(owner)
            else:
                self.selected_civ_id = None
                self.civ_clicked.emit(-1)
            self.update()


# ════════════════════════════════════════════════════════════
# Map Legend
# ════════════════════════════════════════════════════════════
class MapLegendWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 140)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(0, 0, 0, 180))
        p.setPen(Qt.white)
        p.setFont(QFont("Sans", 8, QFont.Bold))
        p.drawText(6, 14, "Terrain Legend")
        p.setFont(QFont("Sans", 8))
        y_pos = 28
        for terrain, color in TERRAIN_COLORS.items():
            p.fillRect(6, y_pos, 12, 10, color)
            p.setPen(Qt.white)
            res = TERRAIN_RESOURCES[terrain]
            p.drawText(22, y_pos + 9, f"{TERRAIN_NAMES[terrain]} ({res})")
            y_pos += 17
        p.end()


# ════════════════════════════════════════════════════════════
# Graph Widget
# ════════════════════════════════════════════════════════════
class GraphWidget(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setMinimumHeight(170)
        self._show_territory = False

    def toggle_mode(self):
        self._show_territory = not self._show_territory
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ml, mr, mt, mb = 55, 20, 22, 25
        gw, gh = w - ml - mr, h - mt - mb
        p.fillRect(self.rect(), QColor(30, 30, 38))
        p.fillRect(ml, mt, gw, gh, QColor(18, 18, 26))

        alive = [c for c in self.engine.civilizations.values() if c.alive]
        if not alive:
            p.setPen(Qt.white)
            p.drawText(self.rect(), Qt.AlignCenter, "No data yet")
            p.end(); return

        histories = {
            c.id: c.territory_history if self._show_territory
            else c.population_history
            for c in alive
        }
        title = ("Territory Over Time" if self._show_territory
                 else "Population Over Time")
        max_len = max(len(h) for h in histories.values())
        if max_len < 2:
            p.setPen(Qt.white)
            p.drawText(self.rect(), Qt.AlignCenter, "Waiting...")
            p.end(); return

        all_vals = [v for hist in histories.values() for v in hist]
        max_val = max(max(all_vals), 1)

        p.setPen(QPen(QColor(60, 60, 70), 1))
        for i in range(5):
            gy = mt + int(gh * i / 4)
            p.drawLine(ml, gy, ml + gw, gy)
            p.setPen(QColor(140, 140, 140))
            p.setFont(QFont("Sans", 7))
            p.drawText(0, gy - 6, ml - 4, 14,
                       Qt.AlignRight | Qt.AlignVCenter,
                       f"{int(max_val * (1 - i / 4)):,}")
            p.setPen(QPen(QColor(60, 60, 70), 1))

        p.setPen(Qt.white)
        p.setFont(QFont("Sans", 9, QFont.Bold))
        p.drawText(ml, mt - 6, title)

        for civ in alive:
            hist = histories[civ.id]
            if len(hist) < 2:
                continue
            p.setPen(QPen(civ.color, 2))
            path = QPainterPath()
            for i, v in enumerate(hist):
                x = ml + gw * i / max(max_len - 1, 1)
                y = mt + gh * (1 - v / max_val)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            p.drawPath(path)

        p.setFont(QFont("Sans", 7))
        lx, ly = ml + 5, mt + 8
        for i, civ in enumerate(alive[:8]):
            p.setPen(QPen(civ.color, 2))
            p.drawLine(lx, ly + i * 13, lx + 14, ly + i * 13)
            p.setPen(QColor(200, 200, 200))
            p.drawText(lx + 18, ly + i * 13 + 4, civ.name)
        p.end()


# ════════════════════════════════════════════════════════════
# Civilization Info Panel
# ════════════════════════════════════════════════════════════
class CivInfoPanel(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.civ_id = None
        self.setMinimumWidth(270)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        self.title_label = QLabel("Select a civilization")
        self.title_label.setFont(QFont("Sans", 13, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.status_label)

        grp_style = (
            "QGroupBox { color: #ccc; border: 1px solid #555; "
            "border-radius: 4px; margin-top: 8px; padding-top: 14px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")

        stats_group = QGroupBox("Statistics")
        stats_group.setStyleSheet(grp_style)
        sg = QVBoxLayout(stats_group); sg.setSpacing(3)
        self.bars = {}
        for key, label, color in [
            ("population", "Population", "#4CAF50"),
            ("technology", "Technology", "#2196F3"),
            ("military",   "Military",   "#f44336"),
            ("resources",  "Resources",  "#FF9800"),
            ("culture",    "Culture",    "#9C27B0"),
            ("stability",  "Stability",  "#00BCD4"),
        ]:
            row = QHBoxLayout(); row.setSpacing(4)
            lbl = QLabel(label); lbl.setFixedWidth(72)
            lbl.setStyleSheet("color: #bbb; font-size: 11px;")
            bar = QProgressBar(); bar.setFixedHeight(14); bar.setTextVisible(True)
            bar.setStyleSheet(
                f"QProgressBar {{ border: 1px solid #555; border-radius: 3px; "
                f"background: #2a2a2a; color: white; font-size: 9px; "
                f"text-align: right; }} "
                f"QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}")
            val_lbl = QLabel(""); val_lbl.setFixedWidth(55)
            val_lbl.setStyleSheet("color: #ddd; font-size: 11px;")
            row.addWidget(lbl); row.addWidget(bar, 1); row.addWidget(val_lbl)
            sg.addLayout(row)
            self.bars[key] = (bar, val_lbl)
        layout.addWidget(stats_group)

        self.extra_label = QLabel("")
        self.extra_label.setStyleSheet("color: #aaa; font-size: 11px;")
        self.extra_label.setWordWrap(True)
        layout.addWidget(self.extra_label)

        self.diplo_group = QGroupBox("Diplomacy")
        self.diplo_group.setStyleSheet(grp_style)
        self.diplo_layout = QVBoxLayout(self.diplo_group)
        self.diplo_layout.setSpacing(2)
        layout.addWidget(self.diplo_group)
        layout.addStretch()
        self.refresh()

    def set_civilization(self, civ_id):
        self.civ_id = civ_id
        self.refresh()

    def refresh(self):
        civ = None
        if self.civ_id and self.civ_id in self.engine.civilizations:
            civ = self.engine.civilizations[self.civ_id]

        if civ is None or not civ.alive:
            self.title_label.setText("Select a civilization")
            self.title_label.setStyleSheet("color: white;")
            self.status_label.setText("Click a territory on the map")
            for key in self.bars:
                self.bars[key][0].setValue(0)
                self.bars[key][1].setText("")
            self.extra_label.setText("")
            while self.diplo_layout.count():
                item = self.diplo_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            return

        self.title_label.setText(f"■ {civ.name}")
        self.title_label.setStyleSheet(f"color: {civ.color.name()};")

        parts = []
        if civ.golden_age:
            parts.append("✨ Golden Age")
        parts.append(f"Age: {civ.age} years")
        if civ.war_weariness > 2:
            parts.append(f"War Weariness: {civ.war_weariness:.1f}")
        self.status_label.setText("  |  ".join(parts))

        max_pop = len(civ.territories) * 500
        self.bars["population"][0].setRange(0, max(max_pop, 1))
        self.bars["population"][0].setValue(civ.population)
        self.bars["population"][1].setText(f"{civ.population:,}")

        self.bars["technology"][0].setRange(0, 100)
        self.bars["technology"][0].setValue(int(civ.technology * 10))
        self.bars["technology"][1].setText(f"{civ.technology:.1f}/10")

        max_mil = max(
            (c.population * 0.01 + c.resources * 0.15
             for c in self.engine.civilizations.values() if c.alive),
            default=100) * 2
        self.bars["military"][0].setRange(0, max(int(max_mil), 1))
        self.bars["military"][0].setValue(int(civ.military_power))
        self.bars["military"][1].setText(f"{civ.military_power:.0f}")

        self.bars["resources"][0].setRange(0, 300)
        self.bars["resources"][0].setValue(int(civ.resources))
        self.bars["resources"][1].setText(f"{civ.resources:.0f}/300")

        self.bars["culture"][0].setRange(0, 100)
        self.bars["culture"][0].setValue(int(min(civ.culture, 100)))
        self.bars["culture"][1].setText(f"{civ.culture:.1f}")

        self.bars["stability"][0].setRange(0, 100)
        self.bars["stability"][0].setValue(int(civ.stability))
        self.bars["stability"][1].setText(f"{civ.stability:.0f}%")

        self.extra_label.setText(
            f"Territories: {len(civ.territories)}  |  "
            f"Capital: ({civ.capital[0]}, {civ.capital[1]})  |  "
            f"Founded: Year {civ.start_year}")

        while self.diplo_layout.count():
            item = self.diplo_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not civ.relations:
            lbl = QLabel("No diplomatic relations")
            lbl.setStyleSheet("color: #888; font-size: 10px;")
            self.diplo_layout.addWidget(lbl)
        else:
            for other_id, rel in sorted(civ.relations.items(), key=lambda x: x[1]):
                if other_id in self.engine.civilizations:
                    other = self.engine.civilizations[other_id]
                    if not other.alive:
                        continue
                    lbl = QLabel(f"  {other.name}: {RELATION_NAMES[rel]}")
                    lbl.setStyleSheet(
                        f"color: {RELATION_COLORS[rel].name()}; font-size: 11px;")
                    self.diplo_layout.addWidget(lbl)


# ════════════════════════════════════════════════════════════
# Main Window
# ════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        accel = (f"Numba: {'ON' if HAS_NUMBA else 'OFF'} | "
                 f"CuPy: {'ON' if HAS_CUPY else 'OFF'}")
        self.setWindowTitle(f"Civilization Simulation — Rise & Fall [{accel}]")
        self.engine = SimulationEngine()
        self.running = False
        self.speed = 5
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._build_ui()
        self._apply_styles()
        self._update_stats()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ── Left ──
        left = QVBoxLayout(); left.setSpacing(6)

        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)
        self.map_widget = MapWidget(self.engine)
        self.map_widget.civ_clicked.connect(self._on_civ_clicked)
        map_layout.addWidget(self.map_widget)
        self.legend = MapLegendWidget(self.map_widget)
        self.legend.move(5, 5); self.legend.raise_()
        left.addWidget(map_container, 0, Qt.AlignCenter)

        ctrl = QHBoxLayout(); ctrl.setSpacing(6)
        self.play_btn = QPushButton("▶  Play")
        self.play_btn.setFixedWidth(90)
        self.play_btn.clicked.connect(self._toggle_play)
        ctrl.addWidget(self.play_btn)
        self.step_btn = QPushButton("⏭  Step")
        self.step_btn.setFixedWidth(80)
        self.step_btn.clicked.connect(self._single_step)
        ctrl.addWidget(self.step_btn)
        self.reset_btn = QPushButton("🔄  Reset")
        self.reset_btn.setFixedWidth(80)
        self.reset_btn.clicked.connect(self._reset)
        ctrl.addWidget(self.reset_btn)
        ctrl.addSpacing(12); ctrl.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 60); self.speed_slider.setValue(self.speed)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self._change_speed)
        ctrl.addWidget(self.speed_slider)
        self.speed_label = QLabel(f"{self.speed} tps")
        self.speed_label.setFixedWidth(45)
        ctrl.addWidget(self.speed_label)
        ctrl.addStretch()
        self.year_label = QLabel("Year: 0")
        self.year_label.setFont(QFont("Sans", 12, QFont.Bold))
        self.year_label.setStyleSheet("color: #FFD700;")
        ctrl.addWidget(self.year_label)
        left.addLayout(ctrl)

        self.graph = GraphWidget(self.engine)
        self.graph.setMinimumWidth(GRID_W * CELL_SIZE)
        self.graph_toggle = QPushButton("📊 Toggle Population / Territory")
        self.graph_toggle.setFixedHeight(24)
        self.graph_toggle.clicked.connect(self.graph.toggle_mode)
        left.addWidget(self.graph_toggle)
        left.addWidget(self.graph)
        main_layout.addLayout(left, 1)

        # ── Right ──
        right = QVBoxLayout(); right.setSpacing(6)
        grp_style = (
            "QGroupBox { color: #ccc; border: 1px solid #555; "
            "border-radius: 4px; margin-top: 8px; padding-top: 14px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")

        overview_group = QGroupBox("Civilizations Overview")
        overview_group.setStyleSheet(grp_style)
        og = QVBoxLayout(overview_group)
        self.overview_table = QTableWidget()
        self.overview_table.setColumnCount(7)
        self.overview_table.setHorizontalHeaderLabels(
            ["Name", "Pop", "Terr", "Tech", "Mil", "Stab", "Status"])
        self.overview_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.overview_table.verticalHeader().setVisible(False)
        self.overview_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.overview_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.overview_table.setFixedHeight(210)
        self.overview_table.setStyleSheet(
            "QTableWidget { background: #1e1e26; color: #ddd; "
            "gridline-color: #444; font-size: 11px; } "
            "QHeaderView::section { background: #2a2a36; color: #ccc; "
            "padding: 3px; border: 1px solid #444; font-size: 11px; }")
        og.addWidget(self.overview_table)
        right.addWidget(overview_group)

        self.civ_panel = CivInfoPanel(self.engine)
        right.addWidget(self.civ_panel, 1)

        events_group = QGroupBox("Events Log")
        events_group.setStyleSheet(grp_style)
        eg = QVBoxLayout(events_group)
        self.event_log = QTextEdit(); self.event_log.setReadOnly(True)
        self.event_log.setStyleSheet(
            "background: #1a1a22; color: #ccc; font-size: 11px; "
            "border: 1px solid #444;")
        self.event_log.setFixedHeight(180)
        eg.addWidget(self.event_log)
        right.addWidget(events_group)

        right_widget = QWidget(); right_widget.setLayout(right)
        right_widget.setFixedWidth(380)
        main_layout.addWidget(right_widget)

    def _apply_styles(self):
        self.setStyleSheet(
            "QMainWindow { background: #1e1e2e; } "
            "QWidget { background: #1e1e2e; color: #ddd; } "
            "QPushButton { background: #3a3a4e; color: #eee; "
            "border: 1px solid #555; border-radius: 4px; "
            "padding: 5px 10px; font-size: 12px; } "
            "QPushButton:hover { background: #4a4a62; } "
            "QPushButton:pressed { background: #2a2a3e; } "
            "QLabel { background: transparent; } "
            "QSlider::groove:horizontal { border: 1px solid #555; "
            "height: 6px; background: #2a2a36; border-radius: 3px; } "
            "QSlider::handle:horizontal { background: #6a6aaa; "
            "border: 1px solid #555; width: 14px; margin: -4px 0; "
            "border-radius: 7px; }")

    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key_Space:   self._toggle_play()
        elif k == Qt.Key_R:     self._reset()
        elif k == Qt.Key_S:     self._single_step()
        elif k == Qt.Key_Escape:
            self.map_widget.selected_civ_id = None
            self.civ_panel.set_civilization(None)
            self.map_widget.update()
        else: super().keyPressEvent(event)

    def _toggle_play(self):
        self.running = not self.running
        if self.running:
            self.play_btn.setText("⏸  Pause")
            self.timer.start(1000 // self.speed)
        else:
            self.play_btn.setText("▶  Play")
            self.timer.stop()

    def _single_step(self):
        if not self.running:
            self.engine.step()
            self._refresh_all()

    def _reset(self):
        self.running = False
        self.play_btn.setText("▶  Play")
        self.timer.stop()
        self.engine.reset()
        self.map_widget.invalidate_terrain_cache()
        self.map_widget.selected_civ_id = None
        self.civ_panel.set_civilization(None)
        self._refresh_all()

    def _change_speed(self, val):
        self.speed = val
        self.speed_label.setText(f"{val} tps")
        if self.running:
            self.timer.setInterval(1000 // self.speed)

    def _tick(self):
        self.engine.step()
        self._refresh_all()

    def _refresh_all(self):
        self.map_widget.update()
        self.graph.update()
        self.civ_panel.refresh()
        self._update_stats()
        self._update_event_log()
        self._update_overview_table()

    def _on_civ_clicked(self, civ_id):
        self.civ_panel.set_civilization(civ_id if civ_id > 0 else None)

    def _update_stats(self):
        alive = [c for c in self.engine.civilizations.values() if c.alive]
        total_pop = sum(c.population for c in alive)
        total_terr = sum(len(c.territories) for c in alive)
        self.year_label.setText(
            f"Year: {self.engine.year}  |  Civs: {len(alive)}  |  "
            f"Pop: {total_pop:,}  |  Territory: {total_terr}")

    def _update_event_log(self):
        events = list(self.engine.events)[-50:]
        self.event_log.setPlainText("\n".join(events))
        sb = self.event_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _update_overview_table(self):
        alive = sorted(
            [c for c in self.engine.civilizations.values() if c.alive],
            key=lambda c: c.population, reverse=True)
        self.overview_table.setRowCount(len(alive))
        for i, civ in enumerate(alive):
            name_item = QTableWidgetItem(f"■ {civ.name}")
            name_item.setForeground(civ.color)
            self.overview_table.setItem(i, 0, name_item)

            pop_item = QTableWidgetItem(f"{civ.population:,}")
            pop_item.setTextAlignment(Qt.AlignCenter)
            self.overview_table.setItem(i, 1, pop_item)

            terr_item = QTableWidgetItem(f"{len(civ.territories)}")
            terr_item.setTextAlignment(Qt.AlignCenter)
            self.overview_table.setItem(i, 2, terr_item)

            tech_item = QTableWidgetItem(f"{civ.technology:.1f}")
            tech_item.setTextAlignment(Qt.AlignCenter)
            self.overview_table.setItem(i, 3, tech_item)

            mil_item = QTableWidgetItem(f"{civ.military_power:.0f}")
            mil_item.setTextAlignment(Qt.AlignCenter)
            self.overview_table.setItem(i, 4, mil_item)

            stab_item = QTableWidgetItem(f"{civ.stability:.0f}%")
            stab_item.setTextAlignment(Qt.AlignCenter)
            if civ.stability > 60:
                stab_item.setForeground(QColor(76, 175, 80))
            elif civ.stability > 30:
                stab_item.setForeground(QColor(255, 152, 0))
            else:
                stab_item.setForeground(QColor(244, 67, 54))
            self.overview_table.setItem(i, 5, stab_item)

            at_war = any(r == Relation.AT_WAR for r in civ.relations.values())
            if civ.golden_age:
                status = "✨ Golden Age"
            elif at_war:
                status = "⚔️ At War"
            elif civ.stability < 30:
                status = "⚠️ Unstable"
            else:
                status = "✔ Stable"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            self.overview_table.setItem(i, 6, status_item)


# ════════════════════════════════════════════════════════════
# Entry Point
# ════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()