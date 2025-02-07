import pgzrun
import pygame.mouse
from pygame.constants import K_SPACE
# from pgzero.game import screen
import minesweeper

CELL_SIZE, INFO_HEIGHT = 18, 30
X_COUNT, Y_COUNT = 19, 14
WIDTH = CELL_SIZE * X_COUNT
BOARD_HEIGHT = CELL_SIZE * Y_COUNT
HEIGHT = BOARD_HEIGHT + INFO_HEIGHT

game = minesweeper.Board(CELL_SIZE, X_COUNT, Y_COUNT)
TITLE = game.name

def update():
    pass

def on_key_down(key):
    # 按下空格键重置游戏
    if key == K_SPACE:
        game.reset()

def on_mouse_up(button):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    game.click(button, mouse_x, mouse_y)

def draw():
    pressed = pygame.mouse.get_pressed()[0]
    mouse_x, mouse_y = pygame.mouse.get_pos()
    game.draw_board(screen, pressed, mouse_x, mouse_y)
    font = pygame.font.Font(None, 32)
    game.draw_info(screen, font, BOARD_HEIGHT + 5)

pgzrun.go()
