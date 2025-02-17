"""
Main.py file is responsible for running the game engine. It handles user input and GUI.
"""

import pygame as p
import pygame.font
import ChessEngine
from Interface import UI
import inspect
import sys
import asyncio

# Set up constants for the game dimensions and settings.
WIDTH: int = 720  # The width of the game window.
HEIGHT: int = 600  # The height of the game window.
MAX_FPS: int = 15  # Maximum frames per second (controls the game speed).
AI = True
ELO = 1320
MOVETIME = 1000
MOVEHINT = True

# Global Game Values
CLOCK: p.time.Clock = None  # Clock object to manage game updates.
GameState: ChessEngine.GameState = ChessEngine.GameState()  # Initialize the game state.
FirstMoveWhite: bool = GameState.isWhiteTurn
MultiPV: int = 2
Paused: bool = False


async def main() -> None:
    """
    The main driver for the chess game. This function handles user input and updates the graphics.
    """
    ui = UI(WIDTH, HEIGHT)
    screen, CLOCK = ui.setPyGameValues()
    ui.loadImages()  # Load images once to save memory.
    # Prepare stockfish
    if AI:
        await subproc("stockfish.exe")
        await sendCommand(
            f"position fen {ChessEngine.FEN.boardToFEN(GameState.board)} {'w' if GameState.isWhiteTurn else 'b'} {GameState.getCastleString()} {GameState.enPassantPlace} {GameState.fiftyMoveRule} {GameState.numOfMoves()}"
        )
        await sendCommand(f"setoption name MultiPV value {MultiPV}\n")
        if ELO:
            await sendCommand("setoption name UCI_LimitStrength value True\n")
            # TODO: Set Depth or Change Move Time to get ELO lower than 1320
            await sendCommand(f"setoption name UCI_Elo value {ELO}\n")
    userClicks: list = []  # A list to store the user clicks.
    toHighlight: list = set()  # A list to keep track of squares to highlight.
    moveHighLight: set = (
        set()
    )  # A list of possible coordinates the selected piece can move to.
    flipped = [False]  # False means white on bottom (if AI: AI plays black)
    drawGameState(
        ui, screen, GameState, userClicks, toHighlight, moveHighLight, flipped
    )
    while True:
        await eventHandler(ui, toHighlight, userClicks, screen, moveHighLight, flipped)
        CLOCK.tick(MAX_FPS)  # Control the game's frame rate.


def drawGameState(
    ui: "UI",
    screen: p.Surface,
    gs: ChessEngine.GameState,
    userClicks: list,
    toHighlight: set,
    moveHighLight: set,
    flipped: list[bool],
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
    ui.drawBoard(
        screen, userClicks, toHighlight, moveHighLight if MOVEHINT else []
    )  # Draw the chessboard.
    ui.drawPieces(screen, gs.board, flipped[0])  # Draw the chess pieces on the board.
    screen.blit(p.transform.flip(screen, False, flipped[0]), (0, 0))
    ui.drawPlaces(screen, flipped[0])  # Draw the ranks and files labels.
    ui.drawNotationLog(screen, GameState.moveLog, GameState.gameUpdate, FirstMoveWhite)
    p.display.flip()  # Update the display.


async def eventHandler(
    ui: "UI",
    toHighlight: set,
    userClicks: list,
    screen: p.Surface,
    possibleMoves: set,
    flipped: list[bool],
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
    global Paused
    Paused = True if GameState.gameUpdate else Paused
    if (
        AI and GameState.isWhiteTurn == flipped[0] and not Paused
    ):  # The moves if for the top opponent
        await sendCommand(
            f"position fen {ChessEngine.FEN.boardToFEN(GameState.board)} {'w' if GameState.isWhiteTurn else 'b'} {GameState.getCastleString()} {GameState.enPassantPlace} {GameState.fiftyMoveRule} {GameState.numOfMoves()}\n",
            False,
        )
        bestToWorst = getMoves(await sendCommand(f"go movetime {MOVETIME}\n", True))
        move = bestToWorst[0][0]
        start, end, promote = ChessEngine.Move.parseSquare(move, GameState.board)
        handleAllMoves(
            ui, [start, end], toHighlight, screen, possibleMoves, flipped, promote
        )
        userClicks.clear()
        possibleMoves.clear()
        drawGameState(
            ui, screen, GameState, userClicks, toHighlight, possibleMoves, flipped
        )
        p.display.flip()
        return

    redraw = False
    for event in p.event.get():
        if event.type == p.QUIT:
            p.quit()
            await terminateProgram("QUIT")
        elif event.type == p.MOUSEBUTTONUP and event.button == 3:
            # Function to highlight selected squares on right-click.
            squareX, squareY = ui.findSquare(*p.mouse.get_pos(), flipped[0])
            toHighlight.add((squareY, squareX))
            redraw = True
        elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            # Handle left-click for moving pieces.
            possibleMoves.clear()
            handleSquareSelection(
                ui,
                *p.mouse.get_pos(),
                userClicks,
                toHighlight,
                screen,
                possibleMoves,
                flipped,
            )
            redraw = True
        elif event.type == p.KEYDOWN and event.key == p.K_LEFT:
            # Undo the last move when the left arrow key is pressed.
            handleLeftButtonDown(userClicks)
            possibleMoves.clear()
            toHighlight.clear()
            redraw = True
        elif event.type == p.KEYDOWN and event.key == p.K_f:
            flipped[0] = not flipped[0]
            redraw = True
        elif event.type == p.KEYDOWN and event.key == p.K_SPACE:
            Paused = not Paused
            print("PAUSE" if Paused else "UNPAUSE")
        elif event.type == p.KEYDOWN and event.key == p.K_r:
            toHighlight.clear()
            redraw = True

    if redraw:
        drawGameState(
            ui, screen, GameState, userClicks, toHighlight, possibleMoves, flipped
        )


def handleLeftButtonDown(userClicks: list) -> bool:
    """
    Handles the event when the left arrow key is pressed to undo the last move.

    :Parameters:
    - userClicks: list
        The list of user clicks (move history).
    """
    userClicks.clear()  # Clear the move list.
    return GameState.undoMove()


def handleSquareSelection(
    ui: "UI",
    mouseX: int,
    mouseY: int,
    userClicks: list,
    toHighlight: list,
    screen: p.Surface,
    possibleMoves: set,
    flipped: list[bool],
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
    squareX, squareY = ui.findSquare(mouseX, mouseY, flipped[0])
    if len(userClicks) == 1:
        userClicks.append((squareY, squareX))
        # Check for castling move.
        if userClicks[0] == userClicks[1]:
            userClicks.clear()
        elif not allowedMove(userClicks, flipped) and not Paused:
            # Reset selection if the move is invalid.
            userClicks[0] = userClicks[1]
            del userClicks[1]  # Delete the item at index 1.
            highlightPosMoves(userClicks, screen, possibleMoves)
        elif not Paused:
            handleAllMoves(ui, userClicks, toHighlight, screen, possibleMoves, flipped)
    elif len(userClicks) == 2:
        userClicks.clear()
        userClicks.append((squareY, squareX))
        highlightPosMoves(userClicks, screen, possibleMoves)
    else:
        userClicks.append((squareY, squareX))
        highlightPosMoves(userClicks, screen, possibleMoves)


def handleAllMoves(
    ui: "UI",
    userClicks: list,
    toHighlight: set,
    screen: p.Surface,
    possibleMoves: list,
    flipped: list[bool],
    promote: str = "",
) -> None:
    toHighlight.clear()
    if GameState.castleChecks(userClicks):
        GameState.castle(userClicks[0], userClicks[1])
    elif pawnChecks(userClicks):
        handlePawnPromotion(
            ui, userClicks, screen, toHighlight, possibleMoves, flipped, promote
        )
    elif enPassantChecks(userClicks):
        GameState.makeEnPassant(userClicks)
    else:
        handleMove(userClicks)


def highlightPosMoves(piece: list, screen: p.Surface, possibleMoves: set) -> None:
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
    for toP, fromP in GameState.possibleMoves:
        if piece == fromP:
            possibleMoves.add(toP)


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
    toHighlight: set,
    possibleMoves: set,
    flipped: list[bool],
    promote: str,
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
    drawGameState(
        ui, screen, GameState, userClicks, toHighlight, possibleMoves, flipped
    )
    if not promote:
        # Prompt the player for the piece to promote to.
        promote = GameState.pawnPromotion(
            (
                (userClicks[1][0], userClicks[1][1]),
                (userClicks[0][0], userClicks[0][1]),
            ),
            screen,
        )
    move = ChessEngine.Move(
        (userClicks[0], userClicks[1]),
        (userClicks[1], userClicks[1]),
        GameState.board,
        3,  # Type of move (pawn promotion).
        promote,
    )
    GameState.makeMove(move)


def getMoves(lines: list[str]):
    lines = lines[-1 - MultiPV : -1]
    bestToWorst: list[list[str]] = []
    for line in lines:
        moves = None
        i = line.find(" pv")
        moves = line[i + 4 :].split()
        bestToWorst.append(moves)
    return bestToWorst


async def terminateProgram(*args):
    global stockfish
    caller = inspect.stack()[1]
    if AI and stockfish:
        stockfish.terminate()
        await stockfish.wait()
    print("\nProgram Termination --")
    for arg in args:
        print("Reason:", arg)
    sys.exit(
        f"Terminated at file {caller.filename} in function {caller.function} at line {caller.lineno}"
    )


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
            line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=5)
            if line.decode("ascii").strip() == "uciok":
                print("STOCKFISH WORKING ")
                break
    except asyncio.TimeoutError:
        await terminateProgram("Stockfish did not respond as expected!")


async def sendCommand(command: str, outputNeeded: bool = False):
    # send command
    stockfish.stdin.write(command.encode("ascii"))
    await stockfish.stdin.drain()
    lines = []
    if outputNeeded:
        # Read the response
        try:
            while True:
                line = await asyncio.wait_for(stockfish.stdout.readline(), timeout=3)
                line = line.decode("ascii").strip()
                lines.append(line)
                if line.startswith("bestmove"):
                    break
        except asyncio.TimeoutError:
            await terminateProgram("Stockfish did not respond as expected!")
    return lines


def allowedMove(userClicks: list[tuple[int]], flipped: list[bool]):
    """
    Check if the move is allowed
    :Returns:
    - isAllowed: bool
    """
    if (userClicks[1], userClicks[0]) not in GameState.possibleMoves:
        return False
    if not AI:
        return True
    if not flipped[0] and GameState.pieceColor(*userClicks[0]) == "b":
        return False
    elif flipped[0] and GameState.pieceColor(*userClicks[0]) == "w":
        return False
    return True


if __name__ == "__main__":
    asyncio.run(main())  # Start the game.
