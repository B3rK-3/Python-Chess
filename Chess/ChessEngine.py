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

    def genPossibleMoves(self):
        """
        Method to generate the possible moves for a chess board depending on the move turn.
        """
        self.possibleMoves = []
        colors = ['w', 'b']
        turn = (0 if self.white_turn else 1)
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                b = self.board[row][col]
                if b[0] == colors[turn]:
                    if b[1] == 'P':
                        self.pawnMoves(row, col, b)
    def pawnMoves(self, row, col, b):
        """
        Check all of the possible moves for a pawn.
        """
        if b == 'w':
            if row == 6:  # To check if the pawn has never been moved therefore it can move 2
                self.possibleMoves.append((row - 2, col, b))
            self.possibleMoves.append((row - 1, col, b))
        elif b == 'b':
            if row == 1:  # To check if the pawn has never been moved therefore it can move 2
                self.possibleMoves.append((row + 2, col, b))
            self.possibleMoves.append((row + 1, col, b))
    def knightMoves(self, row, col, b):
        """
        Check all of the possible moves for a knight ps. there is max 8
        """
        if row + 2 < 8 and col - 1 < 8:
            self.possibleMoves.append((row + 2, col - 1, b))
        if row + 2 < 8 and col + 1 < 8:
            self.possibleMoves.append((row + 2, col + 1, b))
        if row - 2 < 8 and col - 1 < 8:
            self.possibleMoves.append((row - 2, col - 1, b))
        if row - 2 < 8 and col + 1 < 8:
            self.possibleMoves.append((row - 2, col + 1, b))
        # flip
        if col + 2 < 8 and row - 1 < 8:
            self.possibleMoves.append((row - 1, col + 2, b))
        if col + 2 < 8 and row + 1 < 8:
            self.possibleMoves.append((row + 1, col + 2, b))
        if col - 2 < 8 and row - 1 < 8:
            self.possibleMoves.append((row - 1, col - 2, b))
        if col - 2 < 8 and row + 1 < 8:
            self.possibleMoves.append((row + 1, col - 2, b))
    def rookMoves(self, row, col, b):
        """
        Generate all of the possible moves for a rook.
        """
        for i in range(7-row): # moves for downwards
            self.possibleMoves.append((row + i + 1, col, b))
        for i in range(row): # moves for upwards
            self.possibleMoves.append((row - i - 1, col, b))
        for i in range(7-col): # moves to the right
            self.possibleMoves.append((row, col + i + 1, b))
        for i in range(col): # moves to the left
            self.possibleMoves.append((row, col - i - 1, b))
    def bishopMoves(self, row, col, b):
        """
        Generate all of the possible moves for a bishop.
        """
        


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
