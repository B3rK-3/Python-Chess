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

