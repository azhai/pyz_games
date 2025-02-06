import math
import random
from pgzero.constants import mouse


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
    game_over = False
    flower_count = 0

    def __init__(self, cell_size, grid_x_count, grid_y_count):
        self.cell_size = cell_size
        self.grid_x_count = grid_x_count
        self.grid_y_count = grid_y_count
        self.reset()

    def reset(self):
        self.game_over = False
        self.flower_count = 0
        self.grid = [
            [Cell(y, x) for x in range(self.grid_x_count)]
            for y in range(self.grid_y_count)
        ]

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
        possible_list = [
            (x, y) for y in range(self.grid_y_count) for x in range(self.grid_x_count)
            if not (x == sx and y == sy)
        ]
        self.flower_count = int(math.ceil(len(possible_list) / 7))
        for _ in range(self.flower_count):
            n = random.randrange(len(possible_list))
            pos = possible_list.pop(n)
            self.get_cell(*pos).flower = True

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
        if button == mouse.RIGHT and sel_cell.state != "uncovered":
            # 处理右键点击，切换单元格状态
            sel_cell.next_state()
            return

        if button != mouse.LEFT or sel_cell.state == "flag":
            return

        if self.flower_count <= 0:
            self.set_flower_cells(sx, sy)

        if sel_cell.flower:
            sel_cell.state = "uncovered"
            self.game_over = True
            return

        self.show_uncovered_cells(sx, sy)
        complete = all(
            self.get_cell(x, y).is_complete()
            for y in range(self.grid_y_count) for x in range(self.grid_x_count)
        )
        if complete:
            self.game_over = True

    def draw(self, screen, pressed, mouse_x, mouse_y):
        # 绘制游戏界面
        screen.fill((0, 0, 0))

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
