"""
Autonomous Civilization Simulation - App Controller
Entry point: wires engine signals to UI, handles save/load, new game, and app lifecycle.
"""
import sys
from PySide6.QtWidgets import QApplication, QFileDialog

from CivSim.config import SEASON_NAMES, Terrain
from CivSim.engine import SimulationEngine
from CivSim.main_window import MainWindow


class AppController:
    """Connects the SimulationEngine to the MainWindow and handles user interactions."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.engine: SimulationEngine | None = None
        self.playing = False

        self._create_engine()
        self._connect_window_signals()
        self._connect_engine_signals()

    def _create_engine(self) -> None:
        """Create a new simulation engine with current window settings."""
        civ_count = self.window.get_civ_count()
        terrain_preset = self.window.get_terrain_preset()
        self.engine = SimulationEngine(
            civ_count=civ_count,
            terrain_preset=terrain_preset,
        )

    def _connect_window_signals(self) -> None:
        """Wire up UI controls. Only call once - these never change."""
        w = self.window
        # Toolbar controls
        w.btn_play.clicked.connect(self.toggle_play)
        w.btn_reset.clicked.connect(w.map_view.reset_view)
        w.speed_slider.valueChanged.connect(self._on_speed_changed)
        w.duration_combo.currentTextChanged.connect(self._set_duration)
        w.map_view.tile_hovered.connect(self._on_tile_hover)
        w.map_view.zoom_changed.connect(self._on_zoom_changed)

        # Save / Load / New
        w.btn_save.clicked.connect(self._save_game)
        w.btn_load.clicked.connect(self._load_game)
        w.btn_new.clicked.connect(self._new_game)

    def _connect_engine_signals(self) -> None:
        """Wire up engine -> UI signals. Reconnect when a new engine is created."""
        w = self.window
        e = self.engine
        if e is None:
            return
        # Engine signals
        e.update_signal.connect(self._on_update)
        e.log_signal.connect(w.append_log)
        e.gen_report_signal.connect(w.add_generation_report)
        e.notification_signal.connect(w.show_notification)

    def _disconnect_engine_signals(self) -> None:
        """Disconnect the current engine's signals so a stale engine can't
        push updates into the UI after a New Game / Load Game.
        """
        e = self.engine
        if e is None:
            return
        try:
            e.update_signal.disconnect()
            e.log_signal.disconnect()
            e.gen_report_signal.disconnect()
            e.notification_signal.disconnect()
        except (TypeError, RuntimeError):
            # Signal had no connections - safe to ignore.
            pass

    def _on_speed_changed(self, v: int) -> None:
        if self.engine is not None:
            self.engine.speed = v

    def _set_duration(self, text: str) -> None:
        dur_map = {"200 years": 200, "500 years": 500, "1000 years": 1000, "Endless": 0}
        if self.engine:
            self.engine.max_years = dur_map.get(text, 0)

    def toggle_play(self) -> None:
        self.playing = not self.playing
        if self.playing:
            self.window.btn_play.setText("  Pause  ")
            if self.engine and not self.engine.isRunning():
                self.engine.start()
        else:
            self.window.btn_play.setText("  Play  ")
            if self.engine:
                self.engine.running = False

    def _save_game(self) -> None:
        if not self.engine:
            return
        path, _ = QFileDialog.getSaveFileName(
            self.window, "Save Game", "civ_save.json", "JSON Files (*.json)"
        )
        if path:
            was_running = self.engine.running
            self.engine.running = False
            self.engine.save_game(path)
            if was_running:
                self.engine.running = True

    def _load_game(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self.window, "Load Game", "", "JSON Files (*.json)"
        )
        if path and self.engine:
            was_running = self.engine.running
            self.engine.running = False
            self.engine.load_game(path)
            self.playing = False
            self.window.btn_play.setText("  Play  ")
            # Reset UI civ cards and map
            for card in self.window.civ_cards.values():
                self.window.civ_layout.removeWidget(card)
                card.deleteLater()
            self.window.civ_cards.clear()
            self.window.map_view.clear_map()

    def _new_game(self) -> None:
        """Restart the simulation with current settings."""
        if self.engine:
            self.engine.running = False
            self.engine.wait(2000)
            # Flush pending analytics before discarding engine
            try:
                self.engine.analytics.commit()
            except Exception:
                pass
            # Disconnect old engine signals so it can't push stale data
            # into the UI after we swap in a new engine.
            self._disconnect_engine_signals()

        self.playing = False
        self.window.btn_play.setText("  Play  ")

        # Clear UI
        for card in self.window.civ_cards.values():
            self.window.civ_layout.removeWidget(card)
            card.deleteLater()
        self.window.civ_cards.clear()
        self.window.gen_report_panel.clear_reports()
        self.window.log_view.clear()
        self.window.map_view.clear_map()

        # Create new engine and wire up its signals.
        self._create_engine()
        self._connect_engine_signals()

    def _on_tile_hover(self, tx: int, ty: int) -> None:
        if not self.engine:
            return
        t_id = self.engine.terrain_map.get((tx, ty))
        if t_id is not None:
            t_name = Terrain(t_id).name
            owner = self.engine.owner_map.get((tx, ty), "Unclaimed")
            res = self.engine.resource_map.get((tx, ty), "None")
            self.window.tile_info_lbl.setText(
                f"({tx},{ty})  |  Terrain: {t_name}  |  "
                f"Owner: {owner or 'None'}  |  Resource: {res}"
            )

    def _on_zoom_changed(self, zoom_pct: int) -> None:
        self.window.zoom_lbl.setText(f"Zoom: {zoom_pct}%")

    def _on_update(self, data: dict) -> None:
        civ_colors = {c.name: c.color for c in data['civs']}
        season_name = SEASON_NAMES[data['season']]
        gen = data.get('generation', 0)

        self.window.lbl_year.setText(
            f"Year: {data['year']}  |  {season_name}  |  Gen: {gen}"
        )

        # Update map
        self.window.map_view.update_map(
            data['terrain'], data['owners'], civ_colors, data['explored'],
            data['last_path'], data['capitals'], data['trade_routes'],
            data['active_events'], data['resource_map'], data['season']
        )

        # Update minimap
        self.window.minimap.update_data(
            data['terrain'], data['owners'], civ_colors, data['explored']
        )

        # Build civ UI data - pre-compute to reduce per-frame work
        civs_ui_data = []
        for c in data['civs']:
            civs_ui_data.append({
                'name': c.name, 'color': c.color,
                'population': c.population, 'pop_delta': 0,
                'military': c.military, 'mil_delta': 0,
                'technology': c.technology, 'tech_delta': 0,
                'treasury': c.treasury, 'treas_delta': 0,
                'culture': c.culture, 'stability': c.stability,
                'score': c.score, 'last_action': c.last_action,
                'buildings': c.buildings, 'wonders': c.wonders,
                'alliances': c.alliances, 'trade_partners': c.trade_partners,
                'at_war_with': c.at_war_with, 'religion': c.religion,
                'era_name': c.era_name,
                'archetype': c.archetype,
                'archetype_label': c.archetype_label,
                'archetype_desc': c.archetype_desc,
                'strategic_state': c.strategic_state_name,
                'plan_name': c.plan_name,
                'government': c.government,
                'government_label': c.government_label,
                'government_desc': c.government_desc,
                'leader_name': c.leader_name,
                'leader_short_name': c.leader_short_name,
            })
        self.window.update_stats(civs_ui_data)

        # Active events label
        if data['active_events']:
            ev_texts = [
                f"{e.name} -> {e.target_civ} ({e.remaining}t)"
                for e in data['active_events']
            ]
            self.window.event_lbl.setText(" | ".join(ev_texts))
        else:
            self.window.event_lbl.setText("No active events")

    def run(self) -> None:
        self.window.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = AppController()
    controller.run()
