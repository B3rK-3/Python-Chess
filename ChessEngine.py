import pygame as p
import copy


class GameState:
    def __init__(self, userPlaysWhite: bool = True):
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
        print("----")
        print("GAME START")
        print("----")
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bN", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.possibleMoves = set()
        self.opponentMoves = set()
        # Indicates whose turn it is; True if it's white's turn, False if black's.
        self.isWhiteTurn = True
        # A log to keep track of all moves made in the game.
        self.moveLog: list["Move"] = []
        self.castleRightsLog: list[tuple[list[bool]]] = []
        self.enPassantLog: list[str] = []
        self.enPassantPlace: str = "-"
        # castle rights (whiteCastleRights, blackCastleRights)
        self.whiteCastleRights = [
            True,
            True,
            False,
            False,
            False,
        ]  # Queen Side, King Side, Left Rook Moved, King Moved, Right Rook Moved
        self.blackCastleRights = [
            True,
            True,
            False,
            False,
            False,
        ]  # Queen Side, King Side, Left Rook Moved, King Moved, Right Rook Moved
        self.fiftyMoveRule = 0  # counter for 50 move rule
        self.isInCheck = False  # is in check
        self.userPlaysWhite = userPlaysWhite

        #
        self.isWhiteTurn = not self.isWhiteTurn
        kingPos = self.posOfPiece("wK" if self.isWhiteTurn else "bK")[0]
        self.updateCastlingRights(kingPos)
        self.isWhiteTurn = not self.isWhiteTurn
        self.gameUpdate = self.genValidMoves(self.board)

    def genValidMoves(self, board: list) -> str:
        """
        Generates all valid moves for the current player, accounting for checks and checkmates.

        :Parameters:
        - board: list
            The current board state.

        :Returns:
        - list: A list of valid moves.
        """
        if self.fiftyMoveRule == 100:
            pass  # TODO: ask the user if they want to withdraw!
        self.genOpponentMoves(self.board)
        # Get the position of the current player's king.
        self.kingPosition = self.posOfPiece("wK" if self.isWhiteTurn else "bK")[0]
        # Generate all possible moves (not necessarily valid).
        self.possibleMoves = self.genPossibleMoves(board)
        # Check if the king is in check.
        toDelete = self.checkAroundKing(self.kingPosition)
        self.isCheck()
        setToDelete = set()
        for i, t in sorted(toDelete, reverse=True):
            if i in setToDelete:
                continue
            self.possibleMoves.remove(i)
            setToDelete.add(i)
        # update the castling
        self.updateCastlingRights(self.kingPosition)
        # add check symbol to notation
        if self.isInCheck:
            moveObj = self.moveLog[-1]
            moveObj.checkOrMate = "+"
            print(f"Move: {moveObj}")
        if not self.possibleMoves and self.isInCheck:
            # If there are no valid moves and the king is in check, it's checkmate.
            moveObj.checkOrMate = "#"
            print(f"Move: {moveObj}")
            print("Checkmate!", ("Black wins!" if self.isWhiteTurn else "White wins!"))
            return "GG"
        elif not self.possibleMoves:
            # If there are no valid moves but the king is not in check, it's stalemate.
            print("Stalemate!")
            return "SM"
        return ""

    def isCheck(self):
        """
        Module that modifies self.isCheck depending on if it's check
        """
        self.isInCheck = False
        if self.kingPosition in self.opponentMoves:
            self.isInCheck = True

    def genPossibleMoves(self, board: list) -> list:
        """
        Generates all possible moves for the current player, without considering checks.

        :Parameters:
        - board: list
            The current state of the board.

        :Returns:
        - list: A list of all possible moves for the current player.
        """
        possibleMoves = set()
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

    def genOpponentMoves(self, board: list) -> None:
        """
        Method to get opponent moves
        """
        self.isWhiteTurn = not self.isWhiteTurn
        self.opponentMoves = set(move[0] for move in self.genPossibleMoves(self.board))
        self.isWhiteTurn = not self.isWhiteTurn

    def makeMove(self, moveObj: "Move") -> None:
        """
        Executes a move on the board.

        :Parameters:
        - moveObj: Move
            The move object containing the move details.
        """
        print("----")
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

        # Log the stuff
        self.moveLog.append(moveObj)
        self.enPassantLog.append(self.enPassantPlace)
        self.enPassantPlace = "-"

        # fifty-move rule conditions
        if moveObj.pieceMoved[1] == "P" or moveObj.isPieceCaptured:
            self.fiftyMoveRule = 0
        else:
            self.fiftyMoveRule += 1

        # check if the pawn has been double pawn moved
        if (
            abs(moveObj.moverEndSq[0] - moveObj.moverStartSq[0]) == 2
            and moveObj.pieceMoved[1] == "P"
        ):
            self.enPassantPlace = Move.getSqaure(
                (
                    moveObj.moverEndSq[0] + (1 if not self.isWhiteTurn else -1),
                    moveObj.moverEndSq[1],
                )
            )
        self.removeCastleRights(moveObj)

        self.castleRightsLog.append(
            (
                copy.deepcopy(self.whiteCastleRights),
                copy.deepcopy(self.blackCastleRights),
            )
        )
        # Generate the valid moves
        self.gameUpdate = self.genValidMoves(self.board)

    def removeCastleRights(self, moveObj: "Move"):
        # removing castling rights logic according to moved piece
        if moveObj.pieceMoved == "wK":
            self.whiteCastleRights = [False, False, False, True, False]
        elif moveObj.pieceMoved == "bK":
            self.blackCastleRights = [False, False, False, True, False]
        elif moveObj.moverStartSq == (0, 0) or moveObj.moverEndSq == (0, 0):
            self.blackCastleRights[0] = False
            self.blackCastleRights[2] = True
        elif moveObj.moverStartSq == (0, 7) or moveObj.moverEndSq == (0, 7):
            self.blackCastleRights[1] = False
            self.blackCastleRights[4] = True
        elif moveObj.moverStartSq == (7, 0) or moveObj.moverEndSq == (7, 0):
            self.whiteCastleRights[0] = False
            self.whiteCastleRights[2] = True
        elif moveObj.moverStartSq == (7, 7) or moveObj.moverEndSq == (7, 7):
            self.whiteCastleRights[1] = False
            self.whiteCastleRights[4] = True

    def restoreCastleRights(self):
        # restore the rights by popping the most recent rights in the log
        self.whiteCastleRights, self.blackCastleRights = self.castleRightsLog.pop()

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
            self.gameUpdate = ""
            # restore the castle rights from before the move
            self.restoreCastleRights()
            # regenerate possible moves
            self.genValidMoves(self.board)
            print("----")
            print(f"Undo Move: {moveObj}")

    def updateCastlingRights(self, kingPos: tuple):
        if (
            self.isInCheck
            or (self.isWhiteTurn and self.whiteCastleRights[3])
            or (not self.isWhiteTurn and self.blackCastleRights[3])
            or (not self.isWhiteTurn and kingPos != (0, 4))
            or (self.isWhiteTurn and kingPos != (7, 4))
        ):
            # print("Threat 0")
            self.disableCastlingRights()
            return

        # Generate opponent's moves to check for threats along the castling path.
        self.isWhiteTurn = not self.isWhiteTurn  # Switch turn to opponent.
        opponentMoves = self.opponentMoves
        self.isWhiteTurn = not self.isWhiteTurn  # Switch back.
        # Check for threats along the castling paths.
        row = kingPos[0]
        self.checkCastlingPath(row, opponentMoves)
        rights = self.whiteCastleRights if self.isWhiteTurn else self.blackCastleRights

        if rights[0]:
            self.possibleMoves.add(((row, 0), kingPos))
        if rights[1]:
            self.possibleMoves.add(((row, 7), kingPos))
        print("Castle Rights:", self.getCastleString())

    def disableCastlingRights(self):
        if self.isWhiteTurn:
            self.whiteCastleRights[0] = False
            self.whiteCastleRights[1] = False
        else:
            self.blackCastleRights[0] = False
            self.blackCastleRights[1] = False

    def checkCastlingPath(self, row: int, opponentMoves: tuple):
        # Check if any opponent's move attacks the king's row.
        for r, c in opponentMoves:
            if r == row:
                if 4 <= c < 7:  # Threat on the kingside path.
                    # print("Threat 1")
                    self.disableKingsideCastling()
                elif 0 < c <= 4:  # Threat on the queenside path.
                    # print("Threat 2")
                    self.disableQueensideCastling()

        # Check for blocking pieces on castling paths.
        if any(self.board[row][c] != "__" for c in (1, 2, 3)):
            # print("Threat 3")
            self.disableQueensideCastling()
        else:
            if not (
                (self.isWhiteTurn and self.whiteCastleRights[2])
                or (not self.isWhiteTurn and self.blackCastleRights[2])
            ):
                self.enableQueensideCastling()

        if any(self.board[row][c] != "__" for c in (5, 6)):
            # print("Threat 4")
            self.disableKingsideCastling()
        else:
            if not (
                (self.isWhiteTurn and self.whiteCastleRights[4])
                or (not self.isWhiteTurn and self.blackCastleRights[4])
            ):
                self.enableKingsideCastling()

        self.isWhiteTurn = not self.isWhiteTurn
        # Check for blocking pieces on castling paths.
        if any(self.board[7 - row][c] != "__" for c in (1, 2, 3)):
            # print("Threat 3")
            self.disableQueensideCastling()
        else:
            if not (
                (self.isWhiteTurn and self.whiteCastleRights[2])
                or (not self.isWhiteTurn and self.blackCastleRights[2])
            ):
                self.enableQueensideCastling()

        if any(self.board[7 - row][c] != "__" for c in (5, 6)):
            # print("Threat 4")
            self.disableKingsideCastling()
        else:
            if not (
                (self.isWhiteTurn and self.whiteCastleRights[4])
                or (not self.isWhiteTurn and self.blackCastleRights[4])
            ):
                self.enableKingsideCastling()
        self.isWhiteTurn = not self.isWhiteTurn

    def disableKingsideCastling(self):
        if self.isWhiteTurn:
            self.whiteCastleRights[1] = False
        else:
            self.blackCastleRights[1] = False

    def enableKingsideCastling(self):
        if self.isWhiteTurn:
            self.whiteCastleRights[1] = True
        else:
            self.blackCastleRights[1] = True

    def disableQueensideCastling(self):
        if self.isWhiteTurn:
            self.whiteCastleRights[0] = False
        else:
            self.blackCastleRights[0] = False

    def enableQueensideCastling(self):
        if self.isWhiteTurn:
            self.whiteCastleRights[0] = True
        else:
            self.blackCastleRights[0] = True

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
                and abs(moveObj.moverStartSq[0] - moveObj.moverEndSq[0])
                == 2  # Moved two squares.
                and move[1][1] == moveObj.moverEndSq[1]  # Same column as the pawn.
                and move[0][0]
                == moveObj.moverEndSq[0]  # Capturing pawn is next to the moved pawn.
                and (
                    (
                        self.isWhiteTurn and move[1][0] - moveObj.moverEndSq[0] == -1
                    )  # White pawn moving up.
                    or (
                        not self.isWhiteTurn
                        and move[1][0] - moveObj.moverEndSq[0]
                        == 1  # Black pawn moving down.
                    )
                )
            ):
                return True  # En passant is possible.
        return False  # Not an en passant move.

    def pawnPromotion(self, move: list, screen: p.Surface, promoteTo: str = "") -> str:
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
        p_names = [
            "wR",
            "wB",
            "wN",
            "wQ",
            "bR",
            "bB",
            "bN",
            "bQ",
        ]  # Possible promotion pieces.
        IMAGES = {}
        font = p.font.SysFont("Arial", 15)  # Set the font for text display.
        # Load images for promotion options.
        for e in p_names:
            IMAGES[e] = p.transform.scale(p.image.load("img/" + e + ".png"), (75, 75))
        if self.isWhiteTurn:
            # If it's white's turn, set up the promotion options for white.
            shift = 75 * (move[0][1] - 4) if move[0][1] > 4 else 0
            # Draw the promotion selection rectangle.
            p.draw.rect(
                screen,
                (255, 204, 117),  # Background color.
                (move[0][1] * 75 - shift, (move[0][0]) * 75 + 100, 4 * 75, 90),
                border_radius=5,
            )
            p.draw.rect(
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
                f = font.render(
                    str(i + 1), True, (0, 0, 0)
                )  # Render the option number.
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
            shift = 75 * (move[0][1] - 4) if move[0][1] > 4 else 0
            # Draw the promotion selection rectangle.
            p.draw.rect(
                screen,
                (255, 204, 117),  # Background color.
                (move[0][1] * 75 - shift, (move[0][0]) * 75 - 100, 4 * 75, 90),
                border_radius=5,
            )
            p.draw.rect(
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
                f = font.render(
                    str(i - 3), True, (0, 0, 0)
                )  # Render the option number.
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
        return

    def pawnMoves(
        self,
        row: int,
        col: int,
        piece: str,
        board: list,
        possibleMoves: set,
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
                and abs(moveObj.moverEndSq[0] - moveObj.moverStartSq[0])
                == 2  # Moved two squares.
                and row
                == moveObj.moverEndSq[0]  # Pawn is on the same rank as the moved pawn.
            ):
                if col + 1 == moveObj.moverEndSq[1]:
                    # Check for en passant capture to the right.
                    if oColor == "b":
                        possibleMoves.add(((row - 1, col + 1), (row, col)))
                    else:
                        possibleMoves.add(((row + 1, col + 1), (row, col)))
                if col - 1 == moveObj.moverEndSq[1]:
                    # Check for en passant capture to the left.
                    if oColor == "b":
                        possibleMoves.add(((row - 1, col - 1), (row, col)))
                    else:
                        possibleMoves.add(((row + 1, col - 1), (row, col)))
        if piece[0] == "w":
            # White pawn moves.
            if row == 6 and board[row - 1][col] == "__" and board[row - 2][col] == "__":
                # Pawn's first move can be two squares forward if both squares are empty.
                possibleMoves.add(((row - 2, col), (row, col)))
            if board[row - 1][col] == "__":
                # Move one square forward if the square is empty.
                possibleMoves.add(((row - 1, col), (row, col)))
            if col - 1 >= 0 and board[row - 1][col - 1][0] == "b":
                # Capture diagonally to the left if there is a black piece.
                possibleMoves.add(((row - 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row - 1][col + 1][0] == "b":
                # Capture diagonally to the right if there is a black piece.
                possibleMoves.add(((row - 1, col + 1), (row, col)))
        elif piece[0] == "b":
            # Black pawn moves.
            if row == 1 and board[row + 1][col] == "__" and board[row + 2][col] == "__":
                # Pawn's first move can be two squares forward if both squares are empty.
                possibleMoves.add(((row + 2, col), (row, col)))
            if board[row + 1][col] == "__":
                # Move one square forward if the square is empty.
                possibleMoves.add(((row + 1, col), (row, col)))
            if col - 1 >= 0 and board[row + 1][col - 1][0] == "w":
                # Capture diagonally to the left if there is a white piece.
                possibleMoves.add(((row + 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row + 1][col + 1][0] == "w":
                # Capture diagonally to the right if there is a white piece.
                possibleMoves.add(((row + 1, col + 1), (row, col)))

    def knightMoves(
        self,
        row: int,
        col: int,
        piece: str,
        board: list,
        possibleMoves: set,
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
            (2, 1),  # Moves two squares down, one square left/right.
            (-2, -1),
            (-2, 1),  # Moves two squares up, one square left/right.
            (1, 2),
            (-1, 2),  # Moves one square up/down, two squares right.
            (1, -2),
            (-1, -2),  # Moves one square up/down, two squares left.
        ]
        for move in knight_moves:
            r = row + move[0]
            c = col + move[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c][0] != piece[0]:
                    # Add the move if the destination is empty or contains an opponent's piece.
                    possibleMoves.add(((r, c), (row, col)))

    def rookMoves(
        self, row: int, col: int, piece: str, board: list, possibleMoves: set
    ) -> None:
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
                        possibleMoves.add(((r, c), (row, col)))
                    elif board[r][c][0] != piece[0]:
                        possibleMoves.add(((r, c), (row, col)))
                        break
                    else:
                        break
                else:
                    break

    def bishopMoves(
        self, row: int, col: int, piece: str, board: list, possibleMoves: set
    ) -> None:
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
                        possibleMoves.add(((r, c), (row, col)))
                    elif board[r][c][0] != piece[0]:
                        possibleMoves.add(((r, c), (row, col)))
                        break
                    else:
                        break
                else:
                    break

    def queenMoves(
        self, row: int, col: int, piece: str, board: list, possibleMoves: set
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
        self, row: int, col: int, piece: str, board: list, possibleMoves: set
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
            (-1, 0),  # Up
            (1, 0),  # Down
            (0, -1),  # Left
            (0, 1),  # Right
            (-1, 1),  # Up-Right
            (1, 1),  # Down-Right
            (-1, -1),  # Up-Left
            (1, -1),  # Down-Left
        ]
        for d in directions:
            r = row + d[0]
            c = col + d[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c][0] != piece[0]:
                    # Add the move if the destination is empty or contains an opponent's piece.
                    possibleMoves.add(((r, c), (row, col)))

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
        toDelete = set()  # (index, type) # type 0 = pin, 1 = check, 2 = illegal move
        # Check for knight checks and remove illegal king moves.
        self.checkKnightcheck(oColor, self.kingPosition, toDelete)
        self.kingCantMoveWhere(toDelete)

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
                    pType = piece[1]  # Piece type: 'Q', 'R', 'B', 'N', 'P', or 'K'.
                    if pType == "_":
                        continue
                    if pColor == currColor:
                        # If we've already encountered our own piece, stop checking this direction.
                        if locOwnColor:
                            break
                        locOwnColor = (r, c)  # Mark the position of our own piece.
                    else:
                        if locOwnColor:
                            # An opponent's piece is behind our own piece, which might be pinned.
                            print(
                                f"Possible Pin - Pinner: {Move.getSqaure((r,c))} - Dir: {move} - Pinner: {piece}"
                            )
                            self.pinned((r, c), locOwnColor, move, piece[1], toDelete)
                            locOwnColor = False
                            break
                        # Check for checks from opponent pieces.
                        elif (c_off == 0 or r_off == 0) and (pType in "RQ"):
                            # Straight line checks (rook or queen).
                            print(
                                f"Rem Move - Square: {Move.getSqaure((r,c))} - Dir: {move} - Piece: {piece[1]}"
                            )
                            self.remMoves(r, c, True, toDelete, king)
                        elif (c_off != 0 and r_off != 0) and (pType in "BQ"):
                            # Diagonal checks (bishop or queen).
                            print(
                                f"Rem Move - Square: {Move.getSqaure((r, c))} - Dir: {move} - Piece: {piece[1]}"
                            )
                            self.remMoves(r, c, False, toDelete, king)
                        elif (
                            (currColor == "w" and r_off == -1 and abs(c_off) == 1)
                            or (currColor == "b" and r_off == 1 and abs(c_off) == 1)
                        ) and (pType == "P"):
                            # Check for pawn checks.
                            print(
                                f"Rem Move - Square: {Move.getSqaure((r, c))} - Dir: {move} - Piece: {piece[1]}"
                            )
                            self.remMoves(r, c, False, toDelete, king)
                        else:
                            break
                else:
                    break
            locOwnColor = False  # Reset the flag for the next direction.
        return toDelete

    def remMoves(self, r: int, c: int, vh: bool, toDelete: set, kingPos: tuple) -> None:
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
            d_row = kingPos[0] - r
            d_col = kingPos[1] - c
            if d_row == 0:
                # Threat is horizontal.
                for m in self.possibleMoves:
                    if m[1] == kingPos and (
                        (d_col > 0 and (m[0][0] == r and kingPos[1] > m[0][1] > c))
                        or (d_col < 0 and (m[0][0] == r and kingPos[1] < m[0][1] < c))
                    ):
                        # Remove moves that don't block or capture the checking piece.
                        toDelete.add((m, 1))
                    elif m[1] != kingPos and (
                        (d_col > 0 and not (m[0][0] == r and kingPos[1] > m[0][1] >= c))
                        or (
                            d_col < 0
                            and not (m[0][0] == r and kingPos[1] < m[0][1] <= c)
                        )
                    ):
                        toDelete.add((m, 1))
            if d_col == 0:
                # Threat is vertical.
                for m in self.possibleMoves:
                    if m[1] == kingPos and (
                        (d_row > 0 and (m[0][1] == c and kingPos[0] > m[0][0] > r))
                        or (d_row < 0 and (m[0][1] == c and kingPos[0] < m[0][0] < r))
                    ):
                        toDelete.add((m, 1))
                    elif m[1] != kingPos and (
                        (d_row > 0 and not (m[0][1] == c and kingPos[0] > m[0][0] >= r))
                        or (
                            d_row < 0
                            and not (m[0][1] == c and kingPos[0] < m[0][0] <= r)
                        )
                    ):
                        toDelete.add((m, 1))
        else:
            # Diagonal threat.
            d_row = kingPos[0] - r
            d_col = kingPos[1] - c
            d_row = d_row / abs(d_row)
            d_col = d_col / abs(d_col)
            # Build list of positions between the checking piece and the king.
            places = [(r, c), (r + d_row, c + d_col)]
            counter = 2
            while places[-1] != kingPos:
                places.append((r + d_row * counter, c + d_col * counter))
                counter += 1
            for m in self.possibleMoves:
                if m[1] == self.kingPosition:
                    if m[0] == (r, c):
                        continue  # Allow capturing the checking piece.
                    elif m[0] in places:
                        toDelete.add((m, 1))
                elif m[0] not in places:
                    toDelete.add((m, 1))

    def kingCantMoveWhere(self, toDelete: set) -> None:
        """
        Determines squares where the king cannot move due to threats.
        """
        # Create a copy of the board to test moves.
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        y, x = self.kingPosition
        b = [row[:] for row in self.board]
        for move in kMoves:
            y1 = y + move[0]
            x1 = x + move[1]
            move = ((y1, x1), (y, x))
            if 0 <= y1 < 8 and 0 <= x1 < 8 and move in self.possibleMoves:
                b[y1][x1], b[y][x] = b[y][x], "__"
                self.isWhiteTurn = not self.isWhiteTurn
                opponentMoves = self.genPossibleMoves(b)
                opponentMovesCopy = set()
                for oppMove in opponentMoves:
                    opponentMovesCopy.add(oppMove[0])
                self.isWhiteTurn = not self.isWhiteTurn
                if (y1, x1) in opponentMovesCopy:
                    toDelete.add((move, 3))

    def pinned(
        self, pinner: tuple, pinned: tuple, moveDir: tuple, piece: str, toDelete: set
    ) -> None:
        """
        Handles pinning of pieces. Removes moves that would expose the king to check if the piece is pinned.`

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
                for move in self.possibleMoves:
                    movePiece = move[1]
                    if movePiece == pinned:
                        movePlace = move[0]
                        if movePiece[1] - movePlace[1] != 0:
                            # Remove moves that move the pinned piece off the pinning line.
                            toDelete.add((move, 0))
            elif m_r == 0 and (piece == "B" or piece == "Q"):
                print("Pin: B or Q")
                for move in self.possibleMoves:
                    movePiece = move[1]
                    if movePiece == pinned:
                        movePlace = move[0]
                        if movePiece[0] - movePlace[0] != 0 and movePlace != pinned:
                            toDelete.add((move, 0))
        elif piece == "Q" or piece == "B":
            print("Pin: B or Q outside elif")
            for move in self.possibleMoves:
                movePiece = move[1]
                if movePiece == pinned:
                    movePlace = move[0]
                    # Calculate the direction of the move.
                    pieceDir = (
                        (movePiece[0] - movePlace[0])
                        / (abs(movePiece[0] - movePlace[0]) or 1),
                        (movePiece[1] - movePlace[1])
                        / (abs(movePiece[1] - movePlace[1]) or 1),
                    )
                    if pieceDir != moveDir and movePlace != pinner:
                        # Remove moves that move the pinned piece off the pinning line.
                        toDelete.add((move, 0))

    def checkKnightcheck(self, oColor: str, kingPos: tuple, toDelete: set) -> None:
        """
        Checks if the king is under attack by a knight and removes illegal moves accordingly.

        :Parameters:
        - oColor: str
            The opponent's color ('w' or 'b').
        - kingPos: tuple
            The position of the king (row, col).
        """
        posKnightPlaces = set()
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
            for p in self.possibleMoves:
                if p[0] != KnIsPresent and self.board[p[1][0]][p[1][1]][1] != "K":
                    toDelete.add((p, 0))

    def pawnChecks(self, userClicks: list) -> bool:
        """
        Checks if a pawn promotion is possible.

        :Parameters:
        - userClicks: list
            The list of user clicks (current move).

        :Returns:
        - bool: True if pawn promotion is possible, False otherwise.
        """
        return self.board[userClicks[0][0]][userClicks[0][1]][1] == "P" and (
            (userClicks[1][0] == 0) or (userClicks[1][0] == 7)
        )

    def castleChecks(self, userClicks: list) -> bool:
        """
        Checks if castling is possible with the selected pieces.

        :Parameters:
        - userClicks: list
            The list of user clicks (current move).

        :Returns:
        - bool: True if castling is possible, False otherwise.
        """
        return (
            self.board[userClicks[0][0]][userClicks[0][1]][1] == "K"
            and self.board[userClicks[1][0]][userClicks[1][1]][1] == "R"
            and self.board[userClicks[0][0]][userClicks[0][1]][0]
            == self.board[userClicks[1][0]][userClicks[1][1]][0]
            and tuple(userClicks[::-1]) in self.possibleMoves
        )

    def makeEnPassant(self, userClicks: list) -> None:
        """
        Executes an en passant move.

        :Parameters:
        - userClicks: list
            The list of user clicks (current move).
        """
        moveObj = self.moveLog[-1]
        # Create the en passant move.
        moveObj = Move(
            userClicks,  # Piece moved.
            (moveObj.moverEndSq, userClicks[1]),  # Piece captured.
            self.board,
            2,  # Type of move (en passant).
        )
        self.makeMove(moveObj)

    def getCastleString(self):
        # method to get the castling sides in string
        # FEN format
        white = f"{"K" if self.whiteCastleRights[1] else ""}{"Q" if self.whiteCastleRights[0] else ""}"
        black = f"{"k" if self.blackCastleRights[1] else ""}{"q" if self.blackCastleRights[0] else ""}"
        return "-" if not white and not black else white + black

    def numOfMoves(self):
        # return the number of moves
        return max(len(self.moveLog) // 2, 1)

    def getNotationLog(self):
        notations = ""
        for log in self.moveLog:
            notations += log.__str__()
        return notations

    def getBoard(self):
        if self.userPlaysWhite:
            return self.board
        else:
            return [
                [
                    ("w" if p[0] == "b" else ("b" if p[0] != "_" else "_")) + p[1]
                    for p in row
                ]
                for row in self.board
            ]

    def pieceColor(self, y, x):
        return self.board[y][x][0]


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
        self.isPieceCaptured: bool = (
            True
            if (self.pieceOther != "__" and self.pieceMoved[0] != self.pieceOther[0])
            else False
        )
        self.promotedTo: str = promotedTo
        self.type: int = typeOfMove
        self.checkOrMate = ""

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
            return "O-O-O" + self.checkOrMate
        elif self.type == 1:
            return "O-O" + self.checkOrMate
        elif self.type == 3:
            if self.isPieceCaptured:
                return (
                    f"{self.getSqaure(self.moverStartSq)}x{self.getSqaure(self.moverEndSq)}={self.promotedTo}"
                    + self.checkOrMate
                )
            else:
                return (
                    f"{self.getSqaure(self.moverStartSq)}={self.promotedTo}"
                    + self.checkOrMate
                )
        elif self.type == 2 or self.isPieceCaptured:
            return (
                f"{self.getSqaure(self.moverStartSq)}x{self.getSqaure(self.moverEndSq)}"
                + self.checkOrMate
            )
        else:
            return (
                f"{self.getSqaure(self.moverStartSq)}{self.getSqaure(self.moverEndSq)}"
                + self.checkOrMate
            )

    @staticmethod
    def getSqaure(sq: tuple) -> str:
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

    @staticmethod
    def parseSquare(sq: str, board: list[list[str]]):
        sq = sq.replace("+", "").replace("#", "").replace("x", "")
        start = (8 - int(sq[1]), Move.FILES_TO_COLS[sq[0]])
        end = (8 - int(sq[3]), Move.FILES_TO_COLS[sq[2]])
        piece = board[start[0]][start[1]]
        if piece[1] == "K" and abs(start[1] - end[1]) == 2:
            if end[1] == 6:
                end = (end[0], end[1] + 1)
            else:
                end = (end[0], end[1] - 1)
        promote = ""
        if len(sq) > 4:
            promote = sq[4].upper()
        return (start, end, promote)


class FEN:
    @staticmethod
    def boardToFEN(board: list[str]):
        pgn = ""
        for row in board:
            skipAmount = 0
            for column in row:
                if column == "__":
                    skipAmount += 1
                else:
                    if skipAmount > 0:
                        pgn += str(skipAmount)
                        skipAmount = 0
                    pgn += column[1].lower() if column[0] == "b" else column[1]
            if skipAmount > 0:
                pgn += str(skipAmount)
            pgn += "/"
        return pgn[:-1]

    @staticmethod
    def FENtoBoard(pgn: str):
        board = [["__"] * 8 for _ in range(8)]
        i = 0
        row = 0
        while row < 8:
            col = 0
            while col < 8:
                piece = pgn[i]
                try:
                    skipAmount = int(piece)
                    col += skipAmount - 1
                except ValueError:
                    if piece != "/":
                        board[row][col] = (
                            "w" if piece.upper() == piece else "b"
                        ) + piece.upper()
                    else:
                        col -= 1
                i += 1
                col += 1
            row += 1
        return board
