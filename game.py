import os
import socket
import pickle
import numpy as np
from scipy.signal import convolve


class Connect4:
    """
    Object that will contain your game.
    You can interact with it to:
        - Make a move (make_move)
        - Update the opponent's move (update_game)
        - Check whether the player's won or not (check_win)
        - Check whether the game ended or not (check_game_over)
        - Print the current board (display)
        - Print in-game info (display_info)
        - Restart the game (restart)
        - Get the current turn (Connect4.turn: int)
    """

    def __init__(self, player: str, grid_size: tuple = (7, 10)) -> None:
        """
        Args:
            player (str): The symbol to use for your moves.
            grid_size (tuple, optional): Size of the board. Defaults to (7, 10).
        """
        self.turn = 1
        self.grid_size = grid_size

        self.player = player
        self.opponent = "O" if player == "X" else "X"

        self.board = np.zeros(grid_size, dtype=str)
        self.board[:] = " "

    def make_move(self, col: int) -> bool:
        """
        Applies a move on the selected column for our player.

        Args:
            col (int): Column to place a new piece.

        Returns:
            bool: True if the move is valid, False else.
        """
        ncol = self.grid_size[1]

        if col >= ncol:
            # check for valid input
            return False

        if (idx := (self.board[self.board[:, col] == " ", col]).size) > 0:
            # check for free space on col
            self.board[idx - 1, col] = self.player
            self.turn += 1
            return True

        return False

    def update_game(self, opponent_move: int) -> bool:
        """
        Applies a move on the selected column for our opponent.
        No check for validity needed as it has already been checked
        on the other player's Connect4 object before sending.

        Args:
            opponent_move (int): Column selected by the other player.

        Returns:
            bool: True if correctly updated. Should never return False.
        """
        # Try clause has almost zero cost if no exception is catched
        try:
            idx = (self.board[self.board[:, opponent_move] == " ", opponent_move]).size
            self.board[idx - 1, opponent_move] = self.opponent
        except Exception:
            return False
        else:
            return True

    def check_win(self) -> bool:
        """
        Checks whether you've won the game or not. It uses convolution (FFT)
        between the board and basic solution kernels in order to check superposition.
        If the superposition of a kernel with the board reaches 4, the game ends.

        Returns:
            bool: True if we win, False else.
        """

        # We create a zeros matrix that will contain a 1 where out pieces are placed
        b = np.zeros(self.grid_size)
        b[self.board == self.player] = 1

        # KERNELS (basic solutions)
        kernels = (
            np.array([[1], [1], [1], [1]]),  # vertical
            np.array([[1, 1, 1, 1]]),  # horizontal
            np.eye(4, dtype=int),  # lr diagonal
            np.eye(4, dtype=int)[::-1],  # rl diagonal
        )

        # If convolution reaches 4 => complete kernel-board superpos.
        for kernel in kernels:
            c = convolve(b, kernel)
            if any(c[c == 4]):
                return True
        return False

    def check_game_over(self) -> bool:
        """
        Checks whether there is free space on the board or not.
        Should be followed by a "check_win()" call.

        Returns:
            bool: True if there is no free space, False else.
        """
        if np.count_nonzero(self.board) > 0:
            return False
        return True

    def display(self) -> None:
        """
        Will display the current gameboard. First the board is converted into a str,
        and the printed only once to improve speed.
        """
        board = []
        board.append("   " + "  ║  ".join(map(str, range(self.grid_size[1]))))  # header
        for row in self.board:
            board.append(" ═════" + "╬═════" * (self.grid_size[1] - 1))
            board.append("   " + "  ║  ".join(row))
        print("\n".join(board) + "\n\n")

    def display_info(self) -> None:
        """
        Header for the turns where the player moves.
        """
        print(f"\nYou Play!\nCurrent turn: {self.turn}\n")

    def restart(self) -> None:
        """
        Restarts the turn count and the gameboard.
        """
        self.turn = 1
        self.board[:] = " "


class Client:
    def __init__(self, host_ip: str = "") -> None:
        HOST_IP = host_ip if host_ip else socket.gethostbyname(socket.gethostname())
        PORT = 12783

        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv.connect((HOST_IP, PORT))

        self.STATUS = "-p"

        self.player = Connect4("O")
        print(f"\nConnected to {self.serv.getsockname()}!")

    def send_move(self, move: int) -> None:
        self.player.make_move(move)
        os.system("cls")
        self.player.display()
        self.serv.send(pickle.dumps(move))

    def await_move(self) -> bool:
        print(f"\nWaiting for the other player...")
        opp_move = int(pickle.loads(self.serv.recv(1024)))
        self.player.update_game(opp_move)
        self.STATUS = pickle.loads(self.serv.recv(1024))

        os.system("cls")

        self.player.display_info()
        self.player.display()

        if self.STATUS in ("-x", "-d"):
            return False
        return True

    def continue_game(self) -> bool:
        if self.player.check_win():
            self.STATUS = "-o"
            self.serv.send(pickle.dumps(self.STATUS))
            return False

        elif self.player.check_game_over():
            self.STATUS = "-d"
            self.serv.send(pickle.dumps(self.STATUS))
            return False

        self.serv.send(pickle.dumps(self.STATUS))
        return True

    def game_over(self) -> bool:
        if self.STATUS == "-o":
            print(f"Congrats, you won in {self.player.turn - 1} turns!")
        elif self.STATUS == "-d":
            print("It's a draw!")
        elif self.STATUS == "-x":
            print("Sorry, the opponent won.")
        else:
            print("The opponent disconnected, you win.")
            return False
        return True

    def rematch(self) -> bool:
        print(f"\nWaiting for host...")
        host_response = pickle.loads(self.serv.recv(1024))

        # if the host wants a rematch, then the client is asked
        if host_response == "N":
            print(f"\nThe host does not want a rematch.")
            return False

        print(f"\nThe host would like a rematch!")
        client_response = input("Rematch? (Y/N): ").capitalize()
        self.serv.send(pickle.dumps(client_response))

        # if the client wants a rematch, restart the game
        if client_response == "N":
            return False

        self.player.restart()
        return True

    def close(self) -> None:
        _ = input(f"\nThank you for playing!\nPress enter to quit...\n")
        self.serv.close()


class Server:
    def __init__(self) -> None:
        HOST_IP = socket.gethostbyname(socket.gethostname())
        PORT = 12783

        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv.bind((HOST_IP, PORT))
        self.serv.listen(5)
        self.STATUS = "-p"

        self.player = Connect4("X")

        self.client_socket, client_address = self.serv.accept()
        print(f"\nConnected to {client_address}!")

    def send_move(self, move: int) -> None:
        self.player.make_move(move)
        os.system("cls")
        self.player.display()
        self.client_socket.send(pickle.dumps(move))

    def await_move(self) -> bool:
        print(f"\nWaiting for the other player...")

        opp_move = int(pickle.loads(self.client_socket.recv(1024)))
        self.player.update_game(opp_move)
        self.STATUS = pickle.loads(self.client_socket.recv(1024))

        os.system("cls")

        self.player.display_info()
        self.player.display()

        if self.STATUS in ("-o", "-d"):
            return False
        return True

    def continue_game(self) -> bool:
        if self.player.check_win():
            self.STATUS = "-x"
            self.client_socket.send(pickle.dumps(self.STATUS))
            return False

        elif self.player.check_game_over():
            self.STATUS = "-d"
            self.client_socket.send(pickle.dumps(self.STATUS))
            return False

        self.client_socket.send(pickle.dumps(self.STATUS))
        return True

    def game_over(self) -> bool:
        if self.STATUS == "-x":
            print(f"Congrats, you won in {self.player.turn - 1} turns!")
        elif self.STATUS == "-d":
            print("It's a draw!")
        elif self.STATUS == "-o":
            print("Sorry, the opponent won.")
        else:
            print("The opponent disconnected, you win.")
            return False
        return True

    def rematch(self) -> bool:
        host_response = input(f"\nRematch? (Y/N): ").capitalize()
        self.client_socket.send(pickle.dumps(host_response))

        if host_response == "N":
            return False

        print("Waiting for the client to response...")
        client_response = pickle.loads(self.client_socket.recv(1024))

        if client_response == "N":
            print("\nThe client does not want a rematch.")
            return False

        self.player.restart()
        return True

    def close(self) -> None:
        _ = input(f"\nThank you for playing!\nPress enter to quit...\n")
        self.client_socket.close()


if __name__ == "__main__":
    t = Connect4("X")
    t.display()
