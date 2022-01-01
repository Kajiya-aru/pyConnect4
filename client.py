from game import Client


def main():
    """
    This script will launch the guest of the game, who will play second turn
    as "O" and must be executed afetr the server is activated (server.py).
    """
    client = Client()

    while True:  # main loop
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
