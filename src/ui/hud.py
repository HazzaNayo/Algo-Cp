"""
hud.py - Heads-Up Display: uang, pahala, nyawa, timer, combo
"""

import arcade
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_FONT_SIZE, HUD_PADDING, HUD_HEIGHT,
    MAX_LIVES, GAME_DURATION
)


class HUD:
    """Gambar semua elemen HUD di bagian atas layar."""

    def __init__(self):
        self.money    = 0
        self.pahala   = 0
        self.lives    = MAX_LIVES
        self.time_left= GAME_DURATION
        self.combo    = 0
        self.tip_flash= 0.0   # Durasi tampil notif tip
        self.tip_text = ""
        self.notifs   : list[dict] = []   # Floating notifications

    def update(self, delta_time: float):
        self.tip_flash = max(0.0, self.tip_flash - delta_time)
        # Update floating notifs
        for n in self.notifs:
            n["y"]    += 40 * delta_time
            n["alpha"] = max(0, n["alpha"] - 180 * delta_time)
        self.notifs = [n for n in self.notifs if n["alpha"] > 0]

    def add_notif(self, text: str, color=(255, 255, 100, 255)):
        self.notifs.append({
            "text":  text,
            "x":     SCREEN_WIDTH / 2,
            "y":     SCREEN_HEIGHT / 2 + 60,
            "alpha": 255,
            "color": color,
            "size":  22
        })

    def draw(self):
        # ── Bar HUD background
        arcade.draw_lbwh_rectangle_filled(
            0, SCREEN_HEIGHT - HUD_HEIGHT,
            SCREEN_WIDTH, HUD_HEIGHT,
            (25, 15, 5, 210)
        )
        arcade.draw_lbwh_rectangle_outline(
            0, SCREEN_HEIGHT - HUD_HEIGHT,
            SCREEN_WIDTH, HUD_HEIGHT,
            (200, 160, 60, 180), 2
        )

        y = SCREEN_HEIGHT - HUD_HEIGHT / 2

        # ── 💰 Uang
        arcade.draw_text(
            f"💰  Rp{self.money:,}",
            HUD_PADDING, y,
            (255, 230, 80, 255), font_size=HUD_FONT_SIZE,
            anchor_x="left", anchor_y="center", bold=True
        )

        # ── 🙏 Pahala
        arcade.draw_text(
            f"🙏  {self.pahala}",
            230, y,
            (150, 255, 200, 255), font_size=HUD_FONT_SIZE,
            anchor_x="left", anchor_y="center", bold=True
        )

        # ── ❤️ Nyawa (tengah)
        heart_str = "❤️ " * self.lives + "🖤 " * (MAX_LIVES - self.lives)
        arcade.draw_text(
            heart_str.strip(),
            SCREEN_WIDTH / 2, y,
            (255, 80, 80, 255), font_size=HUD_FONT_SIZE,
            anchor_x="center", anchor_y="center"
        )

        # ── ⏱ Timer
        mins  = int(self.time_left) // 60
        secs  = int(self.time_left) % 60
        t_color = (255, 80, 80, 255) if self.time_left < 30 else (255, 255, 255, 255)
        arcade.draw_text(
            f"⏱  {mins:02d}:{secs:02d}",
            SCREEN_WIDTH - 280, y,
            t_color, font_size=HUD_FONT_SIZE,
            anchor_x="left", anchor_y="center", bold=True
        )

        # ── COMBO
        if self.combo >= 3:
            arcade.draw_text(
                f"🔥 COMBO x{self.combo}",
                SCREEN_WIDTH - HUD_PADDING, y,
                (255, 160, 20, 255), font_size=HUD_FONT_SIZE,
                anchor_x="right", anchor_y="center", bold=True
            )

        # ── Floating notifications
        for n in self.notifs:
            alpha = int(n["alpha"])
            color = n["color"][:3] + (alpha,)
            arcade.draw_text(
                n["text"], n["x"], n["y"],
                color, font_size=n["size"],
                anchor_x="center", anchor_y="center", bold=True
            )


