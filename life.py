import pgzrun
from pygame import Rect
from pygame.constants import K_SPACE, K_LEFT, K_RIGHT
from pgzero.constants import mouse
import board

CELL_SIZE = 10
X_COUNT, Y_COUNT = 70, 50

BACK_COLOR = (212, 212, 212)
DEAD_COLOR = (220, 220, 220)
LIVE_COLOR = (255, 0, 255)

class LifeBoard(board.Board):
    """ 细胞游戏 """
    name = "细胞"
    grid = []

    def __init__(self):
        super().__init__(CELL_SIZE, X_COUNT, Y_COUNT)

    def reset(self):
        """ 重开游戏，所有单元格设置为无生命 """
        self.grid = [
            [False] * self.col_count
            for _ in range(self.row_count)
        ]

    def change_grid(self):
        next_grid = []
        for y in range(self.row_count):
            next_grid.append([])
            for x in range(self.col_count):
                neighbor_count = sum(
                    1 for nx, ny in self.get_neighbor_cells(x, y)
                    if self.grid[ny][nx]
                )
                next_grid[y].append(
                    neighbor_count == 3 or
                    (self.grid[y][x] and neighbor_count == 2)
                )
        return next_grid

    def on_clicked(self, button, mouse_x = 0, mouse_y = 0):
        sx, sy = self.get_mouse_loc(mouse_x, mouse_y)
        # print("mouse:", button, sx, sy)
        if button == mouse.LEFT:
            self.grid[sy][sx] = True
        elif button == mouse.RIGHT:
            self.grid[sy][sx] = False

    def on_pressed(self, key):
        num = 1
        if key == K_RIGHT:
            num = 2
        if key == K_LEFT:
            num = 5
        if key == K_SPACE:
            num = 23
        for _ in range(num):
            self.grid = self.change_grid()

    def draw_screen(self, screen):
        screen.fill(BACK_COLOR)

        for y in range(self.row_count):
            for x in range(self.col_count):

                cell_draw_size = self.cell_size - 1
                rect = Rect(
                    (x * self.cell_size, y * self.cell_size),
                    (cell_draw_size, cell_draw_size)
                )

                if self.grid[y][x]:
                    color = LIVE_COLOR
                else:
                    color = DEAD_COLOR

                screen.draw.filled_rect(rect, color)


game = LifeBoard()
TITLE = game.name  # 窗口标题
WIDTH, HEIGHT = game.screen_size

def on_key_down(key):
    game.on_pressed(key)

def on_mouse_move(pos, buttons):
    if mouse.LEFT in buttons:
        game.on_clicked(mouse.LEFT, *pos)
    elif mouse.RIGHT in buttons:
        game.on_clicked(mouse.RIGHT, *pos)

def draw():
    screen.clear()  # 清除屏幕内容
    game.draw_screen(screen)

pgzrun.go()