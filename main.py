import arcade
from src.game import BaksoGame
from src.game import GameState


def main():
    """Main function"""
    game = BaksoGame()
    game.state = GameState.MENU  # Mulai dari MENU, bukan langsung setup
    arcade.run()


if __name__ == "__main__":
    main()
