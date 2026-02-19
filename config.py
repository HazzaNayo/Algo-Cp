"""
Konfigurasi untuk Game Penjual Bakso
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Game Penjual Bakso"

# Game settings
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Asset paths
ASSETS_PATH = "assets"
IMAGES_PATH = f"{ASSETS_PATH}/images"
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"
FONTS_PATH = f"{ASSETS_PATH}/fonts"

# Character paths
CHARACTERS_PATH = f"{IMAGES_PATH}/characters"
ITEMS_PATH = f"{IMAGES_PATH}/items"
BACKGROUNDS_PATH = f"{IMAGES_PATH}/backgrounds"
UI_PATH = f"{IMAGES_PATH}/ui"

# Customer Settings
PEMBELI_SCALE = 1.0
PEMBELI_POS_X = 350
PEMBELI_POS_Y = 120

# Button defaults (center-based coordinates)
# Per-button sizes so each button can have different dimensions
BUTTON1_WIDTH = 270
BUTTON1_HEIGHT = 180
BUTTON2_WIDTH = 270
BUTTON2_HEIGHT = 80
# Button 1 center position (change these to move the buttons)
BUTTON1_CENTER_X = 975  # default: near center horizontally
BUTTON1_CENTER_Y = 360  # default: near bottom area
# Button 2 center position
# Button 2 center position
BUTTON2_CENTER_X = 975
BUTTON2_CENTER_Y = 210

# Mangkok Settings
MANGKOK_SCALE = 0.2
MANGKOK_POS_X = 250  # Center of screen default
MANGKOK_POS_Y = 77
