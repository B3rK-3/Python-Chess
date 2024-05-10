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
        self.posMoves = self.genPossibleMoves(self.board)
        self.kingPos = self.findKingPos()
        self.checkAroundKing(self.kingPos)
        if self.posMoves == [] and self.checkAroundKing(self.kingPos):
            print("Checkmate!", ("Black wins" if not self.white_turn else "White wins"))
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
        Check all the possible moves for a pawn.
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
        Check all the possible moves for a knight ps. there is max 8
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
        color = self.board[king[0]][king[1]][0]
        oColor = ('w' if color == 'b' else 'b')
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        self.kingCantMoveWhere()
        ownColor = 0
        count = 0
        for move in kMoves:
            for i in range(1,8):
                r_off = move[0] * i
                c_off = move[1] * i
                r = r_off + king[0]
                c = c_off + king[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    # TODO ADD A WAY TO CHECK CHECK BY KNIGHT
                    piece = self.board[r][c]
                    if piece[0] == oColor and ((c_off == 0) or (r_off == 0)) and (piece[1] == 'R' or piece[1] == 'Q'):
                        self.remMoves(r,c, True, color)
                        count += 1
                    elif piece[0] == oColor and ((c_off != 0) and (r_off != 0)) and (piece[1] == 'B' or piece[1] == 'Q'):
                        self.remMoves(r, c, False, color)
                        count += 1
                    if piece[0] == oColor:
                        break
                    if piece[0] == color and ownColor != 1:
                        ownColor += 1
                        self.pinned(r, c, move)
                    else: break
                else: break
            ownColor = 0
        return count > 0
    def remMoves(self,r,c, vh, color):
        if vh: # if vertical or horizontal
            for i in range(len(self.posMoves)-1, -1, -1):
                toM = self.posMoves[i]
                if not (self.kingPos[0] < toM[0][0] <= r or self.kingPos[0] > toM[0][0] >= r or self.kingPos[1] < toM[0][1] <= c or self.kingPos[1] > toM[0][1] >= c) and self.board[toM[1][0]][toM[1][1]][1] != 'K': # if the piece that can be moved is not blocking the check then pop it
                    print(1)
                    self.posMoves.pop(i)
                if self.board[toM[1][0]][toM[1][1]][1] == 'K' and (toM[0][0] == r or toM[0][1] == c) and toM[0][0] != r and toM[0][1] != c: # if the king move is in the same row or column as the piece attacking then remove it
                    print(2)
                    self.posMoves.pop(i)
        else:
            d_row = self.kingPos[0] - r
            d_col = self.kingPos[1] - c
            d_row = d_row/abs(d_row)
            d_col = d_col/abs(d_col)
            places = [(r,c),(r+d_row,c+d_col)]
            l = 2
            while places[-1] != self.kingPos:
                places.append((r+d_row*l,c+d_col*l))
                l+=1
            l+=1
            for i in range(len(self.posMoves) - 1, -1, -1):
                print(self.posMoves[i])
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
        kingPossible = []
        for e,i in enumerate(self.posMoves):
            if i[1] == self.kingPos:
                kingPossible.append(e)
        color = self.board[self.kingPos[0]][self.kingPos[1]][0]
        oColor = ('w' if color == 'b' else 'b')
        kMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        for e in kingPossible:
            king = self.posMoves[e][0]
            print(king)
            for move in kMoves:
                for i in range(1, 8):
                    r_off = move[0] * i
                    c_off = move[1] * i
                    r = r_off + king[0]
                    c = c_off + king[1]
                    if 0 <= r < 8 and 0 <= c < 8:
                        piece = self.board[r][c]
                        print(3, piece)
                        if piece[0] == oColor and ((c_off == 0) or (r_off == 0)) and (piece[1] == 'R' or piece[1] == 'Q'):
                            self.posMoves.pop(e)
                            break
                        if piece[0] == oColor and ((c_off != 0) and (r_off != 0)) and (piece[1] == 'B' or piece[1] == 'Q'):
                            self.posMoves.pop(e)
                            break
                        if piece[0] == color:
                            break
    def pinned(self, r1, c1, move):
        def iterateRem(toRem):
            for i in range(len(self.posMoves)-1, -1, -1):
                p = self.posMoves[i]
                if p[1] == toRem:
                    self.posMoves.pop(i)
        color = self.board[r1][c1][0]
        oColor = ('w' if color == 'b' else 'b')
        for i in range(1, 8):
            r_off = move[0] * i
            c_off = move[1] * i
            r = r_off + r1
            c = c_off + c1
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece[0] == oColor and ((c_off == 0) or (r_off == 0)) and (piece[1] == 'R' or piece[1] == 'Q'):
                    iterateRem((r1,c1))
                elif piece[0] == oColor and ((c_off != 0) and (r_off != 0)) and (piece[1] == 'B' or piece[1] == 'Q'):
                    iterateRem((r1, c1))
                if piece[0] == color or piece[0] == oColor:
                    break


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
