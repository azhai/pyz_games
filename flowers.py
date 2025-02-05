import math
import random
import pygame
import pgzrun
# from pgzero.game import screen
from pgzero.constants import mouse


class Cell:
    flower = False
    state = "covered"

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


class MineSweeper:
    def __init__(self, cell_size, grid_x_count, grid_y_count):
        self.cell_size = cell_size
        self.grid_x_count = grid_x_count
        self.grid_y_count = grid_y_count
        self.reset()
        # 初始化缓存字典，用于存储每个单元格周围的花的数量
        self.surrounding_flower_cache = {}

    def reset(self):
        self.game_over = False
        self.first_click = True
        self.selected_x = 0
        self.selected_y = 0
        self.grid = [[Cell() for _ in range(self.grid_x_count)] for _ in range(self.grid_y_count)]

    def get_position_cell(self, a, b) -> Cell | None:
        try:
            return self.grid[a][b]
        except IndexError:
            return None

    def get_selected_cell(self) -> Cell | None:
        return self.get_position_cell(self.selected_y, self.selected_x)

    def get_surrounding_flower_count(self, x, y) -> int:
        flower_count = 0
        if (x, y) in self.surrounding_flower_cache:
            flower_count = self.surrounding_flower_cache[(x, y)]
            return flower_count
        # 使用缓存来避免重复计算
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if (
                        not (dy == 0 and dx == 0)
                        and 0 <= (y + dy) < self.grid_y_count
                        and 0 <= (x + dx) < self.grid_x_count
                        and self.grid[y + dy][x + dx].flower
                ):
                    flower_count += 1
        self.surrounding_flower_cache[(x, y)] = flower_count
        return flower_count

    def update(self):
        # 更新选中的单元格位置
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.selected_x = min(max(math.floor(mouse_x / self.cell_size), 0), self.grid_x_count - 1)
        self.selected_y = min(max(math.floor(mouse_y / self.cell_size), 0), self.grid_y_count - 1)

    def on_key_down(self, key):
        # 按下任意键重置游戏
        self.reset()

    def on_mouse_up(self, button):
        if self.game_over:
            return self.reset()

        sel_cell = self.get_selected_cell()
        if button == mouse.RIGHT:
            # 处理右键点击，切换单元格状态
            sel_cell.next_state()

        if button != mouse.LEFT or sel_cell.state == "flag":
            return

        if self.first_click:
            self.first_click = False
            possible_flower_positions = [
                {"x": x, "y": y} for y in range(self.grid_y_count) for x in range(self.grid_x_count)
                if not (x == self.selected_x and y == self.selected_y)
            ]
            flower_count = min(40, len(possible_flower_positions))
            for _ in range(flower_count):
                n = random.randrange(len(possible_flower_positions))
                position = possible_flower_positions.pop(n)
                x, y = position["x"], position["y"]
                self.get_position_cell(y, x).flower = True

        if sel_cell.flower:
            sel_cell.state = "uncovered"
            self.game_over = True
        else:
            stack = [{"x": self.selected_x, "y": self.selected_y}]
            while stack:
                current = stack.pop()
                x, y = current["x"], current["y"]
                self.get_position_cell(y, x).state = "uncovered"

                if self.get_surrounding_flower_count(x, y) == 0:
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if (
                                    not (dy == 0 and dx == 0)
                                    and 0 <= (y + dy) < self.grid_y_count
                                    and 0 <= (x + dx) < self.grid_x_count
                                    and self.grid[y + dy][x + dx].state in ("covered", "question")
                            ):
                                stack.append({"x": x + dx, "y": y + dy})

            complete = all(
                self.get_position_cell(y, x).is_complete()
                for y in range(self.grid_y_count) for x in range(self.grid_x_count)
            )
            if complete:
                self.game_over = True

    def draw(self):
        # 绘制游戏界面
        screen.fill((0, 0, 0))

        def draw_cell(image, x, y):
            screen.blit(image, (x * self.cell_size, y * self.cell_size))

        for y in range(self.grid_y_count):
            for x in range(self.grid_x_count):
                curr_cell = self.get_position_cell(y, x)
                if curr_cell.state == "uncovered":
                    draw_cell("uncovered", x, y)
                    if curr_cell.flower and self.game_over:
                        draw_cell("flower", x, y)
                    elif self.get_surrounding_flower_count(x, y) > 0:
                        draw_cell(str(self.get_surrounding_flower_count(x, y)), x, y)
                else:
                    if x == self.selected_x and y == self.selected_y and not self.game_over:
                        if pygame.mouse.get_pressed()[0]:
                            if curr_cell.state == "flag":
                                draw_cell("covered", x, y)
                            else:
                                draw_cell("uncovered", x, y)
                        else:
                            draw_cell("covered_highlighted", x, y)
                    else:
                        draw_cell("covered", x, y)

                if curr_cell.state == "flag":
                    draw_cell("flag", x, y)
                elif curr_cell.state == "question":
                    draw_cell("question", x, y)

        self.surrounding_flower_cache = {}


CELL_SIZE = 18
X_COUNT, Y_COUNT = 19, 14
WIDTH = CELL_SIZE * X_COUNT
HEIGHT = CELL_SIZE * Y_COUNT

game = MineSweeper(CELL_SIZE, X_COUNT, Y_COUNT)


def update():
    game.update()


def on_key_down(key):
    game.on_key_down(key)


def on_mouse_up(button):
    game.on_mouse_up(button)


def draw():
    game.draw()


pgzrun.go()
