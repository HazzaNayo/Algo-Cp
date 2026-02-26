"""
game.py - BaksoGame utama dengan mekanik Cooking Fever
"""

import arcade
import os
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
    BACKGROUNDS_PATH, ITEMS_PATH, CHARACTERS_PATH,
    COOK_TIME, KUAH_TIME,
    BAKSO_PRICE, TIP_AMOUNT,
    GAME_DURATION, MAX_LIVES,
    COMBO_THRESHOLD, COMBO_MULTIPLIER,
    UPGRADES,
)
from src.models.cooking_station import BaksoStation, KuahStation, MangkokStation
from src.customer_manager import CustomerManager
from src.models.customer import CustomerState
from src.ui.dialog_box import DialogBox
from src.ui.hud import HUD, UpgradePanel


# ─── Game States ─────────────────────────────────────────────────────────────
class GameState:
    MENU       = "menu"
    PLAYING    = "playing"
    DIALOG     = "dialog"      # Dialog fakir tampil, game freeze
    UPGRADE    = "upgrade"     # Panel upgrade terbuka
    GAME_OVER  = "game_over"


# ─── Cooking Workflow Steps ───────────────────────────────────────────────────
class CookStep:
    IDLE      = 0   # Belum mulai
    MANGKOK   = 1   # Sudah ambil mangkok
    BAKSO     = 2   # Bakso sedang/sudah matang
    KUAH      = 3   # Kuah sedang/sudah tuang
    READY     = 4   # Siap disajikan


class BaksoGame(arcade.Window):
    """Main game window — Cooking Fever style bakso seller."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Sprites
        self.background_list = None
        self.item_sprites    = None
        self.background_sprite = None
        self.gerobak_sprite  = None

        # Player sprite (penjual)
        self.player_sprite   = None
        self.character_list  = None

        # ── Sub-systems
        self.customer_mgr : CustomerManager = None
        self.dialog       : DialogBox       = None
        self.hud          : HUD             = None
        self.upgrade_panel: UpgradePanel    = None

        # ── Cooking stations
        self.mangkok_station : MangkokStation = None
        self.bakso_station   : BaksoStation   = None
        self.kuah_station    : KuahStation    = None

        # ── Cook workflow
        self.cook_step = CookStep.IDLE

        # ── Sajikan Button
        self._sajikan_cx = 640
        self._sajikan_cy = 56
        self._sajikan_w  = 180
        self._sajikan_h  = 44
        self._sajikan_hover   = False
        self._sajikan_pressed = False

        # ── Upgrade Toggle Button
        self._upgrade_btn_cx = SCREEN_WIDTH - 70
        self._upgrade_btn_cy = SCREEN_HEIGHT - 84
        self._upgrade_btn_r  = 28

        # ── Game state
        self.state       = GameState.MENU
        self.money       = 0
        self.pahala      = 0
        self.lives       = MAX_LIVES
        self.time_left   = GAME_DURATION
        self.combo_count = 0

        # Upgrades
        self.purchased_upgrades : set = set()
        self._cook_time_override  = None
        self._kuah_time_override  = None

        # Pending poor customer awaiting dialog result
        self._pending_poor = None

    # ─── Setup ───────────────────────────────────────────────────────────────
    def setup(self):
        """Inisialisasi/restart game."""
        self.background_list = arcade.SpriteList()
        self.item_sprites    = arcade.SpriteList()

        # Background
        self._load_sprite(
            f"{BACKGROUNDS_PATH}/Background.png",
            self.background_list,
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            fit_screen=True
        )

        # Gerobak
        if self.background_list:
            bg = self.background_list[0]
            self._load_sprite(
                f"{ITEMS_PATH}/Gerobak.png",
                self.item_sprites,
                center=(bg.center_x, bg.center_y),
                scale=bg.scale
            )


        # ── Cooking stations
        self.mangkok_station = MangkokStation()
        self.bakso_station   = BaksoStation(self._cook_time_override)
        self.kuah_station    = KuahStation(self._kuah_time_override)
        self.cook_step       = CookStep.IDLE

        # ── Sub-systems
        self.customer_mgr = CustomerManager()
        self.customer_mgr.on_served_normal  = self._on_served
        self.customer_mgr.on_served_poor    = self._on_poor_customer
        self.customer_mgr.on_customer_angry = self._on_angry

        self.dialog        = DialogBox(on_free=self._choose_free, on_pay=self._choose_pay)
        self.hud           = HUD()
        self.upgrade_panel = UpgradePanel(on_upgrade=self._do_upgrade)

        # Game state
        self.state      = GameState.PLAYING
        self.money      = 0
        self.pahala     = 0
        self.lives      = MAX_LIVES
        self.time_left  = GAME_DURATION
        self.combo_count= 0
        self._update_hud()

    def _load_sprite(self, path, sprite_list, center, fit_screen=False, scale=None):
        try:
            s = arcade.Sprite(path)
            s.center_x, s.center_y = center
            if fit_screen:
                sx = SCREEN_WIDTH / s.width + 0.15
                sy = SCREEN_HEIGHT / s.height + 0.15
                s.scale = max(sx, sy)
            elif scale is not None:
                s.scale = scale
            sprite_list.append(s)
            return s
        except Exception as e:
            print(f"[WARN] Could not load {path}: {e}")
            return None

    def _load_player(self):
        try:
            path = f"{CHARACTERS_PATH}/Player.png"
            self.player_sprite = arcade.Sprite(path, 1.0)
            self.player_sprite.center_x = 200
            self.player_sprite.center_y = 180
            self.character_list.append(self.player_sprite)
        except Exception as e:
            print(f"[WARN] Could not load player: {e}")

    # ─── Draw ────────────────────────────────────────────────────────────────
    def on_draw(self):
        self.clear()

        if self.state == GameState.MENU:
            self._draw_menu()
            return

        if self.state == GameState.GAME_OVER:
            self._draw_game_over()
            return

        # Background (paling belakang)
        if self.background_list:
            self.background_list.draw()

        # Customers (di belakang gerobak)
        self.customer_mgr.draw()

        # Items / gerobak (paling depan game elements)
        self.item_sprites.draw()

        # Cooking stations
        self.mangkok_station.draw()
        self.bakso_station.draw()
        self.kuah_station.draw()

        # Sajikan button
        self._draw_sajikan_button()

        # Upgrade toggle button
        self._draw_upgrade_btn()

        # HUD
        self.hud.draw()

        # Upgrade panel (on top)
        self.upgrade_panel.draw(self.money, self.purchased_upgrades)

        # Dialog (topmost)
        self.dialog.draw()

        # Step indicator
        self._draw_cook_step_indicator()

    def _draw_sajikan_button(self):
        """Tombol SAJIKAN di bawah layar — hanya aktif saat cook_step == READY dan ada pembeli."""
        active = (
            self.cook_step == CookStep.READY
            and self.customer_mgr.get_front_customer() is not None
            and self.state == GameState.PLAYING
        )
        if active:
            fill = (200, 100, 10, 240) if self._sajikan_pressed else (240, 140, 20, 240)
            if self._sajikan_hover:
                fill = (255, 170, 40, 255)
        else:
            fill = (80, 80, 80, 160)

        hw, hh = self._sajikan_w / 2, self._sajikan_h / 2
        cx, cy = self._sajikan_cx, self._sajikan_cy
        arcade.draw_lbwh_rectangle_filled(cx - hw, cy - hh, self._sajikan_w, self._sajikan_h, fill)
        arcade.draw_lbwh_rectangle_outline(
            cx - hw, cy - hh, self._sajikan_w, self._sajikan_h,
            (255, 255, 255, 180) if active else (120, 120, 120, 100), 2
        )
        arcade.draw_text(
            "🍜  SAJIKAN",
            cx, cy, (255, 255, 255, 255) if active else (150, 150, 150, 150),
            font_size=16, anchor_x="center", anchor_y="center", bold=True
        )

    def _draw_upgrade_btn(self):
        cx, cy, r = self._upgrade_btn_cx, self._upgrade_btn_cy, self._upgrade_btn_r
        arcade.draw_circle_filled(cx, cy, r, (80, 55, 15, 220))
        arcade.draw_circle_outline(cx, cy, r, (200, 160, 60, 200), 2)
        arcade.draw_text("⚡", cx, cy, (255, 220, 60, 255),
                         font_size=16, anchor_x="center", anchor_y="center")

    def _draw_cook_step_indicator(self):
        """Bar langkah memasak di bawah HUD."""
        steps = [
            ("🥣 Mangkok", self.cook_step >= CookStep.MANGKOK),
            ("🍢 Bakso",   self.cook_step >= CookStep.BAKSO),
            ("🥣 Kuah",   self.cook_step >= CookStep.KUAH),
            ("🍜 Sajikan", self.cook_step == CookStep.READY),
        ]
        x_start = SCREEN_WIDTH // 2 - 260
        y = SCREEN_HEIGHT - 84
        for i, (label, done) in enumerate(steps):
            x = x_start + i * 130
            color = (50, 200, 80, 240) if done else (80, 80, 80, 180)
            arcade.draw_lbwh_rectangle_filled(x, y - 14, 118, 28, color)
            arcade.draw_lbwh_rectangle_outline(x, y - 14, 118, 28,
                                               (255, 255, 255, 120), 1)
            arcade.draw_text(label, x + 59, y, (255, 255, 255, 230),
                             font_size=11, anchor_x="center", anchor_y="center")
            # Arrow
            if i < len(steps) - 1:
                arcade.draw_text("▶", x + 122, y, (200, 200, 200, 180),
                                 font_size=10, anchor_x="center", anchor_y="center")

    def _draw_menu(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (30, 18, 5))
        arcade.draw_text(
            "🍜 Game Penjual Bakso",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80,
            (255, 220, 80, 255), font_size=40,
            anchor_x="center", anchor_y="center", bold=True
        )
        arcade.draw_text(
            "Cooking Fever Style!",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
            (200, 180, 120, 230), font_size=20,
            anchor_x="center", anchor_y="center"
        )
        # Play button
        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 60, 240, 58,
            (220, 130, 20, 240)
        )
        arcade.draw_lbwh_rectangle_outline(
            SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 60, 240, 58,
            (255, 200, 80, 255), 3
        )
        arcade.draw_text(
            "▶  MULAI MAIN",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 31,
            (255, 255, 255, 255), font_size=22,
            anchor_x="center", anchor_y="center", bold=True
        )
        arcade.draw_text(
            "Tekan SPASI atau klik MULAI orang",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
            (160, 140, 100, 200), font_size=14,
            anchor_x="center", anchor_y="center"
        )

    def _draw_game_over(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (15, 8, 2))
        title = "⏱ Waktu Habis!" if self.time_left <= 0 else "💔 Kamu Menyerah!"
        arcade.draw_text(title, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100,
                         (255, 80, 80, 255), font_size=36,
                         anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text(
            f"💰 Pendapatan: Rp{self.money:,}",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
            (255, 230, 80, 255), font_size=24,
            anchor_x="center", anchor_y="center"
        )
        arcade.draw_text(
            f"🙏 Total Pahala: {self.pahala}",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 0,
            (150, 255, 200, 255), font_size=20,
            anchor_x="center", anchor_y="center"
        )
        # Restart button
        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 - 80, 260, 54,
            (180, 100, 10, 230)
        )
        arcade.draw_lbwh_rectangle_outline(
            SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 - 80, 260, 54,
            (255, 180, 60, 255), 2
        )
        arcade.draw_text(
            "🔄  MAIN LAGI",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 53,
            (255, 255, 255, 255), font_size=22,
            anchor_x="center", anchor_y="center", bold=True
        )
        arcade.draw_text(
            "Tekan SPASI",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120,
            (160, 140, 100, 200), font_size=14,
            anchor_x="center", anchor_y="center"
        )

    # ─── Update ──────────────────────────────────────────────────────────────
    def on_update(self, delta_time: float):
        if self.state not in (GameState.PLAYING,):
            return

        # Timer
        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self._game_over()
            return

        # Update cooking stations
        if self.bakso_station.update(delta_time) and self.cook_step == CookStep.BAKSO:
            # Bakso selesai — otomatis siap, tunggu player klik kuah
            self.hud.add_notif("🍢 Bakso matang! Klik Kuah →", (255, 220, 80, 255))

        if self.kuah_station.update(delta_time) and self.cook_step == CookStep.KUAH:
            self.cook_step = CookStep.READY
            self.hud.add_notif("✅ Siap disajikan!", (80, 255, 150, 255))

        # Update customers
        self.customer_mgr.update(delta_time)

        # HUD
        self.hud.time_left = self.time_left
        self.hud.combo     = self.combo_count
        self.hud.update(delta_time)

        # Hover states
        mx, my = self._last_mouse
        self.mangkok_station.update_hover(mx, my)
        self.bakso_station.update_hover(mx, my)
        self.kuah_station.update_hover(mx, my)
        self._sajikan_hover = self._in_sajikan(mx, my)

    # ─── Input ───────────────────────────────────────────────────────────────
    def setup_input(self):
        self._last_mouse = (0, 0)

    def on_mouse_motion(self, x, y, dx, dy):
        self._last_mouse = (x, y)
        self.dialog.on_mouse_motion(x, y)
        self.upgrade_panel.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        # Dialog takes priority
        if self.dialog.visible:
            self.dialog.on_mouse_press(x, y, button, modifiers)
            return

        # Upgrade panel
        if self.upgrade_panel.on_mouse_press(x, y, button, modifiers):
            return

        # Upgrade toggle button
        if self._in_upgrade_btn(x, y):
            self.upgrade_panel.toggle()
            return

        if self.state == GameState.MENU:
            if self._in_menu_play(x, y):
                self.setup()
            return

        if self.state == GameState.GAME_OVER:
            if self._in_game_over_restart(x, y):
                self.setup()
            return

        if self.state != GameState.PLAYING:
            return

        # ── Station clicks (cooking workflow)
        self._handle_station_click(x, y, button, modifiers)

        # ── Sajikan
        if self._in_sajikan(x, y):
            self._sajikan_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.dialog.visible:
            self.dialog.on_mouse_release(x, y, button, modifiers)
            return
        if self.upgrade_panel.on_mouse_release(x, y, button, modifiers):
            return
        if self._sajikan_pressed and self._in_sajikan(x, y):
            self._sajikan_pressed = False
            self._try_sajikan()
        self._sajikan_pressed = False

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.SPACE:
            if self.state in (GameState.MENU, GameState.GAME_OVER):
                self.setup()

    # ─── Station Interaction ─────────────────────────────────────────────────
    def _handle_station_click(self, x, y, button, modifiers):
        """Cooking Fever multi-step click logic."""

        # Step 0 → 1: Klik Mangkok
        if self.mangkok_station.contains(x, y):
            if self.cook_step == CookStep.IDLE:
                self.mangkok_station.start_cooking()
                self.mangkok_station.take()
                self.cook_step = CookStep.MANGKOK
                self.hud.add_notif("✅ Mangkok siap! Sekarang klik Bakso 🍢", (200, 200, 255, 255))
            else:
                self.hud.add_notif("Mangkok sudah ada!", (200, 100, 100, 255))
            return

        # Step 1 → 2: Klik Panci Bakso
        if self.bakso_station.contains(x, y):
            if self.cook_step == CookStep.MANGKOK and not self.bakso_station.is_cooking and not self.bakso_station.is_ready:
                self.bakso_station.start_cooking()
                self.cook_step = CookStep.BAKSO
                self.hud.add_notif("🔥 Bakso sedang dimasak...", (255, 180, 50, 255))
            elif self.cook_step == CookStep.BAKSO and self.bakso_station.is_ready:
                self.bakso_station.take()
                self.hud.add_notif("🍢 Bakso diambil! Klik Kuah 🥣", (200, 200, 255, 255))
            elif self.cook_step < CookStep.MANGKOK:
                self.hud.add_notif("Siapkan mangkok dulu!", (200, 100, 100, 255))
            return

        # Step 2 → 3: Klik Ketel Kuah
        if self.kuah_station.contains(x, y):
            if self.cook_step == CookStep.BAKSO and self.bakso_station.is_done and not self.kuah_station.is_cooking and not self.kuah_station.is_ready:
                self.kuah_station.start_cooking()
                self.cook_step = CookStep.KUAH
                self.hud.add_notif("🥣 Menuang kuah...", (100, 200, 255, 255))
            elif self.cook_step == CookStep.KUAH and self.kuah_station.is_ready:
                self.kuah_station.take()
                self.cook_step = CookStep.READY
                self.hud.add_notif("✅ Siap disajikan! Klik SAJIKAN", (80, 255, 150, 255))
            elif self.cook_step < CookStep.BAKSO:
                self.hud.add_notif("Masak bakso dulu!", (200, 100, 100, 255))
            return

    def _try_sajikan(self):
        """Player menekan tombol Sajikan."""
        if self.cook_step != CookStep.READY:
            self.hud.add_notif("Bakso belum siap!", (200, 100, 100, 255))
            return
        customer = self.customer_mgr.get_front_customer()
        if customer is None:
            self.hud.add_notif("Tidak ada pembeli!", (200, 100, 100, 255))
            return
        # Serve
        self.customer_mgr.serve_front()
        # Reset stations for next order
        self._reset_stations()

    def _reset_stations(self):
        self.mangkok_station.reset()
        self.bakso_station.reset()
        self.kuah_station.reset()
        self.cook_step = CookStep.IDLE

    # ─── Callbacks ───────────────────────────────────────────────────────────
    def _on_served(self, money: int, pahala: int, got_tip: bool):
        self.money  += money
        self.pahala += pahala
        self.combo_count = self.customer_mgr.combo_count

        notif_parts = []
        if money > 0:
            notif_parts.append(f"+Rp{money:,}")
        if pahala > 0:
            notif_parts.append(f"🙏 +{pahala}")
        if got_tip:
            notif_parts.append(f"TIP +Rp{TIP_AMOUNT:,}")
        if self.combo_count >= COMBO_THRESHOLD:
            notif_parts.append(f"🔥 COMBO x{self.combo_count}!")

        if notif_parts:
            self.hud.add_notif("  ".join(notif_parts), (100, 255, 150, 255))

        self._update_hud()

    def _on_poor_customer(self, customer):
        """Tampilkan dialog pilihan untuk pembeli fakir."""
        self._pending_poor = customer
        self.dialog.show()
        self.state = GameState.DIALOG

    def _on_angry(self):
        self.lives -= 1
        self.combo_count = 0
        self.hud.add_notif("💔 Pembeli kecewa! -1 nyawa", (255, 60, 60, 255))
        self._update_hud()
        if self.lives <= 0:
            self._game_over()

    def _choose_free(self):
        """Player memilih memberi bakso gratis."""
        if self._pending_poor:
            self.customer_mgr.resolve_poor(self._pending_poor, give_free=True)
            self._pending_poor = None
        self.state = GameState.PLAYING

    def _choose_pay(self):
        """Player memilih tetap minta pembeli fakir bayar."""
        if self._pending_poor:
            self.customer_mgr.resolve_poor(self._pending_poor, give_free=False)
            self._pending_poor = None
        self.state = GameState.PLAYING

    def _update_hud(self):
        self.hud.money  = self.money
        self.hud.pahala = self.pahala
        self.hud.lives  = self.lives
        self.hud.combo  = self.combo_count

    def _game_over(self):
        self.state = GameState.GAME_OVER

    # ─── Upgrade ─────────────────────────────────────────────────────────────
    def _do_upgrade(self, key: str):
        info = UPGRADES.get(key)
        if not info:
            return
        if key in self.purchased_upgrades:
            self.hud.add_notif("Sudah dibeli!", (200, 200, 100, 255))
            return
        if self.money < info["price"]:
            self.hud.add_notif(f"Uang kurang! Butuh Rp{info['price']:,}", (255, 80, 80, 255))
            return
        self.money -= info["price"]
        self.purchased_upgrades.add(key)
        self.hud.add_notif(f"⚡ {info['name']} dibeli!", (255, 220, 80, 255))

        # Apply effect
        if key == "kuah_turbo":
            self._kuah_time_override = 1.0
            self.kuah_station = KuahStation(1.0)
        elif key == "wajan_ajaib":
            self._cook_time_override = 1.5
            self.bakso_station = BaksoStation(1.5)
        elif key == "gerobak_cute":
            for c in self.customer_mgr.customers:
                c.max_patience *= 1.2
                c.patience = min(c.patience * 1.2, c.max_patience)

        self._update_hud()

    # ─── Hit-tests ────────────────────────────────────────────────────────────
    def _in_sajikan(self, x, y):
        hw, hh = self._sajikan_w / 2, self._sajikan_h / 2
        cx, cy = self._sajikan_cx, self._sajikan_cy
        return cx - hw <= x <= cx + hw and cy - hh <= y <= cy + hh

    def _in_upgrade_btn(self, x, y):
        cx, cy, r = self._upgrade_btn_cx, self._upgrade_btn_cy, self._upgrade_btn_r
        return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2

    def _in_menu_play(self, x, y):
        return (SCREEN_WIDTH / 2 - 120 <= x <= SCREEN_WIDTH / 2 + 120
                and SCREEN_HEIGHT / 2 - 60 <= y <= SCREEN_HEIGHT / 2 - 2)

    def _in_game_over_restart(self, x, y):
        return (SCREEN_WIDTH / 2 - 130 <= x <= SCREEN_WIDTH / 2 + 130
                and SCREEN_HEIGHT / 2 - 80 <= y <= SCREEN_HEIGHT / 2 - 26)
