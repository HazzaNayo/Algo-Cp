import arcade
import math

class RoundButton:
    """
    A simple round button component for Python Arcade.
    """
    def __init__(self, center_x, center_y, radius, color=arcade.color.GRAY, text="", text_color=arcade.color.WHITE):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.text = text
        self.text_color = text_color
        self.hovered = False

    def draw(self):
        # Draw the main circle
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)
        
        # Draw text if any
        if self.text:
            arcade.draw_text(self.text, self.center_x, self.center_y, 
                             self.text_color, font_size=self.radius // 2, 
                             anchor_x="center", anchor_y="center")

    def is_clicked(self, x, y):
        """
        Check if a point (x, y) is within the button's radius.
        """
        distance = math.sqrt((x - self.center_x) ** 2 + (y - self.center_y) ** 2)
        return distance <= self.radius


class RectButton:
    """
    A configurable rectangular (box) button for Python Arcade.

    Usage:
      btn = RectButton(center_x=100, center_y=50, width=200, height=60, text='Play')
      btn.draw()
      if btn.is_clicked(x, y):
          # handle click

    Positioning and sizing helpers:
      btn.set_position(x, y)   # keeps width/height, moves center
      btn.set_size(w, h)       # keeps center, changes size

    Parameters:
      center_x, center_y: center coordinates of the rectangle (default anchor is center)
      width, height: size of the rectangle in pixels
      color: fill color
      border_color, border_width: appearance of border
      text, text_color, font_size: text inside the button
      anchor: 'center' or 'topleft' if you prefer to supply top-left instead
    """

    def __init__(self, center_x=0, center_y=0, width=100, height=40,
                 color=arcade.color.DARK_BLUE, border_color=arcade.color.WHITE,
                 border_width=2, text="", text_color=arcade.color.WHITE,
                 font_size=None, hover_color=None, pressed_color=None,
                 anchor='center'):
        self.anchor = anchor
        if anchor == 'topleft':
            # convert to center-based coordinates
            center_x = center_x + width / 2
            center_y = center_y - height / 2

        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.text = text
        self.text_color = text_color
        self.font_size = font_size or int(min(self.width, self.height) * 0.3)
        self.hover_color = hover_color or arcade.color.BLUE_GRAY
        self.pressed_color = pressed_color or arcade.color.DARK_BLUE

        # state
        self.hovered = False
        self.pressed = False

    def draw(self):
        # choose fill color based on state
        fill = self.color
        if self.pressed:
            fill = self.pressed_color
        elif self.hovered:
            fill = self.hover_color

        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2

        # draw filled rectangle and border using lbwh (left, bottom, width, height)
        left = self.center_x - self.width / 2
        bottom = self.center_y - self.height / 2
        arcade.draw_lbwh_rectangle_filled(left, bottom, self.width, self.height, fill)
        if self.border_width > 0:
            arcade.draw_lbwh_rectangle_outline(left, bottom, self.width, self.height, self.border_color, self.border_width)

        # draw text centered
        if self.text:
            arcade.draw_text(self.text, self.center_x, self.center_y,
                             self.text_color, font_size=self.font_size,
                             anchor_x='center', anchor_y='center')

    def contains(self, x, y):
        """Return True if (x, y) is inside the button rectangle."""
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        return left <= x <= right and bottom <= y <= top

    # alias for semantic clarity
    def is_clicked(self, x, y):
        return self.contains(x, y)

    def set_position(self, center_x, center_y, anchor=None):
        """Set the button position. If anchor=='topleft', converts to center coords."""
        if anchor is None:
            anchor = self.anchor
        if anchor == 'topleft':
            center_x = center_x + self.width / 2
            center_y = center_y - self.height / 2
        self.center_x = center_x
        self.center_y = center_y

    def set_size(self, width, height):
        """Change the button size (keeps center coordinates)."""
        self.width = width
        self.height = height
        # adjust default font size to the new size if user didn't set custom
        self.font_size = int(min(self.width, self.height) * 0.3)

    # convenience methods for UI event handling
    def on_mouse_motion(self, x, y, dx=0, dy=0):
        self.hovered = self.contains(x, y)

    def on_mouse_press(self, x, y, button, modifiers=0):
        if self.contains(x, y):
            self.pressed = True
            return True
        return False

    def on_mouse_release(self, x, y, button, modifiers=0):
        if self.pressed and self.contains(x, y):
            self.pressed = False
            return True
        self.pressed = False
        return False
