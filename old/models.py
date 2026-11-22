"""
Autonomous Civilization Simulation - Data Models
Core game objects: Leader, Civilization, WorldEvent, snapshots, and generation reports.
"""
import random
from PySide6.QtGui import QColor

from CivSim.config import (
    RELIGIONS, WONDERS, REBEL_NAMES, CIV_TEMPLATES, PERSONALITY_ARCHETYPES,
    GOVERNMENTS, LEADER_FIRST_NAMES, LEADER_TITLES, LEADER_EPITHETS,
)
from CivSim.ai import CivAgent


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
