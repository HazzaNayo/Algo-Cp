
import arcade
from src.game import BaksoGame


def main():
    """Main function"""
    game = BaksoGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
