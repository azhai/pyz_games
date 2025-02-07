import math
from random import sample
from pgzero.constants import mouse

BACK_COLOR = (212, 212, 212)
TEXT_COLOR = (218, 165, 32)


class Cell:
    """ 棋盘格子 """
    flower = False
    state = "covered"
    count = -1

    def __init__(self, y, x):
        self.y = y
        self.x = x

    def reset(self):
        self.flower = False
        self.state = "covered"
        self.count = -1

    def is_complete(self) -> bool:
        return self.state == "uncovered" or self.flower

    def next_state(self) -> str:
        """ 切换到下一个状态 """
        if self.state == "covered":
            self.state = "flag"
        elif self.state == "flag":
            self.state = "question"
        else:
            self.state = "covered"
        return self.state


class Board:
    """ 扫雷游戏 """
    grid = []
    flower_remain = 0
    game_over = False
    first_click = True

    def __init__(self, cell_size, grid_x_count, grid_y_count):
        self.cell_size = cell_size
        self.grid_x_count = grid_x_count
        self.grid_y_count = grid_y_count
        self.reset()

    def reset(self):
        self.grid = [
            [Cell(y, x) for x in range(self.grid_x_count)]
            for y in range(self.grid_y_count)
        ]
        self.flower_remain = 0
        self.game_over = False
        self.first_click = True

    def get_cell(self, x, y) -> Cell | None:
        try:
            return self.grid[y][x]
        except IndexError:
            return None

    def get_near_cells(self, x, y) -> [Cell]:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (
                    not (dx == 0 and dy == 0)
                    and 0 <= (x + dx) < self.grid_x_count
                    and 0 <= (y + dy) < self.grid_y_count
                ):
                    yield self.get_cell(x + dx, y + dy)

    def get_selected_pos(self, mouse_x, mouse_y) -> (int, int):
        # 选中的单元格位置
        cell_x = math.floor(max(mouse_x, 0) / self.cell_size)
        sx = min(cell_x, self.grid_x_count - 1)
        cell_y = math.floor(max(mouse_y, 0) / self.cell_size)
        sy = min(cell_y, self.grid_y_count - 1)
        return sx, sy

    def get_surrounding_flower_count(self, x, y) -> int:
        cell = self.get_cell(x, y)
        if cell.count < 0:
            cell.count = sum([1 for c in self.get_near_cells(x, y) if c.flower])
        return cell.count

    def set_flower_cells(self, sx = -1, sy = -1):
        cell_count = self.grid_x_count * self.grid_y_count
        self.flower_remain = int(math.ceil(cell_count / 7))
        exclude = sx * self.grid_y_count + sy
        # 筛选两次更为分散
        indexes = [i for i in range(cell_count) if i != exclude]
        indexes = sample(indexes, self.flower_remain * 2)
        for i in sample(indexes, self.flower_remain):
            x, y = i // self.grid_y_count, i % self.grid_y_count
            self.get_cell(x, y).flower = True

    def show_uncovered_cells(self, sx, sy):
        stack = [(sx, sy)]
        while stack:
            x, y = stack.pop()
            self.get_cell(x, y).state = "uncovered"
            if self.get_surrounding_flower_count(x, y) > 0:
                continue
            for c in self.get_near_cells(x, y):
                if c.state in ("covered", "question"):
                    stack.append((c.x, c.y))

    def click(self, button, mouse_x, mouse_y):
        if self.game_over:
            self.reset()
            return

        sx, sy = self.get_selected_pos(mouse_x, mouse_y)
        sel_cell = self.get_cell(sx, sy)

        if button == mouse.RIGHT:
            if sel_cell.state == "uncovered":
                return
            # 处理右键点击，切换单元格状态
            state = sel_cell.next_state()
            if state == "flag":
                self.flower_remain -= 1
            elif state == "question":
                self.flower_remain += 1
            return

        if sel_cell.state == "flag":
            return

        # if button == mouse.MIDDLE:
        #     if sel_cell.state != "uncovered":
        #         return
        #     for c in self.get_near_cells(sx, sy):
        #         if c.state == "covered":
        #             c.state = "uncovered"
        #     return

        if self.first_click:
            self.first_click = False
            self.set_flower_cells(sx, sy)

        if sel_cell.flower:
            sel_cell.state = "uncovered"
            self.game_over = True
            return

        if self.flower_remain <= 0:
            complete = all(
                self.get_cell(x, y).is_complete()
                for y in range(self.grid_y_count) for x in range(self.grid_x_count)
            )
            if complete:
                self.game_over = True

        self.show_uncovered_cells(sx, sy)

    def draw_board(self, screen, pressed, mouse_x, mouse_y):
        # 绘制游戏界面
        screen.fill(BACK_COLOR)

        def draw_cell(image, cx, cy):
            screen.blit(image, (cx * self.cell_size, cy * self.cell_size))

        def draw_uncovered_cell(cell):
            draw_cell("uncovered", cell.x, cell.y)
            if cell.flower and self.game_over:
                draw_cell("flower", x, y)
                return
            flower_count = self.get_surrounding_flower_count(x, y)
            if flower_count > 0:
                draw_cell(str(flower_count), x, y)

        def draw_selected_cell(cell):
            if not pressed:
                draw_cell("covered_highlighted", cell.x, cell.y)
            elif cell.state == "flag":
                draw_cell("covered", cell.x, cell.y)
            else:
                draw_cell("uncovered", cell.x, cell.y)

        sx, sy = self.get_selected_pos(mouse_x, mouse_y)
        for y in range(self.grid_y_count):
            for x in range(self.grid_x_count):
                curr_cell = self.get_cell(x, y)
                if curr_cell.state == "uncovered":
                    draw_uncovered_cell(curr_cell)
                elif x == sx and y == sy and not self.game_over:
                    draw_selected_cell(curr_cell)
                else:
                    draw_cell("covered", x, y)

                if curr_cell.state == "flag":
                    draw_cell("flag", x, y)
                elif curr_cell.state == "question":
                    draw_cell("question", x, y)

    def draw_info(self, screen, font, height):
        # 绘制游戏信息
        text = ""
        if self.game_over:
            text = " Game Over"
        elif self.flower_remain > 0:
            text = f" Remain: {self.flower_remain}"
        info = font.render(text, True, TEXT_COLOR)
        screen.blit(info, (0, height))
