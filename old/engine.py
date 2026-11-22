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

from CivSim.config import (
    Terrain, TerrainPreset, TERRAIN_PRESETS, RESOURCE_TYPES, RELIGIONS, WONDERS,
    REBEL_NAMES, CIV_TEMPLATES, PERSONALITY_ARCHETYPES, SEASON_NAMES, FOOD_MULTIPLIERS,
    DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT, SEASON_LENGTH, AUTO_SAVE_INTERVAL,
    GOVERNMENTS,
    BIRTH_RATE, DEATH_RATE, FAMINE_THRESHOLD, FAMINE_DEATH_RATE,
    STABILITY_BIRTH_MULT, STABILITY_DEATH_MULT, POP_HARD_CAP_MULT,
    TECH_DIFFUSION_RATE, TECH_DIFFUSION_MIN_GAP,
    BORDER_FRICTION_BASE, BORDER_FRICTION_RELIGION_MULT,
    REBEL_TECH_INHERIT, REBEL_CULTURE_INHERIT,
)
from CivSim.database import GameDefs, AnalyticsDB
from CivSim.ai import DStarLite, ActionType, ThreatAssessment, StrategicState
from CivSim.models import Civ, Leader, WorldEvent, CivSnapshot, GenerationReport


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
