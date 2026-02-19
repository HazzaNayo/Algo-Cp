
import arcade
import os
import random
from src.ui_components import RoundButton, RectButton
from config import *


class BaksoGame(arcade.Window):
    """Main game class"""
    
    def __init__(self):
        """Initialize the game"""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        # Game state
        self.scene = None
        self.background_list = None
        self.character_list = None
        self.character_sprite = None
        self.character_sprite = None
        self.item_sprites = None
        self.mangkok_sprite = None  # Added mangkok sprite
        self.buttons = []
        
    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # Initialize SpriteLists
        self.background_list = arcade.SpriteList()
        self.item_sprites = arcade.SpriteList()

        # Load background
        try:
            self.background_sprite = arcade.Sprite(f"{BACKGROUNDS_PATH}/Background.png")
            
            # Position background at center of screen
            self.background_sprite.center_x = SCREEN_WIDTH // 2
            self.background_sprite.center_y = SCREEN_HEIGHT // 2
            
            # Calculate scale to cover the screen (1280x720)
            # Image is 1000x1000
            scale_x = SCREEN_WIDTH / self.background_sprite.width + 0.15
            scale_y = SCREEN_HEIGHT / self.background_sprite.height + 0.15
            self.background_sprite.scale = max(scale_x, scale_y)
            
            self.background_list.append(self.background_sprite)
        except Exception as e:
            print(f"Error loading background: {e}")

        # Load Gerobak
        try:
            # Load texture
            self.gerobak_sprite = arcade.Sprite(f"{ITEMS_PATH}/Gerobak.png")
            
            # Match background scale and position
            self.gerobak_sprite.scale = self.background_sprite.scale
            self.gerobak_sprite.center_x = self.background_sprite.center_x
            self.gerobak_sprite.center_y = self.background_sprite.center_y
            
            # Add to item list
            self.item_sprites.append(self.gerobak_sprite)
        except Exception as e:
            print(f"Error loading gerobak: {e}")

        # Load Mangkok (Character/Item)
        try:
            self.mangkok_sprite = arcade.Sprite(f"{ITEMS_PATH}/Mangkok.png", MANGKOK_SCALE)
            self.mangkok_sprite.center_x = MANGKOK_POS_X
            self.mangkok_sprite.center_y = MANGKOK_POS_Y
            self.item_sprites.append(self.mangkok_sprite)
        except Exception as e:
            print(f"Error loading mangkok: {e}")

        # Load Character (Pembeli)
        try:
            # Get random pembeli image
            pembeli_path = f"{CHARACTERS_PATH}/Pembeli"
            pembeli_files = [f for f in os.listdir(pembeli_path) if f.endswith('.png')]
            
            if pembeli_files:
                selected_pembeli = random.choice(pembeli_files)
                print(f"Loading random pembeli: {selected_pembeli}")
                self.character_sprite = arcade.Sprite(f"{pembeli_path}/{selected_pembeli}", PEMBELI_SCALE)
            else:
                print("No pembeli images found!")
                return

            # Position character
            self.character_sprite.center_x = PEMBELI_POS_X
            self.character_sprite.center_y = PEMBELI_POS_Y
            
            # Create character list and add sprite
            self.character_list = arcade.SpriteList()
            self.character_list.append(self.character_sprite)
            
        except Exception as e:
            print(f"Error loading character: {e}")

        # Create a sample round button - 100% transparent red (invisible), no text
        self.test_button = RoundButton(center_x=330, center_y=200, radius=80, 
                                      color=(255, 0, 0, 0), text="")
        self.buttons.append(self.test_button)
        # Create two rectangular buttons using config defaults so positions/sizes are easy to tweak
        # Transparent Green Button, no text, no border
        self.rect_btn_1 = RectButton(center_x=BUTTON1_CENTER_X, center_y=BUTTON1_CENTER_Y,
                                     width=BUTTON1_WIDTH, height=BUTTON1_HEIGHT,
                                     color=(0, 100, 0, 0), hover_color=(0, 255, 0, 0),
                                     border_width=0,
                                     text="")
        # Transparent Blue Button, no text, no border
        self.rect_btn_2 = RectButton(center_x=BUTTON2_CENTER_X, center_y=BUTTON2_CENTER_Y,
                                     width=BUTTON2_WIDTH, height=BUTTON2_HEIGHT,
                                     color=(0, 0, 100, 0), hover_color=(0, 0, 255, 0),
                                     border_width=0,
                                     text="")
        # Add to buttons list so they are drawn and checked
        self.buttons.append(self.rect_btn_1)
        self.buttons.append(self.rect_btn_2)
            
    def on_draw(self):
        """Render the screen."""
        self.clear()
        
        # Draw background
        if self.background_list:
            self.background_list.draw()
        
        # Draw character
        if self.character_list:
            self.character_list.draw()
        
        # Draw items
        self.item_sprites.draw()

        # Draw buttons
        for button in self.buttons:
            button.draw()
    
    def on_update(self, delta_time):
        """Movement and game logic"""
        # Update sprites
        self.item_sprites.update()
    
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.ESCAPE:
            arcade.close_window()
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user presses a mouse button."""
        # First let RectButton instances consume press state
        handled = False
        for b in [self.rect_btn_1, self.rect_btn_2]:
            if b.on_mouse_press(x, y, button, modifiers):
                handled = True

        # Fallback to older button types
        if not handled:
            for b in self.buttons:
                # RoundButton uses is_clicked
                if hasattr(b, 'is_clicked') and b.is_clicked(x, y):
                    print(f"Button '{getattr(b, 'text', '')}' clicked at ({x}, {y})!")

    def on_mouse_release(self, x, y, button, modifiers):
        # Check rect buttons for click completion
        for b in [self.rect_btn_1, self.rect_btn_2]:
            if b.on_mouse_release(x, y, button, modifiers):
                print(f"Rect button '{b.text}' clicked at ({x}, {y})!")

    def on_mouse_motion(self, x, y, dx, dy):
        # update hover state for rect buttons
        for b in [self.rect_btn_1, self.rect_btn_2]:
            b.on_mouse_motion(x, y, dx, dy)
