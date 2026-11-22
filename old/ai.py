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
