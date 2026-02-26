"""
cooking_station.py - Stasiun memasak (panci bakso, ketel kuah, mangkok)
"""

import arcade
from config import (
    COOK_TIME, KUAH_TIME,
    BAKSO_STATION_X, BAKSO_STATION_Y,
    KUAH_STATION_X, KUAH_STATION_Y,
    MANGKOK_POS_X, MANGKOK_POS_Y, MANGKOK_SCALE,
    ITEMS_PATH
)


class CookingStation:
    """Base class untuk semua stasiun masak."""

    def __init__(self, x: float, y: float, cook_time: float, label: str):
        self.x          = x
        self.y          = y
        self.cook_time  = cook_time
        self.label      = label

        self.timer      = 0.0       # Timer saat memasak
        self.is_cooking = False     # Sedang memasak?
        self.is_ready   = False     # Sudah matang / siap diambil?
        self.is_done    = False     # Sudah diambil player?

        # Hitbox klik (radius)
        self.click_radius = 55

        # Animasi hover
        self.hovered    = False

    # ─── Update ──────────────────────────────────────────────────────────────
    def update(self, delta_time: float) -> bool:
        """
        Update timer masak.
        Return True jika baru saja selesai memasak.
        """
        if self.is_cooking and not self.is_ready:
            self.timer += delta_time
            if self.timer >= self.cook_time:
                self.timer     = self.cook_time
                self.is_cooking = False
                self.is_ready   = True
                return True
        return False

    # ─── State Control ───────────────────────────────────────────────────────
    def start_cooking(self):
        """Mulai proses memasak."""
        if not self.is_cooking and not self.is_ready:
            self.is_cooking = True
            self.timer      = 0.0

    def take(self):
        """Player mengambil hasil masakan."""
        if self.is_ready:
            self.is_ready   = False
            self.is_done    = True
            return True
        return False

    def reset(self):
        """Reset stasiun ke kondisi awal."""
        self.timer      = 0.0
        self.is_cooking = False
        self.is_ready   = False
        self.is_done    = False

    # ─── Properties ──────────────────────────────────────────────────────────
    @property
    def progress(self) -> float:
        """Kemajuan masak 0.0 – 1.0."""
        if self.cook_time == 0:
            return 1.0
        return min(1.0, self.timer / self.cook_time)

    @property
    def can_click(self) -> bool:
        """Bisa diklik jika belum masak atau sudah siap diambil."""
        return not self.is_cooking and not self.is_done

    # ─── Hit-test ────────────────────────────────────────────────────────────
    def contains(self, mx: float, my: float) -> bool:
        dx = mx - self.x
        dy = my - self.y
        return (dx * dx + dy * dy) <= self.click_radius ** 2

    # ─── Drawing ─────────────────────────────────────────────────────────────
    def draw(self):
        # Lingkaran station
        base_color = (100, 70, 40, 220)
        if self.is_ready:
            base_color = (50, 200, 80, 220)
        elif self.is_cooking:
            base_color = (255, 160, 30, 220)
        elif self.hovered:
            base_color = (140, 100, 60, 220)

        arcade.draw_circle_filled(self.x, self.y, self.click_radius, base_color)
        arcade.draw_circle_outline(self.x, self.y, self.click_radius, (255, 255, 255, 120), 2)

        # Label
        arcade.draw_text(
            self.label,
            self.x, self.y,
            (255, 255, 255, 220), font_size=13,
            anchor_x="center", anchor_y="center", bold=True
        )

        # Progress bar di bawah station
        if self.is_cooking:
            bw = self.click_radius * 2
            bx = self.x - self.click_radius
            by = self.y - self.click_radius - 12
            arcade.draw_lbwh_rectangle_filled(bx, by, bw, 7, (60, 60, 60, 200))
            arcade.draw_lbwh_rectangle_filled(bx, by, bw * self.progress, 7, (255, 200, 0, 230))
            arcade.draw_lbwh_rectangle_outline(bx, by, bw, 7, (255, 255, 255, 120), 1)

        # Tanda centang jika ready
        if self.is_ready:
            arcade.draw_text(
                "✓",
                self.x, self.y + self.click_radius + 10,
                (50, 255, 100, 255), font_size=18,
                anchor_x="center", anchor_y="center", bold=True
            )

    def update_hover(self, mx: float, my: float):
        self.hovered = self.contains(mx, my)


# ─── Concrete Stations ────────────────────────────────────────────────────────
class BaksoStation(CookingStation):
    """Panci bakso — step 1 memasak."""

    def __init__(self, cook_time_override: float | None = None):
        t = cook_time_override if cook_time_override is not None else COOK_TIME
        super().__init__(BAKSO_STATION_X, BAKSO_STATION_Y, t, "🍢 Bakso")


class KuahStation(CookingStation):
    """Ketel kuah — step 2 memasak."""

    def __init__(self, kuah_time_override: float | None = None):
        t = kuah_time_override if kuah_time_override is not None else KUAH_TIME
        super().__init__(KUAH_STATION_X, KUAH_STATION_Y, t, "🥣 Kuah")


class MangkokStation(CookingStation):
    """Mangkok — step 0 menyiapkan mangkok (instan)."""

    def __init__(self):
        super().__init__(MANGKOK_POS_X, MANGKOK_POS_Y, 0.0, "🥣")
        self.click_radius = 40

    def start_cooking(self):
        # Mangkok instan — langsung ready
        self.is_ready = True

    def draw(self):
        base_color = (180, 130, 60, 200) if not self.is_ready else (50, 200, 80, 200)
        if self.hovered:
            base_color = (220, 170, 80, 220)
        arcade.draw_circle_filled(self.x, self.y, self.click_radius, base_color)
        arcade.draw_circle_outline(self.x, self.y, self.click_radius, (255, 255, 255, 120), 2)
        arcade.draw_text(
            self.label,
            self.x, self.y,
            (255, 255, 255, 230), font_size=14,
            anchor_x="center", anchor_y="center", bold=True
        )
        if self.is_ready:
            arcade.draw_text("✓", self.x, self.y + self.click_radius + 10,
                             (50, 255, 100, 255), font_size=18,
                             anchor_x="center", anchor_y="center", bold=True)
