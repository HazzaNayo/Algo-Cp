"""
Konfigurasi untuk Game Penjual Bakso - Cooking Fever Style
"""

# ─── Screen ──────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Game Penjual Bakso"
FPS = 60

# ─── Colors ──────────────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
RED         = (255, 0,   0)
GREEN       = (0,   200, 80)
BLUE        = (0,   0,   255)
YELLOW      = (255, 220, 0)
ORANGE      = (255, 140, 0)
DARK_GREEN  = (20,  160, 60)
DARK_ORANGE = (200, 100, 0)
GRAY        = (80,  80,  80)
LIGHT_GRAY  = (200, 200, 200)
BROWN       = (139, 90,  43)
CREAM       = (255, 248, 220)

# ─── Asset Paths ─────────────────────────────────────────────────────────────
ASSETS_PATH     = "assets"
IMAGES_PATH     = f"{ASSETS_PATH}/images"
SOUNDS_PATH     = f"{ASSETS_PATH}/sounds"
FONTS_PATH      = f"{ASSETS_PATH}/fonts"
CHARACTERS_PATH = f"{IMAGES_PATH}/characters"
ITEMS_PATH      = f"{IMAGES_PATH}/items"
BACKGROUNDS_PATH= f"{IMAGES_PATH}/backgrounds"
UI_PATH         = f"{IMAGES_PATH}/ui"

# ─── Game Mechanics ──────────────────────────────────────────────────────────
BAKSO_PRICE          = 15_000     # Harga bakso (Rp)
TIP_AMOUNT           = 5_000      # Bonus tip saat bar > 70%
GAME_DURATION        = 180.0      # Durasi ronde (detik) = 3 menit
MAX_LIVES            = 3          # Nyawa awal
MAX_QUEUE            = 1          # Maks pembeli di antrian (1 = satu per satu)

# ─── Spawn ───────────────────────────────────────────────────────────────────
SPAWN_INTERVAL       = 6.0        # Jeda antar pembeli baru (detik)
POOR_CUSTOMER_CHANCE = 0.30       # 30% kemungkinan pembeli fakir

# ─── Customer ────────────────────────────────────────────────────────────────
PATIENCE_DURATION    = 30.0       # Bar kesabaran habis dalam X detik
TIP_PATIENCE_THRESH  = 0.70       # Di atas % ini → dapat tip
CUSTOMER_SPEED       = 180        # Pixel per detik (gerak menuju gerobak)
CUSTOMER_WAIT_X      = 500        # X posisi tunggu di depan gerobak
CUSTOMER_WAIT_Y      = 225        # Y posisi tunggu
QUEUE_SPACING        = 160        # Jarak antar pembeli dalam antrian
PEMBELI_SCALE        = 0.65
PEMBELI_POS_X        = 350
PEMBELI_POS_Y        = 120

# ─── Cooking Stations ────────────────────────────────────────────────────────
# Panci Bakso
BAKSO_STATION_X      = 336
BAKSO_STATION_Y      = 240
COOK_TIME            = 3.0        # Detik untuk memasak bakso

# Mie
MIE_STATION_X        = 983
MIE_STATION_Y        = 371
MIE_TIME             = 2.0        # Detik untuk menambah mie

# Sayuran
SAYURAN_STATION_X    = 1025
SAYURAN_STATION_Y    = 216
SAYURAN_TIME         = 1.5        # Detik untuk menambah sayuran

# ─── Mangkok ─────────────────────────────────────────────────────────────────
MANGKOK_SCALE        = 0.20
MANGKOK_POS_X        = 250
MANGKOK_POS_Y        = 77

# Bowl display (layer terpisah — di-overlay satu per satu)
BOWL_DISPLAY_X       = 730
BOWL_DISPLAY_Y       = 100
BOWL_DISPLAY_SCALE   = 0.25
# Bowl display — gambar mangkok berubah sesuai bahan yang sudah ditambahkan
BOWL_STAGES = {
    frozenset():                          f"{ITEMS_PATH}/Mangkok.jpeg",
    frozenset({"bakso"}):                  f"{ITEMS_PATH}/Mangkok_bakso.jpeg",
    frozenset({"bakso", "mie"}):           f"{ITEMS_PATH}/Mangkok_baksomie.jpeg",
    frozenset({"bakso", "mie", "sayuran"}): f"{ITEMS_PATH}/Mangkok_lengkap.jpeg",
}

# Order images — gambar pesanan yang ditampilkan di cloud bubble pembeli
ORDER_IMAGES = {
    "bakso":    f"{ITEMS_PATH}/Mangkok_bakso.jpeg",
    "baksomie": f"{ITEMS_PATH}/Mangkok_baksomie.jpeg",
    "lengkap":  f"{ITEMS_PATH}/Mangkok_lengkap.jpeg",
}

# Order types dan bahan yang dibutuhkan
ORDER_RECIPES = {
    "bakso":    {"bakso"},
    "baksomie": {"bakso", "mie"},
    "lengkap":  {"bakso", "mie", "sayuran"},
}

# Order bubble config (cloud dialog di atas pembeli)
ORDER_BUBBLE_OFFSET_Y = 130       # Jarak Y di atas pembeli
ORDER_BUBBLE_SCALE    = 0.12      # Skala gambar pesanan di bubble
ORDER_BUBBLE_RADIUS   = 55        # Radius bubble cloud

# ─── Combo ───────────────────────────────────────────────────────────────────
COMBO_THRESHOLD      = 3          # Berapa pelayanan beruntun untuk combo
COMBO_MULTIPLIER     = 2          # Uang x2 saat combo aktif


HUD_FONT_SIZE   = 20
HUD_PADDING     = 16
HUD_HEIGHT      = 56

# ─── UI Dialog ───────────────────────────────────────────────────────────────
DIALOG_WIDTH    = 420
DIALOG_HEIGHT   = 220
DIALOG_CENTER_X = SCREEN_WIDTH  // 2
DIALOG_CENTER_Y = SCREEN_HEIGHT // 2

# ─── Buttons (legacy, kept for compatibility) ─────────────────────────────────
BUTTON1_WIDTH    = 270
BUTTON1_HEIGHT   = 180
BUTTON2_WIDTH    = 270
BUTTON2_HEIGHT   = 80
BUTTON1_CENTER_X = 975
BUTTON1_CENTER_Y = 360
BUTTON2_CENTER_X = 975
BUTTON2_CENTER_Y = 210
