from game import Server


def main():
    """
    This script will launch the host of the game, who will play first turn
    as "X" and must be executed before the client.py script.
    """
    server = Server()

    while True:  # main loop
        server.player.display_info()
        server.player.display()

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
