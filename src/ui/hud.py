"""
hud.py - Heads-Up Display: uang, pahala, nyawa, timer, combo
"""

import arcade
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_FONT_SIZE, HUD_PADDING, HUD_HEIGHT,
    MAX_LIVES, GAME_DURATION
)


class HUD:
    """Heads-Up Display — menampilkan uang, pahala, nyawa, waktu, combo."""

    def __init__(self):
        self.money = 0
        self.pahala = 0
        self.lives = 3
        self.time_left = 180.0
        self.combo = 0
        
        # Stock tracking
        self.stock_bakso = 0
        self.stock_mie = 0
        self.stock_sayur = 0

        self.notifications = []

    def add_notif(self, text: str, color: tuple):
        """Tambah notifikasi yang akan ditampilkan."""
        self.notifications.append({
            "text": text,
            "color": color,
            "time": 3.0
        })

    def update(self, delta_time: float):
        """Update notifikasi (fade out)."""
        for notif in self.notifications[:]:
            notif["time"] -= delta_time
            if notif["time"] <= 0:
                self.notifications.remove(notif)

    def draw(self):
        """Draw HUD elements."""
        # Background
        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, (26, 18, 10, 220))
        arcade.draw_lbwh_rectangle_outline(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, (200, 150, 80, 255), 2)

        # Uang (dengan warna berbeda jika mines)
        money_color = (255, 100, 100, 255) if self.money < 0 else (255, 220, 80, 255)
        money_text = f"💰 Rp{abs(self.money):,}"
        if self.money < 0:
            money_text = f"💰 -Rp{abs(self.money):,}"
        
        arcade.draw_text(
            money_text, 20, SCREEN_HEIGHT - 35,
            money_color,
            font_size=16, bold=True
        )

        # Stock bahan (di samping uang)
        stock_text = f"Stok → 🍢 {self.stock_bakso}  |  🍜 {self.stock_mie}  |  🥬 {self.stock_sayur}"
        arcade.draw_text(
            stock_text,
            20, SCREEN_HEIGHT - 65,
            (150, 220, 150, 220),
            font_size=10, bold=True
        )

        # Pahala
        arcade.draw_text(
            f"🙏 Pahala: {self.pahala}", 420, SCREEN_HEIGHT - 35,
            (150, 255, 200, 255),
            font_size=16, bold=True
        )

        # Nyawa
        arcade.draw_text(
            f"❤️ Nyawa: {self.lives}", 720, SCREEN_HEIGHT - 35,
            (255, 100, 100, 255) if self.lives <= 1 else (255, 200, 200, 255),
            font_size=16, bold=True
        )

        # Waktu
        minutes = int(self.time_left) // 60
        seconds = int(self.time_left) % 60
        arcade.draw_text(
            f"⏱️ {minutes}:{seconds:02d}", 1000, SCREEN_HEIGHT - 35,
            (100, 200, 255, 255),
            font_size=16, bold=True
        )

        # Combo
        if self.combo > 1:
            arcade.draw_text(
                f"🔥 x{self.combo}", 1150, SCREEN_HEIGHT - 35,
                (255, 150, 50, 255),
                font_size=16, bold=True
            )

        # Notifikasi
        self._draw_notifications()

    def _draw_notifications(self):
        """Draw notifikasi yang sedang aktif."""
        y_offset = 0
        for notif in self.notifications:
            alpha = int(255 * (notif["time"] / 3.0))  # Fade out
            color = (*notif["color"][:3], alpha)
            arcade.draw_text(
                notif["text"],
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150 - y_offset,
                color,
                font_size=12, anchor_x="center", anchor_y="center", bold=True
            )
            y_offset += 25


