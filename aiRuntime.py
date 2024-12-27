"""
Main.py file is responsible for running the game engine. It handles user input and GUI.
"""

import pygame as p
import pygame.font
import copies.chessFlipHardcoded as ChessEngine
from interfaceCopy import UI
import asyncio
import inspect
import sys

# Set up constants for the game dimensions and settings.
WIDTH: int = 600  # The width of the game window.
HEIGHT: int = 600  # The height of the game window.
MAX_FPS: int = 15  # Maximum frames per second (controls the game speed).

# Global Game Values
stockfish: asyncio.subprocess.Process = None
USERPLAYSWHITE = True
CLOCK: p.time.Clock = None  # Clock object to manage game updates.
GameState: ChessEngine.GameState = ChessEngine.GameState(USERPLAYSWHITE)  # Initialize the game state.
MultiPV: int = 1


async def main() -> None:
    """
    The main driver for the chess game. This function handles user input and updates the graphics.
    """
    ui = UI(WIDTH, HEIGHT, USERPLAYSWHITE)
    screen, CLOCK = ui.setPyGameValues()
    ui.loadImages()  # Load images once to save memory.
    userClicks: list = []  # A list to store the user clicks.
    toHighlight: list = []  # A list to keep track of squares to highlight.
    possibleMoves: list = []  # A list of possible coordinates the selected piece can move to.
    drawGameState(ui, screen, GameState, userClicks, toHighlight, possibleMoves)
    notationLogs = GameState.getNotationLog()
    """await subproc("stockfish.exe")
    await sendCommand(
        f"position fen {ChessEngine.PGN.boardToPGN(GameState.board)} {"w" if GameState.isWhiteTurn else "b"} {GameState.getCastleString()} {GameState.enPassantPlace} {GameState.fiftyMoveRule} {GameState.numOfMoves()} {("moves " + notationLogs) if notationLogs else ''}\n",
        False,
    )"""
    """move = await sendCommand("go movetime 1000\n", True)"""

    p.display.flip()
    while True:
        await eventHandler(ui, toHighlight, userClicks, screen, possibleMoves)
        CLOCK.tick(MAX_FPS)  # Control the game's frame rate.
        p.display.flip()  # Update the display.


async def subproc(path):
    global stockfish
    # try and create a stockfish subprocess with provided path
    try:
        stockfish = await asyncio.create_subprocess_exec(
            path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        await terminateProgram("Provided path does not exist!")

    # Send the "uci" command
    stockfish.stdin.write(b"uci\n")
    await stockfish.stdin.drain()

    # Read the response
    try:
        while True:
            line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=2)
            if line.decode("ascii").strip() == "uciok":
                print("Stockfish working")
                break
    except asyncio.TimeoutError:
        await terminateProgram("Stockfish did not respond as expected!")


async def sendCommand(command: str, outputNeeded: bool):
    # send command

    stockfish.stdin.write(command.encode("ascii"))
    await stockfish.stdin.drain()
    print(command)
    if outputNeeded:
        # Read the response
        try:
            while True:
                line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=2)
                line = line.decode("ascii").strip()
                if line.startswith("bestmove"):
                    print(line)
                    break
        except asyncio.TimeoutError:
            await terminateProgram("Stockfish did not respond as expected!")


def drawGameState(
    ui: "UI",
    screen: p.Surface,
    gs: ChessEngine.GameState,
    draw: list,
    highlight: list,
    possibleMoves: list,
) -> None:
    """
    Responsible for drawing the current game state on the screen.

    :Parameters:
    - screen: p.Surface
        The game window where everything is drawn.
    - gs: ChessEngine.GameState
        The current game state object.
    - draw: list
        A list of squares involved in the current move.
    - highlight: list
        A list of squares to highlight.
    - possibleMoves: list
        A list of possible moves for the selected piece.
    """
    ui.draw_board(screen, draw, highlight, possibleMoves)  # Draw the chessboard.
    ui.draw_pieces(screen, gs.board)  # Draw the chess pieces on the board.
    ui.draw_places(screen)  # Draw the ranks and files labels.


async def eventHandler(
    ui: "UI",
    toHighlight: list,
    userClicks: list,
    screen: p.Surface,
    possibleMoves: list,
) -> None:
    """
    Handles all the events (mouse clicks, key presses) during the game loop.

    :Parameters:
    - toHighlight: list
        Squares to highlight.
    - userClicks: list
        A list to store the user clicks.
    - screen: p.Surface
        The game window where everything is drawn.
    - possibleMoves: list
        Possible moves for the selected piece.
    """
    redraw = False
    for event in p.event.get():
        if event.type == p.QUIT:
            p.quit()
            await terminateProgram("Quit Game")
        elif event.type == p.MOUSEBUTTONUP and event.button == 3:
            # Function to highlight selected squares on right-click.
            squareX, squareY = GameState.findSquare(*p.mouse.get_pos())
            squareHighlight(squareX, squareY, toHighlight)
            redraw = True
        elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            # Handle left-click for moving pieces.
            possibleMoves.clear()
            handleSquareSelection(
                ui, *p.mouse.get_pos(), userClicks, toHighlight, screen, possibleMoves
            )
            redraw = True
        elif event.type == p.KEYDOWN and event.key == p.K_LEFT:
            # Undo the last move when the left arrow key is pressed.
            handleLeftButtonDown(userClicks)
            possibleMoves.clear()
            toHighlight.clear()
            redraw = True
    if redraw:
        drawGameState(ui, screen, GameState, userClicks, toHighlight, possibleMoves)


def handleLeftButtonDown(userClicks: list) -> bool:
    """
    Handles the event when the left arrow key is pressed to undo the last move.

    :Parameters:
    - userClicks: list
        The list of user clicks (move history).
    """
    userClicks.clear()  # Clear the move list.
    return GameState.undoMove()


def squareHighlight(x: int, y: int, toHighlight: list) -> None:
    """
    Adds or removes a square from the highlight list.

    :Parameters:
    - x: int
        The x-coordinate on the board.
    - y: int
        The y-coordinate on the board.
    - toHighlight: list
        The list of squares to highlight.
    """
    if (y, x) not in toHighlight:
        toHighlight.append((y, x))  # Add the square to the highlight list.
    else:
        toHighlight.remove(
            (y, x)
        )  # Remove the square from the highlight list if it's already highlighted.


def handleSquareSelection(
    ui: "UI",
    mouseX: int,
    mouseY: int,
    userClicks: list,
    toHighlight: list,
    screen: p.Surface,
    possibleMoves: list,
) -> None:
    """
    Handles the selection of squares when the user clicks on the board.

    :Parameters:
    - mouseX: int
        The x-coordinate of the mouse click.
    - mouseY: int
        The y-coordinate of the mouse click.
    - userClicks: list
        A list to store the user clicks.
    - toHighlight: list
        Squares to highlight.
    - screen: p.Surface
        The game window where everything is drawn.
    - possibleMoves: list
        Possible moves for the selected piece.
    """
    # Check if the click is within bounds.
    if not (mouseX < WIDTH and mouseY < HEIGHT):
        return  # Out of bounds.
    # Get the square coordinates.
    squareX, squareY = ui.findSquare(mouseX, mouseY)
    if len(userClicks) == 1:
        userClicks.append((squareY, squareX))
        # Check for castling move.
        print(userClicks)
        if GameState.castleChecks(userClicks):
            GameState.castle(userClicks[0], userClicks[1])
        elif (userClicks[1], userClicks[0]) in GameState.posMoves:
            if pawnChecks(userClicks):
                print("promotion")
                handlePawnPromotion(ui, userClicks, screen, toHighlight, possibleMoves)
            elif enPassantChecks(userClicks):
                GameState.makeEnPassant(userClicks)
            else:
                handleMove(userClicks)
        elif userClicks[0] == userClicks[1]:
            userClicks.clear()
        else:
            # Reset selection if the move is invalid.
            userClicks[0] = userClicks[1]
            del userClicks[1]  # Delete the item at index 1.
            highlightPosMoves(userClicks, screen, possibleMoves)
    elif len(userClicks) == 2:
        userClicks.clear()
        userClicks.append((squareY, squareX))
        highlightPosMoves(userClicks, screen, possibleMoves)
    else:
        userClicks.append((squareY, squareX))
        highlightPosMoves(userClicks, screen, possibleMoves)


def highlightPosMoves(piece: list, screen: p.Surface, possibleMoves: list) -> None:
    """
    Highlights possible moves for the selected piece.

    :Parameters:
    - piece: list
        The selected piece coordinates.
    - screen: p.Surface
        The game window where everything is drawn.
    - possibleMoves: list
        Possible moves for the selected piece.
    """
    piece = piece[0]
    for toP, fromP in GameState.posMoves:
        if piece == fromP:
            possibleMoves.append(toP)


def enPassantChecks(userClicks: list) -> bool:
    """
    Checks if an en passant move is possible.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).

    :Returns:
    - bool: True if en passant is possible, False otherwise.
    """
    return GameState.isEnPassant(userClicks)


def pawnChecks(userClicks: list) -> bool:
    """
    Checks if a pawn promotion is possible.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).

    :Returns:
    - bool: True if pawn promotion is possible, False otherwise.
    """
    return GameState.board[userClicks[0][0]][userClicks[0][1]][1] == "P" and (
        (userClicks[1][0] == 0) or (userClicks[1][0] == 7)
    )


def handleMove(userClicks: list) -> None:
    """
    Executes a regular move.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).
    """
    move = ChessEngine.Move(
        (userClicks[0], userClicks[1]), (userClicks[1], userClicks[1]), GameState.board
    )
    GameState.makeMove(move)


def handlePawnPromotion(
    ui: "UI",
    userClicks: list,
    screen: p.Surface,
    toHighlight: list,
    possibleMoves: list,
) -> None:
    """
    Handles pawn promotion when a pawn reaches the opposite end of the board.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).
    - screen: p.Surface
        The game window where everything is drawn.
    - toHighlight: list
        Squares to highlight.
    - possibleMoves: list
        Possible moves for the selected piece.
    """
    # Redraw the game state to update the display before promotion.
    drawGameState(ui, screen, GameState, userClicks, toHighlight, possibleMoves)
    p.display.flip()
    # Prompt the player for the piece to promote to.
    piece = GameState.pawnPromotion(
        ((userClicks[1][0], userClicks[1][1]), (userClicks[0][0], userClicks[0][1])),
        screen,
    )
    move = ChessEngine.Move(
        (userClicks[0], userClicks[1]),
        (userClicks[1], userClicks[1]),
        GameState.board,
        3,  # Type of move (pawn promotion).
        piece,
    )
    GameState.makeMove(move)


async def terminateProgram(*args):
    global stockfish
    caller = inspect.stack()[1]
    if stockfish:
        stockfish.terminate()
        await stockfish.wait()
    print("\nProgram Termination --")
    for arg in args:
        print("Reason:", arg)
    sys.exit(
        f"Terminated at file {caller.filename} in function {caller.function} at line {caller.lineno}"
    )


if __name__ == "__main__":
    asyncio.run(main())  # Start the game.
