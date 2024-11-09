"""
Main.py file is responsible for running the game engine. Will handle user input and GUI.
"""

import pygame as p
import pygame.font

import ChessEngine

# Set up constants for the game dimensions and settings.
WIDTH = HEIGHT = 600  # The height and width of the game window.
SIZE = 8  # The size of the chessboard (8x8).
SQ_EACH_SIZE = HEIGHT // SIZE  # The size of each square on the chessboard.
MAX_FPS = 15  # Maximum frames per second (controls the game speed).

# Global Game Values
IMAGES = {}  # A dictionary to store images of the chess pieces.
GameState = (
    ChessEngine.GameState()
)  # Create a GameState object to keep track of the game state.
CLOCK = None
validMoves = None

def main():
    """
    The main driver for the chess game. This function handles user input and updates the graphics.
    """
    screen = setPyGameValues()
    loadImages()  # Load images once to save memory.
    generateValidMoves()
    userClicks = []  # A list to store the user clicks
    toHighlight = []  # A list to keep track of squares to highlight.
    drawGameState(screen, GameState, userClicks, toHighlight)
    p.display.flip()
    while True:
        eventHandler(toHighlight, userClicks, screen)


def drawGameState(screen, gs, draw, highlight):
    """
    Responsible for drawing the current game state on the screen.
    :param screen: The game window where everything is drawn.
    :param gs: The current game state object.
    :param draw: A list of squares involved in the current move.
    :param highlight: A list of squares to highlight.
    """
    draw_board(screen, draw, highlight)  # Draw the chessboard.
    draw_pieces(screen, gs.board)  # Draw the chess pieces on the board.
    draw_places(screen)  # Draw the ranks and files labels.


def draw_board(screen, draw, highlight):
    """
    Draw the chessboard with alternating colors and highlighted squares.
    :param screen: The game window where everything is drawn.
    :param draw: A list of squares involved in the current move.
    :param highlight: A list of squares to highlight.
    """
    white = True  # A flag to alternate between white and black squares.
    for r in range(SIZE):
        for c in range(SIZE):
            if (r, c) in highlight:
                # Highlight specific squares (e.g., selected or targeted squares).
                p.draw.rect(
                    screen,
                    p.Color(255, 204, 0),  # Color for highlighted squares.
                    (c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE),
                )
            else:
                if (r, c) in draw:
                    # Highlight squares involved in the current move.
                    p.draw.rect(
                        screen,
                        p.Color(255, 255, 102),  # Color for move highlights.
                        (
                            c * SQ_EACH_SIZE,
                            r * SQ_EACH_SIZE,
                            SQ_EACH_SIZE,
                            SQ_EACH_SIZE,
                        ),
                    )
                else:
                    # Draw regular squares with alternating colors.
                    if white:
                        # Light squares.
                        p.draw.rect(
                            screen,
                            p.Color(227, 193, 111),  # Light square color.
                            (
                                c * SQ_EACH_SIZE,
                                r * SQ_EACH_SIZE,
                                SQ_EACH_SIZE,
                                SQ_EACH_SIZE,
                            ),
                        )
                    else:
                        # Dark squares.
                        p.draw.rect(
                            screen,
                            p.Color(184, 139, 74),  # Dark square color.
                            (
                                c * SQ_EACH_SIZE,
                                r * SQ_EACH_SIZE,
                                SQ_EACH_SIZE,
                                SQ_EACH_SIZE,
                            ),
                        )
            white = not white  # Switch color for the next square.
        white = not white  # Switch color at the end of each row.


def draw_pieces(screen, board):
    """
    Draw the chess pieces on the board.
    :param screen: The game window where everything is drawn.
    :param board: The current state of the chessboard.
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


def draw_places(screen):
    """
    Draw the rank (numbers) and file (letters) labels on the board.
    :param screen: The game window where everything is drawn.
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
        if not white:
            white += 1
        else:
            white -= 1


def setPyGameValues():
    global CLOCK
    p.init()  # Initialize all imported pygame modules.
    p.display.set_caption("CHESS IN PYTHON")  # Set the window title.
    CLOCK = p.time.Clock()  # Create a clock object to manage updates.
    return p.display.set_mode((WIDTH, HEIGHT))  # Set up the game window.

def generateValidMoves():
    global validMoves
    validMoves = GameState.genValidMoves(
        GameState.board
    )  # Generate all valid moves for the current board state.


def loadImages():
    """
    Initialize a global dictionary of images. This function loads images for all chess pieces
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


def eventHandler(toHighlight, userClicks, screen):
    for event in p.event.get():
        if event.type == p.QUIT:
            p.quit()
            exit("QUIT")
        elif event.type == p.MOUSEBUTTONUP and event.button == 3:
            # Function to highlight selected squares
            squareX, squareY = findSquare(*p.mouse.get_pos())
            squareHighlight(squareX, squareY, toHighlight)
            generateValidMoves()  # Generate new valid moves.
            toHighlight.clear()
            drawGameState(screen, GameState, userClicks, toHighlight)
        elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            handleSquareSelection(*p.mouse.get_pos(), userClicks, toHighlight, screen)
            generateValidMoves()  # Generate new valid moves.
            toHighlight.clear()
            drawGameState(screen, GameState, userClicks, toHighlight)
        elif event.type == p.KEYDOWN and event.key == p.K_LEFT:
            handleLeftButtonDown(userClicks)
            generateValidMoves()  # Generate new valid moves.
            toHighlight.clear()
            drawGameState(screen, GameState, userClicks, toHighlight)
        CLOCK.tick(MAX_FPS)  # Control the game's frame rate.
        p.display.flip()  # Update the display.


def findSquare(x, y):
    # Convert pixel coordinates to board coordinates.
    x = x // SQ_EACH_SIZE
    y = y // SQ_EACH_SIZE
    return (x, y)


def handleLeftButtonDown(userClicks):
    # Undo the last move when the left arrow key is pressed.
    GameState.undoMove()
    userClicks.clear()  # Clear the move list.


def squareHighlight(x, y, toHighlight):
    if (y, x) not in toHighlight:
        toHighlight.append((y, x))  # Add the square to the highlight list.
    else:
        toHighlight.remove(
            (y, x)
        )  # Remove the square from the highlight list if it's already highlighted.


def handleSquareSelection(mouseX, mouseY, userClicks, toHighlight, screen):
    # Check its within bounds
    # Not elif because we still want to update after clearing the userClicks
    if mouseX < WIDTH and mouseY < HEIGHT:
        # Get the square coords
        squareX, squareY = findSquare(mouseX, mouseY)
        if len(userClicks) == 1:
            userClicks.append((squareY, squareX))
            print(userClicks, "Mouse Down")
            # Check for castling move.
            if (
                GameState.board[userClicks[0][0]][userClicks[0][1]][1] == "K"
                and GameState.board[userClicks[1][0]][userClicks[1][1]][1] == "R"
                and GameState.canCastle(userClicks[0], userClicks[1])
            ):
                GameState.castle(userClicks[0], userClicks[1])
                print("Made Castle Move")
            elif (userClicks[1], userClicks[0]) in validMoves:
                if GameState.board[userClicks[0][0]][userClicks[0][1]][1] == "P" and (
                    (userClicks[1][0] == 0) or (userClicks[1][0] == 7)
                ):
                    print("Pawn Promotion")
                    handlePawnPromotion(userClicks, screen, toHighlight)  # TODO: Freezes
                elif GameState.make_if_en_passant((userClicks[0], userClicks[1])):
                    print(
                        "Made En Passant Move"
                    )  # En passant move handled within make_if_en_passant.
                else:
                    print("Regular Move")
                    # Make a regular move.
                    move = ChessEngine.Move(
                        userClicks[0], userClicks[1], GameState.board
                    )
                    GameState.makeMove(move, None)
            else:
                print("reset")
                userClicks[0] = userClicks[1]
                del userClicks[1]  # Delete the item at index 1
        elif len(userClicks) == 2:
            print("Remove Extra")
            userClicks.clear()
            userClicks.append((squareY, squareX))
        else:
            print("Append point")
            userClicks.append((squareY, squareX))


def handlePawnPromotion(userClicks, screen, toHighlight):
    # Handle pawn promotion
    drawGameState(screen, GameState, userClicks, toHighlight)
    p.display.flip()
    piece = GameState.pawnPromotion(
        ((userClicks[1][0], userClicks[1][1]), (userClicks[0][0], userClicks[0][1])),
        screen,
    )
    print(2)
    move = ChessEngine.Move(userClicks[0], userClicks[1], GameState.board)
    GameState.makeMove(move, None)
    GameState.movePiece(*userClicks[1], piece)
    print(3)
    
    """ # Handle pawn promotion.
    moveC = ChessEngine.Move(move[0], move[1], GameState.board)
    GameState.makeMove(moveC, None)
    drawGameState(screen, GameState, move, toHighlight)
    p.display.flip()
    GameState.pawnPromotion(
        ((move[1][0], move[1][1]), (move[0][0], move[0][1])), screen
    )"""


if __name__ == "__main__":
    main()  # Start the game.
