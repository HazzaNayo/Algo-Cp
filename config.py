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
MAX_QUEUE            = 3          # Maks pembeli di antrian

# ─── Spawn ───────────────────────────────────────────────────────────────────
SPAWN_INTERVAL       = 6.0        # Jeda antar pembeli baru (detik)
POOR_CUSTOMER_CHANCE = 0.30       # 30% kemungkinan pembeli fakir

# ─── Customer ────────────────────────────────────────────────────────────────
PATIENCE_DURATION    = 30.0       # Bar kesabaran habis dalam X detik
TIP_PATIENCE_THRESH  = 0.70       # Di atas % ini → dapat tip
CUSTOMER_SPEED       = 180        # Pixel per detik (gerak menuju gerobak)
CUSTOMER_WAIT_X      = 820        # X posisi tunggu di depan gerobak
CUSTOMER_WAIT_Y      = 175        # Y posisi tunggu
QUEUE_SPACING        = 160        # Jarak antar pembeli dalam antrian
PEMBELI_SCALE        = 0.95
PEMBELI_POS_X        = 350
PEMBELI_POS_Y        = 120

# ─── Cooking Stations ────────────────────────────────────────────────────────
# Panci Bakso
BAKSO_STATION_X      = 310
BAKSO_STATION_Y      = 205
COOK_TIME            = 3.0        # Detik untuk memasak bakso

# Ketel Kuah
KUAH_STATION_X       = 490
KUAH_STATION_Y       = 205
KUAH_TIME            = 2.0        # Detik untuk nuang kuah

# ─── Mangkok ─────────────────────────────────────────────────────────────────
MANGKOK_SCALE        = 0.20
MANGKOK_POS_X        = 250
MANGKOK_POS_Y        = 77

# ─── Combo ───────────────────────────────────────────────────────────────────
COMBO_THRESHOLD      = 3          # Berapa pelayanan beruntun untuk combo
COMBO_MULTIPLIER     = 2          # Uang x2 saat combo aktif

# ─── Upgrades ────────────────────────────────────────────────────────────────
UPGRADES = {
    "kuah_turbo":  {"name": "Kuah Turbo",    "price": 50_000,  "desc": "Kuah 2s → 1s"},
    "wajan_ajaib": {"name": "Wajan Ajaib",   "price": 80_000,  "desc": "Masak 3s → 1.5s"},
    "gerobak_cute":{"name": "Gerobak Cute",  "price": 120_000, "desc": "Kesabaran +20%"},
}

# ─── HUD ─────────────────────────────────────────────────────────────────────
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
