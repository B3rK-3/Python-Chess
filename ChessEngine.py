import pygame as p
from typing import List


class GameState:
    def __init__(self):
        """
        Initializes the GameState object with the starting board configuration,
        sets the initial turn to white, and initializes the move log.

        :Attributes:
        - board: list
            A 2D list representing the chess board. Each element represents a square on the board.
            The notation is as follows: 'bR' = black rook, 'wR' = white rook, '__' = empty square, etc.
        - isWhiteTurn: bool
            Indicates whose turn it is; True if it's white's turn, False if black's.
        - moveLog: List["Move"]
            A log to keep track of all moves made in the game.
        """
        # Initialize the chess board as a 2D list. Each element represents a square on the board.
        # The notation is as follows: 'bR' = black rook, 'wR' = white rook, '__' = empty square, etc.
        self.board = [
            ["bR", "__", "__", "__", "bK", "__", "__", "bR"],
            ["bP", "bP", "wP", "__", "bP", "bP", "wP", "bP"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "bP", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["wP", "wP", "wP", "wP", "__", "wP", "wP", "wP"],
            ["wR", "__", "__", "__", "wK", "__", "__", "wR"],
        ]
        # Indicates whose turn it is; True if it's white's turn, False if black's.
        self.isWhiteTurn = True
        # A log to keep track of all moves made in the game.
        self.moveLog: List["Move"] = []

    def makeMove(self, moveObj: "Move") -> None:
        """
        Executes a move on the board.

        :Parameters:
        - moveObj: Move
            The move object containing the move details.
        """
        # Handles making a move on the board.

        # Remove the other piece (if any) from its starting square.
        self.board[moveObj.otherStartSq[0]][moveObj.otherStartSq[1]] = "__"
        # Place the other piece (if any) to its ending square.
        self.board[moveObj.otherEndSq[0]][moveObj.otherEndSq[1]] = moveObj.pieceOther
        # Remove the moving piece from its starting square.
        self.board[moveObj.moverStartSq[0]][moveObj.moverStartSq[1]] = "__"
        if moveObj.type == 3:
            # Handle promotion move: replace the pawn with the promoted piece.
            self.board[moveObj.moverEndSq[0]][moveObj.moverEndSq[1]] = (
                moveObj.pieceMoved[0] + moveObj.promotedTo
            )
        else:
            # Move the piece to its ending square.
            self.board[moveObj.moverEndSq[0]][moveObj.moverEndSq[1]] = (
                moveObj.pieceMoved
            )
        # Switch turn to the other player.
        self.isWhiteTurn = not self.isWhiteTurn
        # Add the move to the move log.
        self.moveLog.append(moveObj)
        print("Move: ", moveObj)

    def undoMove(self) -> None:
        """
        Undoes the last move made on the board.
        """
        # Undo the last move made.
        if len(self.moveLog) > 0:
            # Get the last move from the move log.
            moveObj = self.moveLog.pop()
            # Remove the piece from its ending square (other piece, e.g., rook in castling).
            self.board[moveObj.otherEndSq[0]][moveObj.otherEndSq[1]] = "__"
            # Remove the moving piece from its ending square.
            self.board[moveObj.moverEndSq[0]][moveObj.moverEndSq[1]] = "__"
            # Restore the other piece to its starting square.
            self.board[moveObj.otherStartSq[0]][moveObj.otherStartSq[1]] = (
                moveObj.pieceOther
            )
            # Restore the moving piece to its starting square.
            self.board[moveObj.moverStartSq[0]][moveObj.moverStartSq[1]] = (
                moveObj.pieceMoved
            )
            # Switch turn back to the previous player.
            self.isWhiteTurn = not self.isWhiteTurn

    def canCastle(self, kingPos: tuple, rookPos: tuple) -> bool:
        """
        Determines if castling is possible for the given king and rook positions.

        :Parameters:
        - kingPos: tuple
            The current position of the king (row, column).
        - rookPos: tuple
            The current position of the rook (row, column).

        :Returns:
        - bool: True if castling is possible, False otherwise.
        """
        # Generate possible castling moves.

        # Initialize a list to keep track of the starting squares of all moves made.
        logs = []  # Accounts for moves like en passant, which are tuples in self.moveLog.
        for moveObj in self.moveLog:
            logs.append(moveObj.moverStartSq)
        if self.isWhiteTurn:
            # Set initial positions for white king and rooks.
            king = (7, 4)
            rooks = {(7, 0), (7, 7)}
        else:
            # Set initial positions for black king and rooks.
            king = (0, 4)
            rooks = {(0, 0), (0, 7)}

        # Check if the king or the rook have moved from their initial positions.
        if kingPos != king or rookPos not in rooks:
            return False  # Cannot castle if king or rook have moved.
        for log in logs:
            if king == log:
                return False  # King has moved before.
            elif log in rooks:
                rooks.remove(log)  # Remove the rook that has moved.
        if not rooks:
            return False  # Both rooks have moved; cannot castle.
        # Generate opponent's moves to check for threats along the castling path.
        self.isWhiteTurn = not self.isWhiteTurn  # Switch turn to opponent.
        oppM = [x[0] for x in self.genValidMoves(self.board)]  # Generate opponent's moves.
        self.isWhiteTurn = not self.isWhiteTurn  # Switch turn back.

        # Check if any opponent's move attacks the king's row.
        row = kingPos[0]
        for r, _ in oppM:
            if r == row:
                return False  # Cannot castle if king is in check or passes through check.
        return True  # Castling is possible.

    def castle(self, kingPos: tuple, rookPos: tuple) -> None:
        """
        Performs a castling move on the board.

        :Parameters:
        - kingPos: tuple
            The current position of the king (row, column).
        - rookPos: tuple
            The current position of the rook (row, column).
        """
        if rookPos[1] == 7:  # Short Castle
            # Create a move object for short castling.
            moveObj = Move(
                (kingPos, (kingPos[0], 6)), (rookPos, (rookPos[0], 5)), self.board, 1
            )
        else:  # Long Castle
            # Create a move object for long castling.
            moveObj = Move(
                (kingPos, (kingPos[0], 2)), (rookPos, (rookPos[0], 3)), self.board, -1
            )
        self.makeMove(moveObj)  # Execute the castling move.

    def isEnPassant(self, move: tuple) -> bool:
        """
        Determines if the given move is an en passant move.

        :Parameters:
        - move: tuple
            The move being made, represented as ((start_row, start_col), (end_row, end_col)).

        :Returns:
        - bool: True if the move is an en passant, False otherwise.
        """
        # Handle en passant move if applicable.
        if len(self.moveLog) >= 1:
            # Get the last move made.
            moveObj = self.moveLog[-1]
            # Check if the last move was a pawn moving two squares forward.
            if (
                moveObj.pieceMoved[1] == "P"  # Last moved piece was a pawn.
                and abs(moveObj.moverStartSq[0] - moveObj.moverEndSq[0]) == 2  # Moved two squares.
                and move[1][1] == moveObj.moverEndSq[1]  # Same column as the pawn.
                and move[0][0] == moveObj.moverEndSq[0]  # Capturing pawn is next to the moved pawn.
                and (
                    (self.isWhiteTurn and move[1][0] - moveObj.moverEndSq[0] == -1)  # White pawn moving up.
                    or (
                        not self.isWhiteTurn and move[1][0] - moveObj.moverEndSq[0] == 1  # Black pawn moving down.
                    )
                )
            ):
                return True  # En passant is possible.
        return False  # Not an en passant move.

    def genValidMoves(self, board: list) -> list:
        """
        Generates all valid moves for the current player, accounting for checks and checkmates.

        :Parameters:
        - board: list
            The current board state.

        :Returns:
        - list: A list of valid moves.
        """
        # Generate all possible moves (not necessarily valid).
        self.posMoves = self.genPossibleMoves(board)
        # Get the position of the current player's king.
        self.kingPos = self.posOfPiece("wK" if self.isWhiteTurn else "bK")[0]
        # Check if the king is in check.
        numOfChecks = self.checkAroundKing(self.kingPos)
        if self.posMoves == [] and numOfChecks:
            # If there are no valid moves and the king is in check, it's checkmate.
            print("Checkmate!", ("Black wins!" if self.isWhiteTurn else "White wins!"))
        elif self.posMoves == []:
            # If there are no valid moves but the king is not in check, it's stalemate.
            print("Stalemate!")
        return self.posMoves


    def genPossibleMoves(self, board: list) -> list:
        """
        Generates all possible moves for the current player, without considering checks.

        :Parameters:
        - board: list
            The current state of the board.

        :Returns:
        - list: A list of all possible moves for the current player.
        """
        possibleMoves = []
        colors = ["w", "b"]  # Define colors for white and black pieces.
        turn = 0 if self.isWhiteTurn else 1  # Determine whose turn it is.
        for row in range(len(board)):
            for col in range(len(board[0])):
                piece = board[row][col]
                if piece[0] == colors[turn]:
                    # Generate moves based on the piece type.
                    if piece[1] == "P":
                        self.pawnMoves(
                            row,
                            col,
                            piece,
                            board,
                            possibleMoves,
                            colors[1 - turn],  # Opponent's color.
                        )
                    elif piece[1] == "N":
                        self.knightMoves(row, col, piece, board, possibleMoves)
                    elif piece[1] == "R":
                        self.rookMoves(row, col, piece, board, possibleMoves)
                    elif piece[1] == "B":
                        self.bishopMoves(row, col, piece, board, possibleMoves)
                    elif piece[1] == "Q":
                        self.queenMoves(row, col, piece, board, possibleMoves)
                    elif piece[1] == "K":
                        self.kingMoves(row, col, piece, board, possibleMoves)
        return possibleMoves

    def pawnMoves(
        self,
        row: int,
        col: int,
        piece: str,
        board: list,
        possibleMoves: list,
        oColor: str,
    ) -> None:
        """
        Generates all possible pawn moves from the given position.

        :Parameters:
        - row: int
            The row index of the pawn.
        - col: int
            The column index of the pawn.
        - piece: str
            The piece representation (e.g., 'wP' for white pawn).
        - board: list
            The current state of the board.
        - possibleMoves: list
            The list to append possible moves to.
        - oColor: str
            The opponent's color ('w' for white, 'b' for black).
        """
        # Handle en passant conditions.
        if len(self.moveLog) >= 1:
            moveObj = self.moveLog[-1]  # Get the last move made.
            if (
                moveObj.pieceMoved[1] == "P"  # Last moved piece was a pawn.
                and abs(moveObj.moverEndSq[0] - moveObj.moverStartSq[0]) == 2  # Moved two squares.
                and row == moveObj.moverEndSq[0]  # Pawn is on the same rank as the moved pawn.
            ):
                if col + 1 == moveObj.moverEndSq[1]:
                    # Check for en passant capture to the right.
                    if oColor == "b":
                        possibleMoves.append(((row - 1, col + 1), (row, col)))
                    else:
                        possibleMoves.append(((row + 1, col + 1), (row, col)))
                if col - 1 == moveObj.moverEndSq[1]:
                    # Check for en passant capture to the left.
                    if oColor == "b":
                        possibleMoves.append(((row - 1, col - 1), (row, col)))
                    else:
                        possibleMoves.append(((row + 1, col - 1), (row, col)))
        if piece[0] == "w":
            # White pawn moves.
            if row == 6 and board[row - 1][col] == "__" and board[row - 2][col] == "__":
                # Pawn's first move can be two squares forward if both squares are empty.
                possibleMoves.append(((row - 2, col), (row, col)))
            if board[row - 1][col] == "__":
                # Move one square forward if the square is empty.
                possibleMoves.append(((row - 1, col), (row, col)))
            if col - 1 >= 0 and board[row - 1][col - 1][0] == "b":
                # Capture diagonally to the left if there is a black piece.
                possibleMoves.append(((row - 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row - 1][col + 1][0] == "b":
                # Capture diagonally to the right if there is a black piece.
                possibleMoves.append(((row - 1, col + 1), (row, col)))
        elif piece[0] == "b":
            # Black pawn moves.
            if row == 1 and board[row + 1][col] == "__" and board[row + 2][col] == "__":
                # Pawn's first move can be two squares forward if both squares are empty.
                possibleMoves.append(((row + 2, col), (row, col)))
            if board[row + 1][col] == "__":
                # Move one square forward if the square is empty.
                possibleMoves.append(((row + 1, col), (row, col)))
            if col - 1 >= 0 and board[row + 1][col - 1][0] == "w":
                # Capture diagonally to the left if there is a white piece.
                possibleMoves.append(((row + 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row + 1][col + 1][0] == "w":
                # Capture diagonally to the right if there is a white piece.
                possibleMoves.append(((row + 1, col + 1), (row, col)))

    def pawnPromotion(self, move: list, screen: p.Surface) -> str:
        """
        Handles pawn promotion when a pawn reaches the opposite end of the board.

        :Parameters:
        - move: list
            The move being made, represented as a list of positions.
        - screen:
            The game screen to display the promotion options.

        :Returns:
        - str: The piece to promote to ('R', 'B', 'N', or 'Q').
        """
        running = True
        p_names = ["wR", "wB", "wN", "wQ", "bR", "bB", "bN", "bQ"]  # Possible promotion pieces.
        IMAGES = {}
        color = ""
        font = p.font.SysFont("Arial", 15)  # Set the font for text display.
        # Load images for promotion options.
        for e in p_names:
            IMAGES[e] = p.transform.scale(p.image.load("img/" + e + ".png"), (75, 75))
        if self.isWhiteTurn:
            # If it's white's turn, set up the promotion options for white.
            color = "w"
            shift = 75 * (move[0][1] - 4) if move[0][1] > 4 else 0
            # Draw the promotion selection rectangle.
            rect = p.draw.rect(
                screen,
                (255, 204, 117),  # Background color.
                (move[0][1] * 75 - shift, (move[0][0]) * 75 + 100, 4 * 75, 90),
                border_radius=5,
            )
            rect = p.draw.rect(
                screen,
                (0, 0, 0),  # Border color.
                (move[0][1] * 75 - shift, (move[0][0]) * 75 + 100, 300, 90),
                2,
                5,
            )
            for i in range(4):
                # Display each promotion option.
                screen.blit(
                    IMAGES[p_names[i]],  # The image of the piece.
                    p.Rect(
                        i * 75 + move[0][1] * 75 - 5 - shift,
                        (move[0][0]) * 75 + 100,
                        75,
                        75,
                    ),
                )
                f = font.render(str(i + 1), True, (0, 0, 0))  # Render the option number.
                screen.blit(
                    f,
                    p.Rect(
                        i * 75 + move[0][1] * 75 + 30 - shift,
                        (move[0][0]) * 75 + 170,
                        75,
                        75,
                    ),
                )
        else:
            # If it's black's turn, set up the promotion options for black.
            color = "b"
            shift = 75 * (move[0][1] - 4) if move[0][1] > 4 else 0
            # Draw the promotion selection rectangle.
            rect = p.draw.rect(
                screen,
                (255, 204, 117),  # Background color.
                (move[0][1] * 75 - shift, (move[0][0]) * 75 - 100, 4 * 75, 90),
                border_radius=5,
            )
            rect = p.draw.rect(
                screen,
                (0, 0, 0),  # Border color.
                (move[0][1] * 75 - shift, (move[0][0]) * 75 - 100, 300, 90),
                2,
                5,
            )
            for i in range(4, len(p_names)):
                # Display each promotion option.
                screen.blit(
                    IMAGES[p_names[i]],  # The image of the piece.
                    p.Rect(
                        i * 75 + move[0][1] * 75 - 303 - shift,
                        (move[0][0]) * 75 - 100,
                        75,
                        75,
                    ),
                )
                f = font.render(str(i - 3), True, (0, 0, 0))  # Render the option number.
                screen.blit(
                    f,
                    p.Rect(
                        i * 75 + move[0][1] * 75 - 268.5 - shift,
                        (move[0][0]) * 75 - 28,
                        75,
                        75,
                    ),
                )
        p.display.flip()  # Update the display.
        while running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                    exit("QUIT")  # Exit the game.
                elif e.type == p.KEYDOWN or e.type == p.KEYUP:
                    # Handle user input for promotion selection.
                    if e.key == p.K_1:
                        running = False
                        return "R"  # Promote to Rook.
                    elif e.key == p.K_2:
                        running = False
                        return "B"  # Promote to Bishop.
                    elif e.key == p.K_3:
                        running = False
                        return "N"  # Promote to Knight.
                    elif e.key == p.K_4:
                        running = False
                        return "Q"  # Promote to Queen.
        return None

    def knightMoves(
        self,
        row: int,
        col: int,
        piece: str,
        board: list,
        possibleMoves: list,
    ) -> None:
        """
        Generates all possible knight moves from the given position.

        :Parameters:
        - row: int
            The row index of the knight.
        - col: int
            The column index of the knight.
        - piece: str
            The piece representation (e.g., 'wN' for white knight).
        - board: list
            The current state of the board.
        - possibleMoves: list
            The list to append possible moves to.
        """
        # List of possible moves a knight can make.
        knight_moves = [
            (2, -1),
            (2, 1),    # Moves two squares down, one square left/right.
            (-2, -1),
            (-2, 1),   # Moves two squares up, one square left/right.
            (1, 2),
            (-1, 2),   # Moves one square up/down, two squares right.
            (1, -2),
            (-1, -2),  # Moves one square up/down, two squares left.
        ]
        for move in knight_moves:
            r = row + move[0]
            c = col + move[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c][0] != piece[0]:
                    # Add the move if the destination is empty or contains an opponent's piece.
                    possibleMoves.append(((r, c), (row, col)))


    def rookMoves(self, row: int, col: int, piece: str, board: list, possibleMoves: list) -> None:
        """
        Generate all possible rook moves from the given position.
        """
        # Directions in which a rook can move: up, down, left, right.
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in directions:
            for i in range(1, 8):
                r = row + d[0] * i
                c = col + d[1] * i
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == "__":
                        possibleMoves.append(((r, c), (row, col)))
                    elif board[r][c][0] != piece[0]:
                        possibleMoves.append(((r, c), (row, col)))
                        break
                    else:
                        break
                else:
                    break

    def bishopMoves(self, row: int, col: int, piece: str, board: list, possibleMoves: list) -> None:
        """
        Generate all possible bishop moves from the given position.
        """
        # Directions in which a bishop can move: diagonals.
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in directions:
            for i in range(1, 8):
                r = row + d[0] * i
                c = col + d[1] * i
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == "__":
                        possibleMoves.append(((r, c), (row, col)))
                    elif board[r][c][0] != piece[0]:
                        possibleMoves.append(((r, c), (row, col)))
                        break
                    else:
                        break
                else:
                    break

    def queenMoves(
        self, row: int, col: int, piece: str, board: list, possibleMoves: list
    ) -> None:
        """
        Generates all possible queen moves from the given position.

        :Parameters:
        - row: int
            The row index of the queen.
        - col: int
            The column index of the queen.
        - piece: str
            The piece representation (e.g., 'wQ' for white queen).
        - board: list
            The current state of the board.
        - possibleMoves: list
            The list to append possible moves to.
        """
        # The queen's moves are a combination of rook and bishop moves.
        self.bishopMoves(row, col, piece, board, possibleMoves)
        self.rookMoves(row, col, piece, board, possibleMoves)


    def kingMoves(
        self, row: int, col: int, piece: str, board: list, possibleMoves: list
    ) -> None:
        """
        Generates all possible king moves (one square in any direction) from the given position.

        :Parameters:
        - row: int
            The row index of the king.
        - col: int
            The column index of the king.
        - piece: str
            The piece representation (e.g., 'wK' for white king).
        - board: list
            The current state of the board.
        - possibleMoves: list
            The list to append possible moves to.
        """
        # Directions the king can move: one square in any direction.
        directions = [
            (-1, 0),   # Up
            (1, 0),    # Down
            (0, -1),   # Left
            (0, 1),    # Right
            (-1, 1),   # Up-Right
            (1, 1),    # Down-Right
            (-1, -1),  # Up-Left
            (1, -1),   # Down-Left
        ]
        for d in directions:
            r = row + d[0]
            c = col + d[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c][0] != piece[0]:
                    # Add the move if the destination is empty or contains an opponent's piece.
                    possibleMoves.append(((r, c), (row, col)))


    def posOfPiece(self, piece: str) -> list:
        """
        Returns the positions of a given piece on the board.

        :Parameters:
        - piece: str
            The piece to find positions of (e.g., 'wK' for white king).

        :Returns:
        - list: A list of positions where the piece is located.
        """
        # Initialize a list to store positions.
        pos = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == piece:
                    pos.append((row, col))  # Add the position to the list.
        return pos


    def checkAroundKing(self, king: tuple) -> bool:
        """
        Checks for checks and pins around the king.

        :Parameters:
        - king: tuple
            The position of the king (row, col).

        :Returns:
        - bool: True if the king is in check, False otherwise.
        """
        # Determine the current color and opponent's color.
        currColor = self.board[king[0]][king[1]][0]
        oColor = "w" if currColor == "b" else "b"
        # Possible directions to check around the king.
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        locOwnColor = False  # Flag to indicate if we've encountered our own piece.
        count = 0  # Counter for the number of checks.

        # Check for knight checks and remove illegal king moves.
        self.checkKnightcheck(oColor, self.kingPos)
        self.kingCantMoveWhere()

        for move in kMoves:  # Check all directions around the king.
            for i in range(1, 8):
                r_off = move[0] * i
                c_off = move[1] * i
                r = r_off + king[0]
                c = c_off + king[1]

                if 0 <= r < 8 and 0 <= c < 8:
                    # Get the piece at the current position.
                    piece = self.board[r][c]
                    pColor = piece[0]  # Piece color: 'w' or 'b'.
                    pType = piece[1]   # Piece type: 'Q', 'R', 'B', 'N', 'P', or 'K'.

                    if pColor == currColor:
                        # If we've already encountered our own piece, stop checking this direction.
                        if locOwnColor:
                            break
                        locOwnColor = (r, c)  # Mark the position of our own piece.
                    else:
                        if locOwnColor:
                            # An opponent's piece is behind our own piece, which might be pinned.
                            print("Pin: ", (r, c), "{", move, "} ", piece)
                            self.pinned((r, c), locOwnColor, move, piece[1])
                            locOwnColor = False
                            break
                        # Check for checks from opponent pieces.
                        elif (c_off == 0 or r_off == 0) and (pType in "RQ"):
                            # Straight line checks (rook or queen).
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, True)
                            count += 1
                        elif (c_off != 0 and r_off != 0) and (pType in "BQ"):
                            # Diagonal checks (bishop or queen).
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, False)
                            count += 1
                        elif (
                            (currColor == "w" and r_off == -1 and abs(c_off) == 1)
                            or (currColor == "b" and r_off == 1 and abs(c_off) == 1)
                        ) and (pType == "P"):
                            # Check for pawn checks.
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, False)
                            count += 1
                        else:
                            break
                else:
                    break
            locOwnColor = False  # Reset the flag for the next direction.
        if count > 0:
            self.check = True  # Mark that the king is in check.
        return count > 0


    def remMoves(self, r: int, c: int, vh: bool) -> None:
        """
        Removes illegal moves due to checks, ensuring the king is not left in check.

        :Parameters:
        - r: int
            The row index of the checking piece.
        - c: int
            The column index of the checking piece.
        - vh: bool
            True if the threat is vertical/horizontal, False if diagonal.
        """
        if vh:  # If the threat is vertical or horizontal.
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            if d_row == 0:
                # Threat is horizontal.
                for i in range(len(self.posMoves) - 1, -1, -1):
                    m = self.posMoves[i]
                    if m[1] == self.kingPos and (
                        (d_col > 0 and (m[0][0] == r and self.kingPos[1] > m[0][1] > c))
                        or (
                            d_col < 0
                            and (m[0][0] == r and self.kingPos[1] < m[0][1] < c)
                        )
                    ):
                        # Remove moves that don't block or capture the checking piece.
                        self.posMoves.pop(i)
                    elif m[1] != self.kingPos and (
                        (
                            d_col > 0
                            and not (m[0][0] == r and self.kingPos[1] > m[0][1] >= c)
                        )
                        or (
                            d_col < 0
                            and not (m[0][0] == r and self.kingPos[1] < m[0][1] <= c)
                        )
                    ):
                        self.posMoves.pop(i)
            if d_col == 0:
                # Threat is vertical.
                for i in range(len(self.posMoves) - 1, -1, -1):
                    m = self.posMoves[i]
                    if m[1] == self.kingPos and (
                        (d_row > 0 and (m[0][1] == c and self.kingPos[0] > m[0][0] > r))
                        or (d_row < 0 and (m[0][1] == c and self.kingPos[0] < m[0][0] < r))
                    ):
                        self.posMoves.pop(i)
                    elif m[1] != self.kingPos and (
                        (
                            d_row > 0
                            and not (m[0][1] == c and self.kingPos[0] > m[0][0] >= r)
                        )
                        or (
                            d_row < 0
                            and not (m[0][1] == c and self.kingPos[0] < m[0][0] <= r)
                        )
                    ):
                        self.posMoves.pop(i)
        else:
            # Diagonal threat.
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            d_row = d_row / abs(d_row)
            d_col = d_col / abs(d_col)
            # Build list of positions between the checking piece and the king.
            places = [(r, c), (r + d_row, c + d_col)]
            counter = 2
            while places[-1] != self.kingPos:
                places.append((r + d_row * counter, c + d_col * counter))
                counter += 1
            for i in range(len(self.posMoves) - 1, -1, -1):
                if self.posMoves[i][1] == self.kingPos:
                    if self.posMoves[i][0] == (r, c):
                        continue  # Allow capturing the checking piece.
                    elif self.posMoves[i][0] in places:
                        self.posMoves.pop(i)
                elif self.posMoves[i][0] not in places:
                    self.posMoves.pop(i)


    def kingCantMoveWhere(self) -> None:
        """
        Determines squares where the king cannot move due to threats.
        """
        # Create a copy of the board to test moves.
        b = [row[:] for row in self.board]
        for e in range(len(self.posMoves) - 1, -1, -1):
            piece = self.posMoves[e]
            if piece[1] == self.kingPos:
                # Simulate the king's move.
                b[piece[0][0]][piece[0][1]] = b[self.kingPos[0]][self.kingPos[1]]
                b[self.kingPos[0]][self.kingPos[1]] = "__"
                self.isWhiteTurn = not self.isWhiteTurn
                # Generate opponent's possible moves.
                moves = self.genPossibleMoves(b)
                # If the destination square is attacked, remove the move.
                if (piece[0][0], piece[0][1]) in [x[0] for x in moves]:
                    self.posMoves.pop(e)
                # Revert the simulated move.
                b[piece[0][0]][piece[0][1]] = self.board[piece[0][0]][piece[0][1]]
                b[self.kingPos[0]][self.kingPos[1]] = self.board[self.kingPos[0]][
                    self.kingPos[1]
                ]
                self.isWhiteTurn = not self.isWhiteTurn


    def pinned(
        self, pinner: tuple, pinned: tuple, moveDir: tuple, piece: str
    ) -> None:
        """
        Handles pinning of pieces. Removes moves that would expose the king to check if the piece is pinned.

        :Parameters:
        - pinner: tuple
            The position of the opponent's piece causing the pin (row, col).
        - pinned: tuple
            The position of the pinned piece (row, col).
        - moveDir: tuple
            The direction of the pinning move (row_offset, col_offset).
        - piece: str
            The type of the opponent's piece causing the pin (e.g., 'Q' for queen).
        """
        m_r = moveDir[0]
        m_c = moveDir[1]
        if m_r == 0 or m_c == 0:
            if m_c == 0 and (piece == "R" or piece == "Q"):
                print("Pin: R or Q")
                for i in range(len(self.posMoves) - 1, -1, -1):
                    movePiece = self.posMoves[i][1]
                    if movePiece == pinned:
                        movePlace = self.posMoves[i][0]
                        if movePiece[1] - movePlace[1] != 0:
                            # Remove moves that move the pinned piece off the pinning line.
                            self.posMoves.pop(i)
            elif m_r == 0 and (piece == "B" or piece == "Q"):
                print("Pin: B or Q")
                for i in range(len(self.posMoves) - 1, -1, -1):
                    movePiece = self.posMoves[i][1]
                    if movePiece == pinned:
                        movePlace = self.posMoves[i][0]
                        if movePiece[0] - movePlace[0] != 0 and movePlace != pinned:
                            self.posMoves.pop(i)
        elif piece == "Q" or piece == "B":
            print("Pin: B or Q outside elif")
            for i in range(len(self.posMoves) - 1, -1, -1):
                movePiece = self.posMoves[i][1]
                if movePiece == pinned:
                    movePlace = self.posMoves[i][0]
                    # Calculate the direction of the move.
                    pieceDir = (
                        (movePiece[0] - movePlace[0]) / (abs(movePiece[0] - movePlace[0]) or 1),
                        (movePiece[1] - movePlace[1]) / (abs(movePiece[1] - movePlace[1]) or 1),
                    )
                    if pieceDir != moveDir and movePlace != pinner:
                        # Remove moves that move the pinned piece off the pinning line.
                        self.posMoves.pop(i)


    def checkKnightcheck(self, oColor: str, kingPos: tuple) -> None:
        """
        Checks if the king is under attack by a knight and removes illegal moves accordingly.

        :Parameters:
        - oColor: str
            The opponent's color ('w' or 'b').
        - kingPos: tuple
            The position of the king (row, col).
        """
        posKnightPlaces = []
        # Generate possible knight moves from the king's position.
        self.knightMoves(kingPos[0], kingPos[1], kingPos, self.board, posKnightPlaces)
        posKnightPlaces = [x[0] for x in posKnightPlaces]
        KnIsPresent = None
        # Check if any of these positions contain an opponent's knight.
        for r, c in posKnightPlaces:
            if self.board[r][c] == oColor + "N":
                KnIsPresent = (r, c)
                break
        if KnIsPresent:
            # Remove moves that do not capture the knight or move the king.
            for i in range(len(self.posMoves) - 1, -1, -1):
                p = self.posMoves[i]
                if p[0] != KnIsPresent and self.board[p[1][0]][p[1][1]][1] != "K":
                    self.posMoves.pop(i)


class Move:
    """
    Represents a chess move with support for special moves such as castling, en passant, and pawn promotion.

    :Attributes:
    - moverStartSq (tuple): Starting square of the primary moving piece (row, col).
    - moverEndSq (tuple): Ending square of the primary moving piece (row, col).
    - otherStartSq (tuple): Starting square of the secondary piece (e.g., rook for castling, en passant target) (row, col).
    - otherEndSq (tuple): Ending square of the secondary piece (row, col).
    - pieceMoved (str): The piece being moved.
    - pieceOther (str): The secondary piece involved in the move.
    - isPieceCaptured (bool): Whether the move captures a piece.
    - promotedTo (str): The piece a pawn is promoted to, if applicable.
    - type (int): Type of move (0 = normal, 1 = short castle, -1 = long castle, 2 = en passant, 3 = pawn promotion).
    """

    # Mappings between ranks/files and rows/columns.
    RANKS_TO_ROWS = {str(i): 8 - i for i in range(1, 9)}
    ROWS_TO_RANKS = {v: k for k, v in RANKS_TO_ROWS.items()}
    FILES_TO_COLS = {chr(i): i - ord("a") for i in range(ord("a"), ord("h") + 1)}
    COLS_TO_FILES = {v: k for k, v in FILES_TO_COLS.items()}

    def __init__(
        self,
        moved: tuple,
        other: tuple,
        board: list,
        typeOfMove: int = 0,
        promotedTo: str = "",
    ):
        """
        Initialize a move with starting and ending squares and additional move information.

        :Parameters:
        - moved: tuple
            Tuple containing (start square, end square) for the primary piece.
        - other: tuple
            Tuple containing (start square, end square) for the secondary piece.
        - board: list
            2D list representing the chess board.
        - typeOfMove: int
            Type of move:
                0 = normal move.
                1 = short castle (O-O).
                -1 = long castle (O-O-O).
                2 = en passant capture.
                3 = pawn promotion.
        - promotedTo: str
            The piece a pawn is promoted to (e.g., 'Q', 'R', 'B', 'N'). Default is an empty string.
        """
        self.moverStartSq: tuple = moved[0]
        self.moverEndSq: tuple = moved[1]
        self.otherStartSq: tuple = other[0]
        if other[1] == (-1, -1):
            # If there is no secondary move (e.g., normal move), set otherEndSq to otherStartSq.
            self.otherEndSq: tuple = other[0]
            self.pieceOther: str = "__"  # No piece involved.
        else:
            self.otherEndSq: tuple = other[1]
            self.pieceOther: str = board[self.otherStartSq[0]][self.otherStartSq[1]]
        self.pieceMoved: str = board[self.moverStartSq[0]][self.moverStartSq[1]]
        self.isPieceCaptured: bool = True if self.pieceOther != "__" else False
        self.promotedTo: str = promotedTo
        self.type: int = typeOfMove

    def __str__(self) -> str:
        """
        Convert the move to a human-readable chess notation.

        :Returns:
        - str: The move in algebraic chess notation.
            - "O-O" for short castle.
            - "O-O-O" for long castle.
            - "e2e4" for normal moves.
            - "e2xf3" for captures.
            - "e7e8=Q" for pawn promotion.
            - "e7xf8=Q" for pawn promotion with capture.
        """
        if self.type == -1:
            return "O-O-O"
        elif self.type == 1:
            return "O-O"
        elif self.type == 3:
            if self.isPieceCaptured:
                return f"{self.get_square(self.moverStartSq)}x{self.get_square(self.moverEndSq)}={self.promotedTo}"
            else:
                return f"{self.get_square(self.moverStartSq)}={self.promotedTo}"
        elif self.type == 2 or self.isPieceCaptured:
            return f"{self.get_square(self.moverStartSq)}x{self.get_square(self.moverEndSq)}"
        else:
            return f"{self.get_square(self.moverStartSq)}{self.get_square(self.moverEndSq)}"

    @staticmethod
    def get_square(sq: tuple) -> str:
        """
        Convert a (row, col) tuple to chess square notation.

        :Parameters:
        - sq: tuple
            A tuple (row, col) representing the square.

        :Returns:
        - str: The square in chess notation (e.g., "e2").
        """
        rank = Move.ROWS_TO_RANKS[sq[0]]  # Convert row index to rank number.
        file = Move.COLS_TO_FILES[sq[1]]  # Convert column index to file letter.
        return f"{file}{rank}"
