import numpy as np
import pygame
import random
import time

class GoBoard():
    def __init__(self, initial_board: np.ndarray):
        self.board = initial_board
        self.height = initial_board.shape[0]
        self.width = initial_board.shape[1]

    def is_on_board(self, pos: tuple[int, int]):
        return 0 <= pos[1] < self.width and 0 <= pos[0] < self.height

    def place_piece(self, player_num: int, pos: tuple[int, int]) -> bool:
        if not self.is_on_board(pos):
            # raise Exception("Shouldn't be placing piece outside of bounds")
            return False

        if self.board[pos] != 0:
            return False

        self.board[pos] = player_num

        other_player_num = self.other_player(player_num)
        did_kill_group = False
        for position in self.get_surrounding_positions(pos):
            if self.board[position] == other_player_num:
                is_group_dead, group_set = self.is_group_dead(position)
                if is_group_dead:
                    did_kill_group = True
                    for group_pos in group_set:
                        self.board[group_pos] = 0

        if did_kill_group:
            return True

        is_group_dead, group_set = self.is_group_dead(pos)
        if is_group_dead:
            self.board[pos] = 0
            return False

        return True

    def other_player(self, player_num: int):
        return 2 if player_num == 1 else 1

    def get_surrounding_positions(self, pos: tuple[int, int], player_num_filter: int|None = None):
        if player_num_filter is None:
            return [position for position in [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)] if self.is_on_board(position)]
        else:
            return [position for position in [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)] if self.is_on_board(position) and self.board[position] == player_num_filter]

    def is_group_dead(self, pos: tuple[int, int]) -> tuple[bool, set[tuple[int, int]]]:
        player_num = self.board[pos]
        other_player_num = self.other_player(player_num)
        group_positions: set[tuple[int, int]] = set()

        if player_num in [0, -1]:
            return False, group_positions

        def group_helper(current_pos: tuple[int, int]) -> bool:
            group_positions.add(current_pos)
            for position in self.get_surrounding_positions(current_pos):
                board_num = self.board[position]
                if position in group_positions or board_num == other_player_num:
                    continue
                if board_num == 0:
                    return False
                if not group_helper(position):
                    return False

            return True

        return group_helper(pos), group_positions

    def __str__(self):
        return self.board.__str__()

def print_board(go_board: GoBoard):
    print("\033[H\033[2J", end="")
    print(go_board)
    time.sleep(2)

def draw(screen, width: int, height: int, cell_size: int, x_offset: int, y_offset: int, go_board: GoBoard):
    grid_color = (255, 255, 255)
    player_one_color = (255, 255, 255)
    player_one_outline_color = (255, 255, 255)
    player_two_color = (50, 50, 50)
    player_two_outline_color = (255, 255, 255)
    open_spot_color = (150, 150, 150)

    def draw_grid():
        end_x = (width - 1) * cell_size + x_offset
        end_y = (height - 1) * cell_size + y_offset
        for x in range(0, width):
            new_x = (x * cell_size) + x_offset
            pygame.draw.line(screen, grid_color, (new_x, y_offset), (new_x, end_y))

        for y in range(0, height):
            new_y = (y * cell_size) + y_offset
            pygame.draw.line(screen, grid_color, (x_offset, new_y), (end_x, new_y))

    def draw_board():
        for x in range(width):
            new_x = (x * cell_size) + x_offset
            for y in range(height):
                new_y = (y * cell_size) + y_offset
                match go_board.board[y][x]:
                    case 0:
                        pygame.draw.circle(screen, open_spot_color, (new_x, new_y), 5, 0)
                    case 1:
                        pygame.draw.circle(screen, player_one_color, (new_x, new_y), 15, 0)
                        pygame.draw.circle(screen, player_one_outline_color, (new_x, new_y), 15, 1)
                    case 2:
                        pygame.draw.circle(screen, player_two_color, (new_x, new_y), 15, 0)
                        pygame.draw.circle(screen, player_two_outline_color, (new_x, new_y), 15, 1)
    draw_grid()
    draw_board()

def main():
    screen_width = 1280
    screen_height = 720
    cell_size = 40
    board_width = 10
    board_height = 10
    x_offset = int((screen_width / 2) - (board_width * cell_size) / 2)
    y_offset = int((screen_height / 2) - (board_height * cell_size) / 2)
    board = np.ndarray((board_height, board_width), dtype=np.int8)
    board.fill(0)
    go_board = GoBoard(board)

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    running = True

    i = 0
    while running:
        player_num = (i % 2) + 1
        mouse_pos = ()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos

        screen.fill("black")

        place_pos = ()
        if player_num == 1 and mouse_pos:
            place_pos = (int((mouse_pos[1] - y_offset + cell_size / 2) // cell_size), int((mouse_pos[0] - x_offset + cell_size / 2) // cell_size))
        elif player_num == 2:
            place_pos = (random.randint(0, board_height - 1), random.randint(0, board_width - 1))

        if place_pos:
            if go_board.place_piece(player_num, place_pos):
                i += 1

        draw(screen, board_width, board_height, cell_size, x_offset, y_offset, go_board)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()