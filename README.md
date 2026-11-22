# Civilization Simulation

An interactive, algorithmically-optimized civilization simulation with a real-time GUI. Watch emergent empires expand, trade, wage war, and collapse on a procedurally generated island map.

---

## Features

- **Procedural Island Terrain**: Radial gradient masking creates natural continents with 6 biome types, each with distinct resource yields.
- **Emergent Civilizations**: Up to 12 AI civs expand, compete for territory, and interact diplomatically or militarily with no scripted narrative.
- **Full Diplomacy System**: Dynamic relationships ranging from Allied to At War, featuring culture flips, peace treaties, and technology sharing.
- **Warfare & Conquest**: Border skirmishes, sieges, capital captures, and civilization collapse driven by war weariness.
- **Dynamic Events**: Plagues, famines, natural disasters, golden ages, cultural renaissances, technological breakthroughs, civil wars, and great migrations.
- **Interactive Map**: Click territories to inspect civilizations, hover for cell data, and view diplomatic routes drawn between capitals.
- **Live Analytics**: Real-time population and territory-over-time line charts for all living civilizations.
- **Detailed Info Panel**: Real-time stats with progress bars and a breakdown of diplomatic relations.

---

## Getting Started

### Prerequisites

- Python 3.10+
- PySide6
- NumPy

### Optional Acceleration

Installing these packages is not required but will significantly improve performance for terrain generation and rendering:

| Package | Purpose | Install Command |
|---|---|---|
| Numba | JIT-compiled kernels for terrain gen, resource income, and adjacency | `pip install numba` |
| CuPy | GPU-accelerated array operations and map rendering | `pip install cupy-cuda12x` *(match your CUDA version)* |

### Installation and Running

```bash
pip install PySide6 numpy
# optionally: pip install numba

python app.py
```

---

## Controls and Usage

The simulation runs autonomously. Your role is observer and explorer:

| Action | Effect |
|---|---|
| Click a territory | Selects that civilization and displays its stats in the right panel |
| Click unclaimed land | Deselects the current civilization |
| Hover over a cell | Shows a tooltip with terrain type, owner, population, and resource yield |
| Speed slider | Adjusts the simulation speed (ticks per second) |
| Pause / Play | Pauses or resumes the simulation |
| Reset | Regenerates the entire world with new terrain and civilizations |
| Toggle Graph | Switches the bottom graph between Population and Territory over time |

---

## Simulation Mechanics

### Terrain and Resources

| Terrain | Resource Yield | Notes |
|---|---|---|
| Ocean | 0 | Impassable; civilizations cannot expand here |
| Plains | 3 | Highest yield; preferred for expansion |
| Forest | 2 | Good yield |
| Mountain | 2 | Moderate yield |
| Desert | 1 | Low yield |
| Tundra | 1 | Low yield; appears near map poles |

### Civilization Stats

- **Population**: Grows based on capacity, stability, technology, and golden age multiplier. Capacity equals territories multiplied by 500.
- **Technology**: Advances stochastically, scaled by culture, stability, and population. Capped at 10.
- **Military Power**: Derived from population, resources, and technology.
- **Resources**: Income from territory (vectorized calculation). Spent on expansion. Capped at 300.
- **Culture**: Grows over time; enables culture flips on weaker neighboring civilizations.
- **Stability**: Affected by overpopulation, resource scarcity, and war weariness. If stability drops to 0, the civilization collapses.
- **War Weariness**: Accumulates during war and decays during peace. High weariness forces peace treaties.

### Diplomacy

Relationships evolve naturally based on proximity, culture, and stability:

```
Neutral  -->  Friendly  -->  Allied
  |                         ^
  v                         |
Hostile  ----------------> At War
```

- **Allied**: Resource sharing, technology transfer, and mutual defense.
- **At War**: Battles, territory capture, and capital sieges.
- **Peace**: Can emerge from war weariness or diplomatic drift.

### Random Events

| Event | Effect | Probability per Year |
|---|---|---|
| Plague | Population -5-15%, stability drop | 0.4% |
| Famine | Resources -15-40, stability drop | 0.3% |
| Natural Disaster | Population -2-8%, stability drop | 0.2% |
| Resource Discovery | Resources +15-50 | 0.3% |
| Cultural Renaissance | Culture +3-10, stability +5 | 0.3% |
| Tech Breakthrough | Technology +0.2-0.5 | 0.2% |
| Great Migration | Population +3-8%, culture gain | 0.2% |
| Grand Monument | Resources +20-45, culture gain | 0.2% |
| Civil War | Lose 25% of territory (requires low stability) | 4% (if stability < 20) |

---

## Technical Highlights

The simulation is built with a focus on algorithmic efficiency, replacing slow Python loops with vectorized and JIT-compiled operations:

**Spatial Queries**
- `SpatialHelper` uses a shifted-array technique for O(H*W) vectorized NumPy spatial queries instead of per-cell Python iteration for border, frontier, and capturable cell detection.

**Diplomacy Optimization**
- An adjacency graph limits diplomacy and war interactions to bordering civilization pairs, reducing complexity from O(A²) all-pairs checking to O(E) edge checking.

**Data Integrity**
- A centralized `_set_cell_owner()` method acts as the single source of truth for territory synchronization, updating the ownership array, territory sets, and adjacency staleness simultaneously.

**Performance Caching**
- `collections.deque` provides O(1) event log rotation with a fixed maximum size.
- A cached terrain base image avoids recomputing static terrain colors every frame.
- A pre-computed terrain resource map enables vectorized `np.sum` for resource income.

**Hardware Acceleration**
- Optional **Numba** JIT kernels accelerate noise smoothing, terrain classification, resource income, and adjacency computation.
- Optional **CuPy** GPU rendering offloads map image composition for large grids.

---

