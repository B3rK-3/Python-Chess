"""
The engine is responsible for storing information about the chess board and game,
deciding whether the play is valid.
"""

import math
import pygame as p


class GameState:
    def __init__(self):
        # This is a 2d list that will represent the board. bR = black rook, wR = white rook
        self.board = [
            ["bR", "bN", "bB", "__", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "__", "bP", "bP", "bP", "bP"],
            ["__", "__", "__", "__", "bP", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["wP", "wP", "wP", "wP", "__", "wP", "wP", "wP"],
            ["wR", "__", "wB", "wQ", "wK", "__", "__", "wR"],
        ]
        # Keeping track of moves
        self.white_turn = True
        # This will be the list that will keep track of the moves
        self.mLog = []
        self.whiteHasCastled = False
        self.blackHasCastled = False

    def makeMove(self, move, move1):
        if not move1:
            self.board[move.startRow][move.startCol] = "__"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.mLog.append(move)
            self.white_turn = not self.white_turn
        else:
            self.board[move1.startRow][move1.startCol] = "__"
            self.board[move1.endRow][move1.endCol] = move1.pieceMoved
            self.board[move.startRow][move.startCol] = "__"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.mLog.append((move, move1))

    def undoMove(self):
        if len(self.mLog) > 0:
            m = self.mLog.pop()
            if not isinstance(m, tuple):
                self.board[m.startRow][m.startCol] = m.pieceMoved
                self.board[m.endRow][m.endCol] = m.pieceCaptured
                self.white_turn = not self.white_turn
            else:
                self.board[m[0].startRow][m[0].startCol] = m[0].pieceMoved
                self.board[m[0].endRow][m[0].endCol] = m[0].pieceCaptured
                self.board[m[1].startRow][m[1].startCol] = m[1].pieceMoved
                self.board[m[1].endRow][m[1].endCol] = m[1].pieceCaptured
                self.white_turn = not self.white_turn
                if not self.white_turn:
                    self.whiteHasCastled = False
                else:
                    self.whiteHasCastled = False

    def genCastle(self):
        logs = [(x.startRow, x.startCol) for x in self.mLog]
        if self.white_turn:
            king = (7, 4)
            rooks = [(7, 0), (7, 7)]
            currRooks = self.posOfPiece("wR")
        else:
            king = (0, 4)
            rooks = [(0, 0), (0, 7)]
            currRooks = self.posOfPiece("bR")
        if king != self.kingPos:
            return False
        rooksInPlace = []
        for rook in currRooks:
            if rook in rooks:
                rooksInPlace.append(rook)

        self.white_turn = not self.white_turn
        oppM = [x[0] for x in self.genValidMoves(self.board)]
        self.white_turn = not self.white_turn
        king = self.kingPos

    def canCastle(self, rook, king):
        if not self.white_turn and self.blackHasCastled:
            return False
        elif self.white_turn and self.whiteHasCastled:
            return False
        logs = [(x.startRow, x.startCol) for x in self.mLog]
        self.white_turn = not self.white_turn
        oppM = [x[0] for x in self.genValidMoves(self.board)]
        self.white_turn = not self.white_turn

        if rook not in logs and king not in logs:
            left = True if rook[1] - king[1] < 0 else False
            if not left:
                for i in range(king[1] + 1, rook[1]):
                    if self.board[king[0]][i] != "__" or (king[0], i) in oppM:
                        return False
            else:
                for i in range(rook[1] + 1, king[1]):
                    if self.board[king[0]][i] != "__" or (king[0], i) in oppM:
                        return False
        return True

    def castleMove(self, rook, king):
        castle = self.canCastle(rook, king)
        if not castle:
            return
        moveC = Move(king, rook, self.board)
        if self.white_turn:
            self.whiteHasCastled = True
        else:
            self.blackHasCastled = True
        left = True if rook[1] - king[1] < 0 else False
        if left:
            kMloc = (king[0], 2)  # math.ceil to account for the right side castling
            rMloc = (kMloc[0], 3)
        else:
            kMloc = (king[0], 6)  # math.ceil to account for the right side castling
            rMloc = (kMloc[0], 5)
        moveK = Move(king, kMloc, self.board)
        moveR = Move(rook, rMloc, self.board)
        self.makeMove(moveK, moveR)
        self.white_turn = not self.white_turn

    def make_if_en_passant(self, move):
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
        self.posMoves = self.genPossibleMoves(board)
        self.kingPos = self.posOfPiece("wK" if self.white_turn else "bK")[0]
        numOfChecks = self.checkAroundKing(self.kingPos)
        if self.posMoves == [] and numOfChecks:
            print("Checkmate!", ("Black wins!" if self.white_turn else "White wins!"))
        elif self.posMoves == []:
            print("Stalemate!")
        return self.posMoves

    def genPossibleMoves(self, board):
        """
        Method to generate the possible moves for a chess board depending on the move turn.
        """
        possibleMoves = []
        colors = ["w", "b"]
        turn = 0 if self.white_turn else 1
        for row in range(len(board)):
            for col in range(len(board[0])):
                b = board[row][col]
                if b[0] == colors[turn]:
                    if b[1] == "P":
                        self.pawnMoves(
                            row,
                            col,
                            b,
                            board,
                            possibleMoves,
                            colors[(1 if self.white_turn else 0)],
                        )
                    elif b[1] == "N":
                        self.knightMoves(row, col, b, board, possibleMoves)
                    elif b[1] == "R":
                        self.rookMoves(row, col, b, board, possibleMoves)
                    elif b[1] == "B":
                        self.bishopMoves(row, col, b, board, possibleMoves)
                    elif b[1] == "Q":
                        self.queenMoves(row, col, b, board, possibleMoves)
                    elif b[1] == "K":
                        self.kingMoves(row, col, b, board, possibleMoves)
        return possibleMoves

    def pawnMoves(self, row, col, b, board, possibleMoves, oColor):
        """
        Check all the possible moves for a pawn.
        """
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
        if b[0] == "w":
            if (
                row == 6 and board[row - 1][col] == "__" and board[row - 2][col] == "__"
            ):  # To check if the pawn has never been moved therefore it can move 2
                possibleMoves.append(((row - 2, col), (row, col)))
            if board[row - 1][col] == "__":
                possibleMoves.append(((row - 1, col), (row, col)))
            if col - 1 >= 0 and board[row - 1][col - 1][0] == "b":
                possibleMoves.append(((row - 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row - 1][col + 1][0] == "b":
                possibleMoves.append(((row - 1, col + 1), (row, col)))
        elif b[0] == "b":
            if (
                row == 1 and board[row + 1][col] == "__" and board[row + 2][col] == "__"
            ):  # To check if the pawn has never been moved therefore it can move 2
                possibleMoves.append(((row + 2, col), (row, col)))
            if board[row + 1][col] == "__":
                possibleMoves.append(((row + 1, col), (row, col)))
            if col - 1 >= 0 and board[row + 1][col - 1][0] == "w":
                possibleMoves.append(((row + 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row + 1][col + 1][0] == "w":
                possibleMoves.append(((row + 1, col + 1), (row, col)))

    def pawnPromotion(self, move, screen):
        running = True
        p_names = ["wR", "wB", "wN", "wQ", "bR", "bB", "bN", "bQ"]
        IMAGES = {}
        color = ""
        font = p.font.SysFont("Arial", 15)
        for e in p_names:
            IMAGES[e] = p.transform.scale(p.image.load("img/" + e + ".png"), (75, 75))
        if not self.white_turn:
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
                if e.type == p.KEYDOWN or e.type == p.KEYUP:
                    if e.key == p.K_1:
                        self.board[move[0][0]][move[0][1]] = color + "R"
                        running = False
                    elif e.key == p.K_2:
                        self.board[move[0][0]][move[0][1]] = color + "B"
                        running = False
                    elif e.key == p.K_3:
                        self.board[move[0][0]][move[0][1]] = color + "N"
                        running = False
                    elif e.key == p.K_4:
                        self.board[move[0][0]][move[0][1]] = color + "Q"
                        running = False

    def knightMoves(self, row, col, b, board, possibleMoves):
        """
        Check all the possible moves for a knight ps. there is max 8
        """
        if row + 2 < 8 and col - 1 >= 0 and board[row + 2][col - 1][0] != b[0]:
            possibleMoves.append(((row + 2, col - 1), (row, col)))
        if row + 2 < 8 and col + 1 < 8 and board[row + 2][col + 1][0] != b[0]:
            possibleMoves.append(((row + 2, col + 1), (row, col)))
        if row - 2 >= 0 and col - 1 >= 0 and board[row - 2][col - 1][0] != b[0]:
            possibleMoves.append(((row - 2, col - 1), (row, col)))
        if row - 2 >= 0 and col + 1 < 8 and board[row - 2][col + 1][0] != b[0]:
            possibleMoves.append(((row - 2, col + 1), (row, col)))
        # flip
        if col + 2 < 8 and row - 1 >= 0 and board[row - 1][col + 2][0] != b[0]:
            possibleMoves.append(((row - 1, col + 2), (row, col)))
        if col + 2 < 8 and row + 1 < 8 and board[row + 1][col + 2][0] != b[0]:
            possibleMoves.append(((row + 1, col + 2), (row, col)))
        if col - 2 >= 0 and row - 1 >= 0 and board[row - 1][col - 2][0] != b[0]:
            possibleMoves.append(((row - 1, col - 2), (row, col)))
        if col - 2 >= 0 and row + 1 < 8 and board[row + 1][col - 2][0] != b[0]:
            possibleMoves.append(((row + 1, col - 2), (row, col)))

    def rookMoves(self, row, col, b, board, possibleMoves):
        """
        Generate all the possible moves for a rook.
        """
        for i in range(7 - row):  # moves for downwards
            if board[row + i + 1][col][0] == b[0]:
                break
            possibleMoves.append(((row + i + 1, col), (row, col)))
            if board[row + i + 1][col][0] != b[0] and board[row + i + 1][col][0] != "_":
                break
        for i in range(row):  # moves for upwards
            if board[row - i - 1][col][0] == b[0]:
                break
            possibleMoves.append(((row - i - 1, col), (row, col)))
            if board[row - i - 1][col][0] != b[0] and board[row - i - 1][col][0] != "_":
                break
        for i in range(7 - col):  # moves to the right
            if board[row][col + i + 1][0] == b[0]:
                break
            possibleMoves.append(((row, col + i + 1), (row, col)))
            if board[row][col + i + 1][0] != b[0] and board[row][col + i + 1][0] != "_":
                break
        for i in range(col):  # moves to the left
            if board[row][col - i - 1][0] == b[0]:
                break
            possibleMoves.append(((row, col - i - 1), (row, col)))
            if board[row][col - i - 1][0] != b[0] and board[row][col - i - 1][0] != "_":
                break

    def bishopMoves(self, row, col, b, board, possibleMoves):
        """
        Generate all the possible moves for a bishop.
        """
        for i in range(1, 8):
            if col + i < 8 and row + i < 8:
                if board[row + i][col + i][0] == b[0]:
                    break
                possibleMoves.append(((row + i, col + i), (row, col)))
                if (
                    board[row + i][col + i][0] != b[0]
                    and board[row + i][col + i][0] != "_"
                ):
                    break
        for i in range(1, 8):
            if col + i < 8 and row - i >= 0:
                if board[row - i][col + i][0] == b[0]:
                    break
                possibleMoves.append(((row - i, col + i), (row, col)))
                if (
                    board[row - i][col + i][0] != b[0]
                    and board[row - i][col + i][0] != "_"
                ):
                    break
        for i in range(1, 8):
            if col - i >= 0 and row - i >= 0:
                if board[row - i][col - i][0] == b[0]:
                    break
                possibleMoves.append(((row - i, col - i), (row, col)))
                if (
                    board[row - i][col - i][0] != b[0]
                    and board[row - i][col - i][0] != "_"
                ):
                    break
        for i in range(1, 8):
            if col - i >= 0 and row + i < 8:
                if board[row + i][col - i][0] == b[0]:
                    break
                possibleMoves.append(((row + i, col - i), (row, col)))
                if (
                    board[row + i][col - i][0] != b[0]
                    and board[row + i][col - i][0] != "_"
                ):
                    break

    def queenMoves(self, row, col, b, board, possibleMoves):
        self.bishopMoves(row, col, b, board, possibleMoves)
        self.rookMoves(row, col, b, board, possibleMoves)

    def kingMoves(self, row, col, b, board, possibleMoves):
        if col + 1 < 8 and row - 1 >= 0 and board[row - 1][col + 1][0] != b[0]:
            possibleMoves.append(((row - 1, col + 1), (row, col)))
        if col + 1 < 8 and row + 1 < 8 and board[row + 1][col + 1][0] != b[0]:
            possibleMoves.append(((row + 1, col + 1), (row, col)))
        if col - 1 >= 0 and row - 1 >= 0 and board[row - 1][col - 1][0] != b[0]:
            possibleMoves.append(((row - 1, col - 1), (row, col)))
        if col - 1 >= 0 and row + 1 < 8 and board[row + 1][col - 1][0] != b[0]:
            possibleMoves.append(((row + 1, col - 1), (row, col)))
        if row - 1 >= 0 and board[row - 1][col][0] != b[0]:
            possibleMoves.append(((row - 1, col), (row, col)))
        if col - 1 >= 0 and board[row][col - 1][0] != b[0]:
            possibleMoves.append(((row, col - 1), (row, col)))
        if row + 1 < 8 and board[row + 1][col][0] != b[0]:
            possibleMoves.append(((row + 1, col), (row, col)))
        if col + 1 < 8 and board[row][col + 1][0] != b[0]:
            possibleMoves.append(((row, col + 1), (row, col)))

    def posOfPiece(self, piece):
        pos = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == piece:
                    pos.append((row, col))
        return pos

    def checkAroundKing(self, king):
        print(self.kingPos)
        currColor = self.board[king[0]][king[1]][0]
        oColor = "w" if currColor == "b" else "b"
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        locOwnColor = (
            False  # Location of our own color where it has a chance of being pinned
        )
        count = 0
        self.checkKnightcheck(oColor, self.kingPos)
        self.kingCantMoveWhere()

        for move in kMoves:  # check all directions around the king
            for i in range(1, 8):
                r_off = move[0] * i
                c_off = move[1] * i
                r = r_off + king[0]
                c = c_off + king[1]

                if 0 <= r < 8 and 0 <= c < 8:
                    # get the current piece we are looking at
                    piece = self.board[r][c]
                    # piece color  "w" or "b"
                    pColor = piece[0]
                    # piece tpye ex: queen or bishop
                    pType = piece[1]
                    # check if the piece is from the same side
                    if pColor == currColor:
                        # if already saw a piece from the same side break
                        if locOwnColor:
                            break
                        locOwnColor = (r, c)
                    # if the piece from the other side
                    else:
                        # if located one of our own team before, it means that the old piece can be pinned
                        # 1 row ex: "wK" "wP" "bQ" wP is pinned
                        if locOwnColor:
                            print("Pin: ", (r, c), "{", move, "} ", piece)
                            self.pinned((r, c), locOwnColor, move, piece[1])
                            locOwnColor = False
                            break
                        # from here we know that we did not find any of our own pieces and the piexe color is the opposite side so we have to check for checks
                        elif (
                            (c_off == 0 or r_off == 0) and (pType in "RQ")
                        ):  # check if we are solely on the x or y axis with no slope (only queen and rook can check)
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, True, currColor)
                            count += 1
                        elif (c_off and r_off) and (
                            pType in "BQ"
                        ):  # if we have slope (only queen and bishops can pin)
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, False, currColor)
                            count += 1
                        elif (
                            (currColor == "w" and r_off == -1 and abs(c_off) == 1)
                            or (currColor == "b" and r_off == abs(c_off) == 1)
                        ) and (
                            pType == "P"
                        ):  # check of a paw pin where it can only be pinned if the
                            print("Rem: ", (r, c), "{", move, "} ", piece[1])
                            self.remMoves(r, c, False, currColor)
                            count += 1
                        else:
                            break
            locOwnColor = False
        return count > 0

    def remMoves(self, r, c, vh, color):
        if vh:  # if vertical or horizontal
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
        This function checks if a piece is pinned to the king by a rook, bishop, or queen.
        If it is pinned, it removes moves that involve the pinned piece if moving it would
        expose the king to a check.
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
                    # if self.board[pinned[0]][pinned[1]][1] == "P" and :
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
                if (
                    p[0] != KnIsPresent and self.board[p[1][0]][p[1][1]][1] != "K"
                ):  # if the piece being checked is not king and it does not eat the Knight, pop it
                    self.posMoves.pop(i)
        else:
            pass


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

    def getChessNotation(self):
        return (
            self.colsToFiles[self.startCol]
            + self.rowsToRanks[self.startRow]
            + self.colsToFiles[self.endCol]
            + self.rowsToRanks[self.endRow]
        )
