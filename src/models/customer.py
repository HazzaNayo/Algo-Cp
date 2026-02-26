"""
customer.py - Model untuk Pembeli Biasa dan Pembeli Fakir
"""

import arcade
import os
import random
from config import (
    PATIENCE_DURATION, CUSTOMER_SPEED, CUSTOMER_WAIT_X, CUSTOMER_WAIT_Y,
    QUEUE_SPACING, POOR_CUSTOMER_CHANCE, PEMBELI_SCALE, CHARACTERS_PATH,
    SCREEN_WIDTH, TIP_PATIENCE_THRESH
)


# ─── Customer States ──────────────────────────────────────────────────────────
class CustomerState:
    WALKING   = "walking"    # Berjalan menuju gerobak
    WAITING   = "waiting"    # Menunggu dilayani
    SERVED    = "served"     # Sedang dilayani (proses masak)
    HAPPY     = "happy"      # Sudah dapat bakso, berterima kasih
    LEAVING   = "leaving"    # Berjalan pergi dari layar
    ANGRY     = "angry"      # Kehabisan sabar, pergi kecewa


class Customer(arcade.Sprite):
    """Base class untuk semua pembeli."""

    def __init__(self, image_path: str, scale: float, queue_slot: int):
        super().__init__(image_path, scale)

        self.queue_slot    = queue_slot          # Slot antrian (0, 1, 2)
        self.state         = CustomerState.WALKING
        self.patience      = PATIENCE_DURATION   # Timer kesabaran
        self.max_patience  = PATIENCE_DURATION
        self.is_poor       = False               # Override di subclass

        # Target posisi tunggu berdasarkan slot
        self.target_x = CUSTOMER_WAIT_X - (queue_slot * QUEUE_SPACING)
        self.target_y = CUSTOMER_WAIT_Y

        # Spawn dari luar layar (kanan)
        self.center_x = SCREEN_WIDTH + 80
        self.center_y = CUSTOMER_WAIT_Y

        # Efek state visual
        self.flash_timer   = 0.0
        self.emotion_timer = 0.0   # Timer untuk tampilkan emoji

    # ─── Properties ──────────────────────────────────────────────────────────
    @property
    def patience_ratio(self) -> float:
        """Rasio kesabaran sisa (0.0 – 1.0)."""
        return max(0.0, self.patience / self.max_patience)

    @property
    def gets_tip(self) -> bool:
        """True jika masih layak dapat tip saat disajikan."""
        return self.patience_ratio >= TIP_PATIENCE_THRESH

    # ─── Update ──────────────────────────────────────────────────────────────
    def update_customer(self, delta_time: float) -> str | None:
        """
        Panggil tiap frame dari game loop.
        Return event string atau None:
          'arrived'  – pembeli sampai di posisi tunggu
          'angry'    – sabar habis, pembeli pergi kecewa
          'gone'     – pembeli sudah keluar dari layar
        """
        event = None

        if self.state == CustomerState.WALKING:
            event = self._update_walking(delta_time)

        elif self.state == CustomerState.WAITING:
            event = self._update_waiting(delta_time)

        elif self.state in (CustomerState.HAPPY, CustomerState.ANGRY, CustomerState.LEAVING):
            event = self._update_leaving(delta_time)

        self.flash_timer = max(0.0, self.flash_timer - delta_time)
        return event

    def _update_walking(self, dt: float) -> str | None:
        dx = self.target_x - self.center_x
        speed = CUSTOMER_SPEED * dt
        if abs(dx) <= speed:
            self.center_x = self.target_x
            self.center_y = self.target_y
            self.state = CustomerState.WAITING
            return "arrived"
        self.center_x += speed if dx > 0 else -speed
        return None

    def _update_waiting(self, dt: float) -> str | None:
        if self.queue_slot == 0:
            # Hanya pembeli di slot 0 (paling depan) yang sabarnya berkurang
            self.patience -= dt
            if self.patience <= 0:
                self.patience = 0
                self.state = CustomerState.ANGRY
                self.flash_timer = 1.5
                return "angry"
        return None

    def _update_leaving(self, dt: float) -> str | None:
        self.center_x -= CUSTOMER_SPEED * dt
        if self.center_x < -120:
            return "gone"
        return None

    # ─── Actions ─────────────────────────────────────────────────────────────
    def mark_served(self):
        """Dipanggil saat bakso disajikan."""
        self.state = CustomerState.SERVED

    def finish_leave(self, happy: bool = True):
        """Pembeli mulai berjalan pergi."""
        self.state = CustomerState.HAPPY if happy else CustomerState.LEAVING

    def advance_queue(self):
        """Pembeli maju satu slot ke depan antrian."""
        self.queue_slot = max(0, self.queue_slot - 1)
        self.target_x = CUSTOMER_WAIT_X - (self.queue_slot * QUEUE_SPACING)

    # ─── Drawing Extras ───────────────────────────────────────────────────────
    def draw_patience_bar(self):
        """Gambar bar kesabaran di atas sprite."""
        if self.state not in (CustomerState.WAITING, CustomerState.SERVED):
            return

        bar_w  = 70
        bar_h  = 8
        bx     = self.center_x - bar_w / 2
        by     = self.center_y + 80

        # Background
        arcade.draw_lbwh_rectangle_filled(bx, by, bar_w, bar_h, (60, 60, 60, 200))

        # Fill
        ratio  = self.patience_ratio
        fill_w = bar_w * ratio
        if ratio > 0.5:
            color = (50, 200, 80, 230)
        elif ratio > 0.25:
            color = (255, 180, 0, 230)
        else:
            color = (220, 40, 40, 230)

        if fill_w > 0:
            arcade.draw_lbwh_rectangle_filled(bx, by, fill_w, bar_h, color)

        # Border
        arcade.draw_lbwh_rectangle_outline(bx, by, bar_w, bar_h, (255, 255, 255, 150), 1)

    def draw_label(self):
        """Gambar label jenis pembeli."""
        pass  # Override di subclass jika perlu


# ─── Normal Customer ─────────────────────────────────────────────────────────
class NormalCustomer(Customer):
    """Pembeli biasa — bayar harga normal."""

    def __init__(self, queue_slot: int):
        path = f"{CHARACTERS_PATH}/Pembeli/Pembeli_Normal1.png"
        super().__init__(path, PEMBELI_SCALE, queue_slot)
        self.is_poor = False


# ─── Poor Customer ───────────────────────────────────────────────────────────
class PoorCustomer(Customer):
    """Pembeli fakir — memicu dialog pilihan Gratis / Bayar."""

    _SPRITES = ["Pembeli_fakir1.png"]  # Tambah file lain jika ada

    def __init__(self, queue_slot: int):
        sprite_name = random.choice(self._SPRITES)
        path = f"{CHARACTERS_PATH}/Pembeli/{sprite_name}"
        super().__init__(path, PEMBELI_SCALE, queue_slot)
        self.is_poor = True

    def draw_label(self):
        """Tampilkan ikon di atas kepala pembeli fakir."""
        if self.state == CustomerState.WAITING:
            arcade.draw_text(
                "😔",
                self.center_x, self.center_y + 96,
                (255, 220, 0, 220), font_size=16,
                anchor_x="center", anchor_y="center"
            )


# ─── Factory ─────────────────────────────────────────────────────────────────
def create_customer(queue_slot: int) -> Customer:
    """Buat pembeli acak (biasa atau fakir)."""
    if random.random() < POOR_CUSTOMER_CHANCE:
        return PoorCustomer(queue_slot)
    return NormalCustomer(queue_slot)
