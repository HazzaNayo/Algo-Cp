"""
game.py - BaksoGame utama dengan mekanik Cooking Fever
         Workflow: Mangkok → Bakso → Mie → Sayuran → SAJIKAN
"""

import arcade
import os
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FULLSCREEN,
    BACKGROUNDS_PATH, ITEMS_PATH, CHARACTERS_PATH,
    COOK_TIME, MIE_TIME, SAYURAN_TIME,
    BAKSO_PRICE, MIE_PRICE, SAYURAN_PRICE, TIP_AMOUNT,
    GAME_DURATION, MAX_LIVES,
    COMBO_THRESHOLD, COMBO_MULTIPLIER,
    ORDER_RECIPES,
    SPAWN_RATE, MAX_QUEUE,
    RESET_PENALTY,
    INITIAL_STOCK_BAKSO, INITIAL_STOCK_MIE, INITIAL_STOCK_SAYUR, INITIAL_MONEY,
    STORE_BAKSO_PRICE, STORE_MIE_PRICE, STORE_SAYUR_PRICE,
    MAX_POOR_CUSTOMERS, POOR_CUSTOMER_BONUS_TIME,
)
from src.models.cooking_station import (
    BaksoStation, MieStation, SayuranStation, MangkokStation, BowlDisplay
)
from src.customer_manager import CustomerManager
from src.models.customer import CustomerState
from src.ui.dialog_box import DialogBox
from src.ui.hud import HUD
from src.ui.store import Store


# ─── Game States ─────────────────────────────────────────────────────────────
class GameState:
    MENU       = "menu"
    STORE      = "store"      # State untuk store
    PLAYING    = "playing"
    PAUSED     = "paused"
    DIALOG     = "dialog"
    GAME_OVER  = "game_over"


class BaksoGame(arcade.Window):
    """Main game window — Cooking Fever style bakso seller."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=FULLSCREEN)
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

        # ── Sajikan Button
        self._sajikan_cx = 1000  # Ubah dari 730 ke kanan
        self._sajikan_cy = 50
        self._sajikan_w  = 180
        self._sajikan_h  = 44
        self._sajikan_hover   = False
        self._sajikan_pressed = False

        # ── Reset Button (untuk undo pesanan salah)
        self._reset_btn_cx = 1000  # Ubah dari 730 ke kanan
        self._reset_btn_cy = 120
        self._reset_btn_w  = 180
        self._reset_btn_h  = 44
        self._reset_btn_hover   = False
        self._reset_btn_pressed = False

        # ── Game state
        self.state       = GameState.MENU  # Mulai dari MENU
        self.money       = 0
        self.pahala      = 0
        self.lives       = MAX_LIVES
        self.time_left   = GAME_DURATION
        self.combo_count = 0

        # ── Store
        self.store: Store = None

        # ── Store button di menu (dipindahkan ke kanan)
        self._store_btn_x = SCREEN_WIDTH / 2 + 250      # Lebih ke kanan
        self._store_btn_y = SCREEN_HEIGHT / 2 - 31      # Selaras dengan tombol MULAI MAIN
        self._store_btn_w = 180
        self._store_btn_h = 50
        self._store_btn_hover = False

        # ── Rush Hour tracking
        # self.is_rush_hour = False
        # self.rush_hour_time_remaining = 0

        # ── Queue selection
        self._selected_customer_idx = None
        self._customer_buttons = []

        # Pending poor customer awaiting dialog result
        self._pending_poor = None

        # Mouse tracker
        self._last_mouse = (0, 0)

        # Pause button
        self._pause_btn_x = SCREEN_WIDTH - 60
        self._pause_btn_y = SCREEN_HEIGHT - 90
        self._pause_btn_w = 50
        self._pause_btn_h = 50

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
        self.money      = INITIAL_MONEY     # Mulai dengan uang awal 0
        self.pahala     = 0
        self.lives      = MAX_LIVES
        self.time_left  = GAME_DURATION
        self.combo_count= 0
        self._selected_customer_idx = None
        
        # ── Stock awal bahan (modal pemain)
        self.stock_bakso = INITIAL_STOCK_BAKSO
        self.stock_mie = INITIAL_STOCK_MIE
        self.stock_sayur = INITIAL_STOCK_SAYUR
        
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

        if self.state == GameState.STORE:
            self.store.draw(self.money)
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

        # Bowl display
        self.bowl_display.draw()

        # Sajikan button
        self._draw_sajikan_button()

        # Reset button
        self._draw_reset_button()

        # HUD
        self.hud.draw()

        # Dialog
        self.dialog.draw()

        # Pause button
        self._draw_pause_button()

        # Step indicator
        self._draw_cook_step_indicator()

        # Queue buttons (untuk memilih customer)
        self._draw_queue_buttons()

        # Pause overlay
        if self.state == GameState.PAUSED:
            self._draw_pause_menu()

    def _draw_pause_button(self):
        """Draw pause/resume button di top-right."""
        cx = self._pause_btn_x
        cy = self._pause_btn_y
        w = self._pause_btn_w
        h = self._pause_btn_h

        is_hover = self._in_pause_button(self._last_mouse[0], self._last_mouse[1])
        color = (255, 100, 100, 255) if is_hover else (200, 80, 80, 255)
        outline = (255, 200, 100, 255) if is_hover else (200, 150, 80, 255)

        # Background button
        arcade.draw_lbwh_rectangle_filled(cx - w // 2, cy - h // 2, w, h, color)
        arcade.draw_lbwh_rectangle_outline(cx - w // 2, cy - h // 2, w, h, outline, 2)

        # Icon (pause atau play)
        icon = "⏸" if self.state == GameState.PLAYING else "▶"
        arcade.draw_text(
            icon, cx, cy,
            (255, 255, 255, 255),
            font_size=20,
            anchor_x="center", anchor_y="center", bold=True
        )

    def _draw_pause_menu(self):
        """Draw overlay pause menu."""
        # Semi-transparent dark overlay
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 150))

        # Dialog box
        dialog_w = 500
        dialog_h = 300
        dialog_x = SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = SCREEN_HEIGHT // 2 - dialog_h // 2

        arcade.draw_lbwh_rectangle_filled(dialog_x, dialog_y, dialog_w, dialog_h, (40, 30, 20, 255))
        arcade.draw_lbwh_rectangle_outline(dialog_x, dialog_y, dialog_w, dialog_h, (200, 150, 80, 255), 3)

        # Title
        arcade.draw_text(
            "⏸ PAUSED",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            (255, 200, 80, 255),
            font_size=32,
            anchor_x="center", anchor_y="center", bold=True
        )

        # Info
        arcade.draw_text(
            "Tekan P atau klik untuk melanjutkan",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
            (200, 200, 200, 255),
            font_size=14,
            anchor_x="center", anchor_y="center"
        )

        # Resume button
        btn_w = 200
        btn_h = 50
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        btn_y = SCREEN_HEIGHT // 2 - btn_h // 2

        is_hover = self._in_resume_button(self._last_mouse[0], self._last_mouse[1])
        btn_color = (80, 230, 130, 255) if is_hover else (50, 200, 100, 255)

        arcade.draw_lbwh_rectangle_filled(btn_x, btn_y, btn_w, btn_h, btn_color)
        arcade.draw_lbwh_rectangle_outline(btn_x, btn_y, btn_w, btn_h, (255, 255, 255, 255), 2)
        arcade.draw_text(
            "▶ LANJUTKAN",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            (255, 255, 255, 255),
            font_size=16,
            anchor_x="center", anchor_y="center", bold=True
        )

        # Quit button
        quit_btn_w = 200
        quit_btn_h = 50
        quit_btn_x = SCREEN_WIDTH // 2 - quit_btn_w // 2
        quit_btn_y = SCREEN_HEIGHT // 2 - 100

        is_quit_hover = self._in_quit_button(self._last_mouse[0], self._last_mouse[1])
        quit_color = (255, 100, 100, 255) if is_quit_hover else (230, 80, 80, 255)

        arcade.draw_lbwh_rectangle_filled(quit_btn_x, quit_btn_y, quit_btn_w, quit_btn_h, quit_color)
        arcade.draw_lbwh_rectangle_outline(quit_btn_x, quit_btn_y, quit_btn_w, quit_btn_h, (255, 255, 255, 255), 2)
        arcade.draw_text(
            "🏠 MENU",
            SCREEN_WIDTH // 2, quit_btn_y + quit_btn_h // 2,
            (255, 255, 255, 255),
            font_size=16,
            anchor_x="center", anchor_y="center", bold=True
        )

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

    def _draw_reset_button(self):
        """Draw reset/undo button untuk membersihkan pesanan salah."""
        customer = self.customer_mgr.get_front_customer()
        has_ingredients = (
            self.bowl_display is not None
            and len(self.bowl_display.ingredients) > 0
            and self.state == GameState.PLAYING
        )

        cx, cy = self._reset_btn_cx, self._reset_btn_cy
        accent = (120, 120, 120, 170)
        status = "KOSONG"
        if has_ingredients:
            accent = (255, 150, 80, 240)
            status = "KLIK UNTUK ULANG"
            if self._reset_btn_pressed:
                accent = (220, 130, 60, 245)
            elif self._reset_btn_hover:
                accent = (255, 170, 100, 250)
        elif self._reset_btn_hover:
            accent = (170, 170, 170, 200)

        # Hotspot marker kecil
        arcade.draw_circle_filled(cx, cy, 6, accent)
        if self._reset_btn_hover or has_ingredients:
            arcade.draw_circle_outline(cx, cy, 16, accent, 2)

        # Tag utama
        chip_w = 150
        chip_h = 30
        chip_x = cx - chip_w / 2
        chip_y = cy + 14
        arcade.draw_lbwh_rectangle_filled(chip_x, chip_y, chip_w, chip_h, (26, 18, 10, 220))
        arcade.draw_lbwh_rectangle_outline(chip_x, chip_y, chip_w, chip_h, accent, 2)
        arcade.draw_text(
            "ULANG",
            cx, chip_y + chip_h / 2,
            (245, 235, 215, 255) if has_ingredients else (170, 170, 170, 220),
            font_size=13, anchor_x="center", anchor_y="center", bold=True
        )

        # Status kecil di bawah hotspot
        arcade.draw_text(
            status, cx, cy - 14,
            accent if has_ingredients else (155, 155, 155, 210),
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

        # Tombol MULAI MAIN
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

        # Tombol STORE
        store_color = (150, 100, 30, 240) if self._store_btn_hover else (120, 80, 20, 220)
        arcade.draw_lbwh_rectangle_filled(
            self._store_btn_x - self._store_btn_w / 2, self._store_btn_y - self._store_btn_h / 2,
            self._store_btn_w, self._store_btn_h, store_color
        )
        arcade.draw_lbwh_rectangle_outline(
            self._store_btn_x - self._store_btn_w / 2, self._store_btn_y - self._store_btn_h / 2,
            self._store_btn_w, self._store_btn_h, (200, 150, 80, 255), 2
        )
        arcade.draw_text(
            "🏪  TOKO",
            self._store_btn_x, self._store_btn_y,
            (255, 255, 255, 255), font_size=18,
            anchor_x="center", anchor_y="center", bold=True
        )

        arcade.draw_text(
            "Tekan SPASI atau klik MULAI",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100,
            (160, 140, 100, 200), font_size=14,
            anchor_x="center", anchor_y="center"
        )

    def _draw_queue_buttons(self):
        """Draw tombol untuk memilih customer dari antrian."""
        customers = self.customer_mgr.customers
        if len(customers) <= 1:
            self._customer_buttons = []
            return

        # Hanya tampilkan jika ada lebih dari 1 pembeli
        self._customer_buttons = []
        start_x = 50
        start_y = SCREEN_HEIGHT - 110
        btn_w = 120
        btn_h = 50
        spacing = 10

        for i, customer in enumerate(customers):
            if i >= 5:  # Max 5 tombol ditampilkan
                remaining = len(customers) - 5
                arcade.draw_text(
                    f"+{remaining} lainnya",
                    start_x + 5 * (btn_w + spacing), start_y + btn_h // 2,
                    (200, 200, 200, 255),
                    font_size=10, anchor_x="left", anchor_y="center", bold=True
                )
                break

            btn_x = start_x + i * (btn_w + spacing)
            btn_y = start_y

            is_selected = (i == self._selected_customer_idx)
            is_hover = self._in_queue_button(self._last_mouse[0], self._last_mouse[1], i)

            # Warna button
            if is_selected:
                btn_color = (100, 200, 255, 255)
                outline_color = (200, 255, 100, 255)
            elif is_hover:
                btn_color = (150, 150, 200, 255)
                outline_color = (200, 200, 255, 255)
            else:
                btn_color = (100, 100, 150, 255)
                outline_color = (150, 150, 200, 255)

            # Draw button
            arcade.draw_lbwh_rectangle_filled(btn_x, btn_y, btn_w, btn_h, btn_color)
            arcade.draw_lbwh_rectangle_outline(btn_x, btn_y, btn_w, btn_h, outline_color, 2)

            # Label (customer type)
            label = "💰 Mampu" if not customer.is_poor else "😔 Fakir"
            arcade.draw_text(
                label, btn_x + btn_w // 2, btn_y + btn_h - 15,
                (255, 255, 255, 255),
                font_size=9, anchor_x="center", anchor_y="center", bold=True
            )

            # Order type + quantity
            order_label = f"{customer.order_type[:3].upper()}×{customer.order_quantity}"
            arcade.draw_text(
                order_label, btn_x + btn_w // 2, btn_y + 10,
                (200, 220, 255, 255),
                font_size=8, anchor_x="center", anchor_y="center", bold=True
            )

            self._customer_buttons.append((btn_x, btn_y, btn_w, btn_h))

    # ─── Update ──────────────────────────────────────────────────────────────
    def on_update(self, delta_time: float):
        if self.state == GameState.PAUSED or self.state != GameState.PLAYING:
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

        # Update customers dengan spawn rate normal
        self.customer_mgr.spawn_rate = SPAWN_RATE
        self.customer_mgr.max_queue = MAX_QUEUE
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
        self._reset_btn_hover = self._in_reset_btn(mx, my)

    # ─── Input ───────────────────────────────────────────────────────────────
    def on_mouse_motion(self, x, y, dx, dy):
        self._last_mouse = (x, y)
        if self.state == GameState.MENU:
            self._store_btn_hover = self._in_store_btn(x, y)
        elif self.state == GameState.STORE:
            self.store.update_hover(x, y)
        if self.dialog:
            self.dialog.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        # Store click
        if self.state == GameState.STORE:
            if self.store._in_back_btn(x, y):
                self.state = GameState.MENU
                return
            
            if self.store._in_bakso_btn(x, y):
                self.money, success = self.store.try_buy_bakso(self.money)
                if success:
                    self.hud.add_notif(f"✅ Bakso +1 | -{STORE_BAKSO_PRICE:,} Rp", (100, 220, 150, 255))
                    self._update_hud()
                else:
                    self.hud.add_notif("❌ Uang tidak cukup!", (255, 100, 100, 255))
                return
            
            if self.store._in_mie_btn(x, y):
                self.money, success = self.store.try_buy_mie(self.money)
                if success:
                    self.hud.add_notif(f"✅ Mie +1 | -{STORE_MIE_PRICE:,} Rp", (100, 220, 150, 255))
                    self._update_hud()
                else:
                    self.hud.add_notif("❌ Uang tidak cukup!", (255, 100, 100, 255))
                return
            
            if self.store._in_sayur_btn(x, y):
                self.money, success = self.store.try_buy_sayur(self.money)
                if success:
                    self.hud.add_notif(f"✅ Sayur +1 | -{STORE_SAYUR_PRICE:,} Rp", (100, 220, 150, 255))
                    self._update_hud()
                else:
                    self.hud.add_notif("❌ Uang tidak cukup!", (255, 100, 100, 255))
                return

        # Pause menu click
        if self.state == GameState.PAUSED:
            if self._in_resume_button(x, y):
                self.state = GameState.PLAYING
                return
            if self._in_quit_button(x, y):
                self.state = GameState.MENU
                self._selected_customer_idx = None
                return

        if self.dialog.visible:
            self.dialog.on_mouse_press(x, y, button, modifiers)
            return
        
        if self.state == GameState.MENU:
            if self._in_menu_play(x, y):
                self.setup()
                self.state = GameState.PLAYING
                return
            if self._in_store_btn(x, y):
                self.store = Store()
                self.state = GameState.STORE
                return

        if self.state == GameState.GAME_OVER:
            if self._in_game_over_restart(x, y):
                self.setup()
                self.state = GameState.PLAYING
                return
            if self._in_game_over_menu(x, y):
                self.state = GameState.MENU
                return

        if self.state != GameState.PLAYING:
            return

        # Pause button
        if self._in_pause_button(x, y):
            self.state = GameState.PAUSED
            return

        # Queue buttons (memilih customer)
        for i in range(len(self._customer_buttons)):
            if self._in_queue_button(x, y, i):
                self._selected_customer_idx = i if self._selected_customer_idx != i else None
                self.hud.add_notif(f"Pelanggan #{i+1} dipilih", (150, 200, 255, 255))
                return

        # Reset button (undo pesanan salah)
        if self._in_reset_btn(x, y):
            self._reset_btn_pressed = True
            self._do_reset_bowl()
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
        self._reset_btn_pressed = False

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.SPACE:
            if self.state in (GameState.MENU, GameState.GAME_OVER):
                self.setup()
        elif key == arcade.key.P:
            # Toggle pause
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
        elif key == arcade.key.R:
            # Reset bowl (undo)
            if self.state == GameState.PLAYING:
                self._do_reset_bowl()

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
            elif self.stock_bakso <= 0:
                self.hud.add_notif("❌ Stok bakso habis!", (255, 100, 100, 255))
            elif self.bakso_station.is_ready:
                self.bakso_station.take()
                bd.add_ingredient("bakso")
                self.stock_bakso -= 1
                self._check_complete()
                self.hud.add_notif("🍢 Bakso ditambahkan!", (200, 200, 255, 255))
                self._update_hud()
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
            elif self.stock_mie <= 0:
                self.hud.add_notif("❌ Stok mie habis!", (255, 100, 100, 255))
            elif self.mie_station.is_ready:
                self.mie_station.take()
                bd.add_ingredient("mie")
                self.stock_mie -= 1
                self._check_complete()
                self.hud.add_notif("🍜 Mie ditambahkan!", (200, 200, 255, 255))
                self._update_hud()
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
            elif self.stock_sayur <= 0:
                self.hud.add_notif("❌ Stok sayuran habis!", (255, 100, 100, 255))
            elif self.sayuran_station.is_ready:
                self.sayuran_station.take()
                bd.add_ingredient("sayuran")
                self.stock_sayur -= 1
                self._check_complete()
                self.hud.add_notif("🥬 Sayuran ditambahkan!", (100, 220, 80, 255))
                self._update_hud()
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

    def _do_reset_bowl(self):
        """Reset/undo pesanan — bersihkan mangkok dan semua bahan."""
        if len(self.bowl_display.ingredients) > 0 or self.bowl_display.has_mangkok:
            # Kurangi uang sebagai penalty (bisa mines)
            self.money -= RESET_PENALTY
            
            self.hud.add_notif(f"🔄 Pesanan dibatalkan! -{RESET_PENALTY:,} Rp", (255, 150, 100, 255))
            self._update_hud()
            self._reset_stations()
        else:
            self.hud.add_notif("Tidak ada pesanan untuk dibatalkan", (150, 150, 150, 200))

    def _reset_stations(self):
        self.mangkok_station.reset()
        self.bakso_station.reset()
        self.mie_station.reset()
        self.sayuran_station.reset()
        self.bowl_display.reset()

    # ─── Callbacks ───────────────────────────────────────────────────────────
    def _on_served(self, money: int, pahala: int, got_tip: bool):
        self.money  += money       # Bisa negative jika sudah mines
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
        self.hud.stock_bakso = self.stock_bakso
        self.hud.stock_mie = self.stock_mie
        self.hud.stock_sayur = self.stock_sayur

    def _game_over(self):
        self.state = GameState.GAME_OVER

    def _draw_game_over(self):
        """Draw game over screen dengan summary total penghasilan dan pahala."""
        # Background gelap
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

        # Main dialog box
        dialog_w = 900
        dialog_h = 500
        dialog_x = SCREEN_WIDTH // 2 - dialog_w // 2
        dialog_y = SCREEN_HEIGHT // 2 - dialog_h // 2

        arcade.draw_lbwh_rectangle_filled(
            dialog_x, dialog_y, dialog_w, dialog_h,
            (40, 30, 10, 255)
        )
        arcade.draw_lbwh_rectangle_outline(
            dialog_x, dialog_y, dialog_w, dialog_h,
            (200, 150, 80, 255), 3
        )

        # Title - Performance rating (bukan "WAKTU HABIS")
        rating_text = self._get_performance_rating()
        arcade.draw_text(
            rating_text,
            SCREEN_WIDTH // 2, dialog_y + dialog_h - 60,
            (255, 220, 80, 255),
            font_size=32, anchor_x="center", anchor_y="center", bold=True
        )

        # Divider line
        arcade.draw_line(
            dialog_x + 50, dialog_y + dialog_h - 100,
            dialog_x + dialog_w - 50, dialog_y + dialog_h - 100,
            (200, 150, 80, 255), 2
        )

        # Summary section
        summary_y = dialog_y + dialog_h - 140

        # Total penghasilan
        money_color = (255, 100, 100, 255) if self.money < 0 else (100, 255, 150, 255)
        money_text = f"💰 Total Penghasilan"
        money_value = f"Rp{abs(self.money):,}"
        if self.money < 0:
            money_value = f"-Rp{abs(self.money):,}"

        arcade.draw_text(
            money_text,
            dialog_x + 100, summary_y,
            (255, 255, 255, 255),
            font_size=16, anchor_x="left", anchor_y="center", bold=True
        )
        arcade.draw_text(
            money_value,
            dialog_x + dialog_w - 100, summary_y,
            money_color,
            font_size=20, anchor_x="right", anchor_y="center", bold=True
        )

        # Total pahala
        pahala_text = f"🙏 Total Kebaikan"
        pahala_value = f"{self.pahala} Pahala"

        arcade.draw_text(
            pahala_text,
            dialog_x + 100, summary_y - 60,
            (255, 255, 255, 255),
            font_size=16, anchor_x="left", anchor_y="center", bold=True
        )
        arcade.draw_text(
            pahala_value,
            dialog_x + dialog_w - 100, summary_y - 60,
            (150, 255, 200, 255),
            font_size=20, anchor_x="right", anchor_y="center", bold=True
        )

        # Total nyawa
        lives_text = f"❤️ Nyawa Tersisa"
        lives_value = f"{max(0, self.lives)}"

        arcade.draw_text(
            lives_text,
            dialog_x + 100, summary_y - 120,
            (255, 255, 255, 255),
            font_size=16, anchor_x="left", anchor_y="center", bold=True
        )
        arcade.draw_text(
            lives_value,
            dialog_x + dialog_w - 100, summary_y - 120,
            (255, 150, 150, 255),
            font_size=20, anchor_x="right", anchor_y="center", bold=True
        )

        # Divider line
        arcade.draw_line(
            dialog_x + 50, dialog_y + 100,
            dialog_x + dialog_w - 50, dialog_y + 100,
            (200, 150, 80, 255), 2
        )

        # Buttons
        # Restart button
        restart_btn_w = 200
        restart_btn_h = 50
        restart_btn_x = SCREEN_WIDTH // 2 - restart_btn_w // 2 - 120
        restart_btn_y = dialog_y + 20

        is_restart_hover = self._in_game_over_restart(self._last_mouse[0], self._last_mouse[1])
        restart_color = (80, 230, 130, 255) if is_restart_hover else (50, 200, 100, 255)

        arcade.draw_lbwh_rectangle_filled(restart_btn_x, restart_btn_y, restart_btn_w, restart_btn_h, restart_color)
        arcade.draw_lbwh_rectangle_outline(restart_btn_x, restart_btn_y, restart_btn_w, restart_btn_h, (255, 255, 255, 255), 2)
        arcade.draw_text(
            "🔄 ULANG",
            restart_btn_x + restart_btn_w // 2, restart_btn_y + restart_btn_h // 2,
            (255, 255, 255, 255),
            font_size=14, anchor_x="center", anchor_y="center", bold=True
        )

        # Menu button
        menu_btn_w = 200
        menu_btn_h = 50
        menu_btn_x = SCREEN_WIDTH // 2 + 120 - menu_btn_w // 2
        menu_btn_y = dialog_y + 20

        is_menu_hover = self._in_game_over_menu(self._last_mouse[0], self._last_mouse[1])
        menu_color = (200, 100, 100, 255) if is_menu_hover else (170, 80, 80, 255)

        arcade.draw_lbwh_rectangle_filled(menu_btn_x, menu_btn_y, menu_btn_w, menu_btn_h, menu_color)
        arcade.draw_lbwh_rectangle_outline(menu_btn_x, menu_btn_y, menu_btn_w, menu_btn_h, (255, 255, 255, 255), 2)
        arcade.draw_text(
            "🏠 MENU",
            menu_btn_x + menu_btn_w // 2, menu_btn_y + menu_btn_h // 2,
            (255, 255, 255, 255),
            font_size=14, anchor_x="center", anchor_y="center", bold=True
        )

        # Instructions
        arcade.draw_text(
            "Tekan SPASI untuk main lagi",
            SCREEN_WIDTH // 2, 50,
            (160, 140, 100, 200),
            font_size=12, anchor_x="center", anchor_y="center"
        )

    def _get_performance_rating(self) -> str:
        """Hitung rating performa player berdasarkan uang saja."""
        if self.money > 100000:
            return "⭐⭐⭐ SEMPURNA! Kamu master penjual bakso!"
        elif self.money > 50000:
            return "⭐⭐ BAGUS! Bisnis berkembang pesat!"
        elif self.money > 0:
            return "⭐ CUKUP. Terus berjuang!"
        elif self.money == 0:
            return "😌 BREAK EVEN. Mulai dari nol lagi!"
        else:
            return "😭 RUGI! Coba lagi dengan strategi lebih baik."

    # ─── Hit-tests ───────────────────────────────────────────────────────────
    def _in_sajikan(self, x, y):
        hw, hh = self._sajikan_w / 2, self._sajikan_h / 2
        cx, cy = self._sajikan_cx, self._sajikan_cy
        return cx - hw <= x <= cx + hw and cy - hh <= y <= cy + hh

    def _in_reset_btn(self, x, y):
        hw, hh = self._reset_btn_w / 2, self._reset_btn_h / 2
        cx, cy = self._reset_btn_cx, self._reset_btn_cy
        return cx - hw <= x <= cx + hw and cy - hh <= y <= cy + hh

    def _in_pause_button(self, x, y):
        cx, cy = self._pause_btn_x, self._pause_btn_y
        w, h = self._pause_btn_w, self._pause_btn_h
        return cx - w // 2 <= x <= cx + w // 2 and cy - h // 2 <= y <= cy + h // 2

    def _in_resume_button(self, x, y):
        btn_w, btn_h = 200, 50
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        btn_y = SCREEN_HEIGHT // 2 - btn_h // 2
        return btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h

    def _in_quit_button(self, x, y):
        quit_btn_w, quit_btn_h = 200, 50
        quit_btn_x = SCREEN_WIDTH // 2 - quit_btn_w // 2
        quit_btn_y = SCREEN_HEIGHT // 2 - 100
        return quit_btn_x <= x <= quit_btn_x + quit_btn_w and quit_btn_y <= y <= quit_btn_y + quit_btn_h

    def _in_menu_play(self, x, y):
        return (SCREEN_WIDTH / 2 - 120 <= x <= SCREEN_WIDTH / 2 + 120
                and SCREEN_HEIGHT / 2 - 60 <= y <= SCREEN_HEIGHT / 2 - 2)

    def _in_game_over_restart(self, x, y):
        restart_btn_w = 200
        restart_btn_h = 50
        restart_btn_x = SCREEN_WIDTH // 2 - restart_btn_w // 2 - 120
        restart_btn_y = 20
        return restart_btn_x <= x <= restart_btn_x + restart_btn_w and restart_btn_y <= y <= restart_btn_y + restart_btn_h

    def _in_game_over_menu(self, x, y):
        menu_btn_w = 200
        menu_btn_h = 50
        menu_btn_x = SCREEN_WIDTH // 2 + 120 - menu_btn_w // 2
        menu_btn_y = 20
        return menu_btn_x <= x <= menu_btn_x + menu_btn_w and menu_btn_y <= y <= menu_btn_y + menu_btn_h

    def _in_store_btn(self, x, y):
        return (self._store_btn_x - self._store_btn_w / 2 <= x <= self._store_btn_x + self._store_btn_w / 2
                and self._store_btn_y - self._store_btn_h / 2 <= y <= self._store_btn_y + self._store_btn_h / 2)

    def _in_queue_button(self, x, y, idx: int) -> bool:
        """Cek apakah click di tombol antrian pembeli."""
        if idx >= len(self._customer_buttons):
            return False
        btn_x, btn_y, btn_w, btn_h = self._customer_buttons[idx]
        return btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h


