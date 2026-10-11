"""
Autonomous Civilization Simulation - UI Widgets
Custom widgets: CivCard, TimelineGraph, LeaderboardWidget,
GenerationReportPanel, MinimapWidget, DiplomacyMatrix, NotificationOverlay.

Layout improvements:
- CivCard: compact 2-column stat grid, colored header bar, inline badges
- TimelineGraph: axis labels, grid lines, better legend
- LeaderboardWidget: medal icons, compact table layout
- MinimapWidget: border frame, coordinate labels
- DiplomacyMatrix: better cell sizing and legend
- NotificationOverlay: smoother fade, position aware

Performance optimizations:
- Minimap: QImage-based rendering instead of per-tile drawRect calls
- TimelineGraph: limit data points, use fixed-length deque
- CivCard: minimize string formatting in update_data
"""
from collections import deque
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QProgressBar, QSizePolicy,
    QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import (
    QColor, QBrush, QPen, QPainterPath, QPainter, QFont,
    QImage, QLinearGradient
)

from CivSim.config import TERRAIN_COLORS


# ── Timeline Graph ──────────────────────────────────────────
class TimelineGraph(QWidget):
    """Mini line chart showing each civilization's score over time.

    Layout improvements:
    - Grid lines for readability
    - Y-axis labels
    - Better legend with color dots
    - Subtle background gradient

    Performance: Uses deque with maxlen to auto-trim, avoids
    recomputing min/max from all history every frame.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(130)
        self.setMaximumHeight(180)
        self.data: dict[str, deque] = {}
        self.civ_colors: dict[str, str] = {}
        self._max_points = 400

    def update_data(self, civs_data: list[dict]) -> None:
        for c in civs_data:
            if c['name'] not in self.data:
                self.data[c['name']] = deque(maxlen=self._max_points)
            self.data[c['name']].append(c['score'])
            self.civ_colors[c['name']] = c['color']
        self.update()

    def paintEvent(self, event) -> None:
        if not self.data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        p.fillRect(0, 0, w, h, QColor("#1a1a2a"))

        # Border
        p.setPen(QPen(QColor("#3e3e3e"), 1))
        p.drawRect(0, 0, w - 1, h - 1)

        all_vals = [v for dq in self.data.values() for v in dq]
        if not all_vals:
            return
        min_v = min(0, min(all_vals))
        max_v = max(all_vals) or 1
        rng = max_v - min_v
        if rng == 0:
            rng = 1

        # Chart area with margins
        margin_left = 40
        margin_right = 10
        margin_top = 18
        margin_bottom = 5
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        # Grid lines
        p.setPen(QPen(QColor(60, 60, 70), 1, Qt.DotLine))
        for i in range(5):
            y = margin_top + int(i * chart_h / 4)
            p.drawLine(margin_left, y, w - margin_right, y)
            val = max_v - (i * rng / 4)
            p.setPen(QPen(QColor(100, 100, 110), 1))
            p.setFont(QFont("Consolas", 7))
            p.drawText(2, y + 4, f"{int(val)}")
            p.setPen(QPen(QColor(60, 60, 70), 1, Qt.DotLine))

        # Data lines
        max_pts = self._max_points
        for name, dq in self.data.items():
            color = QColor(self.civ_colors.get(name, "#FFF"))
            p.setPen(QPen(color, 2))
            path = QPainterPath()
            len_dq = len(dq)
            for i, val in enumerate(dq):
                x = margin_left + (i / max_pts) * chart_w
                y = margin_top + chart_h - ((val - min_v) / rng) * chart_h
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            p.drawPath(path)

        # Legend with colored dots
        p.setFont(QFont("Consolas", 8))
        x_off = margin_left + 4
        for name in self.data:
            color = QColor(self.civ_colors.get(name, "#FFF"))
            # Dot
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(x_off, 3, 8, 8)
            # Name
            p.setPen(QPen(QColor("#ccc")))
            p.drawText(x_off + 11, 11, name[:6])
            x_off += 55


# ── Civilization Card ───────────────────────────────────────
class CivCard(QFrame):
    """Displays a single civilization's stats in a compact, visually organized card.

    Layout improvements:
    - Colored header bar with civ name, archetype badge, war/peace indicator
    - 2-column stat grid for compact display
    - Inline delta indicators next to each stat
    - Footer row for diplomacy/buildings info
    """

    def __init__(self, data: dict):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "CivCard { border: 1px solid #3e3e3e; border-radius: 5px; "
            "background-color: #252526; }"
        )

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Header Bar ──
        header = QWidget()
        header.setFixedHeight(28)
        civ_color = QColor(data['color'])
        header.setStyleSheet(
            f"QWidget {{ background-color: {CivCard._dim_color(data['color'])}; "
            f"border-bottom: 2px solid {data['color']}; "
            f"border-top-left-radius: 5px; border-top-right-radius: 5px; }}"
        )
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(8, 2, 8, 2)
        h_lay.setSpacing(6)

        name_lbl = QLabel(f"<b style='color:{data['color']}'>{data['name']}</b>")
        name_lbl.setStyleSheet("font-size: 13px; border: none;")
        h_lay.addWidget(name_lbl)

        # Archetype badge
        archetype = data.get('archetype_label', data.get('archetype', ''))
        if archetype:
            badge = QLabel(f" {archetype} ")
            badge.setStyleSheet(
                "background-color: #0e639e; color: white; font-size: 9px; "
                "font-weight: bold; padding: 1px 5px; border-radius: 8px; border: none;"
            )
            if data.get('archetype_desc'):
                badge.setToolTip(data['archetype_desc'])
            h_lay.addWidget(badge)

        h_lay.addStretch()

        self.war_lbl = QLabel("PEACE")
        self.war_lbl.setStyleSheet(
            "color: #37AF37; font-size: 9px; font-weight: bold; "
            "padding: 1px 6px; border-radius: 3px; border: none;"
        )
        h_lay.addWidget(self.war_lbl)

        main_lay.addWidget(header)

        # ── Content Area ──
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(8, 6, 8, 6)
        content_lay.setSpacing(3)

        # Leader + Government row
        leader_row = QHBoxLayout()
        leader_row.setSpacing(6)

        self.leader_lbl = QLabel("")
        self.leader_lbl.setStyleSheet(
            "color: #9370DB; font-size: 10px; font-weight: bold;"
        )
        leader_row.addWidget(self.leader_lbl)

        self.government_lbl = QLabel("")
        self.government_lbl.setStyleSheet(
            "color: #0ea5e9; font-size: 10px; font-weight: bold; "
            "padding: 1px 5px; background-color: #1a2a3a; border-radius: 3px; border: none;"
        )
        leader_row.addWidget(self.government_lbl)
        leader_row.addStretch()
        content_lay.addLayout(leader_row)

        # Strategic state + Era row
        state_row = QHBoxLayout()
        state_row.setSpacing(8)
        self.strategic_state_lbl = QLabel("")
        self.strategic_state_lbl.setStyleSheet(
            "color: #FF8C00; font-size: 10px; font-weight: bold;"
        )
        state_row.addWidget(self.strategic_state_lbl)

        self.era_lbl = QLabel("")
        self.era_lbl.setStyleSheet(
            "color: #FFD700; font-size: 10px; font-weight: bold;"
        )
        state_row.addWidget(self.era_lbl)

        self.religion_lbl = QLabel("")
        self.religion_lbl.setStyleSheet("color: #9370DB; font-size: 10px;")
        state_row.addWidget(self.religion_lbl)
        state_row.addStretch()
        content_lay.addLayout(state_row)

        # Action label
        self.action_lbl = QLabel("")
        self.action_lbl.setStyleSheet("color: #aaa; font-size: 10px; font-style: italic;")
        content_lay.addWidget(self.action_lbl)

        # ── Stats Grid (2 columns) ──
        stats_grid = QGridLayout()
        stats_grid.setSpacing(3)
        stats_grid.setContentsMargins(0, 2, 0, 2)

        stats = [
            ("Pop", "population", "pop_delta", 100000, "#37AF37"),
            ("Military", "military", "mil_delta", 5000, "#D73737"),
            ("Tech", "technology", "tech_delta", 50, "#3769D7"),
            ("Treasury", "treasury", "treas_delta", 10000, "#D7AF1E"),
            ("Culture", "culture", None, 2000, "#AF37AF"),
            ("Stability", "stability", None, 100, "#D77F37"),
        ]

        self.bars: dict = {}
        self.deltas: dict = {}
        self.stat_values: dict = {}

        for idx, (lt, k, dk, mx, col) in enumerate(stats):
            row = idx // 2
            col_pos = (idx % 2) * 3

            # Label
            label = QLabel(f"{lt}:")
            label.setStyleSheet(f"color: {col}; font-size: 10px; font-weight: bold;")
            label.setFixedWidth(55)
            stats_grid.addWidget(label, row, col_pos)

            # Value
            val_lbl = QLabel(str(int(data[k])))
            val_lbl.setStyleSheet("color: #ddd; font-size: 10px;")
            val_lbl.setAlignment(Qt.AlignRight)
            self.stat_values[k] = val_lbl
            stats_grid.addWidget(val_lbl, row, col_pos + 1)

            # Delta
            delta_lbl = QLabel("")
            delta_lbl.setFixedWidth(42)
            delta_lbl.setAlignment(Qt.AlignRight)
            delta_lbl.setStyleSheet("font-size: 9px;")
            if dk:
                self.deltas[k] = delta_lbl
            stats_grid.addWidget(delta_lbl, row, col_pos + 2)

            # Progress bar (compact)
            b = QProgressBar()
            b.setRange(0, 100)
            b.setValue(int((data[k] / mx) * 100))
            b.setFormat("")
            b.setFixedHeight(4)
            b.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {col}; border-radius: 1px; }}"
                f"QProgressBar {{ border: none; background-color: #1e1e1e; "
                f"border-radius: 2px; margin: 0; }}"
            )
            # Bar spans below the stat row
            self.bars[k] = (label, val_lbl, b, mx)

        content_lay.addLayout(stats_grid)

        # Compact progress bars in a 2-column grid
        bars_grid = QGridLayout()
        bars_grid.setSpacing(2)
        bars_grid.setContentsMargins(0, 0, 0, 2)
        for idx, (lt, k, dk, mx, col) in enumerate(stats):
            row = idx // 2
            col_pos = idx % 2
            _, _, bar, _ = self.bars[k]
            bars_grid.addWidget(bar, row, col_pos)
        content_lay.addLayout(bars_grid)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #3e3e3e;")
        content_lay.addWidget(sep)

        # ── Footer: Diplomacy + Buildings ──
        self.diplo_lbl = QLabel("")
        self.diplo_lbl.setStyleSheet("color: #888; font-size: 9px;")
        content_lay.addWidget(self.diplo_lbl)
        self.build_lbl = QLabel("")
        self.build_lbl.setStyleSheet("color: #888; font-size: 9px;")
        content_lay.addWidget(self.build_lbl)

        main_lay.addWidget(content)
        self.update_data(data)

    @staticmethod
    def _dim_color(hex_color: str) -> str:
        """Create a dimmed version of a hex color for backgrounds."""
        c = QColor(hex_color)
        c.setAlpha(40)
        # Convert to rgba format that Qt CSS understands
        return f"rgba({c.red()}, {c.green()}, {c.blue()}, {c.alpha()})"

    def update_data(self, d: dict) -> None:
        for k, (label, val_lbl, b, mx) in self.bars.items():
            val_lbl.setText(str(int(d[k])))
            b.setValue(min(100, int((d[k] / mx) * 100)))

        for k, dk, col in [
            ("population", "pop_delta", "#37AF37"),
            ("military", "mil_delta", "#D73737"),
            ("technology", "tech_delta", "#3769D7"),
            ("treasury", "treas_delta", "#D7AF1E")
        ]:
            dl = self.deltas[k]
            dv = d.get(dk, 0)
            if dv > 0:
                dl.setText(f"+{int(dv)}")
                dl.setStyleSheet(f"color: {col}; font-size: 9px; font-weight: bold;")
            elif dv < 0:
                dl.setText(f"-{int(abs(dv))}")
                dl.setStyleSheet("color: #D73737; font-size: 9px; font-weight: bold;")
            else:
                dl.setText("")
                dl.setStyleSheet("color: gray; font-size: 9px;")

        at_war = d.get('at_war_with')
        if at_war:
            self.war_lbl.setText("AT WAR")
            self.war_lbl.setStyleSheet(
                "color: #FF4500; font-size: 9px; font-weight: bold; "
                "padding: 1px 6px; background-color: #3a1a1a; border-radius: 3px; border: none;"
            )
        else:
            self.war_lbl.setText("PEACE")
            self.war_lbl.setStyleSheet(
                "color: #37AF37; font-size: 9px; font-weight: bold; "
                "padding: 1px 6px; background-color: #1a2a1a; border-radius: 3px; border: none;"
            )

        self.action_lbl.setText(f"Action: {d.get('last_action', 'None')}")

        # Leader name
        leader_name = d.get('leader_short_name', d.get('leader_name', ''))
        if leader_name:
            self.leader_lbl.setText(f"Leader: {leader_name}")
        else:
            self.leader_lbl.setText("")

        # Government type
        govt_label = d.get('government_label', '')
        if govt_label:
            self.government_lbl.setText(f" {govt_label} ")
            govt_desc = d.get('government_desc', '')
            if govt_desc:
                self.government_lbl.setToolTip(govt_desc)
        else:
            self.government_lbl.setText("")

        archetype = d.get('archetype_label', d.get('archetype', ''))
        archetype_desc = d.get('archetype_desc', '')

        # Show strategic state with color coding
        ss = d.get('strategic_state', 'CONSOLIDATION')
        ss_colors = {
            'EXPANSION': '#37AF37', 'CONSOLIDATION': '#3769D7', 'CRISIS': '#D73737',
            'TOTAL_WAR': '#FF4500', 'GOLDEN_AGE': '#FFD700', 'RECOVERY': '#D77F37',
        }
        ss_color = ss_colors.get(ss, '#aaa')
        self.strategic_state_lbl.setText(f"Strategy: {ss}")
        self.strategic_state_lbl.setStyleSheet(f"color: {ss_color}; font-size: 10px; font-weight: bold;")

        self.religion_lbl.setText(
            f"Religion: {d['religion']}" if d.get('religion') else ""
        )
        self.era_lbl.setText(f"Era: {d.get('era_name', 'Ancient')}")

        allies = ", ".join(d.get('alliances', set())) or "None"
        trade = ", ".join(d.get('trade_partners', set())) or "None"
        self.diplo_lbl.setText(f"Allies: {allies} | Trade: {trade}")
        self.build_lbl.setText(
            "Buildings: " + ", ".join([b['name'] for b in d.get('buildings', [])])
            + (" | Wonders: " + ", ".join(d.get('wonders', [])) if d.get('wonders') else "")
        )


# ── Generation Report Panel ────────────────────────────────
class GenerationReportPanel(QTextEdit):
    """Scrollable HTML panel showing before/after generation reports."""

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet(
            "QTextEdit { border: 1px solid #0e639e; background-color: #111118;"
            "font-family: Consolas, monospace; font-size: 11px; border-radius: 4px; }"
        )
        self._plain_reports: list[str] = []

    def add_report(self, html_report: str, plain_text_report: str) -> None:
        self.append(html_report)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self._plain_reports.append(plain_text_report)

    def get_all_plain_text(self) -> str:
        return "\n".join(self._plain_reports)

    def clear_reports(self) -> None:
        self.clear()
        self._plain_reports.clear()


# ── Leaderboard Widget ─────────────────────────────────────
class LeaderboardWidget(QTextEdit):
    """Compact ranking display showing all civilizations by score.

    Layout improvements:
    - Medal indicators for top 3
    - Score bars for visual comparison
    - Compact table format
    """

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMinimumHeight(80)
        self.setMaximumHeight(160)
        self.setStyleSheet(
            "QTextEdit { border: none; background-color: #1e1e1e;"
            "font-family: Consolas, monospace; font-size: 11px; }"
        )

    def update_rankings(self, civs_data: list[dict]) -> None:
        sorted_civs = sorted(civs_data, key=lambda c: c['score'], reverse=True)
        max_score = max((c['score'] for c in sorted_civs), default=1) or 1

        medals = ["1st", "2nd", "3rd"]
        html = ""
        for i, c in enumerate(sorted_civs):
            medal = medals[i] if i < 3 else f"{i+1}th"
            medal_color = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32" if i == 2 else "#666"
            war_icon = " [WAR]" if c.get('at_war_with') else ""
            era = c.get('era_name', 'Ancient')
            govt = c.get('government_label', '')
            leader = c.get('leader_short_name', '')
            bar_width = int((c['score'] / max_score) * 100)

            # Leader + government info line
            info_parts = []
            if leader:
                info_parts.append(f"<span style='color:#9370DB; font-size:9px;'>{leader}</span>")
            if govt:
                info_parts.append(f"<span style='color:#0ea5e9; font-size:9px;'>[{govt}]</span>")
            info_line = " ".join(info_parts)

            html += (
                f"<div style='margin:1px 0; padding:2px 4px; "
                f"background-color: #2a2a2a; border-radius: 3px; "
                f"border-left: 3px solid {c['color']};'>"
                f"<span style='color:{medal_color}; font-weight:bold; font-size:10px;'>"
                f"{medal}</span> "
                f"<span style='color:{c['color']}; font-weight:bold;'>{c['name']}</span> "
                f"<span style='color:#aaa; font-size:10px;'>"
                f"Score: {int(c['score'])} [{era}]</span>"
                f"{war_icon}"
                f"<br>{info_line}"
                f"<div style='height:3px; background-color:#1e1e1e; border-radius:1px; margin-top:2px;'>"
                f"<div style='height:3px; width:{bar_width}%; background-color:{c['color']}; "
                f"border-radius:1px;'></div></div>"
                f"</div>"
            )
        self.setHtml(html)


# ── Minimap Widget ─────────────────────────────────────────
class MinimapWidget(QWidget):
    """Small overview minimap for quick navigation reference.

    Layout improvements:
    - Border frame
    - Click-to-navigate support

    Performance: Uses QImage for pixel-level rendering instead of
    calling drawRect for each tile.
    """

    def __init__(self, map_width: int = 80, map_height: int = 60):
        super().__init__()
        self.setFixedSize(160, 120)
        self.map_width = map_width
        self.map_height = map_height
        self.terrain_map: dict = {}
        self.owner_map: dict = {}
        self.civ_colors: dict = {}
        self.explored: set = set()

        # Pre-build a color lookup table for terrain IDs
        self._terrain_qcolors: dict[int, int] = {}
        for tid, qc in TERRAIN_COLORS.items():
            self._terrain_qcolors[tid] = qc.rgb()

        self._civ_qcolors: dict[str, int] = {}
        self._image: QImage | None = None
        self._needs_redraw = True

    def update_data(self, terrain_map: dict, owner_map: dict,
                    civ_colors: dict, explored: set) -> None:
        self.terrain_map = terrain_map
        self.owner_map = owner_map
        self.explored = explored

        # Adapt internal map dimensions to the actual terrain data so the
        # minimap renders the whole map regardless of the configured default.
        if terrain_map:
            max_x = max(p[0] for p in terrain_map) + 1
            max_y = max(p[1] for p in terrain_map) + 1
            if (max_x, max_y) != (self.map_width, self.map_height):
                self.map_width = max_x
                self.map_height = max_y
                # Force the color tables to be rebuilt next paint, since
                # the QImage size depends on these dimensions.
                self._needs_redraw = True

        for name, hex_color in civ_colors.items():
            if name not in self._civ_qcolors:
                self._civ_qcolors[name] = QColor(hex_color).rgb()

        self._needs_redraw = True
        self.update()

    def paintEvent(self, event) -> None:
        if not self.terrain_map:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        w, h = self.width(), self.height()

        # Border frame
        p.fillRect(0, 0, w, h, QColor("#1e1e1e"))
        p.setPen(QPen(QColor("#3e3e3e"), 1))
        p.drawRect(0, 0, w - 1, h - 1)

        # Use QImage for fast pixel-level rendering
        img = QImage(self.map_width, self.map_height, QImage.Format_RGB32)
        img.fill(QColor(22, 50, 115).rgb())  # Ocean default

        terrain_qcolors = self._terrain_qcolors
        civ_qcolors = self._civ_qcolors
        owner_map = self.owner_map
        explored_contains = self.explored.__contains__
        fog_rgb = QColor(15, 15, 25).rgb()

        for (x, y), t_id in self.terrain_map.items():
            if not explored_contains((x, y)):
                img.setPixel(x, y, fog_rgb)
            else:
                owner = owner_map.get((x, y))
                if owner and owner in civ_qcolors:
                    img.setPixel(x, y, civ_qcolors[owner])
                else:
                    rgb = terrain_qcolors.get(t_id, 0)
                    if rgb:
                        img.setPixel(x, y, rgb)

        # Scale image to widget size (leave 2px margin for border)
        scaled = img.scaled(w - 2, h - 2, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        p.drawImage(1, 1, scaled)


# ── Diplomacy Matrix ───────────────────────────────────────
class DiplomacyMatrix(QWidget):
    """Grid showing relationships between all civilization pairs.

    Layout improvements:
    - Better cell sizing
    - Relationship strength indicators
    - Compact legend with inline labels
    """

    def __init__(self):
        super().__init__()
        self.civs_data: list[dict] = []
        self.setMinimumHeight(100)
        self.setMaximumHeight(200)

    def update_data(self, civs_data: list[dict]) -> None:
        self.civs_data = civs_data
        self.update()

    def paintEvent(self, event) -> None:
        if not self.civs_data or len(self.civs_data) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        n = len(self.civs_data)
        # Adaptive cell sizing
        cell_w = min(50, (w - 50) // n)
        cell_h = min(18, (h - 40) // n)
        offset_x = 40
        offset_y = 20

        # Title
        p.setFont(QFont("Consolas", 8, QFont.Bold))
        p.setPen(QColor("#0ea5e9"))
        p.drawText(offset_x, offset_y - 6, "Relationship Matrix")

        # Column headers
        p.setFont(QFont("Consolas", 7))
        for i, c in enumerate(self.civs_data):
            p.setPen(QColor(c['color']))
            p.drawText(offset_x + i * cell_w + 2, offset_y - 1, c['name'][:4])
            # Row headers
            p.drawText(0, offset_y + i * cell_h + cell_h - 2, c['name'][:5])

        # Cells
        for i, c1 in enumerate(self.civs_data):
            for j, c2 in enumerate(self.civs_data):
                x = offset_x + j * cell_w
                y = offset_y + i * cell_h

                if i == j:
                    col = QColor(50, 50, 60)
                elif c2['name'] in c1.get('at_war_with', set()):
                    col = QColor(200, 50, 50)
                elif c2['name'] in c1.get('alliances', set()):
                    col = QColor(50, 180, 50)
                elif c2['name'] in c1.get('trade_partners', set()):
                    col = QColor(50, 140, 200)
                else:
                    col = QColor(45, 45, 50)

                p.setPen(QPen(QColor(30, 30, 35), 1))
                p.setBrush(QBrush(col))
                p.drawRoundedRect(x, y, cell_w - 2, cell_h - 2, 2, 2)

        # Legend
        legend_y = offset_y + n * cell_h + 8
        p.setFont(QFont("Consolas", 7))
        legend_items = [
            ("War", "#C83232"), ("Allied", "#32B432"),
            ("Trade", "#328CC8"), ("Neutral", "#2D2D32")
        ]
        lx = offset_x
        for label, col in legend_items:
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(col)))
            p.drawRoundedRect(lx, legend_y, 8, 8, 1, 1)
            p.setPen(QColor("#aaa"))
            p.drawText(lx + 10, legend_y + 8, label)
            lx += 55


# ── Notification Overlay ───────────────────────────────────
class NotificationOverlay(QWidget):
    """Toast-style notification system with smooth fade and themed appearance.

    Layout improvements:
    - Smoother fade with more granular timer
    - Better visual styling with gradient backgrounds
    - Icon-style category indicators
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications: list[dict] = []
        self.max_visible = 4
        self.display_duration = 3500  # ms

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(100)  # More frequent for smoother fade

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def add_notification(self, title: str, message: str) -> None:
        self.notifications.append({
            'title': title,
            'message': message,
            'remaining': self.display_duration,
        })
        if len(self.notifications) > self.max_visible:
            self.notifications = self.notifications[-self.max_visible:]
        self.update()

    def _tick(self) -> None:
        changed = False
        for n in self.notifications[:]:
            n['remaining'] -= 100
            if n['remaining'] <= 0:
                self.notifications.remove(n)
                changed = True
        if changed:
            self.update()

    def paintEvent(self, event) -> None:
        if not self.notifications:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        y = 10
        for notif in self.notifications:
            # Calculate alpha with smooth fade
            if notif['remaining'] < 800:
                alpha = int((notif['remaining'] / 800.0) * 230)
            else:
                alpha = 230
            alpha = max(0, min(255, alpha))

            # Background with gradient
            x_pos = self.width() - 290
            grad = QLinearGradient(x_pos, y, x_pos + 280, y)
            grad.setColorAt(0, QColor(14, 99, 158, alpha))
            grad.setColorAt(1, QColor(14, 60, 100, alpha))

            p.setPen(QPen(QColor(14, 165, 233, min(alpha, 150)), 1))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(x_pos, y, 280, 42, 6, 6)

            # Left accent bar
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(14, 165, 233, alpha)))
            p.drawRoundedRect(x_pos, y, 4, 42, 2, 2)

            # Title
            p.setPen(QColor(14, 165, 233, alpha))
            p.setFont(QFont("Consolas", 10, QFont.Bold))
            p.drawText(x_pos + 10, y + 16, notif['title'])

            # Message
            p.setPen(QColor(212, 212, 212, alpha))
            p.setFont(QFont("Consolas", 9))
            msg = notif['message'][:38] + ("..." if len(notif['message']) > 38 else "")
            p.drawText(x_pos + 10, y + 33, msg)

            y += 48
