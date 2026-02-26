"""
dialog_box.py - Popup dialog untuk pembeli fakir (pilih Gratis / Bayar)
"""

import arcade
from config import (
    DIALOG_WIDTH, DIALOG_HEIGHT, DIALOG_CENTER_X, DIALOG_CENTER_Y,
    SCREEN_WIDTH, SCREEN_HEIGHT, BAKSO_PRICE
)


class DialogBox:
    """
    Panel popup semi-transparan dengan dua pilihan:
    🎁 Gratis  |  💰 Bayar Normal

    Usage:
        dialog = DialogBox(on_free=..., on_pay=...)
        dialog.show()
        # dalam on_draw: dialog.draw()
        # dalam on_mouse_press / on_mouse_release: dialog.on_mouse_press / release
    """

    BTN_W = 150
    BTN_H = 48
    BTN_GAP = 24

    def __init__(self, on_free=None, on_pay=None):
        self.on_free = on_free
        self.on_pay  = on_pay
        self.visible = False

        cx = DIALOG_CENTER_X
        cy = DIALOG_CENTER_Y

        # Tombol Gratis (kiri)
        self._btn_free_cx = cx - self.BTN_W / 2 - self.BTN_GAP / 2
        self._btn_free_cy = cy - DIALOG_HEIGHT / 2 + self.BTN_H + 16

        # Tombol Bayar (kanan)
        self._btn_pay_cx  = cx + self.BTN_W / 2 + self.BTN_GAP / 2
        self._btn_pay_cy  = self._btn_free_cy

        # Press state
        self._pressed_free = False
        self._pressed_pay  = False
        self._hover_free   = False
        self._hover_pay    = False

    # ─── Visibility ──────────────────────────────────────────────────────────
    def show(self):
        self.visible = True
        self._pressed_free = False
        self._pressed_pay  = False

    def hide(self):
        self.visible = False

    # ─── Hit-test helpers ────────────────────────────────────────────────────
    def _in_free(self, x, y):
        cx, cy = self._btn_free_cx, self._btn_free_cy
        hw, hh = self.BTN_W / 2, self.BTN_H / 2
        return cx - hw <= x <= cx + hw and cy - hh <= y <= cy + hh

    def _in_pay(self, x, y):
        cx, cy = self._btn_pay_cx, self._btn_pay_cy
        hw, hh = self.BTN_W / 2, self.BTN_H / 2
        return cx - hw <= x <= cx + hw and cy - hh <= y <= cy + hh

    # ─── Events ──────────────────────────────────────────────────────────────
    def on_mouse_motion(self, x, y, dx=0, dy=0):
        if not self.visible:
            return
        self._hover_free = self._in_free(x, y)
        self._hover_pay  = self._in_pay(x, y)

    def on_mouse_press(self, x, y, button, modifiers=0) -> bool:
        if not self.visible:
            return False
        if self._in_free(x, y):
            self._pressed_free = True
            return True
        if self._in_pay(x, y):
            self._pressed_pay = True
            return True
        return True   # Blok klik di luar panel juga

    def on_mouse_release(self, x, y, button, modifiers=0) -> bool:
        if not self.visible:
            return False
        if self._pressed_free and self._in_free(x, y):
            self._pressed_free = False
            self.hide()
            if self.on_free:
                self.on_free()
            return True
        if self._pressed_pay and self._in_pay(x, y):
            self._pressed_pay = False
            self.hide()
            if self.on_pay:
                self.on_pay()
            return True
        self._pressed_free = False
        self._pressed_pay  = False
        return False

    # ─── Draw ────────────────────────────────────────────────────────────────
    def draw(self):
        if not self.visible:
            return

        cx = DIALOG_CENTER_X
        cy = DIALOG_CENTER_Y
        w  = DIALOG_WIDTH
        h  = DIALOG_HEIGHT

        # ── Overlay gelap
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 140)
        )

        # ── Panel utama
        lx = cx - w / 2
        by = cy - h / 2
        arcade.draw_lbwh_rectangle_filled(lx, by, w, h, (45, 30, 15, 235))
        arcade.draw_lbwh_rectangle_outline(lx, by, w, h, (220, 180, 80, 255), 3)

        # ── Judul
        arcade.draw_text(
            "Pembeli Fakir Datang!",
            cx, cy + h / 2 - 28,
            (255, 225, 100, 255), font_size=18,
            anchor_x="center", anchor_y="center", bold=True
        )

        # ── Sub-teks
        arcade.draw_text(
            f"Kasih gratis atau tetap bayar Rp{BAKSO_PRICE:,}?",
            cx, cy + 12,
            (240, 230, 200, 220), font_size=13,
            anchor_x="center", anchor_y="center"
        )

        # ── Tombol Gratis
        self._draw_btn(
            self._btn_free_cx, self._btn_free_cy,
            "🎁  Gratis",
            base=(30, 140, 60), hover=(40, 190, 80),
            pressed=self._pressed_free, hovered=self._hover_free
        )

        # ── Tombol Bayar
        self._draw_btn(
            self._btn_pay_cx, self._btn_pay_cy,
            f"💰  Bayar",
            base=(180, 100, 20), hover=(220, 130, 30),
            pressed=self._pressed_pay, hovered=self._hover_pay
        )

    def _draw_btn(self, cx, cy, label, base, hover, pressed, hovered):
        if pressed:
            color = tuple(max(0, c - 40) for c in base) + (255,)
        elif hovered:
            color = hover + (255,)
        else:
            color = base + (240,)

        hw, hh = self.BTN_W / 2, self.BTN_H / 2
        arcade.draw_lbwh_rectangle_filled(cx - hw, cy - hh, self.BTN_W, self.BTN_H, color)
        arcade.draw_lbwh_rectangle_outline(
            cx - hw, cy - hh, self.BTN_W, self.BTN_H,
            (255, 255, 255, 160), 2
        )
        arcade.draw_text(
            label, cx, cy,
            (255, 255, 255, 255), font_size=15,
            anchor_x="center", anchor_y="center", bold=True
        )
