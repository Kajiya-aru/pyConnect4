from game import Client


def main():
    """
    This script will launch the guest of the game.
    Must be executed after the server is up (server.py).
    """
    client = Client()

    while True:  # main loop

        if client.start_playing():
            client.player.display_info()
            client.player.display()
        else:
            client.await_move()

        while True:  # game loop
            move = int(input(f"Enter next move: "))
            client.send_move(move)

            if not client.continue_game():
                break

            if not client.await_move():
                break

        client.game_over()

        if not client.rematch():
            break

    client.close()


if __name__ == "__main__":
    main()
