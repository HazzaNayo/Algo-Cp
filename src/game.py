"""
game.py - BaksoGame utama dengan mekanik Cooking Fever
         Workflow: Mangkok → Bakso → Mie → Sayuran → SAJIKAN
"""

import arcade
import os
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
    BACKGROUNDS_PATH, ITEMS_PATH, CHARACTERS_PATH,
    COOK_TIME, MIE_TIME, SAYURAN_TIME,
    BAKSO_PRICE, TIP_AMOUNT,
    GAME_DURATION, MAX_LIVES,
    COMBO_THRESHOLD, COMBO_MULTIPLIER,
    ORDER_RECIPES,
)
from src.models.cooking_station import (
    BaksoStation, MieStation, SayuranStation, MangkokStation, BowlDisplay
)
from src.customer_manager import CustomerManager
from src.models.customer import CustomerState
from src.ui.dialog_box import DialogBox
from src.ui.hud import HUD


# ─── Game States ─────────────────────────────────────────────────────────────
class GameState:
    MENU       = "menu"
    PLAYING    = "playing"
    DIALOG     = "dialog"
    GAME_OVER  = "game_over"


# ─── Cooking States ──────────────────────────────────────────────────────────
# Tidak lagi sequential — player bisa masukkan bahan dalam urutan apapun
# State dihitung dari: has_mangkok + ingredients set di BowlDisplay


class BaksoGame(arcade.Window):
    """Main game window — Cooking Fever style bakso seller."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Sprites
        self.background_list   = None
        self.item_sprites      = None
        self.background_sprite = None
        self.gerobak_sprite    = None

        # ── Sub-systems
        self.customer_mgr  : CustomerManager = None
        self.dialog        : DialogBox       = None
        self.hud           : HUD             = None

        # ── Cooking stations
        self.mangkok_station  : MangkokStation  = None
        self.bakso_station    : BaksoStation     = None
        self.mie_station      : MieStation       = None
        self.sayuran_station  : SayuranStation   = None

        # ── Bowl display (gambar mangkok)
        self.bowl_display : BowlDisplay = None

        # ── Cook workflow (non-sequential)
        # State dilacak lewat bowl_display.has_mangkok dan bowl_display.ingredients

        # ── Sajikan Button
        self._sajikan_cx = 730
        self._sajikan_cy = 30
        self._sajikan_w  = 180
        self._sajikan_h  = 44
        self._sajikan_hover   = False
        self._sajikan_pressed = False

        # ── Game state
        self.state       = GameState.MENU
        self.money       = 0
        self.pahala      = 0
        self.lives       = MAX_LIVES
        self.time_left   = GAME_DURATION
        self.combo_count = 0

        # Pending poor customer awaiting dialog result
        self._pending_poor = None

        # Mouse tracker
        self._last_mouse = (0, 0)

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
        self.mangkok_station  = MangkokStation()
        self.bakso_station    = BaksoStation()
        self.mie_station      = MieStation()
        self.sayuran_station  = SayuranStation()

        # ── Bowl display
        self.bowl_display = BowlDisplay()

        # ── Sub-systems
        self.customer_mgr = CustomerManager()
        self.customer_mgr.on_served_normal  = self._on_served
        self.customer_mgr.on_served_poor    = self._on_poor_customer
        self.customer_mgr.on_customer_angry = self._on_angry

        self.dialog        = DialogBox(on_free=self._choose_free, on_pay=self._choose_pay)
        self.hud           = HUD()

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
        self.mie_station.draw()
        self.sayuran_station.draw()

        # Bowl display (gambar mangkok berubah sesuai step)
        self.bowl_display.draw()

        # Sajikan button
        self._draw_sajikan_button()

        # HUD
        self.hud.draw()

        # Dialog (topmost)
        self.dialog.draw()

        # Step indicator
        self._draw_cook_step_indicator()

    def _draw_sajikan_button(self):
        # Cek apakah bowl cocok dengan pesanan pembeli depan
        customer = self.customer_mgr.get_front_customer()
        active = (
            self.bowl_display is not None
            and customer is not None
            and self.bowl_display.matches_order(customer.order_type)
            and self.state == GameState.PLAYING
        )

        cx, cy = self._sajikan_cx, self._sajikan_cy
        accent = (120, 120, 120, 170)
        status = "BELUM SIAP"
        if active:
            accent = (80, 230, 130, 240)
            status = "KLIK UNTUK SAJI"
            if self._sajikan_pressed:
                accent = (55, 195, 105, 245)
            elif self._sajikan_hover:
                accent = (110, 245, 155, 250)
        elif self._sajikan_hover:
            accent = (170, 170, 170, 200)

        # Hotspot marker kecil
        arcade.draw_circle_filled(cx, cy, 6, accent)
        if self._sajikan_hover or active:
            arcade.draw_circle_outline(cx, cy, 16, accent, 2)

        # Tag utama (gaya sama dengan stasiun lain)
        chip_w = 150
        chip_h = 30
        chip_x = cx - chip_w / 2
        chip_y = cy + 14
        arcade.draw_lbwh_rectangle_filled(chip_x, chip_y, chip_w, chip_h, (26, 18, 10, 220))
        arcade.draw_lbwh_rectangle_outline(chip_x, chip_y, chip_w, chip_h, accent, 2)
        arcade.draw_text(
            "SAJIKAN",
            cx, chip_y + chip_h / 2,
            (245, 235, 215, 255) if active else (170, 170, 170, 220),
            font_size=13, anchor_x="center", anchor_y="center", bold=True
        )

        # Status kecil di bawah hotspot
        arcade.draw_text(
            status, cx, cy - 14,
            accent if active else (155, 155, 155, 210),
            font_size=10, anchor_x="center", anchor_y="center", bold=True
        )

    def _draw_cook_step_indicator(self):
        """Bar status bahan — sesuaikan dengan pesanan pembeli."""
        bd = self.bowl_display
        has_m = bd.has_mangkok if bd else False
        ings  = bd.ingredients if bd else set()
        
        # Dapatkan pesanan pembeli depan
        customer = self.customer_mgr.get_front_customer()
        order_type = customer.order_type if customer else "lengkap"
        required = ORDER_RECIPES.get(order_type, {"bakso", "mie", "sayuran"})
        
        steps = [("🥣 Mangkok", has_m)]
        if "bakso" in required:
            steps.append(("🍢 Bakso", "bakso" in ings))
        if "mie" in required:
            steps.append(("🍜 Mie", "mie" in ings))
        if "sayuran" in required:
            steps.append(("🥬 Sayur", "sayuran" in ings))
        
        is_match = bd.matches_order(order_type) if (bd and customer) else False
        steps.append(("🍜 Sajikan", is_match))
        
        total_w = len(steps) * 115 + (len(steps) - 1) * 8
        x_start = SCREEN_WIDTH // 2 - total_w // 2
        y = SCREEN_HEIGHT - 84
        for i, (label, done) in enumerate(steps):
            x = x_start + i * 123
            color = (50, 200, 80, 240) if done else (80, 80, 80, 180)
            arcade.draw_lbwh_rectangle_filled(x, y - 14, 112, 28, color)
            arcade.draw_lbwh_rectangle_outline(x, y - 14, 112, 28,
                                               (255, 255, 255, 120), 1)
            arcade.draw_text(label, x + 56, y, (255, 255, 255, 230),
                             font_size=11, anchor_x="center", anchor_y="center")

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
            "Tekan SPASI atau klik MULAI",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
            (160, 140, 100, 200), font_size=14,
            anchor_x="center", anchor_y="center"
        )

    def _draw_game_over(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (15, 8, 2))
        title = "⏱ Waktu Habis!" if self.time_left <= 0 else "💔 Nyawa Habis!"
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
        if self.state != GameState.PLAYING:
            return

        # Timer
        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self._game_over()
            return

        # Update cooking stations (all run independently)
        if self.bakso_station.update(delta_time) and self.bakso_station.is_ready:
            self.hud.add_notif("🍢 Bakso matang! Klik untuk ambil", (255, 220, 80, 255))

        if self.mie_station.update(delta_time) and self.mie_station.is_ready:
            self.hud.add_notif("🍜 Mie siap! Klik untuk ambil", (255, 220, 80, 255))

        if self.sayuran_station.update(delta_time) and self.sayuran_station.is_ready:
            self.hud.add_notif("🥬 Sayuran siap! Klik untuk ambil", (100, 220, 80, 255))

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
        self.mie_station.update_hover(mx, my)
        self.sayuran_station.update_hover(mx, my)
        self._sajikan_hover = self._in_sajikan(mx, my)

    # ─── Input ───────────────────────────────────────────────────────────────
    def on_mouse_motion(self, x, y, dx, dy):
        self._last_mouse = (x, y)
        self.dialog.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.dialog.visible:
            self.dialog.on_mouse_press(x, y, button, modifiers)
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
        """Non-sequential cooking: Mangkok dulu, lalu bahan bebas urutan."""
        bd = self.bowl_display

        # Mangkok harus diambil pertama
        if self.mangkok_station.contains(x, y):
            if not bd.has_mangkok:
                self.mangkok_station.start_cooking()
                self.mangkok_station.take()
                bd.set_mangkok()
                self.hud.add_notif("✅ Mangkok siap! Tambahkan bahan apapun", (200, 200, 255, 255))
            else:
                self.hud.add_notif("Mangkok sudah ada!", (200, 100, 100, 255))
            return

        # Cek apakah mangkok sudah diambil
        if not bd.has_mangkok:
            if (self.bakso_station.contains(x, y) or
                self.mie_station.contains(x, y) or
                self.sayuran_station.contains(x, y)):
                self.hud.add_notif("Siapkan mangkok dulu!", (200, 100, 100, 255))
            return

        # Jangan terima bahan baru kalau pesanan sudah cocok
        customer = self.customer_mgr.get_front_customer()
        if customer and bd.matches_order(customer.order_type):
            return
        
        # Dapatkan bahan yang dibutuhkan pesanan
        order_type = customer.order_type if customer else "lengkap"
        required = ORDER_RECIPES.get(order_type, {"bakso", "mie", "sayuran"})

        # Bakso — bisa diklik kapan saja setelah mangkok
        if self.bakso_station.contains(x, y):
            if "bakso" in bd.ingredients:
                self.hud.add_notif("Bakso sudah ditambahkan!", (200, 200, 100, 255))
            elif self.bakso_station.is_ready:
                self.bakso_station.take()
                bd.add_ingredient("bakso")
                self._check_complete()
                self.hud.add_notif("🍢 Bakso ditambahkan!", (200, 200, 255, 255))
            elif not self.bakso_station.is_cooking:
                self.bakso_station.start_cooking()
                self.hud.add_notif("🔥 Bakso sedang dimasak...", (255, 180, 50, 255))
            else:
                self.hud.add_notif("Bakso masih dimasak...", (255, 200, 100, 255))
            return

        # Mie — hanya jika diperlukan oleh pesanan
        if self.mie_station.contains(x, y):
            if "mie" not in required:
                self.hud.add_notif("Pesanan ini tidak butuh mie!", (200, 200, 100, 255))
            elif "mie" in bd.ingredients:
                self.hud.add_notif("Mie sudah ditambahkan!", (200, 200, 100, 255))
            elif self.mie_station.is_ready:
                self.mie_station.take()
                bd.add_ingredient("mie")
                self._check_complete()
                self.hud.add_notif("🍜 Mie ditambahkan!", (200, 200, 255, 255))
            elif not self.mie_station.is_cooking:
                self.mie_station.start_cooking()
                self.hud.add_notif("🍜 Mie sedang disiapkan...", (255, 200, 80, 255))
            else:
                self.hud.add_notif("Mie masih disiapkan...", (255, 200, 100, 255))
            return

        # Sayuran — hanya jika diperlukan oleh pesanan
        if self.sayuran_station.contains(x, y):
            if "sayuran" not in required:
                self.hud.add_notif("Pesanan ini tidak butuh sayuran!", (200, 200, 100, 255))
            elif "sayuran" in bd.ingredients:
                self.hud.add_notif("Sayuran sudah ditambahkan!", (200, 200, 100, 255))
            elif self.sayuran_station.is_ready:
                self.sayuran_station.take()
                bd.add_ingredient("sayuran")
                self._check_complete()
                self.hud.add_notif("🥬 Sayuran ditambahkan!", (100, 220, 80, 255))
            elif not self.sayuran_station.is_cooking:
                self.sayuran_station.start_cooking()
                self.hud.add_notif("🥬 Sayuran sedang disiapkan...", (100, 220, 80, 255))
            else:
                self.hud.add_notif("Sayuran masih disiapkan...", (200, 220, 100, 255))
            return

    def _check_complete(self):
        """Cek apakah bahan sudah sesuai pesanan pembeli depan."""
        customer = self.customer_mgr.get_front_customer()
        if customer and self.bowl_display.matches_order(customer.order_type):
            order_name = {"bakso": "Bakso", "baksomie": "Bakso Mie", "lengkap": "Lengkap"}
            self.hud.add_notif(f"✅ Pesanan {order_name.get(customer.order_type, '')} siap! Klik SAJIKAN", (80, 255, 150, 255))

    def _try_sajikan(self):
        """Player menekan tombol Sajikan."""
        customer = self.customer_mgr.get_front_customer()
        if customer is None:
            self.hud.add_notif("Tidak ada pembeli!", (200, 100, 100, 255))
            return
        if not self.bowl_display.matches_order(customer.order_type):
            order_name = {"bakso": "Bakso", "baksomie": "Bakso Mie", "lengkap": "Lengkap"}
            self.hud.add_notif(f"Pesanan belum sesuai! Pembeli ingin: {order_name.get(customer.order_type, '')}", (200, 100, 100, 255))
            return
        self.customer_mgr.serve_front()
        self._reset_stations()

    def _reset_stations(self):
        self.mangkok_station.reset()
        self.bakso_station.reset()
        self.mie_station.reset()
        self.sayuran_station.reset()
        self.bowl_display.reset()

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
        if self._pending_poor:
            self.customer_mgr.resolve_poor(self._pending_poor, give_free=True)
            self._pending_poor = None
        self.state = GameState.PLAYING

    def _choose_pay(self):
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

    # Hit-tests
    def _in_sajikan(self, x, y):
        hw, hh = self._sajikan_w / 2, self._sajikan_h / 2
        cx, cy = self._sajikan_cx, self._sajikan_cy
        return cx - hw <= x <= cx + hw and cy - hh <= y <= cy + hh

    def _in_menu_play(self, x, y):
        return (SCREEN_WIDTH / 2 - 120 <= x <= SCREEN_WIDTH / 2 + 120
                and SCREEN_HEIGHT / 2 - 60 <= y <= SCREEN_HEIGHT / 2 - 2)

    def _in_game_over_restart(self, x, y):
        return (SCREEN_WIDTH / 2 - 130 <= x <= SCREEN_WIDTH / 2 + 130
                and SCREEN_HEIGHT / 2 - 80 <= y <= SCREEN_HEIGHT / 2 - 26)


