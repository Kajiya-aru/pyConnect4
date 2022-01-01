from game import Server
import random


def main():
    """
    This script will launch the host of the game.
    Must be executed before the client.py script.
    """
    server = Server()

    while True:  # main loop

        first = random.random() < 0.5
        server.start_playing(first=first)

        if first:
            server.player.display_info()
            server.player.display()
        else:
            server.await_move()

        while True:  # game loop
            move = int(input(f"Enter next move: "))
            server.send_move(move)

            if not server.continue_game():
                break

            if not server.await_move():
                break

        server.game_over()

        if not server.rematch():
            break

    server.close()


if __name__ == "__main__":
    main()
