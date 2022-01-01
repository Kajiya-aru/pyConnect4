# pyConnect4
 The traditional Connect4 game, to be played on local online through the command line.

## Instructions
 * Copy the repository on both players' computers.
 * First, run the "server.py" file on one computer. This will launch the server that will host the game.
 * Now, run the "client.py" file on the other computer.
 * Once the connection is established, the game will start.

## Dependecies
 * Numpy: used to hold the game pieces' distribution and for simplicity of programming.
 * Scipy (convolve): convolution between the game board (2D matrix) and the basic solution kernels (4 2D matrices)
 can be carried out to quickly get all the feasible superpositions between them. This way, if a "4" is found on the
 resulting matrix, it will mean a player has won the game. 