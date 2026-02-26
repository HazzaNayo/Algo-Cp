"""
hud.py - Heads-Up Display: uang, pahala, nyawa, timer, combo
"""

import arcade
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_FONT_SIZE, HUD_PADDING, HUD_HEIGHT,
    MAX_LIVES, GAME_DURATION, UPGRADES
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

        # ── Cooking Instructions (bottom-left guide)
        self._draw_cooking_guide()

    def _draw_cooking_guide(self):
        """Panduan langkah masak di pojok kiri bawah."""
        steps = [
            "1. Klik 🥣 Mangkok",
            "2. Klik 🍢 Bakso → tunggu masak",
            "3. Klik 🥣 Kuah → tunggu tuang",
            "4. Klik  SAJIKAN  → layani pembeli",
        ]
        base_y = 92
        arcade.draw_lbwh_rectangle_filled(8, base_y - 10, 280, len(steps) * 20 + 16,
                                          (0, 0, 0, 120))
        for i, step in enumerate(steps):
            arcade.draw_text(
                step,
                16, base_y + (len(steps) - 1 - i) * 20,
                (200, 200, 200, 200), font_size=11,
                anchor_x="left", anchor_y="center"
            )


class UpgradePanel:
    """Panel upgrade sederhana yang muncul saat tombol diklik."""

    BTN_W = 200
    BTN_H = 54
    PAD   = 12

    def __init__(self, on_upgrade=None):
        self.visible    = False
        self.on_upgrade = on_upgrade
        self._hover     = {}
        self._pressed   = {}

        keys = list(UPGRADES.keys())
        self._keys = keys
        total_h = len(keys) * (self.BTN_H + self.PAD) + self.PAD + 40
        self.panel_x = 50
        self.panel_y = 100
        self.panel_w = self.BTN_W + self.PAD * 2
        self.panel_h = total_h

    def toggle(self):
        self.visible = not self.visible

    def _btn_rect(self, idx):
        x = self.panel_x + self.PAD
        y = self.panel_y + self.panel_h - 50 - idx * (self.BTN_H + self.PAD)
        return x, y, self.BTN_W, self.BTN_H

    def _in_btn(self, idx, mx, my):
        x, y, w, h = self._btn_rect(idx)
        return x <= mx <= x + w and y <= my <= y + h

    def on_mouse_motion(self, mx, my):
        for i in range(len(self._keys)):
            self._hover[i] = self._in_btn(i, mx, my)

    def on_mouse_press(self, mx, my, button, mods=0):
        if not self.visible:
            return False
        # Close button (X)
        cx = self.panel_x + self.panel_w - 20
        cy = self.panel_y + self.panel_h - 20
        if abs(mx - cx) < 14 and abs(my - cy) < 14:
            self.visible = False
            return True
        for i in range(len(self._keys)):
            if self._in_btn(i, mx, my):
                self._pressed[i] = True
                return True
        return self.visible   # Block clicks when open

    def on_mouse_release(self, mx, my, button, mods=0):
        if not self.visible:
            return False
        for i, key in enumerate(self._keys):
            if self._pressed.get(i) and self._in_btn(i, mx, my):
                self._pressed[i] = False
                if self.on_upgrade:
                    self.on_upgrade(key)
                return True
            self._pressed[i] = False
        return False

    def draw(self, money: int, purchased: set):
        if not self.visible:
            return

        # Panel background
        arcade.draw_lbwh_rectangle_filled(
            self.panel_x, self.panel_y,
            self.panel_w, self.panel_h,
            (30, 20, 8, 230)
        )
        arcade.draw_lbwh_rectangle_outline(
            self.panel_x, self.panel_y,
            self.panel_w, self.panel_h,
            (200, 160, 60, 220), 2
        )

        # Title
        arcade.draw_text(
            "⚡ Upgrade",
            self.panel_x + self.panel_w / 2,
            self.panel_y + self.panel_h - 22,
            (255, 220, 80, 255), font_size=15,
            anchor_x="center", anchor_y="center", bold=True
        )

        # Close X
        arcade.draw_text(
            "✕",
            self.panel_x + self.panel_w - 20,
            self.panel_y + self.panel_h - 20,
            (200, 100, 100, 255), font_size=14,
            anchor_x="center", anchor_y="center", bold=True
        )

        for i, key in enumerate(self._keys):
            info = UPGRADES[key]
            x, y, w, h = self._btn_rect(i)
            is_bought = key in purchased
            affordable = money >= info["price"]

            if is_bought:
                fill = (40, 120, 50, 200)
            elif not affordable:
                fill = (60, 60, 60, 180)
            elif self._pressed.get(i):
                fill = (140, 90, 10, 230)
            elif self._hover.get(i):
                fill = (180, 120, 20, 230)
            else:
                fill = (100, 70, 15, 220)

            arcade.draw_lbwh_rectangle_filled(x, y, w, h, fill)
            arcade.draw_lbwh_rectangle_outline(x, y, w, h, (200, 160, 60, 160), 1)

            label = f"{'✓ ' if is_bought else ''}{info['name']}"
            arcade.draw_text(label, x + 8, y + h - 16,
                             (255, 230, 150, 255), font_size=12,
                             anchor_x="left", anchor_y="center", bold=True)
            arcade.draw_text(info["desc"], x + 8, y + 10,
                             (200, 200, 200, 200), font_size=10,
                             anchor_x="left", anchor_y="center")
            price_color = (100, 200, 100, 255) if affordable and not is_bought else (150, 150, 150, 200)
            arcade.draw_text(
                "SUDAH DIBELI" if is_bought else f"Rp{info['price']:,}",
                x + w - 8, y + h / 2,
                price_color, font_size=10,
                anchor_x="right", anchor_y="center", bold=True
            )
