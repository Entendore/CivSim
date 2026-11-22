"""
Autonomous Civilization Simulation - Main Window
Primary application window with tabbed sidebar, organized toolbar,
status bar, keyboard shortcuts, and professional layout.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QPushButton, QSlider, QLabel,
    QScrollArea, QComboBox, QCheckBox, QTextEdit,
    QTabWidget, QStatusBar, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QColor

from CivSim.config import (
    DARK_STYLESHEET, TerrainPreset, TERRAIN_PRESETS,
    MIN_CIV_COUNT, MAX_CIV_COUNT,
)
from CivSim.map_view import MapView
from CivSim.widgets import (
    TimelineGraph, CivCard, GenerationReportPanel, LeaderboardWidget,
    MinimapWidget, DiplomacyMatrix, NotificationOverlay,
)


# ── Section Frame Helper ───────────────────────────────────────
class SectionFrame(QFrame):
    """A collapsible-looking frame with a styled header label and content area."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "SectionFrame { border: 1px solid #3e3e3e; border-radius: 4px; "
            "background-color: #252526; }"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        header = QLabel(title)
        header.setStyleSheet(
            "color: #0ea5e9; font-size: 11px; font-weight: bold; "
            "padding: 2px 6px; background-color: #1a3a4a; border-radius: 3px;"
        )
        lay.addWidget(header)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(4)
        lay.addLayout(self.content_layout)

    def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.content_layout.addLayout(layout)


# ── Main Window ────────────────────────────────────────────────
class MainWindow(QMainWindow):
    """Main application window with tabbed sidebar, organized toolbar, and status bar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autonomous Civilization Simulation - Ultimate Edition")
        self.resize(1500, 900)
        self.setStyleSheet(DARK_STYLESHEET)

        # ── Toolbar ─────────────────────────────────────────
        self._build_toolbar()

        # ── Main Layout ────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left: Map with tile info bar
        map_container = QWidget()
        map_lay = QVBoxLayout(map_container)
        map_lay.setContentsMargins(0, 0, 0, 0)
        map_lay.setSpacing(0)

        self.map_view = MapView()
        map_lay.addWidget(self.map_view, stretch=1)

        # Tile info strip below map
        self.tile_info_lbl = QLabel("Hover over map tile for info...")
        self.tile_info_lbl.setStyleSheet(
            "padding: 4px 8px; background-color: #252526; color: #aaa; "
            "border-top: 1px solid #3e3e3e; font-size: 11px;"
        )
        map_lay.addWidget(self.tile_info_lbl)
        splitter.addWidget(map_container)

        # Right panel: Tabbed interface
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet(self._tab_stylesheet())
        splitter.addWidget(self.tabs)

        # ── Tab 1: Overview ────────────────────────────────
        overview_w = QWidget()
        overview_lay = QVBoxLayout(overview_w)
        overview_lay.setContentsMargins(4, 4, 4, 4)
        overview_lay.setSpacing(6)

        # Mini row: Minimap + Leaderboard side by side
        mini_row = QHBoxLayout()
        mini_row.setSpacing(6)

        minimap_section = SectionFrame("MINIMAP")
        self.minimap = MinimapWidget()
        minimap_section.add_widget(self.minimap)
        mini_row.addWidget(minimap_section)

        leaderboard_section = SectionFrame("LEADERBOARD")
        self.leaderboard = LeaderboardWidget()
        leaderboard_section.add_widget(self.leaderboard)
        mini_row.addWidget(leaderboard_section, stretch=1)

        overview_lay.addLayout(mini_row)

        # Timeline
        timeline_section = SectionFrame("TIMELINE")
        self.timeline = TimelineGraph()
        timeline_section.add_widget(self.timeline)
        overview_lay.addWidget(timeline_section)

        # Diplomacy matrix
        diplo_section = SectionFrame("DIPLOMACY")
        self.diplomacy_matrix = DiplomacyMatrix()
        diplo_section.add_widget(self.diplomacy_matrix)
        overview_lay.addWidget(diplo_section)

        # Active events
        self.event_lbl = QLabel("No active events")
        self.event_lbl.setStyleSheet(
            "padding: 6px; color: #D7AF1E; border: 1px solid #3e3e3e; "
            "border-radius: 4px; background-color: #2a2a1a; font-size: 11px;"
        )
        overview_lay.addWidget(self.event_lbl)
        overview_lay.addStretch()
        self.tabs.addTab(overview_w, "Overview")

        # ── Tab 2: Civilizations ───────────────────────────
        civs_w = QWidget()
        civs_lay = QVBoxLayout(civs_w)
        civs_lay.setContentsMargins(4, 4, 4, 4)
        civs_lay.setSpacing(4)

        self.civ_scroll = QScrollArea()
        self.civ_scroll.setWidgetResizable(True)
        self.civ_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.civ_container = QWidget()
        self.civ_layout = QVBoxLayout(self.civ_container)
        self.civ_layout.setAlignment(Qt.AlignTop)
        self.civ_layout.setSpacing(6)
        self.civ_scroll.setWidget(self.civ_container)
        civs_lay.addWidget(self.civ_scroll)
        self.tabs.addTab(civs_w, "Civilizations")

        # ── Tab 3: Log ─────────────────────────────────────
        log_w = QWidget()
        log_lay = QVBoxLayout(log_w)
        log_lay.setContentsMargins(4, 4, 4, 4)
        log_lay.setSpacing(4)

        # Log filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(6)
        filter_lbl = QLabel("Filter:")
        filter_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
        filter_row.addWidget(filter_lbl)
        self.log_filter = QComboBox()
        self.log_filter.addItem("All")
        self.log_filter.setFixedWidth(120)
        filter_row.addWidget(self.log_filter)
        filter_row.addStretch()
        log_lay.addLayout(filter_row)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet(
            "QTextEdit { border: 1px solid #3e3e3e; background-color: #111118;"
            "font-family: Consolas, monospace; font-size: 11px; border-radius: 4px; }"
        )
        log_lay.addWidget(self.log_view)
        self.tabs.addTab(log_w, "Log")

        # ── Tab 4: Reports ─────────────────────────────────
        reports_w = QWidget()
        reports_lay = QVBoxLayout(reports_w)
        reports_lay.setContentsMargins(4, 4, 4, 4)
        reports_lay.setSpacing(4)

        gen_header = QLabel("GENERATION REPORTS (Before -> After)")
        gen_header.setStyleSheet(
            "padding: 6px; background-color: #0e639e; color: white;"
            "font-weight: bold; border-radius: 4px; font-size: 12px;"
        )
        reports_lay.addWidget(gen_header)
        self.gen_report_panel = GenerationReportPanel()
        reports_lay.addWidget(self.gen_report_panel)
        self.tabs.addTab(reports_w, "Reports")

        # ── Splitter sizing ────────────────────────────────
        splitter.setSizes([950, 550])

        self.civ_cards: dict[str, CivCard] = {}

        # ── Notification Overlay ────────────────────────────
        self.notification_overlay = NotificationOverlay(self)

        # ── Status Bar ─────────────────────────────────────
        self._build_status_bar()

        # ── Overlay Toggles ─────────────────────────────────
        # Each toggle updates the flag AND triggers an immediate redraw
        # via MapView.refresh_overlays(), so the user sees the change
        # without waiting for the next simulation tick.
        self.chk_fog.toggled.connect(self._on_fog_toggled)
        self.chk_resources.toggled.connect(self._on_resources_toggled)
        self.chk_borders.toggled.connect(self._on_borders_toggled)

        # ── Keyboard Shortcuts ──────────────────────────────
        self._setup_shortcuts()

    # ── Toolbar Builder ─────────────────────────────────────
    def _build_toolbar(self) -> None:
        """Build organized toolbar with grouped controls."""
        self.toolbar = QToolBar("Controls")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setStyleSheet(
            "QToolBar { background-color: #2d2d2d; border-bottom: 2px solid #1a1a1a; "
            "spacing: 4px; padding: 3px 6px; }"
        )
        self.addToolBar(self.toolbar)

        # ─ Group 1: Simulation Controls ──
        self.btn_play = QPushButton("  Play  ")
        self.btn_play.setToolTip("Start/Pause simulation (Space)")
        self.btn_play.setStyleSheet(self._tool_button_style("#0e639e"))
        self.toolbar.addWidget(self.btn_play)

        self.btn_reset = QPushButton("Reset View")
        self.btn_reset.setToolTip("Reset map view (R)")
        self.btn_reset.setStyleSheet(self._tool_button_style("#555"))
        self.toolbar.addWidget(self.btn_reset)

        self.toolbar.addSeparator()

        # ─ Group 2: Speed ──
        speed_lbl = QLabel("Speed:")
        speed_lbl.setStyleSheet("color: #aaa; font-size: 11px; margin-left: 4px;")
        self.toolbar.addWidget(speed_lbl)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 500)
        self.speed_slider.setValue(150)
        self.speed_slider.setFixedWidth(100)
        self.speed_slider.setToolTip("Simulation speed (+/-)")
        self.toolbar.addWidget(self.speed_slider)

        self.toolbar.addSeparator()

        # ─ Group 3: Game Settings ──
        settings_lbl = QLabel("  Duration:")
        settings_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
        self.toolbar.addWidget(settings_lbl)
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["200 years", "500 years", "1000 years", "Endless"])
        self.duration_combo.setFixedWidth(100)
        self.toolbar.addWidget(self.duration_combo)

        civs_lbl = QLabel("Civs:")
        civs_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
        self.toolbar.addWidget(civs_lbl)
        self.civ_count_combo = QComboBox()
        for i in range(MIN_CIV_COUNT, MAX_CIV_COUNT + 1):
            self.civ_count_combo.addItem(f"{i}")
        self.civ_count_combo.setCurrentIndex(2)
        self.civ_count_combo.setFixedWidth(45)
        self.toolbar.addWidget(self.civ_count_combo)

        terrain_lbl = QLabel("Map:")
        terrain_lbl.setStyleSheet("color: #aaa; font-size: 11px;")
        self.toolbar.addWidget(terrain_lbl)
        self.terrain_combo = QComboBox()
        self.terrain_combo.addItems(list(TERRAIN_PRESETS.keys()))
        self.terrain_combo.setFixedWidth(110)
        self.toolbar.addWidget(self.terrain_combo)

        self.toolbar.addSeparator()

        # ─ Group 4: View Toggles ──
        toggle_style = "QCheckBox { color: #ccc; font-size: 11px; spacing: 3px; }"

        self.chk_fog = QCheckBox("Fog")
        self.chk_fog.setChecked(True)
        self.chk_fog.setToolTip("Toggle fog of war (F)")
        self.chk_fog.setStyleSheet(toggle_style)
        self.toolbar.addWidget(self.chk_fog)

        self.chk_resources = QCheckBox("Res")
        self.chk_resources.setChecked(True)
        self.chk_resources.setToolTip("Toggle resource markers (G)")
        self.chk_resources.setStyleSheet(toggle_style)
        self.toolbar.addWidget(self.chk_resources)

        self.chk_borders = QCheckBox("Brd")
        self.chk_borders.setChecked(True)
        self.chk_borders.setToolTip("Toggle border lines (B)")
        self.chk_borders.setStyleSheet(toggle_style)
        self.toolbar.addWidget(self.chk_borders)

        self.chk_gen_reports = QCheckBox("Rpts")
        self.chk_gen_reports.setChecked(True)
        self.chk_gen_reports.setToolTip("Show generation reports")
        self.chk_gen_reports.setStyleSheet(toggle_style)
        self.toolbar.addWidget(self.chk_gen_reports)

        self.toolbar.addSeparator()

        # ─ Group 5: File Operations ──
        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save game (Ctrl+S)")
        self.btn_save.setStyleSheet(self._tool_button_style("#2d6a2d"))
        self.toolbar.addWidget(self.btn_save)

        self.btn_load = QPushButton("Load")
        self.btn_load.setToolTip("Load game (Ctrl+O)")
        self.btn_load.setStyleSheet(self._tool_button_style("#2d6a2d"))
        self.toolbar.addWidget(self.btn_load)

        self.btn_new = QPushButton("New Game")
        self.btn_new.setToolTip("Restart with current settings")
        self.btn_new.setStyleSheet(self._tool_button_style("#8b5e00"))
        self.toolbar.addWidget(self.btn_new)

        # Spacer to push year to right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        # Year display at far right
        self.lbl_year = QLabel("Year: -3000 | Spring | Gen: 0")
        self.lbl_year.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #0ea5e9; "
            "padding: 4px 10px; background-color: #1a2a3a; border-radius: 4px;"
        )
        self.toolbar.addWidget(self.lbl_year)

    def _build_status_bar(self) -> None:
        """Build status bar at the bottom of the window."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(
            "QStatusBar { background-color: #252526; border-top: 1px solid #3e3e3e; "
            "color: #888; font-size: 11px; padding: 2px; }"
            "QStatusBar::item { border: none; }"
        )
        # Zoom indicator
        self.zoom_lbl = QLabel("Zoom: 100%")
        self.zoom_lbl.setStyleSheet("color: #aaa; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.zoom_lbl)

        # Active civ count
        self.civ_count_lbl = QLabel("Civs: 0")
        self.civ_count_lbl.setStyleSheet("color: #aaa; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.civ_count_lbl)

    @staticmethod
    def _tool_button_style(bg_color: str) -> str:
        """Generate consistent toolbar button style."""
        # Compute lighter/darker variants from the base color
        base = QColor(bg_color)
        hover = base.lighter(120).name()
        pressed = base.darker(130).name()
        return (
            f"QPushButton {{ background-color: {bg_color}; color: white; "
            f"border: none; padding: 4px 10px; border-radius: 3px; "
            f"font-size: 11px; font-weight: bold; }}"
            f"QPushButton:hover {{ background-color: {hover}; }}"
            f"QPushButton:pressed {{ background-color: {pressed}; }}"
        )

    @staticmethod
    def _tab_stylesheet() -> str:
        """Custom stylesheet for tab widget."""
        return (
            "QTabWidget::pane { border: 1px solid #3e3e3e; background-color: #1e1e1e; "
            "border-radius: 4px; }"
            "QTabBar::tab { background-color: #2d2d2d; color: #aaa; "
            "padding: 6px 16px; border: 1px solid #3e3e3e; "
            "border-bottom: none; border-top-left-radius: 4px; "
            "border-top-right-radius: 4px; margin-right: 2px; font-size: 11px; }"
            "QTabBar::tab:selected { background-color: #1e1e1e; color: #0ea5e9; "
            "font-weight: bold; border-bottom: 2px solid #0ea5e9; }"
            "QTabBar::tab:hover { background-color: #333; color: #ccc; }"
        )

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts for common actions."""
        play_action = QAction(self)
        play_action.setShortcut(QKeySequence("Space"))
        play_action.triggered.connect(self.btn_play.click)
        self.addAction(play_action)

        reset_action = QAction(self)
        reset_action.setShortcut(QKeySequence("R"))
        reset_action.triggered.connect(self.btn_reset.click)
        self.addAction(reset_action)

        speed_up = QAction(self)
        speed_up.setShortcut(QKeySequence("+"))
        speed_up.triggered.connect(lambda: self.speed_slider.setValue(
            min(500, self.speed_slider.value() + 20)
        ))
        self.addAction(speed_up)

        speed_down = QAction(self)
        speed_down.setShortcut(QKeySequence("-"))
        speed_down.triggered.connect(lambda: self.speed_slider.setValue(
            max(10, self.speed_slider.value() - 20)
        ))
        self.addAction(speed_down)

        fog_action = QAction(self)
        fog_action.setShortcut(QKeySequence("F"))
        fog_action.triggered.connect(lambda: self.chk_fog.toggle())
        self.addAction(fog_action)

        res_action = QAction(self)
        res_action.setShortcut(QKeySequence("G"))
        res_action.triggered.connect(lambda: self.chk_resources.toggle())
        self.addAction(res_action)

        border_action = QAction(self)
        border_action.setShortcut(QKeySequence("B"))
        border_action.triggered.connect(lambda: self.chk_borders.toggle())
        self.addAction(border_action)

        save_action = QAction(self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.btn_save.click)
        self.addAction(save_action)

        load_action = QAction(self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self.btn_load.click)
        self.addAction(load_action)

        # Tab switching shortcuts (1-4)
        for i in range(4):
            tab_action = QAction(self)
            tab_action.setShortcut(QKeySequence(f"Alt+{i+1}"))
            idx = i
            tab_action.triggered.connect(lambda checked, x=idx: self.tabs.setCurrentIndex(x))
            self.addAction(tab_action)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, 'notification_overlay'):
            self.notification_overlay.setGeometry(self.rect())

    # ── Overlay Toggle Handlers ───────────────────────────────
    def _on_fog_toggled(self, v: bool) -> None:
        self.map_view.show_fog = v
        self.map_view.refresh_overlays()

    def _on_resources_toggled(self, v: bool) -> None:
        self.map_view.show_resources = v
        self.map_view.refresh_overlays()

    def _on_borders_toggled(self, v: bool) -> None:
        self.map_view.show_borders = v
        self.map_view.refresh_overlays()

    def update_stats(self, civs_data: list[dict]) -> None:
        for c in civs_data:
            if c['name'] not in self.civ_cards:
                card = CivCard(c)
                self.civ_layout.addWidget(card)
                self.civ_cards[c['name']] = card
                self.log_filter.addItem(c['name'])
            else:
                self.civ_cards[c['name']].update_data(c)
        self.timeline.update_data(civs_data)
        self.leaderboard.update_rankings(civs_data)
        self.diplomacy_matrix.update_data(civs_data)
        self.civ_count_lbl.setText(f"Civs: {len(civs_data)}")

    def append_log(self, text: str) -> None:
        parts = text.split(": ", 2)
        if len(parts) == 3:
            year, civ_name, action = parts
            if (self.log_filter.currentText() != "All"
                    and self.log_filter.currentText() != civ_name):
                return
            html = (
                f"<span style='color:gray'>{year}:</span> "
                f"<b style='color:#D7AF1E'>{civ_name}</b> {action}"
            )
            self.log_view.append(html)
        else:
            self.log_view.append(text)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )

    def add_generation_report(self, html_report: str, plain_text_report: str) -> None:
        if self.chk_gen_reports.isChecked():
            self.gen_report_panel.add_report(html_report, plain_text_report)

    def show_notification(self, title: str, message: str) -> None:
        self.notification_overlay.add_notification(title, message)

    def get_civ_count(self) -> int:
        return MIN_CIV_COUNT + self.civ_count_combo.currentIndex()

    def get_terrain_preset(self) -> str:
        return self.terrain_combo.currentText()
