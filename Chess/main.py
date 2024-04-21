"""
Main.py file is responsible for running the game. Will handle user input and GUI.
"""
import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 800
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
        IMAGES[e] = p.transform.scale(p.image.load('Chess/img/' + e + '.png'), (SQ_EACH_SIZE, SQ_EACH_SIZE))

def main(): # Driver code for the main chess game
    p.init()
    load_images() # done only once to save memory
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('CHESS IN PYTHON')
    clock = p.time.Clock()
    FPS = MAX_FPS
    gs = ChessEngine.GameState()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        draw_game_state(screen,gs)
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
    x = y = 0
    for r in range(SIZE):
        for c in range(SIZE):
            if white:
                p.draw.rect(screen, p.Color(227,193,111), (x, y, SQ_EACH_SIZE, SQ_EACH_SIZE))
                white = False
            else:
                p.draw.rect(screen, p.Color(184,139,74), (x, y, SQ_EACH_SIZE, SQ_EACH_SIZE))
                white = True
            x += SQ_EACH_SIZE
        white = not white
        y += SQ_EACH_SIZE
        x = 0
def draw_pieces(screen, board):
    """
    draw the pieces
    :param screen:
    :param gs:
    :return:
    """

if __name__ == '__main__':
    main()








