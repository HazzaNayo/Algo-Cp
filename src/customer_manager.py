"""
customer_manager.py - Mengelola antrian & spawn pembeli
"""

import arcade
import random
from config import (
    BAKSO_PRICE, MIE_PRICE, SAYURAN_PRICE, TIP_AMOUNT, TIP_PATIENCE_THRESH,
    SPAWN_INTERVAL, MAX_QUEUE, COMBO_THRESHOLD, COMBO_MULTIPLIER,
)
from src.models.customer import Customer, CustomerState, create_customer


class CustomerManager:
    """
    Mengelola siklus hidup semua pembeli:
    spawn periodik → antrian → dilayani → pergi
    """

    def __init__(self):
        self.customers: list[Customer] = []
        # SpriteList khusus untuk draw — Arcade 3.x tidak support Sprite.draw() langsung
        self.sprite_list = arcade.SpriteList()

        self.spawn_timer    = 0.0
        self.spawn_interval = SPAWN_INTERVAL

        # Combo
        self.combo_count  = 0      # Berapa pelayanan beruntun sukses
        self.active_combo = False  # Combo sedang aktif?

        # Callbacks — diset oleh BaksoGame
        self.on_served_normal  = None   # fn(uang_dapat, pahala, got_tip)
        self.on_served_poor    = None   # fn(customer) → tampilkan dialog
        self.on_customer_angry = None   # fn() → kurangi nyawa

    # ─── Update ──────────────────────────────────────────────────────────────
    def update(self, delta_time: float):
        """Panggil setiap frame."""
        self._try_spawn(delta_time)

        to_remove = []
        for customer in self.customers:
            event = customer.update_customer(delta_time)

            if event == "arrived":
                if customer.queue_slot == 0:
                    customer.state = CustomerState.WAITING

            elif event == "angry":
                self.combo_count  = 0
                self.active_combo = False
                if self.on_customer_angry:
                    self.on_customer_angry()
                customer.finish_leave(happy=False)

            elif event == "gone":
                to_remove.append(customer)

        for c in to_remove:
            slot = c.queue_slot
            self.customers.remove(c)
            if c in self.sprite_list:
                self.sprite_list.remove(c)
            # Majukan semua pembeli di belakang
            for other in self.customers:
                if other.queue_slot > slot:
                    other.advance_queue()

    # ─── Spawn ───────────────────────────────────────────────────────────────
    def _try_spawn(self, delta_time: float):
        self.spawn_timer += delta_time
        # Hanya spawn pembeli baru jika tidak ada pembeli aktif sama sekali
        has_active = any(
            c.state in (CustomerState.WALKING, CustomerState.WAITING,
                        CustomerState.SERVED, CustomerState.HAPPY,
                        CustomerState.ANGRY, CustomerState.LEAVING)
            for c in self.customers
        )
        if self.spawn_timer >= self.spawn_interval and not has_active:
            self.spawn_timer = 0.0
            customer = create_customer(0)  # Selalu slot 0 (hanya 1 pembeli)
            self.customers.append(customer)
            self.sprite_list.append(customer)

    # ─── Serving ─────────────────────────────────────────────────────────────
    def get_front_customer(self) -> Customer | None:
        """Kembalikan pembeli paling depan yang sedang menunggu."""
        for c in self.customers:
            if c.queue_slot == 0 and c.state == CustomerState.WAITING:
                return c
        return None

    def serve_front(self):
        """
        Dipanggil oleh game saat player meng-klik 'sajikan'.
        Cek jenis pembeli dan panggil callback yang sesuai.
        """
        customer = self.get_front_customer()
        if customer is None:
            return

        customer.mark_served()

        if customer.is_poor:
            if self.on_served_poor:
                self.on_served_poor(customer)
        else:
            self._complete_serve(customer, paid=True)

    def resolve_poor(self, customer: Customer, give_free: bool):
        """Dipanggil setelah player memilih di dialog fakir."""
        self._complete_serve(customer, paid=not give_free, is_poor=True, free=give_free)

    def _complete_serve(self, customer: Customer,
                        paid: bool, is_poor: bool = False, free: bool = False):
        money = 0
        if paid:
            multiplier = COMBO_MULTIPLIER if self.active_combo else 1
            money = BAKSO_PRICE * multiplier
            if customer.gets_tip:
                money += TIP_AMOUNT

        if paid:
            self.combo_count += 1
            self.active_combo = self.combo_count >= COMBO_THRESHOLD

        pahala = 1 if (is_poor and free) else 0

        if self.on_served_normal:
            self.on_served_normal(money, pahala, customer.gets_tip and paid)

        customer.finish_leave(happy=True)

    def serve_customer(self, idx: int):
        """Serve customer di index tertentu (untuk rush hour)."""
        if 0 <= idx < len(self.customers):
            customer = self.customers[idx]
            # Proses serve customer
            money, pahala, got_tip = self._calculate_reward(customer)
            if customer.is_poor:
                self.on_served_poor(customer)
            else:
                self.on_served_normal(money, pahala, got_tip)
            # Remove customer dari antrian
            self.customers.pop(idx)
            self.combo_count += 1

    def _calculate_reward(self, customer: Customer) -> tuple[int, int, bool]:
        """
        Hitung reward berdasarkan ingredients & quantity.
        Return: (money, pahala, got_tip)
        """
        # Base price per mangkok
        price_per_bowl = 0
        
        if customer.order_type == "bakso":
            price_per_bowl = BAKSO_PRICE
        elif customer.order_type == "baksomie":
            price_per_bowl = BAKSO_PRICE + MIE_PRICE
        elif customer.order_type == "lengkap":
            price_per_bowl = BAKSO_PRICE + MIE_PRICE + SAYURAN_PRICE
        
        # Total money = price per bowl × quantity
        money = price_per_bowl * customer.order_quantity

        # Pahala berdasarkan kesabaran
        pahala = 0
        got_tip = False
        
        if customer.patience_percent >= TIP_PATIENCE_THRESH:
            # Bonus: dapat tip
            money += TIP_AMOUNT * customer.order_quantity
            got_tip = True
        
        # Pahala bonus jika customer puas
        if customer.patience_percent > 0.5:
            pahala = customer.order_quantity  # 1-3 pahala sesuai jumlah pesanan

        return money, pahala, got_tip

    # ─── Drawing ─────────────────────────────────────────────────────────────
    def draw(self):
        # Gambar semua sprite sekaligus via SpriteList (Arcade 3.x compatible)
        self.sprite_list.draw()
        # Gambar overlay per-customer (bar + label) secara individual
        for customer in self.customers:
            customer.draw_patience_bar()
            customer.draw_label()
