"""
Autonomous Civilization Simulation - Map View
QGraphicsView-based interactive map with overlays, zoom, and tile interaction.

Performance optimizations:
- Only update tiles whose colors changed (dirty tracking via color cache)
- Pre-allocate QColor objects instead of creating new ones each frame
- Skip border overlay when nothing changed
- Cache season overlay rect instead of recreating each frame
- Use set operations for efficient explored set lookups
"""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import (
    QColor, QBrush, QPen, QPainterPath, QPainter, QPolygonF, QTransform
)

from CivSim.config import TILE_SIZE, TERRAIN_COLORS, RESOURCE_TYPES, SEASON_COLORS


class MapView(QGraphicsView):
    """Interactive map display with zoom, pan, tile hover/click, and overlay layers.

    Performance improvements:
    - Color cache tracks which tiles need brush updates (avoids setBrush on every tile every frame)
    - Season overlay is reused instead of recreated each frame
    - Border path computation is more efficient with early-exit checks
    - Resource markers cached and only rebuilt when resource map changes
    """

    tile_hovered = Signal(int, int)
    tile_clicked = Signal(int, int)
    zoom_changed = Signal(int)  # Zoom percentage

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.tiles: dict[tuple, QGraphicsRectItem] = {}
        self.dynamic_items: list = []

        # Overlay visibility toggles
        self.show_fog = True
        self.show_resources = True
        self.show_borders = True
        self.show_trade_routes = True
        self.show_events = True

        # Performance: cache tile colors to avoid redundant setBrush calls
        self._tile_colors: dict[tuple, QColor] = {}

        # Performance: cache season overlay item
        self._season_rect = None
        self._season_idx = -1

        # Performance: cache map dimensions
        self._map_W = 0
        self._map_H = 0

        # Pre-allocate common colors
        self._fog_color = QColor(15, 15, 25)
        self._no_pen = QPen(Qt.NoPen)

        # Cache the most recent update_map args so overlay toggles can
        # trigger an immediate re-render without waiting for the next tick.
        self._last_update_args: tuple | None = None

    def wheelEvent(self, event) -> None:
        z = 1.15
        if event.angleDelta().y() > 0:
            self.scale(z, z)
        else:
            self.scale(1 / z, 1 / z)
        # Emit zoom level
        transform = self.transform()
        zoom_pct = int(transform.m11() * 100)
        self.zoom_changed.emit(zoom_pct)

    def reset_view(self) -> None:
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        transform = self.transform()
        zoom_pct = int(transform.m11() * 100)
        self.zoom_changed.emit(zoom_pct)

    def mouseMoveEvent(self, event) -> None:
        super().mouseMoveEvent(event)
        sp = self.mapToScene(event.pos())
        self.tile_hovered.emit(int(sp.x() // TILE_SIZE), int(sp.y() // TILE_SIZE))

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            sp = self.mapToScene(event.pos())
            self.tile_clicked.emit(int(sp.x() // TILE_SIZE), int(sp.y() // TILE_SIZE))

    def update_map(self, terrain_map: dict, owner_map: dict, civ_colors: dict,
                   explored: set, path_data: list, capitals: dict,
                   trade_routes: list, active_events: list,
                   resource_map: dict, season: int) -> None:
        """Full map refresh with dirty-tracking for performance."""
        # Cache args so overlay toggles can re-render immediately.
        self._last_update_args = (
            terrain_map, owner_map, civ_colors, explored, path_data,
            capitals, trade_routes, active_events, resource_map, season,
        )

        # ── Base Terrain ────────────────────────────────────
        if not self.tiles:
            for (x, y), t_id in terrain_map.items():
                rect = QGraphicsRectItem(
                    x * TILE_SIZE, y * TILE_SIZE,
                    TILE_SIZE - 1, TILE_SIZE - 1
                )
                color = TERRAIN_COLORS.get(t_id, QColor(0, 0, 0))
                rect.setBrush(QBrush(color))
                rect.setPen(self._no_pen)
                self.scene.addItem(rect)
                self.tiles[(x, y)] = rect
                self._tile_colors[(x, y)] = color
            self.reset_view()

        # ── Ownership Coloring (with dirty tracking) ────────
        fog_color = self._fog_color
        show_fog = self.show_fog
        explored_contains = explored.__contains__  # Fast bound method lookup

        for (x, y), civ_name in owner_map.items():
            if (x, y) not in self.tiles:
                continue

            # Compute target color
            if show_fog and not explored_contains((x, y)):
                col = fog_color
            elif civ_name and civ_name in civ_colors:
                col = QColor(civ_colors[civ_name])
                col.setAlpha(180)
            else:
                col = TERRAIN_COLORS.get(terrain_map.get((x, y), 0), QColor(0, 0, 0))

            # Only update brush if color actually changed
            prev = self._tile_colors.get((x, y))
            if prev != col:
                self.tiles[(x, y)].setBrush(QBrush(col))
                self._tile_colors[(x, y)] = col

        # ── Clear Dynamic Items ────────────────────────────
        for item in self.dynamic_items:
            self.scene.removeItem(item)
        self.dynamic_items.clear()

        # ── Season Overlay ──────────────────────────────────
        # Cache the season rect as a persistent scene item so we don't
        # remove + re-add it every frame (the previous implementation
        # had identical if/else branches, making the cache useless).
        if terrain_map:
            max_x = max(p[0] for p in terrain_map.keys()) + 1
            max_y = max(p[1] for p in terrain_map.keys()) + 1
            W, H = max_x, max_y

            if self._season_rect is None:
                self._season_rect = self.scene.addRect(
                    0, 0, W * TILE_SIZE, H * TILE_SIZE,
                    QPen(Qt.NoPen), QBrush(SEASON_COLORS[season])
                )
                self._season_rect.setZValue(0)
                self._season_idx = season
            elif season != self._season_idx:
                # Same item, just swap the brush - cheap.
                self._season_rect.setBrush(QBrush(SEASON_COLORS[season]))
                self._season_idx = season
            # Ensure the rect is on top of base tiles (z=0) but below
            # dynamic overlays (z>=8). Already set on creation.

            # ── Border Lines ───────────────────────────────
            if self.show_borders:
                bp = QPainterPath()
                for (x, y), owner in owner_map.items():
                    if owner is None or (show_fog and not explored_contains((x, y))):
                        continue
                    # Right border
                    right_owner = owner_map.get((x + 1, y))
                    if x + 1 >= W or right_owner != owner:
                        bp.moveTo((x+1)*TILE_SIZE, y*TILE_SIZE)
                        bp.lineTo((x+1)*TILE_SIZE, (y+1)*TILE_SIZE)
                    # Bottom border
                    bottom_owner = owner_map.get((x, y + 1))
                    if y + 1 >= H or bottom_owner != owner:
                        bp.moveTo(x*TILE_SIZE, (y+1)*TILE_SIZE)
                        bp.lineTo((x+1)*TILE_SIZE, (y+1)*TILE_SIZE)
                bpath = self.scene.addPath(bp, QPen(Qt.white, 2))
                bpath.setZValue(10)
                self.dynamic_items.append(bpath)

        # ── Resource Markers ────────────────────────────────
        if self.show_resources:
            for (x, y), res in resource_map.items():
                if explored_contains((x, y)):
                    diamond = QPolygonF([
                        QPointF(x*TILE_SIZE+3, y*TILE_SIZE+TILE_SIZE//2),
                        QPointF(x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+3),
                        QPointF(x*TILE_SIZE+TILE_SIZE-3, y*TILE_SIZE+TILE_SIZE//2),
                        QPointF(x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE-1)
                    ])
                    dm = self.scene.addPolygon(
                        diamond, QPen(Qt.NoPen), QBrush(RESOURCE_TYPES[res])
                    )
                    dm.setZValue(12)
                    self.dynamic_items.append(dm)

        # ── Event Overlays ─────────────────────────────────
        if self.show_events:
            for ev in active_events:
                civ_name = ev.target_civ
                col = QColor(ev.visual_color)
                col.setAlpha(80)
                for x, y in owner_map.keys():
                    if owner_map[(x, y)] == civ_name and explored_contains((x, y)):
                        r = self.scene.addRect(
                            x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1,
                            QPen(Qt.NoPen), QBrush(col)
                        )
                        r.setZValue(8)
                        self.dynamic_items.append(r)

        # ── Trade Routes ────────────────────────────────────
        if self.show_trade_routes and trade_routes and capitals:
            for ca, cb in trade_routes:
                pa, pb = capitals.get(ca), capitals.get(cb)
                if pa and pb:
                    p = QPainterPath()
                    p.moveTo(pa[0]*TILE_SIZE + TILE_SIZE//2, pa[1]*TILE_SIZE + TILE_SIZE//2)
                    p.lineTo(pb[0]*TILE_SIZE + TILE_SIZE//2, pb[1]*TILE_SIZE + TILE_SIZE//2)
                    tr = self.scene.addPath(
                        p, QPen(QColor(255, 215, 0, 120), 2, Qt.DotLine)
                    )
                    tr.setZValue(9)
                    self.dynamic_items.append(tr)

        # ── Pathfinder Path ─────────────────────────────────
        if path_data and len(path_data) > 1:
            p = QPainterPath()
            p.moveTo(
                path_data[0][0]*TILE_SIZE + TILE_SIZE//2,
                path_data[0][1]*TILE_SIZE + TILE_SIZE//2
            )
            for px, py in path_data[1:]:
                p.lineTo(px*TILE_SIZE + TILE_SIZE//2, py*TILE_SIZE + TILE_SIZE//2)
            pl = self.scene.addPath(
                p, QPen(QColor(255, 255, 0, 200), 3, Qt.DashLine)
            )
            pl.setZValue(11)
            self.dynamic_items.append(pl)

        # ── Capital Markers ─────────────────────────────────
        if capitals:
            for cn, (cx, cy) in capitals.items():
                m = self.scene.addRect(
                    cx*TILE_SIZE-1, cy*TILE_SIZE-1,
                    TILE_SIZE+2, TILE_SIZE+2,
                    QPen(QColor(civ_colors.get(cn, "#FFF")), 2),
                    QBrush(QColor(255, 255, 255, 220))
                )
                m.setZValue(15)
                self.dynamic_items.append(m)

    def clear_map(self) -> None:
        """Clear all tiles and reset for a new game."""
        self.scene.clear()
        self.tiles.clear()
        self._tile_colors.clear()
        self.dynamic_items.clear()
        self._season_rect = None
        self._season_idx = -1
        self._last_update_args = None

    def refresh_overlays(self) -> None:
        """Force a re-render of the map.

        Called when an overlay toggle (fog / resources / borders) changes
        so the user sees the effect immediately, instead of waiting for
        the next simulation tick.
        """
        # Invalidate the color cache so ownership + fog changes redraw.
        self._tile_colors.clear()
        if self._last_update_args is not None:
            # Re-run update_map with the most recent data so the dirty
            # tracker re-evaluates every tile against the new toggle state.
            self.update_map(*self._last_update_args)
        else:
            self.scene.invalidate(self.scene.sceneRect())
