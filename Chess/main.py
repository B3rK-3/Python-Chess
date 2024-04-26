"""
Main.py file is responsible for running the game engine. Will handle user input and GUI.
"""
import pygame as p
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
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                mx, my = p.mouse.get_pos()
                if mx < HEIGHT and my < WIDTH:
                    mpx = mx//SQ_EACH_SIZE
                    mpy = my//SQ_EACH_SIZE
                    move.append((mpx, mpy))
                    if len(move) == 2 and (move[0] == move[1]) or gs.board[move[0][1]][move[0][0]] == "__": # clears move if the tuples move[0] and move[1] are the same and if the last move was done by dragging also removes move if the first clik was void
                        move.clear()
                if len(move) == 2: # making sure there were two clicks before
                    moveC = ChessEngine.Move((move[0][1], move[0][0]), (move[1][1], move[1][0]), gs.board)
                    gs.makeMove(moveC)
                    print(moveC.getChessNotation())
                    move.clear()
                dragging = True
            elif e.type == p.MOUSEBUTTONUP:
                mx, my = p.mouse.get_pos()
                my = my//SQ_EACH_SIZE
                mx = mx//SQ_EACH_SIZE
                if mpx < SIZE and mpy < SIZE and mx < HEIGHT and my < WIDTH and gs.board[mpy][mpx] != "__" and (mx,my) != (mpx, mpy): #make sure that the dragged is not empty and within bounds
                    #for the if condition the last condition makes sure that the we are not trying to drag it into the same place (it messes with the click move property)
                    moveC = ChessEngine.Move((mpy, mpx), (my, mx), gs.board)
                    gs.makeMove(moveC)
                    mpx, mpy = 1000, 1000
                    dragging = False
                    move.clear()
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
    draw_pieces(screen, gs.board) # helper function to draw the pices

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
                p.draw.rect(screen, p.Color(227,193,111), (c*SQ_EACH_SIZE, r*SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
            else:
                p.draw.rect(screen, p.Color(184,139,74), (c*SQ_EACH_SIZE, r*SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))
            white = not white
        white = not white
def draw_pieces(screen, board):
    """
    draw the pieces
    :param screen:
    :param gs:
    :return:
    """
    for r in range(SIZE):
        for c in range(SIZE):
            pc = board[r][c]
            if pc != "__": #not empty
                screen.blit(IMAGES[pc], p.Rect(c*SQ_EACH_SIZE, r*SQ_EACH_SIZE, SQ_EACH_SIZE, SQ_EACH_SIZE))


if __name__ == '__main__':
    main()








