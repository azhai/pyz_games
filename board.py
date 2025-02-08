import math
import pygame.mouse

class Board:
    """ 棋盘 """

    def __init__(self, cell_size, col_count, row_count, info_height = 0):
        self.cell_size = cell_size
        self.col_count = col_count
        self.row_count = row_count
        self.info_height = info_height
        self.reset()

    def reset(self):
        """ 重开游戏 """
        raise NotImplemented

    @property
    def screen_size(self):
        """ 棋盘大小 """
        width = self.col_count * self.cell_size
        height = self.row_count * self.cell_size + self.info_height
        return width, height

    def mouse_button(self) -> int:
        """ 判断鼠标点击用的左、中、右、上、下哪个键 """
        pressed = pygame.mouse.get_pressed()
        return self.get_mouse_btn(pressed)

    @staticmethod
    def get_mouse_btn(pressed) -> int:
        """ 鼠标的按键 """
        try:
            return pressed.index(True) + 1
        except ValueError:
            return 0

    def mouse_location(self) -> (int, int):
        """ 将鼠标点击坐标转化为对应位置的单元格 """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.get_mouse_loc(mouse_x, mouse_y)

    def get_mouse_loc(self, mouse_x, mouse_y) -> (int, int):
        """ 鼠标选中的单元格位置 """
        sx = min(math.floor(mouse_x / self.cell_size), self.col_count - 1)
        sy = min(math.floor(mouse_y / self.cell_size), self.row_count - 1)
        return sx, sy

    def get_neighbor_cells(self, x, y) -> [(int, int)]:
        """ 找出周围（最多）8个单元格 """
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (
                        not (dx == 0 and dy == 0)
                        and 0 <= (x + dx) < self.col_count
                        and 0 <= (y + dy) < self.row_count
                ):
                    yield x + dx, y + dy