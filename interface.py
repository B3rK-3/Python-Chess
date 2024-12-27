import pygame as p
import pygame.font

# Set up constants for the game dimensions and settings.
SIZE: int = 8  # The size of the chessboard (8x8).
LIGHT_SQUARE_COLOR: p.Color = p.Color(227, 193, 111)  # Light square color.
DARK_SQUARE_COLOR: p.Color = p.Color(184, 139, 74)  # Dark square color.
HIGHLIGHT_COLOR: tuple = (255, 204, 0, 100)  # Color for highlighting squares.
MOVE_HIGHLIGHT_COLOR: tuple = (255, 255, 102, 200)  # Color for move highlights.
POSSIBLE_MOVES: tuple = (255, 234, 0, 128)  # Color for possible moves highlights.


class UI:
    def __init__(self, width: int, height: int, whiteOnBottom: int = True):
        self.height = height
        self.width = width
        self.SQ_EACH_SIZE: int = (
            height // SIZE
        )  # The size of each square on the chessboard.
        self.IMAGES: dict[
            str, p.Surface
        ] = {}  # A dictionary to store images of the chess pieces.
        self.whiteFirst = whiteOnBottom

    def loadImages(self) -> None:
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
            self.IMAGES[piece] = p.transform.scale(
                p.image.load(
                    f"./img/{(piece if self.whiteFirst else ("b" if piece[0] == "w" else "w") + piece[1])}.png"
                ),
                (self.SQ_EACH_SIZE, self.SQ_EACH_SIZE),
            )

    def draw_board(
        self, screen: p.Surface, draw: list, highlight: list, possibleMoves: list
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
        if self.whiteFirst:
            colors = [
                LIGHT_SQUARE_COLOR,
                DARK_SQUARE_COLOR,
            ]  # Light and dark square colors.
        else:
            colors = [
                DARK_SQUARE_COLOR,
                LIGHT_SQUARE_COLOR,
            ]  # Light and dark square colors.
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
                        (
                            c * self.SQ_EACH_SIZE,
                            r * self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                        ),
                    )
                    color = MOVE_HIGHLIGHT_COLOR
                    modified = True
                if modified:
                    # Create a semi-transparent surface for highlights.
                    overlay = p.Surface(
                        (self.SQ_EACH_SIZE, self.SQ_EACH_SIZE), p.SRCALPHA
                    )  # Use SRCALPHA for transparency.
                    p.draw.rect(
                        screen,
                        color,
                        (
                            c * self.SQ_EACH_SIZE,
                            r * self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                        ),
                    )
                else:
                    p.draw.rect(
                        screen,
                        color,
                        (
                            c * self.SQ_EACH_SIZE,
                            r * self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                        ),
                    )
        for r, c in possibleMoves:
            # Create a semi-transparent surface for possible moves.
            overlay = p.Surface(
                (self.SQ_EACH_SIZE, self.SQ_EACH_SIZE), p.SRCALPHA
            )  # Use SRCALPHA for transparency.
            overlay.fill(
                POSSIBLE_MOVES
            )  # Add an alpha value (0-255), 128 is semi-transparent.
            # Draw the transparent rectangle on the screen.
            screen.blit(overlay, (c * self.SQ_EACH_SIZE, r * self.SQ_EACH_SIZE))

    def draw_places(self, screen: p.Surface, flipped: bool = False) -> None:
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
            f = font.render(
                letters[i - 1], True, colors[(1 - white if flipped else white)]
            )
            screen.blit(
                f,
                (
                    64 * i + i * 11 - 10 + (3 if letters[i - 1] == "f" else 0),
                    self.height - 17 - (3 if letters[i - 1] == "g" else 0),
                ),
            )
            # Draw rank labels on the left side of the board.
            f = font.render(
                str((9 - i if flipped else i)),
                True,
                colors[(1 - white if flipped else white)],
            )
            screen.blit(f, (1, 75 * (9 - i) - 75))
            white = 1 - white  # Alternate the color.

    def draw_pieces(
        self, screen: p.Surface, board: list, flipped: bool = False
    ) -> None:
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
                        self.IMAGES[pc]
                        if not flipped
                        else p.transform.flip(self.IMAGES[pc], False, True),
                        p.Rect(
                            c * self.SQ_EACH_SIZE,
                            r * self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                            self.SQ_EACH_SIZE,
                        ),
                    )

    def setPyGameValues(self) -> p.Surface:
        """
        Initializes Pygame settings and creates the game window.

        :Returns:
        - p.Surface: The game window surface.
        """
        global CLOCK
        p.init()  # Initialize all imported Pygame modules.
        p.display.set_caption("CHESS IN PYTHON")  # Set the window title.
        CLOCK = p.time.Clock()  # Create a clock object to manage updates.
        return (
            p.display.set_mode((self.width, self.height)),
            CLOCK,
        )  # Set up the game window.

    def findSquare(self, x: int, y: int, flipped: bool = False) -> tuple:
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
        x = x // self.SQ_EACH_SIZE
        y = ((600 - y) if flipped else y) // self.SQ_EACH_SIZE
        print(x, y)
        return (x, y)
