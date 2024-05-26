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
    move = [] # two tuples [(7,7), (6,3)] will store where the user wants to move the piece to
    mpx = 0
    mpy = 0
    vMoves = gs.genValidMoves(gs.board)
    highlight = []
    en_passant = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                exit("QUIT")
            elif e.type == p.MOUSEBUTTONUP and e.button == 3:
                hx, hy = p.mouse.get_pos()
                hy = hy//SQ_EACH_SIZE
                hx = hx//SQ_EACH_SIZE
                if (hy,hx) not in highlight:
                    highlight.append((hy,hx))
                else:
                    highlight.remove((hy,hx))
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = p.mouse.get_pos()
                if len(move) == 2 and ((move[1][0], move[1][1]), (move[0][0], move[0][1])) not in vMoves:
                    move.clear()
                if mx < HEIGHT and my < WIDTH:
                    mpx = mx//SQ_EACH_SIZE
                    mpy = my//SQ_EACH_SIZE
                    move.append((mpy, mpx))
                    print(move, "DOWN")
                    if len(move) == 2 and ((move[1][0], move[1][1]),(move[0][0], move[0][1])) not in vMoves:
                        move = [move[1]]


            elif e.type == p.MOUSEBUTTONUP and e.button == 1:
                mx, my = p.mouse.get_pos()
                my = my//SQ_EACH_SIZE
                mx = mx//SQ_EACH_SIZE
                if not (my,mx) in move:
                    move.append((my,mx))
                print(move, "UP")
                if len(move) == 2 and gs.board[move[0][0]][move[0][1]] != "__": #make sure that the dragged is not empty and within bounds
                    #for the if condition the last condition makes sure that the we are not trying to drag it into the same place (it messes with the click move property)
                    if ((move[1][0], move[1][1]), (move[0][0], move[0][1])) in vMoves and gs.board[move[0][0]][move[0][1]][1] == "P" and ((move[1][0] == 0) or (move[1][0] == 7)):
                        moveC = ChessEngine.Move(move[0], move[1], gs.board)
                        gs.makeMove(moveC, None)
                        draw_game_state(screen, gs, move, highlight)
                        p.display.flip()
                        gs.pawnPromotion(((move[1][0], move[1][1]), (move[0][0], move[0][1])), screen)
                        vMoves = gs.genValidMoves(gs.board)  # gen new valid moves
                    else:
                        if ((move[1][0], move[1][1]),(move[0][0], move[0][1])) in vMoves and gs.make_if_en_passant(((move[0][0], move[0][1]), (move[1][0], move[1][1]))):
                            pass
                        else:
                            if gs.board[mpy][mpx][1] == "K" and gs.board[my][mx][1] == "R":
                                gs.castleMove((my, mx), (mpy, mpx))
                                vMoves = gs.genValidMoves(gs.board)
                            elif ((move[1][0], move[1][1]),(move[0][0], move[0][1])) in vMoves:
                                moveC = ChessEngine.Move(move[0], move[1], gs.board)
                                gs.makeMove(moveC, None)
                                highlight = []
                                vMoves = gs.genValidMoves(gs.board) #gen new valid moves
                                mpx, mpy = 1000, 1000
                            else:
                                move = [move[1]]
                elif len(move) == 2:
                    move = [move[1]]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gs.undoMove()
                    vMoves = gs.genValidMoves(gs.board)  # gen new valid moves
                    move.clear()

            p.display.flip()
        draw_game_state(screen, gs, move, highlight)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs, draw, highlight):
    """
    Responsible for graphics game state
    :param screen:
    :param gs:
    :return:
    """
    draw_board(screen, draw, highlight) # helper function to draw the board
    draw_pieces(screen, gs.board) # helper function to draw the pieces
    draw_places(screen)

def draw_board(screen, draw, highlight):
    """
    draw the board
    :param screen:
    :return:
    """
    white = True
    for r in range(SIZE):
        for c in range(SIZE):
            if (r,c) in highlight:
                p.draw.rect(screen, p.Color(255, 204, 0),(c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
            else:
                if (r,c) in draw:
                    p.draw.rect(screen, p.Color(255, 255, 102),(c * SQ_EACH_SIZE, r * SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
                else:
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








