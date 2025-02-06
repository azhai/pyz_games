import pgzrun
import pygame.mouse
from pygame.constants import K_SPACE
# from pgzero.game import screen
import minesweeper

CELL_SIZE = 18
X_COUNT, Y_COUNT = 19, 14
WIDTH = CELL_SIZE * X_COUNT
HEIGHT = CELL_SIZE * Y_COUNT
game = minesweeper.Board(CELL_SIZE, X_COUNT, Y_COUNT)

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
    game.draw(screen, pressed, mouse_x, mouse_y)

pgzrun.go()
