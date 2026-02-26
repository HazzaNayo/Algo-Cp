
import arcade
from src.game import BaksoGame


def main():
    """Main function"""
    game = BaksoGame()
    game._last_mouse = (0, 0)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
