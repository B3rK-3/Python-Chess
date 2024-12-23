"""
Main.py file is responsible for running the game engine. It handles user input and GUI.
"""

import pygame as p
import pygame.font

import ChessEngine

# Set up constants for the game dimensions and settings.
WIDTH: int = 600  # The width of the game window.
HEIGHT: int = 600  # The height of the game window.
SIZE: int = 8  # The size of the chessboard (8x8).
SQ_EACH_SIZE: int = HEIGHT // SIZE  # The size of each square on the chessboard.
MAX_FPS: int = 15  # Maximum frames per second (controls the game speed).
LIGHT_SQUARE_COLOR: p.Color = p.Color(227, 193, 111)  # Light square color.
DARK_SQUARE_COLOR: p.Color = p.Color(184, 139, 74)  # Dark square color.
HIGHLIGHT_COLOR: tuple = (255, 204, 0, 100)  # Color for highlighting squares.
MOVE_HIGHLIGHT_COLOR: tuple = (255, 255, 102, 200)  # Color for move highlights.
POSSIBLE_MOVES: tuple = (255, 234, 0, 128)  # Color for possible moves highlights.

# Global Game Values
IMAGES: dict = {}  # A dictionary to store images of the chess pieces.
GameState: ChessEngine.GameState = ChessEngine.GameState()  # Initialize the game state.
CLOCK: p.time.Clock = None  # Clock object to manage game updates.
validMoves: list = None  # List to store valid moves.


def main() -> None:
    """
    The main driver for the chess game. This function handles user input and updates the graphics.
    """
    screen = setPyGameValues()
    loadImages()  # Load images once to save memory.
    generateValidMoves()
    userClicks: list = []  # A list to store the user clicks.
    toHighlight: list = []  # A list to keep track of squares to highlight.
    possibleMoves: list = []  # A list of possible coordinates the selected piece can move to.
    drawGameState(screen, GameState, userClicks, toHighlight, possibleMoves)
    p.display.flip()
    while True:
        eventHandler(toHighlight, userClicks, screen, possibleMoves)
        CLOCK.tick(MAX_FPS)  # Control the game's frame rate.
        p.display.flip()  # Update the display.


def drawGameState(
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
    draw_board(screen, draw, highlight, possibleMoves)  # Draw the chessboard.
    draw_pieces(screen, gs.board)  # Draw the chess pieces on the board.
    draw_places(screen)  # Draw the ranks and files labels.


def draw_board(
    screen: p.Surface, draw: list, highlight: list, possibleMoves: list
) -> None:
    """
    Draws the chessboard with highlighted squares.

    :Parameters:
    - screen: p.Surface
        The game window where everything is drawn.
    - draw: list
        Squares involved in the current move.
    - highlight: list
        Squares to highlight.
    - possibleMoves: list
        Possible moves for the selected piece.
    """
    colors = [LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR]  # Light and dark square colors.
    for r in range(SIZE):
        for c in range(SIZE):
            modified = False
            color = colors[(r + c) % 2]  # Alternate color based on row and column.
            if (r, c) in highlight:
                color = HIGHLIGHT_COLOR
                modified = True
            elif (r, c) in draw:
                p.draw.rect(
                    screen,
                    color,
                    (c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE),
                )
                color = MOVE_HIGHLIGHT_COLOR
                modified = True
            if modified:
                # Create a semi-transparent surface for highlights.
                overlay = p.Surface(
                    (SQ_EACH_SIZE, SQ_EACH_SIZE), p.SRCALPHA
                )  # Use SRCALPHA for transparency.
                p.draw.rect(
                    screen,
                    color,
                    (c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE),
                )
            else:
                p.draw.rect(
                    screen,
                    color,
                    (c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE),
                )
    for r, c in possibleMoves:
        # Create a semi-transparent surface for possible moves.
        overlay = p.Surface(
            (SQ_EACH_SIZE, SQ_EACH_SIZE), p.SRCALPHA
        )  # Use SRCALPHA for transparency.
        overlay.fill(
            POSSIBLE_MOVES
        )  # Add an alpha value (0-255), 128 is semi-transparent.
        # Draw the transparent rectangle on the screen.
        screen.blit(overlay, (c * SQ_EACH_SIZE, r * SQ_EACH_SIZE))


def draw_pieces(screen: p.Surface, board: list) -> None:
    """
    Draws the chess pieces on the board.

    :Parameters:
    - screen: p.Surface
        The game window where everything is drawn.
    - board: list
        The current state of the chessboard.
    """
    for r in range(SIZE):
        for c in range(SIZE):
            pc = board[r][c]  # Get the piece at the current position.
            if pc != "__":  # If the square is not empty.
                # Draw the piece image on the board.
                screen.blit(
                    IMAGES[pc],
                    p.Rect(
                        c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE
                    ),
                )


def draw_places(screen: p.Surface) -> None:
    """
    Draws the rank (numbers) and file (letters) labels on the board.

    :Parameters:
    - screen: p.Surface
        The game window where everything is drawn.
    """
    letters = "abcdefgh"  # File labels.
    font = pygame.font.SysFont("Arial", 15)  # Font for the labels.
    colors = ((255, 204, 117), (153, 102, 51))  # Colors for the labels.
    white = 0  # A flag to alternate label colors.

    for i in range(1, len(letters) + 1):
        # Draw file labels at the bottom of the board.
        f = font.render(letters[i - 1], True, colors[white])
        screen.blit(
            f,
            (
                64 * i + i * 11 - 10 + (3 if letters[i - 1] == "f" else 0),
                HEIGHT
                - 15
                - (3 if letters[i - 1] == "g" or letters[i - 1] == "h" else 0),
            ),
        )
        # Draw rank labels on the left side of the board.
        f = font.render(str(i), True, colors[(white if not white else 1)])
        screen.blit(f, (1, 75 * (9 - i) - 75))
        white = 1 - white  # Alternate the color.


def setPyGameValues() -> p.Surface:
    """
    Initializes Pygame settings and creates the game window.

    :Returns:
    - p.Surface: The game window surface.
    """
    global CLOCK
    p.init()  # Initialize all imported Pygame modules.
    p.display.set_caption("CHESS IN PYTHON")  # Set the window title.
    CLOCK = p.time.Clock()  # Create a clock object to manage updates.
    return p.display.set_mode((WIDTH, HEIGHT))  # Set up the game window.


def generateValidMoves() -> None:
    """
    Generates all valid moves for the current board state and updates the global variable.
    """
    global validMoves
    validMoves = GameState.genValidMoves(
        GameState.board
    )  # Generate all valid moves for the current board state.


def loadImages() -> None:
    """
    Initializes a global dictionary of images. This function loads images for all chess pieces
    and scales them to fit the squares on the chessboard. It is called once at the start.
    """
    p_names = [
        "wP",
        "wR",
        "wB",
        "wN",
        "wQ",
        "wK",
        "bP",
        "bR",
        "bB",
        "bN",
        "bQ",
        "bK",
    ]  # List of piece names.
    for piece in p_names:
        # Load and scale the image for each piece, then store it in the IMAGES dictionary.
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"./img/{piece}.png"), (SQ_EACH_SIZE, SQ_EACH_SIZE)
        )


def eventHandler(
    toHighlight: list, userClicks: list, screen: p.Surface, possibleMoves: list
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
    genMoves = False
    for event in p.event.get():
        if event.type == p.QUIT:
            p.quit()
            exit("QUIT")
        elif event.type == p.MOUSEBUTTONUP and event.button == 3:
            # Function to highlight selected squares on right-click.
            squareX, squareY = findSquare(*p.mouse.get_pos())
            squareHighlight(squareX, squareY, toHighlight)
            redraw = True
        elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            # Handle left-click for moving pieces.
            possibleMoves.clear()
            genMoves  = handleSquareSelection(
                *p.mouse.get_pos(), userClicks, toHighlight, screen, possibleMoves
            )
            redraw = True
        elif event.type == p.KEYDOWN and event.key == p.K_LEFT:
            # Undo the last move when the left arrow key is pressed.
            redraw = handleLeftButtonDown(userClicks)
            genMoves = redraw
            possibleMoves.clear()
            toHighlight.clear()
            redraw = True
            genMoves = True
    if redraw:
        drawGameState(screen, GameState, userClicks, toHighlight, possibleMoves)
    if genMoves:
        generateValidMoves()


def findSquare(x: int, y: int) -> tuple:
    """
    Converts pixel coordinates to board coordinates.

    :Parameters:
    - x: int
        The x-coordinate in pixels.
    - y: int
        The y-coordinate in pixels.

    :Returns:
    - tuple: The (column, row) on the board.
    """
    x = x // SQ_EACH_SIZE
    y = y // SQ_EACH_SIZE
    return (x, y)


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
    mouseX: int,
    mouseY: int,
    userClicks: list,
    toHighlight: list,
    screen: p.Surface,
    possibleMoves: list,
) -> bool:
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
    redraw = False
    # Check if the click is within bounds.
    if not (mouseX < WIDTH and mouseY < HEIGHT):
        return redraw  # Out of bounds.
    # Get the square coordinates.
    squareX, squareY = findSquare(mouseX, mouseY)
    if len(userClicks) == 1:
        userClicks.append((squareY, squareX))
        # Check for castling move.
        if castleChecks(userClicks):
            castle(userClicks)
            redraw = True
        elif (userClicks[1], userClicks[0]) in validMoves:
            if pawnChecks(userClicks):
                handlePawnPromotion(userClicks, screen, toHighlight, possibleMoves)
            elif enPassantChecks(userClicks):
                makeEnPassant(userClicks)
            else:
                handleMove(userClicks)
            redraw = True
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
    return redraw

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
    for toP, fromP in validMoves:
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


def makeEnPassant(userClicks: list) -> None:
    """
    Executes an en passant move.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).
    """
    moveObj = GameState.moveLog[-1]
    # Create the en passant move.
    moveObj = ChessEngine.Move(
        userClicks,  # Piece moved.
        (moveObj.moverEndSq, userClicks[1]),  # Piece captured.
        GameState.board,
        2,  # Type of move (en passant).
    )
    GameState.makeMove(moveObj)


def castleChecks(userClicks: list) -> bool:
    """
    Checks if castling is possible with the selected pieces.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).

    :Returns:
    - bool: True if castling is possible, False otherwise.
    """
    return (
        GameState.board[userClicks[0][0]][userClicks[0][1]][1] == "K"
        and GameState.board[userClicks[1][0]][userClicks[1][1]][1] == "R"
        and GameState.canCastle(userClicks[0], userClicks[1])
    )


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


def castle(userClicks: list) -> None:
    """
    Executes a castling move.

    :Parameters:
    - userClicks: list
        The list of user clicks (current move).
    """
    GameState.castle(userClicks[0], userClicks[1])


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
    userClicks: list, screen: p.Surface, toHighlight: list, possibleMoves: list
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
    drawGameState(screen, GameState, userClicks, toHighlight, possibleMoves)
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


if __name__ == "__main__":
    main()  # Start the game.
