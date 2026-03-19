"""
cooking_station.py - Stasiun memasak (panci bakso, mie, sayuran, mangkok)
                   + BowlDisplay (gambar mangkok yang berubah sesuai step)
"""

import arcade
from config import (
    COOK_TIME, MIE_TIME, SAYURAN_TIME,
    BAKSO_STATION_X, BAKSO_STATION_Y,
    MIE_STATION_X, MIE_STATION_Y,
    SAYURAN_STATION_X, SAYURAN_STATION_Y,
    MANGKOK_POS_X, MANGKOK_POS_Y, MANGKOK_SCALE,
    BOWL_DISPLAY_X, BOWL_DISPLAY_Y, BOWL_DISPLAY_SCALE,
    BOWL_STAGES, ITEMS_PATH, ORDER_RECIPES
)


class CookingStation:
    """Base class untuk semua stasiun masak."""

    def __init__(self, x: float, y: float, cook_time: float, label: str):
        self.x          = x
        self.y          = y
        self.cook_time  = cook_time
        self.label      = label

        self.timer      = 0.0
        self.is_cooking = False
        self.is_ready   = False
        self.is_done    = False

        self.click_radius = 55
        self.hovered    = False

    def update(self, delta_time: float) -> bool:
        if self.is_cooking and not self.is_ready:
            self.timer += delta_time
            if self.timer >= self.cook_time:
                self.timer      = self.cook_time
                self.is_cooking = False
                self.is_ready   = True
                return True
        return False

    def start_cooking(self):
        if not self.is_cooking and not self.is_ready:
            self.is_cooking = True
            self.timer      = 0.0

    def take(self):
        if self.is_ready:
            self.is_ready = False
            self.is_done  = True
            return True
        return False

    def reset(self):
        self.timer      = 0.0
        self.is_cooking = False
        self.is_ready   = False
        self.is_done    = False

    @property
    def progress(self) -> float:
        if self.cook_time == 0:
            return 1.0
        return min(1.0, self.timer / self.cook_time)

    @property
    def can_click(self) -> bool:
        return not self.is_cooking and not self.is_done

    def contains(self, mx: float, my: float) -> bool:
        dx = mx - self.x
        dy = my - self.y
        return (dx * dx + dy * dy) <= self.click_radius ** 2

    def draw(self):
        # Hotspot marker (bukan tombol bulat besar)
        accent = (180, 150, 110, 230)
        status = "KLIK"
        if self.is_ready:
            accent = (80, 230, 130, 240)
            status = "SIAP"
        elif self.is_cooking:
            accent = (255, 185, 80, 240)
            status = "MASAK..."
        elif self.hovered:
            accent = (235, 195, 130, 240)

        # Titik hotspot
        arcade.draw_circle_filled(self.x, self.y, 6, accent)
        if self.hovered or self.is_cooking or self.is_ready:
            arcade.draw_circle_outline(self.x, self.y, 16, accent, 2)

        # Tag label di atas hotspot
        chip_w = max(96, len(self.label) * 8 + 26)
        chip_h = 24
        chip_x = self.x - chip_w / 2
        chip_y = self.y + 18
        arcade.draw_lbwh_rectangle_filled(chip_x, chip_y, chip_w, chip_h, (26, 18, 10, 220))
        arcade.draw_lbwh_rectangle_outline(chip_x, chip_y, chip_w, chip_h, accent, 2)
        arcade.draw_text(
            self.label, self.x, chip_y + chip_h / 2,
            (245, 235, 215, 255), font_size=12,
            anchor_x="center", anchor_y="center", bold=True
        )

        # Status kecil di bawah hotspot
        arcade.draw_text(
            status, self.x, self.y - 14,
            accent, font_size=10,
            anchor_x="center", anchor_y="center", bold=True
        )

        if self.is_cooking:
            bw = max(100, chip_w)
            bx = self.x - bw / 2
            by = chip_y + chip_h + 5
            arcade.draw_lbwh_rectangle_filled(bx, by, bw, 6, (50, 45, 40, 220))
            arcade.draw_lbwh_rectangle_filled(bx, by, bw * self.progress, 6, (255, 190, 70, 235))
            arcade.draw_lbwh_rectangle_outline(bx, by, bw, 6, (255, 255, 255, 110), 1)

    def update_hover(self, mx: float, my: float):
        self.hovered = self.contains(mx, my)


# ─── Concrete Stations ────────────────────────────────────────────────────────
class BaksoStation(CookingStation):
    """Panci bakso — step 1."""
    def __init__(self, cook_time_override: float | None = None):
        t = cook_time_override if cook_time_override is not None else COOK_TIME
        super().__init__(BAKSO_STATION_X, BAKSO_STATION_Y, t, "🍢 Bakso")
        self.click_radius = 72


class MieStation(CookingStation):
    """Mie — step 2."""
    def __init__(self, mie_time_override: float | None = None):
        t = mie_time_override if mie_time_override is not None else MIE_TIME
        super().__init__(MIE_STATION_X, MIE_STATION_Y, t, "🍜 Mie")
        self.click_radius = 72

class SayuranStation(CookingStation):
    """Sayuran — step 3."""
    def __init__(self, sayuran_time_override: float | None = None):
        t = sayuran_time_override if sayuran_time_override is not None else SAYURAN_TIME
        super().__init__(SAYURAN_STATION_X, SAYURAN_STATION_Y, t, "🥬 Sayur")


class MangkokStation(CookingStation):
    """Mangkok button dengan sprite mangkok kosong."""
    def __init__(self):
        super().__init__(MANGKOK_POS_X, MANGKOK_POS_Y, 0.0, "Mangkok")
        self.click_radius = 40
        self._sprite = None
        self._sprite_list = arcade.SpriteList()
        try:
            self._sprite = arcade.Sprite(f"{ITEMS_PATH}/Mangkok.jpeg", MANGKOK_SCALE)
            self._sprite.center_x = self.x
            self._sprite.center_y = self.y
            self._sprite_list.append(self._sprite)
        except Exception as e:
            print(f"[WARN] Could not load mangkok sprite: {e}")

    def start_cooking(self):
        self.is_ready = True

    def draw(self):
        accent = (210, 165, 90, 230)
        status = "AMBIL"
        if self.is_ready:
            accent = (80, 230, 130, 240)
            status = "SIAP"
        elif self.hovered:
            accent = (240, 195, 120, 240)

        if self._sprite is not None:
            self._sprite_list.draw()
            if self.hovered or self.is_ready:
                arcade.draw_ellipse_outline(
                    self.x, self.y, self.click_radius * 2.4, self.click_radius * 2.0, accent, 2
                )
        else:
            arcade.draw_text(
                self.label, self.x, self.y,
                (255, 255, 255, 230), font_size=14,
                anchor_x="center", anchor_y="center", bold=True
            )

        arcade.draw_text(
            status, self.x, self.y - self.click_radius - 8,
            accent, font_size=11,
            anchor_x="center", anchor_y="center", bold=True
        )
# ─── Bowl Display (Combined Images) ─────────────────────────────────────────
class BowlDisplay:
    """
    Menampilkan mangkok dengan gambar gabungan yang berubah
    sesuai bahan yang sudah ditambahkan.
    Menggunakan gambar: Mangkok.jpeg, Mangkok_bakso.jpeg,
    Mangkok_baksomie.jpeg, Mangkok_lengkap.jpeg
    """

    def __init__(self):
        self.x     = BOWL_DISPLAY_X
        self.y     = BOWL_DISPLAY_Y
        self.scale = BOWL_DISPLAY_SCALE
        self.ingredients: set[str] = set()
        self.has_mangkok = False

        # Pre-load semua stage images
        self._stage_sprites: dict[frozenset, arcade.Sprite] = {}
        self._sprite_list = arcade.SpriteList()
        for ingredient_set, path in BOWL_STAGES.items():
            try:
                s = arcade.Sprite(path, self.scale)
                s.center_x = self.x
                s.center_y = self.y
                s.visible  = False
                self._stage_sprites[ingredient_set] = s
                self._sprite_list.append(s)
            except Exception as e:
                print(f"[WARN] Could not load bowl stage '{path}': {e}")

        self._current_key = None

    def set_mangkok(self):
        """Player mengambil mangkok kosong."""
        self.has_mangkok = True
        self.ingredients.clear()
        self._update_display()

    def add_ingredient(self, name: str):
        """Tambah bahan (bakso/mie/sayuran) ke mangkok."""
        self.ingredients.add(name)
        self._update_display()

    @property
    def is_complete(self) -> bool:
        """True jika semua 3 bahan sudah masuk (legacy/fallback)."""
        return len(self.ingredients) >= 3

    def matches_order(self, order_type: str) -> bool:
        """Cek apakah bahan di mangkok cocok dengan pesanan pembeli."""
        required = ORDER_RECIPES.get(order_type)
        if not required:
            return False
        return self.has_mangkok and self.ingredients == required

    def is_ready_for_order(self, order_type: str) -> bool:
        """Cek apakah mangkok sudah siap untuk pesanan tertentu."""
        return self.has_mangkok and self.matches_order(order_type)

    def _update_display(self):
        """Update gambar mangkok berdasarkan bahan saat ini."""
        # Sembunyikan semua
        for s in self._stage_sprites.values():
            s.visible = False
        self._current_key = None

        if not self.has_mangkok:
            return

        # Cari gambar yang cocok dengan bahan saat ini
        key = frozenset(self.ingredients)
        if key in self._stage_sprites:
            self._stage_sprites[key].visible = True
            self._current_key = key
        else:
            # Fallback: tampilkan mangkok kosong
            empty_key = frozenset()
            if empty_key in self._stage_sprites:
                self._stage_sprites[empty_key].visible = True
                self._current_key = empty_key

    def reset(self):
        self.has_mangkok = False
        self.ingredients.clear()
        self._update_display()

    def set_stage(self, stage: str | None):
        """Legacy compatibility."""
        pass

    def draw(self):
        # Draw the current stage sprite
        self._sprite_list.draw()
        # Label di bawah mangkok
        if self.has_mangkok:
            parts = []
            if "bakso" in self.ingredients:
                parts.append("🍢")
            if "mie" in self.ingredients:
                parts.append("🍜")
            if "sayuran" in self.ingredients:
                parts.append("🥬")
            label = " + ".join(parts) if parts else "Kosong"
            color = (80, 255, 120, 255) if len(self.ingredients) > 0 else (255, 240, 200, 220)
            arcade.draw_text(
                label, self.x, self.y - 70,
                color, font_size=12,
                anchor_x="center", anchor_y="center", bold=True
            )

