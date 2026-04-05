"""
store.py - UI Store untuk membeli bahan pokok
"""
import arcade
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STORE_BAKSO_PRICE, STORE_MIE_PRICE, STORE_SAYUR_PRICE,
)


class Store:
    """Toko untuk membeli bahan pokok — stok unlimited."""

    def __init__(self):
        # Button states
        self.bakso_hover = False
        self.mie_hover = False
        self.sayur_hover = False
        self.back_hover = False

        # Button positions
        self.bakso_btn_x = SCREEN_WIDTH // 2 - 250
        self.bakso_btn_y = SCREEN_HEIGHT // 2 + 80
        self.bakso_btn_w = 180
        self.bakso_btn_h = 60

        self.mie_btn_x = SCREEN_WIDTH // 2
        self.mie_btn_y = SCREEN_HEIGHT // 2 + 80
        self.mie_btn_w = 180
        self.mie_btn_h = 60

        self.sayur_btn_x = SCREEN_WIDTH // 2 + 250
        self.sayur_btn_y = SCREEN_HEIGHT // 2 + 80
        self.sayur_btn_w = 180
        self.sayur_btn_h = 60

        self.back_btn_x = SCREEN_WIDTH // 2 - 100
        self.back_btn_y = SCREEN_HEIGHT // 2 - 150
        self.back_btn_w = 200
        self.back_btn_h = 50

    def update_hover(self, mx, my):
        """Update hover states."""
        self.bakso_hover = self._in_bakso_btn(mx, my)
        self.mie_hover = self._in_mie_btn(mx, my)
        self.sayur_hover = self._in_sayur_btn(mx, my)
        self.back_hover = self._in_back_btn(mx, my)

    def draw(self, money: int):
        """Draw store UI."""
        # Background
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (30, 18, 5, 255))

        # Title
        arcade.draw_text(
            "🏪 TOKO BAHAN BAKSO",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
            (255, 220, 80, 255),
            font_size=36, anchor_x="center", anchor_y="center", bold=True
        )

        # Money display
        money_color = (255, 100, 100, 255) if money < 0 else (255, 220, 80, 255)
        money_text = f"💰 Uang: Rp{abs(money):,}"
        if money < 0:
            money_text = f"💰 Uang: -Rp{abs(money):,}"
        
        arcade.draw_text(
            money_text,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 110,
            money_color,
            font_size=20, anchor_x="center", anchor_y="center", bold=True
        )

        # Bakso button
        self._draw_item_button(
            self.bakso_btn_x, self.bakso_btn_y, self.bakso_btn_w, self.bakso_btn_h,
            "🍢 BAKSO", f"Rp{STORE_BAKSO_PRICE:,}",
            self.bakso_hover, money >= STORE_BAKSO_PRICE
        )

        # Mie button
        self._draw_item_button(
            self.mie_btn_x, self.mie_btn_y, self.mie_btn_w, self.mie_btn_h,
            "🍜 MIE", f"Rp{STORE_MIE_PRICE:,}",
            self.mie_hover, money >= STORE_MIE_PRICE
        )

        # Sayur button
        self._draw_item_button(
            self.sayur_btn_x, self.sayur_btn_y, self.sayur_btn_w, self.sayur_btn_h,
            "🥬 SAYUR", f"Rp{STORE_SAYUR_PRICE:,}",
            self.sayur_hover, money >= STORE_SAYUR_PRICE
        )

        # Back button
        back_color = (100, 200, 150, 255) if self.back_hover else (80, 180, 130, 255)
        arcade.draw_lbwh_rectangle_filled(
            self.back_btn_x - self.back_btn_w // 2, self.back_btn_y - self.back_btn_h // 2,
            self.back_btn_w, self.back_btn_h, back_color
        )
        arcade.draw_lbwh_rectangle_outline(
            self.back_btn_x - self.back_btn_w // 2, self.back_btn_y - self.back_btn_h // 2,
            self.back_btn_w, self.back_btn_h, (255, 255, 255, 255), 2
        )
        arcade.draw_text(
            "← KEMBALI",
            self.back_btn_x, self.back_btn_y,
            (255, 255, 255, 255),
            font_size=16, anchor_x="center", anchor_y="center", bold=True
        )

    def _draw_item_button(self, x, y, w, h, name: str, price: str, hover: bool, can_buy: bool):
        """Draw tombol item (stok unlimited)."""
        # Determine colors
        if not can_buy:
            btn_color = (100, 50, 50, 200)
            text_color = (150, 100, 100, 200)
            outline_color = (150, 80, 80, 200)
        elif hover:
            btn_color = (180, 120, 50, 255)
            text_color = (255, 255, 255, 255)
            outline_color = (255, 200, 100, 255)
        else:
            btn_color = (150, 100, 30, 240)
            text_color = (255, 255, 255, 255)
            outline_color = (200, 150, 80, 255)

        # Draw button
        arcade.draw_lbwh_rectangle_filled(x - w // 2, y - h // 2, w, h, btn_color)
        arcade.draw_lbwh_rectangle_outline(x - w // 2, y - h // 2, w, h, outline_color, 2)

        # Name
        arcade.draw_text(
            name, x, y + 15,
            text_color, font_size=16,
            anchor_x="center", anchor_y="center", bold=True
        )

        # Price
        arcade.draw_text(
            price, x, y - 5,
            (200, 220, 100, 255) if can_buy else (100, 100, 100, 200),
            font_size=12, anchor_x="center", anchor_y="center", bold=True
        )

        # Status jika tidak bisa beli
        if not can_buy:
            arcade.draw_text(
                "UANG KURANG",
                x, y - 18,
                (255, 100, 100, 255), font_size=9,
                anchor_x="center", anchor_y="center", bold=True
            )

    def _in_bakso_btn(self, x, y) -> bool:
        return (self.bakso_btn_x - self.bakso_btn_w // 2 <= x <= self.bakso_btn_x + self.bakso_btn_w // 2
                and self.bakso_btn_y - self.bakso_btn_h // 2 <= y <= self.bakso_btn_y + self.bakso_btn_h // 2)

    def _in_mie_btn(self, x, y) -> bool:
        return (self.mie_btn_x - self.mie_btn_w // 2 <= x <= self.mie_btn_x + self.mie_btn_w // 2
                and self.mie_btn_y - self.mie_btn_h // 2 <= y <= self.mie_btn_y + self.mie_btn_h // 2)

    def _in_sayur_btn(self, x, y) -> bool:
        return (self.sayur_btn_x - self.sayur_btn_w // 2 <= x <= self.sayur_btn_x + self.sayur_btn_w // 2
                and self.sayur_btn_y - self.sayur_btn_h // 2 <= y <= self.sayur_btn_y + self.sayur_btn_h // 2)

    def _in_back_btn(self, x, y) -> bool:
        return (self.back_btn_x - self.back_btn_w // 2 <= x <= self.back_btn_x + self.back_btn_w // 2
                and self.back_btn_y - self.back_btn_h // 2 <= y <= self.back_btn_y + self.back_btn_h // 2)

    def try_buy_bakso(self, money: int) -> tuple[int, bool]:
        """Coba beli bakso. Return (uang baru, success)."""
        if money >= STORE_BAKSO_PRICE:
            return money - STORE_BAKSO_PRICE, True
        return money, False

    def try_buy_mie(self, money: int) -> tuple[int, bool]:
        """Coba beli mie. Return (uang baru, success)."""
        if money >= STORE_MIE_PRICE:
            return money - STORE_MIE_PRICE, True
        return money, False

    def try_buy_sayur(self, money: int) -> tuple[int, bool]:
        """Coba beli sayuran. Return (uang baru, success)."""
        if money >= STORE_SAYUR_PRICE:
            return money - STORE_SAYUR_PRICE, True
        return money, False