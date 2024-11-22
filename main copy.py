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
IMAGES = {}  # A dictionary to store images of the chess pieces.


def load_images():
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


def main():
    """
    The main driver for the chess game. This function handles user input and updates the graphics.
    """
    p.init()  # Initialize all imported pygame modules.
    load_images()  # Load images once to save memory.
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Set up the game window.
    p.display.set_caption("CHESS IN PYTHON")  # Set the window title.
    clock = p.time.Clock()  # Create a clock object to manage updates.
    FPS = MAX_FPS  # Set the frames per second.
    gs = (
        ChessEngine.GameState()
    )  # Create a GameState object to keep track of the game state.
    running = True  # A flag to control the main loop.
    move = []  # A list to store the player's move as two positions.
    mpx = 0  # Mouse position x-coordinate.
    mpy = 0  # Mouse position y-coordinate.
    vMoves = gs.genValidMoves(
        gs.board
    )  # Generate all valid moves for the current board state.
    highlight = []  # A list to keep track of squares to highlight.
    en_passant = False  # A flag for en passant moves (not used directly here).

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                # If the user clicks the close button, exit the game.
                running = False
                exit("QUIT")
            elif e.type == p.MOUSEBUTTONUP and e.button == 3:
                # Right mouse button released; used for highlighting squares.
                hx, hy = p.mouse.get_pos()  # Get the mouse position.
                hy = (
                    hy // SQ_EACH_SIZE
                )  # Convert pixel coordinates to board coordinates.
                hx = hx // SQ_EACH_SIZE
                if (hy, hx) not in highlight:
                    highlight.append((hy, hx))  # Add the square to the highlight list.
                else:
                    highlight.remove(
                        (hy, hx)
                    )  # Remove the square from the highlight list if it's already highlighted.
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                # Left mouse button pressed; potential start of a move.
                mx, my = p.mouse.get_pos()  # Get the mouse position.
                # If the move list has two positions and the move is invalid, clear the move list.
                if (
                    len(move) == 2
                    and ((move[1][0], move[1][1]), (move[0][0], move[0][1]))
                    not in vMoves
                ):
                    move.clear()
                if mx < WIDTH and my < HEIGHT:
                    mpx = (
                        mx // SQ_EACH_SIZE
                    )  # Convert pixel coordinates to board coordinates.
                    mpy = my // SQ_EACH_SIZE
                    move.append((mpy, mpx))  # Append the position to the move list.
                    print(move, "DOWN")
                    # If the move list has two positions and the move is invalid, reset the move list.
                    if len(move) == 2 and (
                        ((move[1][0], move[1][1]), (move[0][0], move[0][1]))
                        not in vMoves
                        and (
                            gs.board[move[0][0]][move[0][1]][1] != "K"
                            and gs.board[move[1][0]][move[1][1]][1] != "R"
                        )
                    ):
                        print("Reset the move tuple")
                        move = [move[1]]

            elif e.type == p.MOUSEBUTTONUP and e.button == 1:
                # Left mouse button released; potential end of a move.
                mx, my = p.mouse.get_pos()
                my = (
                    my // SQ_EACH_SIZE
                )  # Convert pixel coordinates to board coordinates.
                mx = mx // SQ_EACH_SIZE
                if (my, mx) not in move:
                    move.append((my, mx))  # Append the position to the move list.
                print(move, "UP")
                if (
                    len(move) == 2 and gs.board[move[0][0]][move[0][1]] != "__"
                ):  # Ensure the starting square is not empty.
                    # Check for pawn promotion.
                    if (
                        ((move[1][0], move[1][1]), (move[0][0], move[0][1])) in vMoves
                        and gs.board[move[0][0]][move[0][1]][1] == "P"
                        and ((move[1][0] == 0) or (move[1][0] == 7))
                    ):
                        # Handle pawn promotion.
                        moveC = ChessEngine.Move(move[0], move[1], gs.board)
                        gs.makeMove(moveC, None)
                        draw_game_state(screen, gs, move, highlight)
                        p.display.flip()
                        gs.pawnPromotion(
                            ((move[1][0], move[1][1]), (move[0][0], move[0][1])), screen
                        )
                        vMoves = gs.genValidMoves(gs.board)  # Generate new valid moves.
                    else:
                        # Check for en passant move.
                        if (
                            (move[1][0], move[1][1]),
                            (move[0][0], move[0][1]),
                        ) in vMoves and gs.isEnPassant(
                            ((move[0][0], move[0][1]), (move[1][0], move[1][1]))
                        ):
                            pass  # En passant move handled within make_if_en_passant.
                        else:
                            # Check for castling move.
                            if (
                                gs.board[move[0][0]][move[0][1]][1] == "K"
                                and gs.board[move[1][0]][move[1][1]][1] == "R"
                                and gs.canCastle(move[0], move[1])
                            ):
                                print("Castle")
                                gs.castle(move[0], move[1])
                                vMoves = gs.genValidMoves(
                                    gs.board
                                )  # Generate new valid moves.
                            elif (
                                (move[1][0], move[1][1]),
                                (move[0][0], move[0][1]),
                            ) in vMoves:
                                # Make a regular move.
                                moveC = ChessEngine.Move(move[0], move[1], gs.board)
                                gs.makeMove(moveC, None)
                                highlight = []  # Clear highlights after a move.
                                vMoves = gs.genValidMoves(
                                    gs.board
                                )  # Generate new valid moves.
                                mpx, mpy = 1000, 1000  # Reset mouse positions.
                            else:
                                # If the move is invalid, reset the move list.
                                move = [move[1]]
                elif len(move) == 2:
                    # If the starting square is empty, reset the move list.
                    move = [move[1]]
            elif e.type == p.KEYDOWN:
                # Handle key presses.
                if e.key == p.K_LEFT:
                    # Undo the last move when the left arrow key is pressed.
                    gs.undoMove()
                    vMoves = gs.genValidMoves(gs.board)  # Generate new valid moves.
                    move.clear()  # Clear the move list.

            p.display.flip()  # Update the display.
        draw_game_state(screen, gs, move, highlight)  # Draw the current game state.
        clock.tick(MAX_FPS)  # Control the game's frame rate.
        p.display.flip()  # Update the display.



def draw_game_state(screen, gs, draw, highlight):
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
    pass
if __name__ == "__main__":
    main()  # Start the game.
