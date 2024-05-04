"""
The engine is responsible for storing information about the chess board and game,
deciding whether the play is valid.
"""


class GameState():
    def __init__(self):
        # This is a 2d list that will represent the board. bR = black rook, wR = white rook
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['__', '__', '__', '__', '__', '__', '__', '__'],
            ['__', '__', '__', '__', '__', '__', '__', '__'],
            ['__', '__', '__', '__', '__', '__', '__', '__'],
            ['__', '__', '__', '__', '__', '__', '__', '__'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        # Keeping track of moves
        self.white_turn = True
        # This will be the list that will keep track of the moves
        self.mLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "__"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.mLog.append(move)
        self.white_turn = not self.white_turn

    def undoMove(self):
        if len(self.mLog) > 0:
            m = self.mLog.pop()
            self.board[m.startRow][m.startCol] = m.pieceMoved
            self.board[m.endRow][m.endCol] = m.pieceCaptured
            self.white_turn = not self.white_turn

    def genValidMoves(self):
        """"""
        def findInvalidMoves(i, kingPos):
            moveP, fromP = self.posMoves[i]
            # print(moveP, fromP)
            board = [x[:] for x in self.board]
            board[moveP[0]][moveP[1]] = board[fromP[0]][fromP[1]]
            board[fromP[0]][fromP[1]] = "__"
            self.white_turn = not self.white_turn
            b1 = [x[0] for x in self.genPossibleMoves(board)]
            if kingPos in b1:
                self.posMoves.pop(i)
            self.white_turn = not self.white_turn


        self.posMoves = self.genPossibleMoves(self.board)
        kingPos = self.findKingPos()

        for i in range(len(self.posMoves)-1, -1, -1):
            findInvalidMoves(i, kingPos)
        return self.posMoves
    def genPossibleMoves(self, board):
        """
        Method to generate the possible moves for a chess board depending on the move turn.
        """
        possibleMoves = []
        colors = ['w', 'b']
        turn = (0 if self.white_turn else 1)
        for row in range(len(board)):
            for col in range(len(board[0])):
                b = board[row][col]
                if b[0] == colors[turn]:
                    if b[1] == 'P':
                        self.pawnMoves(row, col, b, board, possibleMoves)
                    elif b[1] == 'N':
                        self.knightMoves(row, col, b, board, possibleMoves)
                    elif b[1] == 'R':
                        self.rookMoves(row, col, b, board, possibleMoves)
                    elif b[1] == 'B':
                        self.bishopMoves(row, col, b, board, possibleMoves)
                    elif b[1] == 'Q':
                        self.queenMoves(row, col, b, board, possibleMoves)
                    elif b[1] == 'K':
                        self.kingMoves(row, col, b, board, possibleMoves)
        return possibleMoves
    def pawnMoves(self, row, col, b, board, possibleMoves):
        """
        Check all of the possible moves for a pawn.
        """
        if b[0] == 'w':
            if row == 6 and board[row-1][col] == "__" and board[row-2][col] == "__":  # To check if the pawn has never been moved therefore it can move 2
                possibleMoves.append(((row - 2, col), (row, col)))
            if board[row-1][col] == "__":
                possibleMoves.append(((row - 1, col), (row, col)))
            if col - 1 >= 0 and board[row-1][col-1][0] == 'b':
                possibleMoves.append(((row - 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row-1][col+1][0] == 'b':
                possibleMoves.append(((row - 1, col + 1), (row, col)))
        elif b[0] == 'b':
            if row == 1 and board[row+1][col] == "__" and board[row+2][col] == '__':  # To check if the pawn has never been moved therefore it can move 2
                possibleMoves.append(((row + 2, col), (row, col)))
            if board[row+1][col] == "__":
                possibleMoves.append(((row + 1, col), (row, col)))
            if col - 1 >= 0 and board[row + 1][col - 1][0] == 'w':
                possibleMoves.append(((row + 1, col - 1), (row, col)))
            if col + 1 < 8 and board[row + 1][col + 1][0] == 'w':
                possibleMoves.append(((row + 1, col + 1), (row, col)))
    def knightMoves(self, row, col, b, board, possibleMoves):
        """
        Check all of the possible moves for a knight ps. there is max 8
        """
        if row + 2 < 8 and col - 1 < 8 and board[row + 2][col-1][0] != b[0]:
            possibleMoves.append(((row + 2, col - 1), (row, col)))
        if row + 2 < 8 and col + 1 < 8 and board[row + 2][col+1][0] != b[0]:
            possibleMoves.append(((row + 2, col + 1), (row, col)))
        if row - 2 < 8 and col - 1 < 8 and board[row - 2][col-1][0] != b[0]:
            possibleMoves.append(((row - 2, col - 1), (row, col)))
        if row - 2 < 8 and col + 1 < 8 and board[row - 2][col+1][0] != b[0]:
            possibleMoves.append(((row - 2, col + 1), (row, col)))
        # flip
        if col + 2 < 8 and row - 1 < 8 and board[row - 1][col+2][0] != b[0]:
            possibleMoves.append(((row - 1, col + 2), (row, col)))
        if col + 2 < 8 and row + 1 < 8 and board[row + 1][col+2][0] != b[0]:
            possibleMoves.append(((row + 1, col + 2), (row, col)))
        if col - 2 < 8 and row - 1 < 8 and board[row - 1][col-2][0] != b[0]:
            possibleMoves.append(((row - 1, col - 2), (row, col)))
        if col - 2 < 8 and row + 1 < 8 and board[row + 1][col-2][0] != b[0]:
            possibleMoves.append(((row + 1, col - 2), (row, col)))
    def rookMoves(self, row, col, b, board, possibleMoves):
        """
        Generate all of the possible moves for a rook.
        """
        for i in range(7-row): # moves for downwards
            if board[row + i + 1][col][0] == b[0]:
                break
            possibleMoves.append(((row + i + 1, col), (row, col)))
            if board[row + i + 1][col][0] != b[0] and board[row + i + 1][col][0] != '_':
                break
        for i in range(row): # moves for upwards
            if board[row - i - 1][col][0] == b[0]:
                break
            possibleMoves.append(((row - i - 1, col), (row, col)))
            if board[row - i - 1][col][0] != b[0] and board[row - i - 1][col][0] != '_':
                break
        for i in range(7-col): # moves to the right
            if board[row][col+i+1][0] == b[0]:
                break
            possibleMoves.append(((row, col + i + 1), (row, col)))
            if board[row][col + i + 1][0] != b[0] and board[row][col + i + 1][0] != '_':
                break
        for i in range(col): # moves to the left
            if board[row][col-i-1][0] == b[0]:
                break
            possibleMoves.append(((row, col - i - 1), (row, col)))
            if board[row][col - i - 1][0] != b[0] and board[row][col - i - 1][0] != '_':
                break
    def bishopMoves(self, row, col, b, board, possibleMoves):
        """
        Generate all of the possible moves for a bishop.
        """
        for i in range(1, 8):
            if col + i < 8 and row + i < 8:
                if board[row + i][col + i][0] == b[0]:
                    break
                possibleMoves.append(((row+i,col+i),(row, col)))
                if board[row + i][col + i][0] != b[0] and board[row + i][col + i][0] != "_":
                    break
        for i in range(1, 8):
            if col + i < 8 and row - i >= 0:
                if board[row - i][col + i][0] == b[0]:
                    break
                possibleMoves.append(((row-i,col+i),(row, col)))
                if board[row - i][col + i][0] != b[0] and board[row - i][col + i][0] != "_":
                    break
        for i in range(1, 8):
            if col - i >= 0 and row - i >= 0:
                if board[row - i][col-i][0] == b[0]:
                    break
                possibleMoves.append(((row-i,col-i),(row, col)))
                if board[row - i][col - i][0] != b[0] and board[row - i][col - i][0] != "_":
                    break
        for i in range(1, 8):
            if col - i >= 0 and row + i < 8:
                if board[row + i][col-i][0] == b[0]:
                    break
                possibleMoves.append(((row+i,col-i),(row, col)))
                if board[row + i][col - i][0] != b[0] and board[row + i][col - i][0] != "_":
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
    def findKingPos(self):
        kingPos = ()
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.white_turn and self.board[row][col] == "wK":
                    kingPos = (row, col)
                    break
                if not self.white_turn and self.board[row][col] == "bK":
                    kingPos = (row, col)
                    break
        return kingPos




class Move():
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
        return self.colsToFiles[self.startCol] + self.rowsToRanks[self.startRow] + self.colsToFiles[self.endCol] + \
            self.rowsToRanks[self.endRow]
