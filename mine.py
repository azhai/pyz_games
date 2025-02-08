import math
from random import sample

import pgzrun
import pygame.font
from pgzero.constants import mouse
from pygame.constants import K_SPACE

import board

# 单元格大小，由图片素材大小决定，底部信息栏高度与字体相关
CELL_SIZE, INFO_HEIGHT = 18, 30
# 棋盘大小 14行19列
X_COUNT, Y_COUNT = 19, 14

BACK_COLOR = (212, 212, 212)
TEXT_COLOR = (240, 165, 32)


class Cell:
    """ 棋盘格子 """
    is_mime = False
    state = "covered"
    count = -1

    def __init__(self, y, x):
        self.y = y
        self.x = x

    def reset(self):
        self.is_mime = False
        self.state = "covered"
        self.count = -1

    def is_complete(self) -> bool:
        return self.state == "uncovered" or self.is_mime

    def next_state(self) -> str:
        """ 切换到下一个状态 """
        if self.state == "covered":
            self.state = "flag"
        elif self.state == "flag":
            self.state = "question"
        else:
            self.state = "covered"
        return self.state


class MineBoard(board.Board):
    """ 扫雷游戏 """
    name = "扫雷"
    grid = []
    mime_remain = 0
    game_over = False  # 游戏结束，如果同时mime_remain==0则是胜利
    first_click = True  # 左键点击第一个单元格

    def __init__(self):
        super().__init__(CELL_SIZE, X_COUNT, Y_COUNT, INFO_HEIGHT)

    def reset(self):
        """ 重开游戏，埋雷推迟到第一次点击 """
        self.grid = [
            [Cell(y, x) for x in range(self.col_count)]
            for y in range(self.row_count)
        ]
        self.mime_remain = 0
        self.game_over = False
        self.first_click = True

    def get_cell(self, x, y) -> Cell | None:
        try:
            return self.grid[y][x]
        except IndexError:
            return None

    def get_near_cells(self, x, y) -> [Cell]:
        """ 找出周围（最多）8个单元格 """
        for x, y in self.get_neighbor_cells(x, y):
            yield self.get_cell(x, y)

    def get_surrounding_mime_count(self, x, y) -> int:
        """ 获取周围8格地雷数量，缓存在当前单元格中 """
        cell = self.get_cell(x, y)
        if cell.count < 0:
            cell.count = sum(
                1 for c in self.get_near_cells(x, y) if c.is_mime
            )
        return cell.count

    def set_mime_cells(self, sx=-1, sy=-1):
        """ 埋雷，数量为总单元格数的1/7 """
        cell_count = self.col_count * self.row_count
        self.mime_remain = int(math.ceil(cell_count / 7))
        exclude = sx * self.row_count + sy
        # 筛选两次，让地雷更为分散
        indexes = [i for i in range(cell_count) if i != exclude]
        indexes = sample(indexes, self.mime_remain * 3)
        for i in sample(indexes, self.mime_remain):
            x, y = i // self.row_count, i % self.row_count
            self.get_cell(x, y).is_mime = True

    def open_more_cells(self, stack):
        """ 点开当前单元格，如果是鼠标中键点击，同时点开附近八格 """
        while stack:
            x, y = stack.pop()
            self.get_cell(x, y).state = "uncovered"
            if self.get_surrounding_mime_count(x, y) > 0:
                continue
            for c in self.get_near_cells(x, y):
                if c.state in ("covered", "question"):
                    stack.append((c.x, c.y))

    def on_right_clicked(self, cell):
        """ 鼠标右键点击 """
        if cell.state == "uncovered":
            return
        # 处理右键点击，切换单元格状态
        state = cell.next_state()
        if state == "flag":
            self.mime_remain -= 1
        elif state == "question":
            self.mime_remain += 1

    def on_clicked(self, button, mouse_x, mouse_y):
        """ 鼠标（包括左、中、右）点击操作 """
        if self.game_over:
            self.reset()
            return

        # 将鼠标点击坐标转化为对应位置的单元格
        sx, sy = self.get_mouse_loc(mouse_x, mouse_y)
        # print("mouse:", button, sx, sy)
        sel_cell = self.get_cell(sx, sy)

        if button == mouse.RIGHT:
            return self.on_right_clicked(sel_cell)
        if sel_cell.state == "flag":
            return

        if self.first_click:
            self.first_click = False
            # 左键点击第一个单元格，这时开始埋雷，并且这个格子肯定不是地雷
            self.set_mime_cells(sx, sy)

        # 鼠标左键或中键点击到地雷，游戏结束
        if sel_cell.is_mime:
            sel_cell.state = "uncovered"
            self.game_over = True
            return

        stack = [(sx, sy)]
        if button == mouse.MIDDLE:
            # 中键点击，打开周围8格
            for c in self.get_near_cells(sx, sy):
                if c.state == "covered":
                    stack.append((c.x, c.y))
        self.open_more_cells(stack)

        if self.mime_remain <= 0:
            # 检查当前游戏是否完成，即是否胜利
            complete = all(
                self.get_cell(x, y).is_complete()
                for y in range(self.row_count) for x in range(self.col_count)
            )
            if complete:
                self.game_over = True

    def draw_board(self, screen, button=0, mouse_x=0, mouse_y=0):
        """ 根据各自状态绘制棋盘中所有单元格 """
        # 绘制背景颜色
        screen.fill(BACK_COLOR)

        def draw_cell(image, cx, cy):
            screen.blit(image, (cx * self.cell_size, cy * self.cell_size))

        def draw_uncovered_cell(cell):
            draw_cell("uncovered", cell.x, cell.y)
            if cell.is_mime and self.game_over:
                draw_cell("flower", x, y)
                return
            mime_count = self.get_surrounding_mime_count(x, y)
            if mime_count > 0:
                draw_cell(str(mime_count), x, y)

        # def draw_selected_cell(cell):
        #     if button != mouse.LEFT:
        #         draw_cell("covered_highlighted", cell.x, cell.y)
        #     elif cell.state == "flag":
        #         draw_cell("covered", cell.x, cell.y)
        #     else:
        #         draw_cell("uncovered", cell.x, cell.y)

        # sx, sy = self.get_mouse_loc(mouse_x, mouse_y)
        # print("mouse:", button, sx, sy)

        # 依次绘制棋盘所有单元格
        for y in range(self.row_count):
            for x in range(self.col_count):
                curr_cell = self.get_cell(x, y)
                if curr_cell.state == "uncovered":
                    draw_uncovered_cell(curr_cell)
                # elif x == sx and y == sy and not self.game_over:
                #     draw_selected_cell(curr_cell)
                else:
                    draw_cell("covered", x, y)

                if curr_cell.state == "flag":
                    draw_cell("flag", x, y)
                elif curr_cell.state == "question":
                    draw_cell("question", x, y)

    def draw_info(self, screen, font, height):
        # 绘制底部信息
        text = ""
        if self.game_over:
            if self.mime_remain > 0:
                text = " Game Over"
            else:
                text = " You Win !"
        elif self.mime_remain > 0:
            text = f" Remain: {self.mime_remain}"
        info = font.render(text, True, TEXT_COLOR)
        screen.blit(info, (0, height))


game = MineBoard()
TITLE = game.name  # 窗口标题
WIDTH, HEIGHT = game.screen_size


def on_key_down(key):
    # 按下空格键重置游戏
    if key == K_SPACE:
        game.reset()


def on_mouse_up(pos, button):
    game.on_clicked(button, *pos)


def draw():
    screen.clear()  # 清除屏幕内容
    game.draw_board(screen)
    font = pygame.font.Font(None, 32)
    height = HEIGHT - INFO_HEIGHT + 5
    game.draw_info(screen, font, height)


pgzrun.go()
