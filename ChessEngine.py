import math
import pygame as p


class GameState:
    def __init__(self):
        # Initialize the chess board as a 2D list. Each element represents a square on the board.
        # The notation is as follows: 'bR' = black rook, 'wR' = white rook, '__' = empty square, etc.
        self.board = [
            ["bR", "__", "__", "__", "bK", "__", "__", "bR"],
            ["bP", "bP", "wP", "__", "bP", "bP", "wP", "bP"],
            ["__", "__", "__", "__", "bP", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["wP", "wP", "wP", "wP", "__", "wP", "wP", "wP"],
            ["wR", "__", "__", "__", "wK", "__", "__", "wR"],
        ]
        # Indicates whose turn it is; True if it's white's turn, False if black's.
        self.white_turn = True
        # A log to keep track of all moves made in the game.
        self.mLog = []

    def makeMove(self, move, move1):
        # Handles making a move on the board.
        if not move1:
            # Update the board by moving the piece to the new location.
            self.board[move.startRow][move.startCol] = (
                "__"  # Empty the starting square.
            )
            self.board[move.endRow][move.endCol] = (
                move.pieceMoved
            )  # Place the piece in the new square.
            # Add the move to the move log.
            self.mLog.append(move)
        else:
            # If move1 exists (e.g., for castling or en passant), handle both moves.
            self.board[move1.startRow][move1.startCol] = "__"
            self.board[move1.endRow][move1.endCol] = move1.pieceMoved
            self.board[move.startRow][move.startCol] = "__"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            # Add both moves to the move log as a tuple.
            self.mLog.append((move, move1))
        # Switch the turn to the other player.
        self.white_turn = not self.white_turn

    def undoMove(self):
        # Undo the last move made.
        if len(self.mLog) > 0:
            m = self.mLog.pop()
            if not isinstance(m, tuple):
                # If the last move was a single move.
                self.board[m.startRow][m.startCol] = (
                    m.pieceMoved
                )  # Move piece back to original square.
                self.board[m.endRow][m.endCol] = (
                    m.pieceCaptured
                )  # Restore captured piece.
            else:
                # If the last move involved two moves (e.g., castling).
                self.board[m[0].startRow][m[0].startCol] = m[0].pieceMoved
                self.board[m[0].endRow][m[0].endCol] = m[0].pieceCaptured
                self.board[m[1].startRow][m[1].startCol] = m[1].pieceMoved
                self.board[m[1].endRow][m[1].endCol] = m[1].pieceCaptured
            self.white_turn = not self.white_turn  # Switch turns back.

    def canCastle(self, kingPos, rookPos):
        print("inside canCastle")
        # Generate possible castling moves.
        logs = []  # Accounting for the possibility that a move like en passant has been made which is a tuple in the self.mLog list
        for each in self.mLog:
            if isinstance(each, tuple):
                logs.append((each[0].startRow, each[0].startCol))
                logs.append((each[1].startRow, each[1].startCol))
            else:
                logs.append((each.startRow, each.startCol))
        if self.white_turn:
            # Set positions for white king and rooks.
            king = (7, 4)
            rooks = {(7, 0), (7, 7)}
        else:
            # Set positions for black king and rooks.
            king = (0, 4)
            rooks = {(0, 0), (0, 7)}

        # Check move logs to see rooks or king was moved
        if kingPos != king or rookPos not in rooks:
            print(1)
            return False
        for log in logs:
            if king == log:
                print(2)
                return False
            elif log in rooks:
                rooks.remove(log)
        if not rooks:
            print(3)
            return False
        # Generate opponent's moves.
        self.white_turn = not self.white_turn
        oppM = [x[0] for x in self.genValidMoves(self.board)]
        self.white_turn = not self.white_turn

        # Check if there is threats in the castle axis
        row = kingPos[0]
        for r, _ in oppM:
            if r == row:
                print(4)
                return False
        return True

    def castle(self, kingPos, rookPos):
        if rookPos[1] == 7:  # Short Castle
            kingM = Move(kingPos, (kingPos[0], 6), self.board)
            rookM = Move(rookPos, (rookPos[0], 5), self.board)
        else:  # Long Castle
            kingM = Move(kingPos, (kingPos[0], 2), self.board)
            rookM = Move(rookPos, (rookPos[0], 3), self.board)
        self.makeMove(rookM, kingM)

    def make_if_en_passant(self, move):
        # Handle en passant move if applicable.
        if len(self.mLog) > 1:
            lastMove = self.mLog[-1]
            if (
                not isinstance(lastMove, tuple)
                and lastMove.pieceMoved[1] == "P"
                and abs(lastMove.endRow - lastMove.startRow) == 2
                and move[1][1] == lastMove.endCol
                and move[0][0] == lastMove.endRow
                and (
                    (self.white_turn and move[1][0] - lastMove.endRow == -1)
                    or (not self.white_turn and move[1][0] - lastMove.endRow == 1)
                )
            ):
                # Create the en passant move.
                passer = Move(move[0], move[1], self.board)
                passed = Move(
                    (lastMove.endRow, lastMove.endCol),
                    (lastMove.endRow + (-1 if self.white_turn else 1), lastMove.endCol),
                    self.board,
                )
                self.makeMove(passer, passed)
                self.white_turn = not self.white_turn
                return True

    def genValidMoves(self, board):
        # Generate all valid moves for the current player.
        self.posMoves = self.genPossibleMoves(board)
        self.kingPos = self.posOfPiece("wK" if self.white_turn else "bK")[0]
        numOfChecks = self.checkAroundKing(self.kingPos)
        if self.posMoves == [] and numOfChecks:
            # If there are no valid moves and the king is in check, it's checkmate.
            print("Checkmate!", ("Black wins!" if self.white_turn else "White wins!"))
        elif self.posMoves == []:
            # If there are no valid moves but the king is not in check, it's stalemate.
            print("Stalemate!")
        return self.posMoves

    def genPossibleMoves(self, board):
        """
        Generate all possible moves for the current player, without considering checks.
        """
        possibleMoves = []
        colors = ["w", "b"]
        turn = 0 if self.white_turn else 1
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
                            colors[1 - turn],
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

    def pawnMoves(self, row, col, piece, board, possibleMoves, oColor):
        """
        Generate all possible pawn moves from the given position.
        """
        # En passant conditions.
        if len(self.mLog) > 1:
            lastMove = self.mLog[-1]
            if (
                not isinstance(lastMove, tuple)
                and lastMove.pieceMoved[1] == "P"
                and abs(lastMove.endRow - lastMove.startRow) == 2
                and row == lastMove.endRow
            ):
                if col + 1 == lastMove.endCol:
                    if oColor == "b":
                        possibleMoves.append(((row - 1, col + 1), (row, col)))
                    else:
                        possibleMoves.append(((row + 1, col + 1), (row, col)))
                if col - 1 == lastMove.endCol:
                    if oColor == "b":
                        possibleMoves.append(((row - 1, col - 1), (row, col)))
                    else:
                        possibleMoves.append(((row + 1, col - 1), (row, col)))
        if piece[0] == "w":
            # White pawn moves.
            if row == 6 and board[row - 1][col] == "__" and board[row - 2][col] == "__":
                # Pawn's first move can be two squares forward.
                possibleMoves.append(((row - 2, col), (row, col)))
            if board[row - 1][col] == "__":
                # Move one square forward.
                possibleMoves.append(((row - 1, col), (row, col)))
            if col - 1 >= 0 and board[row - 1][col - 1][0] == "b":
                # Capture diagonally to the left.
                possibleMoves.append(((row - 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row - 1][col + 1][0] == "b":
                # Capture diagonally to the right.
                possibleMoves.append(((row - 1, col + 1), (row, col)))
        elif piece[0] == "b":
            # Black pawn moves.
            if row == 1 and board[row + 1][col] == "__" and board[row + 2][col] == "__":
                # Pawn's first move can be two squares forward.
                possibleMoves.append(((row + 2, col), (row, col)))
            if board[row + 1][col] == "__":
                # Move one square forward.
                possibleMoves.append(((row + 1, col), (row, col)))
            if col - 1 >= 0 and board[row + 1][col - 1][0] == "w":
                # Capture diagonally to the left.
                possibleMoves.append(((row + 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row + 1][col + 1][0] == "w":
                # Capture diagonally to the right.
                possibleMoves.append(((row + 1, col + 1), (row, col)))

    def pawnPromotion(self, move, screen):
        # Handle pawn promotion when a pawn reaches the opposite end of the board.
        running = True
        p_names = ["wR", "wB", "wN", "wQ", "bR", "bB", "bN", "bQ"]
        IMAGES = {}
        color = ""
        font = p.font.SysFont("Arial", 15)
        for e in p_names:
            IMAGES[e] = p.transform.scale(p.image.load("img/" + e + ".png"), (75, 75))
        if self.white_turn:
            # If it's black's turn, set up the promotion options for white.
            color = "w"
            shift = 75 * (move[0][1] - 4) if move[0][1] > 4 else 0
            rect = p.draw.rect(
                screen,
                (255, 204, 117),
                (move[0][1] * 75 - shift, (move[0][0]) * 75 + 100, 4 * 75, 90),
                border_radius=5,
            )
            rect = p.draw.rect(
                screen,
                (0, 0, 0),
                (move[0][1] * 75 - shift, (move[0][0]) * 75 + 100, 300, 90),
                2,
                5,
            )
            for i in range(4):
                screen.blit(
                    IMAGES[p_names[i]],
                    p.Rect(
                        i * 75 + move[0][1] * 75 - 5 - shift,
                        (move[0][0]) * 75 + 100,
                        75,
                        75,
                    ),
                )
                f = font.render(str(i + 1), True, (0, 0, 0))
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
            # If it's white's turn, set up the promotion options for black.
            color = "b"
            shift = 75 * (move[0][1] - 4) if move[0][1] > 4 else 0
            rect = p.draw.rect(
                screen,
                (255, 204, 117),
                (move[0][1] * 75 - shift, (move[0][0]) * 75 - 100, 4 * 75, 90),
                border_radius=5,
            )
            rect = p.draw.rect(
                screen,
                (0, 0, 0),
                (move[0][1] * 75 - shift, (move[0][0]) * 75 - 100, 300, 90),
                2,
                5,
            )
            for i in range(4, len(p_names)):
                screen.blit(
                    IMAGES[p_names[i]],
                    p.Rect(
                        i * 75 + move[0][1] * 75 - 303 - shift,
                        (move[0][0]) * 75 - 100,
                        75,
                        75,
                    ),
                )
                f = font.render(str(i - 3), True, (0, 0, 0))
                screen.blit(
                    f,
                    p.Rect(
                        i * 75 + move[0][1] * 75 - 268.5 - shift,
                        (move[0][0]) * 75 - 28,
                        75,
                        75,
                    ),
                )
        p.display.flip()
        while running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                    exit("QUIT")
                elif e.type == p.KEYDOWN or e.type == p.KEYUP:
                    if e.key == p.K_1:
                        return color + "R"
                        running = False
                    elif e.key == p.K_2:
                        return color + "B"
                        running = False
                    elif e.key == p.K_3:
                        return color + "N"
                        running = False
                    elif e.key == p.K_4:
                        return color + "Q"
                        running = False
        return None

    def knightMoves(self, row, col, piece, board, possibleMoves):
        """
        Generate all possible knight moves from the given position.
        There are up to 8 possible moves for a knight.
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
                    possibleMoves.append(((r, c), (row, col)))

    def rookMoves(self, row, col, piece, board, possibleMoves):
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

    def bishopMoves(self, row, col, piece, board, possibleMoves):
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

    def queenMoves(self, row, col, piece, board, possibleMoves):
        # The queen's moves are a combination of rook and bishop moves.
        self.bishopMoves(row, col, piece, board, possibleMoves)
        self.rookMoves(row, col, piece, board, possibleMoves)

    def kingMoves(self, row, col, piece, board, possibleMoves):
        # Generate all possible king moves (one square in any direction).
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, 1),
            (1, 1),
            (-1, -1),
            (1, -1),
        ]
        for d in directions:
            r = row + d[0]
            c = col + d[1]
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c][0] != piece[0]:
                    possibleMoves.append(((r, c), (row, col)))

    def posOfPiece(self, piece):
        # Return positions of a given piece on the board.
        pos = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == piece:
                    pos.append((row, col))
        return pos

    def checkAroundKing(self, king):
        # Check for checks and pins around the king.
        print(self.kingPos)
        currColor = self.board[king[0]][king[1]][0]
        oColor = "w" if currColor == "b" else "b"
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        locOwnColor = False  # Flag to indicate if we've encountered our own piece.
        count = 0
        self.checkKnightcheck(oColor, self.kingPos)
        self.kingCantMoveWhere()

        for move in kMoves:  # Check all directions around the king.
            for i in range(1, 8):
                r_off = move[0] * i
                c_off = move[1] * i
                r = r_off + king[0]
                c = c_off + king[1]

                if 0 <= r < 8 and 0 <= c < 8:
                    # Get the current piece we are looking at.
                    piece = self.board[r][c]
                    # Piece color: "w" or "b".
                    pColor = piece[0]
                    # Piece type, e.g., 'Q' for queen, 'B' for bishop.
                    pType = piece[1]
                    # Check if the piece is from the same side.
                    if pColor == currColor:
                        # If already saw a piece from the same side, break.
                        if locOwnColor:
                            break
                        locOwnColor = (r, c)
                    else:
                        # If located one of our own pieces before, it means that the old piece can be pinned.
                        if locOwnColor:
                            print("Pin: ", (r, c), "{", move, "} ", piece)
                            self.pinned((r, c), locOwnColor, move, piece[1])
                            locOwnColor = False
                            break
                        # Check for checks from opponent pieces.
                        elif (c_off == 0 or r_off == 0) and (pType in "RQ"):
                            # Check if we are solely on the x or y axis with no slope (only queen and rook can check).
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, True, currColor)
                            count += 1
                        elif (c_off and r_off) and (pType in "BQ"):
                            # If we have slope (only queen and bishops can pin).
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, False, currColor)
                            count += 1
                        elif (
                            (currColor == "w" and r_off == -1 and abs(c_off) == 1)
                            or (currColor == "b" and r_off == abs(c_off) == 1)
                        ) and (pType == "P"):
                            # Check for pawn check.
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, False, currColor)
                            count += 1
                        else:
                            break
                else:
                    break
            locOwnColor = False
        if count > 0:
            self.check = True
        return count > 0
    
    def movePiece(self, r, c, piece):
        self.board[r][c] = piece

    def remMoves(self, r, c, vh, color):
        # Remove illegal moves due to checks.
        if vh:  # If vertical or horizontal.
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            if d_row == 0:
                for i in range(len(self.posMoves) - 1, -1, -1):
                    m = self.posMoves[i]
                    if m[1] == self.kingPos and (
                        (d_col > 0 and (m[0][0] == r and self.kingPos[1] > m[0][1] > c))
                        or (
                            d_col < 0
                            and (m[0][0] == r and self.kingPos[1] < m[0][1] < c)
                        )
                    ):
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
                print(self.posMoves)
                for i in range(len(self.posMoves) - 1, -1, -1):
                    m = self.posMoves[i]
                    if m[1] == self.kingPos and (
                        (d_row > 0 and (m[0][1] == c and self.kingPos[0] > m[0][0] > r))
                        or (d_row < 0 and (m[0][1] == c and m[0][0] != r))
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
            # Diagonal threats.
            print(self.kingPos)
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            d_row = d_row / abs(d_row)
            d_col = d_col / abs(d_col)
            places = [(r, c), (r + d_row, c + d_col)]
            l = 2
            while places[-1] != self.kingPos:
                print("while")
                places.append((r + d_row * l, c + d_col * l))
                l += 1
            l += 1
            for i in range(len(self.posMoves) - 1, -1, -1):
                if self.posMoves[i][1] == self.kingPos:
                    if self.posMoves[i][0][0] == r and (self.posMoves[i][0][1] == c):
                        continue
                    elif self.posMoves[i][0] in places or self.posMoves[i][0] == (
                        r + d_row * l,
                        c + d_col * l,
                    ):
                        self.posMoves.pop(i)
                elif self.posMoves[i][0] not in places:
                    self.posMoves.pop(i)

    def kingCantMoveWhere(self):
        # Determine squares where the king cannot move due to threats.
        b = [row[:] for row in self.board]
        for e in range(len(self.posMoves) - 1, -1, -1):
            piece = self.posMoves[e]
            if piece[1] == self.kingPos:
                b[piece[0][0]][piece[0][1]] = b[self.kingPos[0]][self.kingPos[1]]
                b[self.kingPos[0]][self.kingPos[1]] = "__"
                self.white_turn = not self.white_turn
                moves = self.genPossibleMoves(b)
                if (piece[0][0], piece[0][1]) in [x[0] for x in moves]:
                    self.posMoves.pop(e)
                b[piece[0][0]][piece[0][1]] = self.board[piece[0][0]][piece[0][1]]
                b[self.kingPos[0]][self.kingPos[1]] = self.board[self.kingPos[0]][
                    self.kingPos[1]
                ]
                self.white_turn = not self.white_turn

    def pinned(self, pinner, pinned, moveDir, piece):
        """
        Handle pinning of pieces. Remove moves that would expose the king to check if the piece is pinned.
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
                            self.posMoves.pop(i)
            elif m_r == 0 and (piece == "B" or piece == "Q"):
                print("Pin: B or Q")
                for i in range(len(self.posMoves) - 1, -1, -1):
                    movePiece = self.posMoves[i][1]
                    if movePiece == pinned:
                        movePlace = self.posMoves[i][0]

                        print(movePlace)
                        if movePiece[0] - movePlace[0] != 0 and movePlace != pinned:
                            self.posMoves.pop(i)
        elif piece == "Q" or piece == "B":
            print("Pin: B or Q outside elif")
            for i in range(len(self.posMoves) - 1, -1, -1):
                movePiece = self.posMoves[i][1]
                if movePiece == pinned:
                    movePlace = self.posMoves[i][0]
                    pieceDir = (
                        (movePiece[0] - movePlace[0])
                        / abs(
                            (
                                (movePiece[0] - movePlace[0])
                                if not movePiece[0] - movePlace[0] == 0
                                else 1
                            )
                        ),
                        (movePiece[1] - movePlace[1])
                        / abs(
                            (
                                (movePiece[1] - movePlace[1])
                                if not movePiece[1] - movePlace[1] == 0
                                else 1
                            )
                        ),
                    )
                    print(movePlace)
                    if pieceDir != moveDir and movePlace != pinner:
                        self.posMoves.pop(i)

    def checkKnightcheck(self, oColor, kingPos):
        # Check if the king is under attack by a knight.
        posKnightPlaces = []
        self.knightMoves(kingPos[0], kingPos[1], kingPos, self.board, posKnightPlaces)
        posKnightPlaces = [x[0] for x in posKnightPlaces]
        KnIsPresent = None
        for r, c in posKnightPlaces:
            if self.board[r][c] == oColor + "N":
                KnIsPresent = (r, c)
                break
        if KnIsPresent:
            for i in range(len(self.posMoves) - 1, -1, -1):
                p = self.posMoves[i]
                if p[0] != KnIsPresent and self.board[p[1][0]][p[1][1]][1] != "K":
                    # If the piece being moved is not the king and it does not capture the knight, remove the move.
                    self.posMoves.pop(i)
        else:
            pass


class Move:
    # Mappings between ranks/files and rows/columns.
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, typeOfMove = None):
        # Initialize a move with starting and ending squares.
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.type = typeOfMove

    def getChessNotation(self):
        # Return the move in standard chess notation.
        return (
            self.colsToFiles[self.startCol]
            + self.rowsToRanks[self.startRow]
            + self.colsToFiles[self.endCol]
            + self.rowsToRanks[self.endRow]
        )
