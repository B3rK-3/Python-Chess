"""
Main.py file is responsible for running the game engine. Will handle user input and GUI.
"""
import pygame as p
import pygame.font

from Python_Chess_Engine.Chess import ChessEngine

WIDTH = HEIGHT = 600
SIZE = 8
SQ_EACH_SIZE = HEIGHT // SIZE
MAX_FPS = 15
IMAGES = {}

def load_images():
    """
    INITIALIZING A GLOBAL DICT OF IMAGES. ONLY LOADED ONCE
    """
    p_names = ['wP', 'wR', 'wB', 'wN', 'wQ', 'wK', 'bP', 'bR', 'bB', 'bN', 'bQ', 'bK']
    for e in p_names:
        IMAGES[e] = p.transform.scale(p.image.load('img/' + e + '.png'), (SQ_EACH_SIZE, SQ_EACH_SIZE))

def main(): # Driver code for the main chess game
    p.init()
    load_images() # done only once to save memory
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('CHESS IN PYTHON')
    clock = p.time.Clock()
    FPS = MAX_FPS
    gs = ChessEngine.GameState()
    running = True
    dragging = False
    move = [] # two tuples [(7,7), (6,3)] will store where the user wants to move the piece to
    mpx = 0
    mpy = 0
    vMoves = gs.genValidMoves(gs.board)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                mx, my = p.mouse.get_pos()
                if mx < HEIGHT and my < WIDTH:
                    mpx = mx//SQ_EACH_SIZE
                    mpy = my//SQ_EACH_SIZE
                    move.append((mpy, mpx))
                    print(move)
                if len(move) == 2:
                    if gs.board[move[0][0]][move[0][1]][1] == "P":
                        print("down")
                        s = gs.is_en_passant(move)
                    if gs.board[move[0][0]][move[0][1]][1] != "P" or not s:
                        if gs.board[move[0][0]][move[0][1]][1] == "K" and gs.board[move[1][0]][move[1][1]][1] == "R":
                            gs.castleMove(move[1], move[0])
                            dragging = True
                            vMoves = gs.genValidMoves(gs.board)
                            move.clear()
                        elif ((move[1][0], move[1][1]),(move[0][0], move[0][1])) in vMoves: # making sure there were two clicks before
                            moveC = ChessEngine.Move((move[0][0], move[0][1]), (move[1][0], move[1][1]), gs.board)
                            gs.makeMove(moveC, None)
                            vMoves = gs.genValidMoves(gs.board) #gen new valid moves
                            dragging = True
                            move.clear()
                        elif gs.board[mpy][mpx] != '__':
                            move = [(mpx, mpy)]
                            print(move)
                    move.clear()

            elif e.type == p.MOUSEBUTTONUP:
                mx, my = p.mouse.get_pos()
                my = my//SQ_EACH_SIZE
                mx = mx//SQ_EACH_SIZE
                if mpx < SIZE and mpy < SIZE and mx < HEIGHT and my < WIDTH and gs.board[mpy][mpx] != "__" and (mx,my) != (mpx, mpy): #make sure that the dragged is not empty and within bounds
                    #for the if condition the last condition makes sure that the we are not trying to drag it into the same place (it messes with the click move property)
                    if gs.board[mpy][mpx][1] == "P":
                        print("up")
                        s = gs.is_en_passant(((mpy, mpx), (my, mx)))
                    if gs.board[mpy][mpx][1] == "K" and gs.board[my][mx][1] == "R":
                        gs.castleMove((my, mx), (mpy, mpx))
                        dragging = False
                        vMoves = gs.genValidMoves(gs.board)
                    elif ((my,mx),(mpy,mpx)) in vMoves:
                        moveC = ChessEngine.Move((mpy, mpx), (my, mx), gs.board)
                        gs.makeMove(moveC, None)
                        vMoves = gs.genValidMoves(gs.board) #gen new valid moves
                        mpx, mpy = 1000, 1000
                        dragging = False
                    move.clear()

            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gs.undoMove()
                    vMoves = gs.genValidMoves(gs.board)  # gen new valid moves

            p.display.flip()
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs):
    """
    Responsible for graphics game state
    :param screen:
    :param gs:
    :return:
    """
    draw_board(screen) # helper function to draw the board
    draw_pieces(screen, gs.board) # helper function to draw the pieces
    draw_places(screen)

def draw_board(screen):
    """
    draw the board
    :param screen:
    :return:
    """
    white = True
    for r in range(SIZE):
        for c in range(SIZE):
            if white:
                p.draw.rect(screen, p.Color(227, 193, 111), (c*SQ_EACH_SIZE, r*SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
            else:
                p.draw.rect(screen, p.Color(184, 139, 74), (c*SQ_EACH_SIZE, r*SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
            white = not white
        white = not white
def draw_pieces(screen, board):
    """
    draw the pieces
    :param screen:
    :param gs:1
    :return:
    """
    for r in range(SIZE):
        for c in range(SIZE):
            pc = board[r][c]
            if pc != "__": #not empty
                screen.blit(IMAGES[pc], p.Rect(c*SQ_EACH_SIZE, r*SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
def draw_places(screen):
    letters = 'abcdefgh'
    font = pygame.font.SysFont("Arial", 15)
    colors = ((255, 204, 117), (153, 102, 51))
    white = 0
    for i in range(1,len(letters)+1):
        f = font.render(letters[i-1], True, colors[white])
        screen.blit(f, (64 * i+i*11-10+(3 if letters[i-1] == 'f' else 0), HEIGHT-15-(3 if letters[i-1] == 'g' or letters[i-1] == 'h' else 0)))
        f = font.render(str(i), True, colors[(white if not white else 1)])
        screen.blit(f, (1, 75 * (9-i)-75))
        if not white:
            white+=1
        else:
            white-=1

if __name__ == '__main__':
    main()








