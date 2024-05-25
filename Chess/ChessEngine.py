"""
The engine is responsible for storing information about the chess board and game,
deciding whether the play is valid.
"""
import math

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
    def canCastle(self,rook,king):
        if not self.white_turn and self.blackHasCastled:
            return False
        if self.white_turn and self.whiteHasCastled:
            return False
        logs = [(x.startRow, x.startCol) for x in self.mLog]
        self.white_turn = not self.white_turn
        oppM = [x[0] for x in self.genValidMoves(self.board)]
        self.white_turn = not self.white_turn
        if rook not in logs and king not in logs:
            left = (True if rook[1] - king[1] < 0 else False)
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
        left = (True if rook[1] - king[1] < 0 else False)
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
            print("heere")
            if not isinstance(lastMove, tuple) and lastMove.pieceMoved[1] == "P" and abs(lastMove.endRow - lastMove.startRow) == 2 and move[1][1] == lastMove.endCol and move[0][0] == lastMove.endRow and ((self.white_turn and move[1][0]-lastMove.endRow == -1) or (not self.white_turn and move[1][0]-lastMove.endRow == 1)):
                passer = Move(move[0], move[1], self.board)
                passed = Move((lastMove.endRow,lastMove.endCol), (lastMove.endRow+(-1 if self.white_turn else 1),lastMove.endCol), self.board)
                self.makeMove(passer, passed)
                self.white_turn = not self.white_turn
                return True
    def genValidMoves(self, board):
        """"""
        """
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
            findInvalidMoves(i, kingPos)"""
        self.posMoves = self.genPossibleMoves(board)
        self.kingPos = self.findKingPos()
        self.checkAroundKing(self.kingPos)
        if self.posMoves == [] and self.checkAroundKing(self.kingPos):
            print("Checkmate!", ("Black wins!" if self.white_turn else "White wins!"))
        elif self.posMoves == []:
            print("Stalemate!")
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
                        self.pawnMoves(row, col, b, board, possibleMoves, colors[(1 if self.white_turn else 0)])
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
    def pawnMoves(self, row, col, b, board, possibleMoves, oColor):
        """
        Check all the possible moves for a pawn.
        """
        if len(self.mLog) > 1:
            lastMove = self.mLog[-1]
            if not isinstance(lastMove, tuple) and lastMove.pieceMoved[1] == "P" and abs(lastMove.endRow - lastMove.startRow) == 2 and row == lastMove.endRow:
                if col + 1 == lastMove.endCol:
                    if oColor == 'b':
                        possibleMoves.append(((row -1, col+1), (row, col)))
                    else:
                        possibleMoves.append(((row +1, col+1), (row, col)))
                if col - 1 == lastMove.endCol:
                    if oColor == 'b':
                        possibleMoves.append(((row -1, col-1), (row, col)))
                    else:
                        possibleMoves.append(((row +1, col-1), (row, col)))
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
        Check all the possible moves for a knight ps. there is max 8
        """
        if row + 2 < 8 and col - 1 >= 0 and board[row + 2][col-1][0] != b[0]:
            possibleMoves.append(((row + 2, col - 1), (row, col)))
        if row + 2 < 8 and col + 1 < 8 and board[row + 2][col+1][0] != b[0]:
            possibleMoves.append(((row + 2, col + 1), (row, col)))
        if row - 2 >= 0 and col - 1 >= 0 and board[row - 2][col-1][0] != b[0]:
            possibleMoves.append(((row - 2, col - 1), (row, col)))
        if row - 2 >= 0 and col + 1 < 8 and board[row - 2][col+1][0] != b[0]:
            possibleMoves.append(((row - 2, col + 1), (row, col)))
        # flip
        if col + 2 < 8 and row - 1 >= 0 and board[row - 1][col+2][0] != b[0]:
            possibleMoves.append(((row - 1, col + 2), (row, col)))
        if col + 2 < 8 and row + 1 < 8 and board[row + 1][col+2][0] != b[0]:
            possibleMoves.append(((row + 1, col + 2), (row, col)))
        if col - 2 >= 0 and row - 1 >= 0 and board[row - 1][col-2][0] != b[0]:
            possibleMoves.append(((row - 1, col - 2), (row, col)))
        if col - 2 >= 0 and row + 1 < 8 and board[row + 1][col-2][0] != b[0]:
            possibleMoves.append(((row + 1, col - 2), (row, col)))
    def rookMoves(self, row, col, b, board, possibleMoves):
        """
        Generate all the possible moves for a rook.
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
        Generate all the possible moves for a bishop.
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
    def checkPin(self, pos, king, it):
        """allM = [x[0] for x in self.posMoves] #all moves that we can move to
        color = ('w' if king[0] == 'b' else 'b')
        vMove = self.posMoves[it][0][0] - self.posMoves[it][1][0] #vertical move. can move up if neg and down if pos
        hMove = self.posMoves[it][0][1] - self.posMoves[it][1][1] #horizontal move. can move left if neg and right if pos
        #check horizontal and vertical

        def checkVer():
            for i in range(pos[0]+1,7-pos[0]): # moves for downwards
                b = self.board[i][pos[1]]
                if (b == color+'Q' or b == color+'R'): #check if rook or queen since only they can pin vertically and horizontally
                    if (i, pos[1]) not in allM:
                        popped = self.posMoves.pop(it)
                    else:
                        posM = [x if x[0] == (i,pos) else None for x in self.posMoves]
                        print(posM)
                        self.eatM.append(posM)
                    if popped:
                        return
                elif b[0] !='__':
                    break
            for i in range(pos[0]-1,-1,-1): # moves for upwards
                b = self.board[i][pos[1]]
                if (b == color + 'Q' or b == color + 'R'):  # check if rook or queen since only they can pin vertically and horizontally
                    if (i, pos[1]) not in allM:
                        popped = self.posMoves.pop(it)
                    else:
                        posM = [x if x[0] == (i, pos[1]) else None for x in self.posMoves]
                        print(posM)
                        self.eatM.append(posM)
                    if popped:
                        return
                elif b[0] != '__':
                    break
        def checkHor():
            for i in range(pos[1]+1,7-pos[1]): # moves to the right
                b = self.board[pos[0]][i]
                if (b == color + 'Q' or b == color + 'R'):  # check if rook or queen since only they can pin vertically and horizontally
                    if (pos[0], i) not in allM:
                        popped = self.posMoves.pop(it)
                    else:
                        posM = [x if x[0] == (pos[0], i) else None for x in self.posMoves]
                        print(posM)
                        self.eatM.append(posM)
                    if popped:
                        return
                elif b[0] != '__':
                    break
            for i in range(pos[1]-1,-1,-1): # moves to the left
                b = self.board[pos[0]][i]
                if (b == color + 'Q' or b == color + 'R'):  # check if rook or queen since only they can pin vertically and horizontally
                    if (pos[0], i) not in allM:
                        popped = self.posMoves.pop(it)
                    else:
                        posM = [x if x[0] == (pos[0], i) else None for x in self.posMoves]
                        print(posM)
                        self.eatM.append(posM)
                    if popped:
                        return
                elif b[0] != '__':
                    break
        #check diagonally
        def checkRU(): #right || up right and  bottom left
            for i in range(1, 8):
                col = pos[1] + i
                row = pos[0] + i
                if col < 8 and row < 8:
                    b = self.board[row][col]
                    if (
                            b == color + 'Q' or b == color + 'B'):  # check if bishop or queen since only they can pin diagonally
                        if (row, col) not in allM:
                            popped = self.posMoves.pop(it)
                        else:
                            posM = [x if x[0] == (row, col) else None for x in self.posMoves]
                            print(posM)
                            self.eatM.append(posM)
                        if popped:
                            return
                    elif b[0] != '__':
                        break
            for i in range(1, 8):
                col = pos[1] + i
                row = pos[0] - i
                if col < 8 and row >= 0:
                    if col >= 0 and row < 8:
                        b = self.board[row][col]
                        if (
                                b == color + 'Q' or b == color + 'B'):  # check if bishop or queen since only they can pin diagonally
                            if (row, col) not in allM:
                                popped = self.posMoves.pop(it)
                            else:
                                posM = [x if x[0] == (row, col) else None for x in self.posMoves]
                                print(posM)
                                self.eatM.append(posM)
                            if popped:
                                return
                        elif b[0] != '__':
                            break
        def checkLU():#left || down right and up left
            for i in range(1, 8):
                col = pos[1] - i
                row = pos[0] - i
                if col >= 0 and row >= 0:
                    if col >= 0 and row < 8:
                        b = self.board[row][col]
                        if (
                                b == color + 'Q' or b == color + 'B'):  # check if bishop or queen since only they can pin diagonally
                            if (row, col) not in allM:
                                popped = self.posMoves.pop(it)
                            else:
                                posM = [x if x[0] == (row, col) else None for x in self.posMoves]
                                print(posM)
                                self.eatM.append(posM)
                            if popped:
                                return
                        elif b[0] != '__':
                            break
            for i in range(1, 8):
                col = pos[1]-i
                row = pos[0]+i
                if col >= 0 and row < 8:
                    b = self.board[row][col]
                    if (b == color + 'Q' or b == color + 'B'):  # check if bishop or queen since only they can pin diagonally
                        if (row, col) not in allM:
                            popped = self.posMoves.pop(it)
                        else:
                            posM = [x if x[0] == (row, col) else None for x in self.posMoves]
                            print(posM)
                            self.eatM.append(posM)
                        if popped:
                            return
                    elif b[0] != '__':
                        break


        if vMove == 0 and hMove:
            checkVer()""" #Half written algorithm to check if it is pin.
        #It can work if more conditions are added, but I found an easier way to do it.
        #The code will stay just in case. New Code ->>
    def checkAroundKing(self, king):
        print(self.kingPos)
        color = self.board[king[0]][king[1]][0]
        oColor = ('w' if color == 'b' else 'b')
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        ownColor = None
        count = 0
        self.checkKnightcheck(oColor, self.kingPos)
        self.kingCantMoveWhere()

        for move in kMoves: #check all directions around the king
            for i in range(1,8):
                r_off = move[0] * i
                c_off = move[1] * i
                r = r_off + king[0]
                c = c_off + king[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.board[r][c]
                    if piece[0] == color:
                        if ownColor:
                            break
                        ownColor = (r,c)
                    elif piece[0] == oColor and ownColor:
                        print("Pin: ", (r,c), "{", move,"} ", piece)
                        self.pinned((r, c), ownColor, move, piece[1])
                        ownColor = None
                        break
                    if piece[0] == oColor and ((c_off == 0) or (r_off == 0)) and (piece[1] == 'R' or piece[1] == 'Q'):
                        print("Rem: ", (r, c), "{", move, "} ", piece[1])
                        self.remMoves(r,c, True, color)
                        count += 1
                    elif piece[0] == oColor and ((c_off != 0) and (r_off != 0)) and (piece[1] == 'B' or piece[1] == 'Q'):
                        print("Rem: ", (r, c), "{", move, "} ", piece[1])
                        self.remMoves(r, c, False, color)
                        count += 1
                    elif piece[0] == oColor and ((abs(c_off) == 1) and (abs(r_off) == 1)) and (piece[1] == 'P'):
                        print("Rem: ", (r, c), "{", move, "} ", piece[1])
                        self.remMoves(r,c,False,color)
                    if piece[0] == oColor:
                        break
            ownColor = None
        return count > 0
    def remMoves(self,r,c, vh, color):
        if vh: # if vertical or horizontal
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            if d_row == 0:
                for i in range(len(self.posMoves)-1, -1, -1):
                    m = self.posMoves[i]
                    if m[1] == self.kingPos and ((d_col > 0 and (m[0][0] == r and self.kingPos[1] > m[0][1] > c)) or (d_col < 0 and (m[0][0] == r and self.kingPos[1] < m[0][1] < c))):
                        self.posMoves.pop(i)
                    elif m[1] != self.kingPos and ((d_col > 0 and not (m[0][0] == r and self.kingPos[1] > m[0][1] >= c)) or (d_col < 0 and not (m[0][0] == r and self.kingPos[1] < m[0][1] <= c))):
                        self.posMoves.pop(i)
            if d_col == 0:
                print(self.posMoves)
                for i in range(len(self.posMoves)-1, -1, -1):
                    m = self.posMoves[i]
                    if m[1] == self.kingPos and ((d_row > 0 and (m[0][1] == c and self.kingPos[0] > m[0][0] > r)) or (d_row < 0 and (m[0][1] == c and m[0][0] != r))):
                        self.posMoves.pop(i)
                    elif m[1] != self.kingPos and ((d_row > 0 and not (m[0][1] == c and self.kingPos[0] > m[0][0] >= r)) or (d_row < 0 and not (m[0][1] == c and self.kingPos[0] < m[0][0] <= r))):
                        self.posMoves.pop(i)

        else:
            print(self.kingPos)
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            d_row = d_row/abs(d_row)
            d_col = d_col/abs(d_col)
            places = [(r,c),(r+d_row,c+d_col)]
            l = 2
            while places[-1] != self.kingPos:
                print("while")
                places.append((r+d_row*l,c+d_col*l))
                l+=1
            l+=1
            for i in range(len(self.posMoves) - 1, -1, -1):
                if self.posMoves[i][1] == self.kingPos:
                    if self.posMoves[i][0][0] == r and (self.posMoves[i][0][1] == c):
                        continue
                    elif (self.posMoves[i][0] in places or self.posMoves[i][0] == (r+d_row*l,c+d_col*l)):
                        self.posMoves.pop(i)
                elif self.posMoves[i][0] not in places:
                    self.posMoves.pop(i)
            """if not ((self.kingPos[0] <= toM[0][0] < r and self.kingPos[1] >= toM[0][1] > c) or (self.kingPos[0] >= toM[0][0] > r and self.kingPos[1] >= toM[0][1] > c) or (self.kingPos[0] >= toM[0][0] > r and self.kingPos[1] <= toM[0][1] < c) or (self.kingPos[0] <= toM[0][0] < r and self.kingPos[1] <= toM[0][1] < c)) and self.board[toM[1][0]][toM[1][1]][1] != 'K': # if it is not between the king and queen diagonally or orthogonally
                print(3,'\t', r, c)
                self.posMoves.pop(i)
            if self.board[toM[1][0]][toM[1][1]][1] == 'K' and ((self.kingPos[0] < toM[0][0] <= r and self.kingPos[1] > toM[0][1] > c) or (self.kingPos[0] > toM[0][0] >= r and self.kingPos[1] > toM[0][1] >= c) or (self.kingPos[0] > toM[0][0] > r and self.kingPos[1] < toM[0][1] <= c) or (self.kingPos[0] < toM[0][0] <= r and self.kingPos[1] < toM[0][1] < c)):
                print(4, toM)
                self.posMoves.pop(i)"""
    def kingCantMoveWhere(self):
        b = [row[:] for row in self.board]
        for e in range(len(self.posMoves)-1,-1,-1):
            piece = self.posMoves[e]
            if piece[1] == self.kingPos:
                b[piece[0][0]][piece[0][1]] = b[self.kingPos[0]][self.kingPos[1]]
                b[self.kingPos[0]][self.kingPos[1]] = "__"
                self.white_turn = not self.white_turn
                moves = self.genPossibleMoves(b)
                if (piece[0][0], piece[0][1]) in [x[0] for x in moves]:
                    self.posMoves.pop(e)
                b[piece[0][0]][piece[0][1]] = self.board[piece[0][0]][piece[0][1]]
                b[self.kingPos[0]][self.kingPos[1]] = self.board[self.kingPos[0]][self.kingPos[1]]
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
            if m_c == 0 and (piece == 'R' or piece == 'Q'):
                print("Pin: R or Q")
                for i in range(len(self.posMoves)-1,-1,-1):
                    movePiece = self.posMoves[i][1]
                    if movePiece == pinned:
                        movePlace = self.posMoves[i][0]
                        if movePiece[1] - movePlace[1] != 0:
                            self.posMoves.pop(i)
            elif m_r == 0 and (piece == 'B' or piece == 'Q'):
                print("Pin: B or Q")
                for i in range(len(self.posMoves)-1,-1,-1):
                    movePiece = self.posMoves[i][1]
                    if movePiece == pinned:
                        movePlace = self.posMoves[i][0]
                        if movePiece[0] - movePlace[0] != 0:
                            self.posMoves.pop(i)
        elif piece == 'Q' or piece == 'B':
            print("Pin: B or Q outside elif")
            for i in range(len(self.posMoves) - 1, -1, -1):
                movePiece = self.posMoves[i][1]
                if movePiece == pinned:
                    #if self.board[pinned[0]][pinned[1]][1] == "P" and :
                    movePlace = self.posMoves[i][0]
                    pieceDir = ((movePiece[0]-movePlace[0]) / abs(((movePiece[0]-movePlace[0]) if not movePiece[0]-movePlace[0] == 0 else 1)), (movePiece[1]-movePlace[1]) / abs(((movePiece[1]-movePlace[1]) if not movePiece[1]-movePlace[1] == 0 else 1)))
                    if pieceDir != moveDir:
                        self.posMoves.pop(i)
    def checkKnightcheck(self, oColor, kingPos):
        posKnightPlaces = []
        self.knightMoves(kingPos[0], kingPos[1], kingPos, self.board, posKnightPlaces)
        posKnightPlaces = [x[0] for x in posKnightPlaces]
        KnIsPresent = None
        for r,c in posKnightPlaces:
            if self.board[r][c] == oColor+'N':
                KnIsPresent = (r,c)
                break
        if KnIsPresent:
            for i in range(len(self.posMoves)-1, -1, -1):
                p = self.posMoves[i]
                if p[0] != KnIsPresent and self.board[p[1][0]][p[1][1]][1] != 'K': #if the piece being checked is not king and it does not eat the Knight, pop it
                    self.posMoves.pop(i)
        else:
            pass




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
