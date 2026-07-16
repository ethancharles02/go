import numpy as np
import pygame
import random
import time

from go_board import GoBoard
from go_group import GoGroup
from mcts_agent import MCTSAgent
from constants import *

def print_board(go_board: GoBoard):
    print("\033[H\033[2J", end="")
    print(go_board)
    time.sleep(2)

def draw_grid(screen, grid_color: int, width: int, height: int, cell_size: int, x_offset: int, y_offset: int):
    end_x = (width - 1) * cell_size + x_offset
    end_y = (height - 1) * cell_size + y_offset
    for x in range(0, width):
        new_x = (x * cell_size) + x_offset
        pygame.draw.line(screen, grid_color, (new_x, y_offset), (new_x, end_y))

    for y in range(0, height):
        new_y = (y * cell_size) + y_offset
        pygame.draw.line(screen, grid_color, (x_offset, new_y), (end_x, new_y))

def draw_board(go_board: GoBoard, screen, player_one_color, player_one_outline_color, player_two_color, player_two_outline_color, open_spot_color, width, height, cell_size, x_offset, y_offset):
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

def draw_player_num(player_num, player_one_color, player_two_color, screen, font: pygame.font.Font):
    color = player_one_color if player_num == 1 else player_two_color
    text_surface = font.render(f"Current Move: {player_num}", True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (0, 0)
    screen.blit(text_surface, text_rect)

def main():
    x_offset = int((SCREEN_WIDTH / 2) - (BOARD_WIDTH * CELL_SIZE) / 2)
    y_offset = int((SCREEN_HEIGHT / 2) - (BOARD_HEIGHT * CELL_SIZE) / 2)
    board = np.ndarray((BOARD_HEIGHT, BOARD_WIDTH), dtype=GoGroup)
    board.fill(0)
    go_board = GoBoard(board)

    max_iterations = 1000
    max_simulation_depth = 20
    mcts_agent = MCTSAgent(2, max_iterations, max_simulation_depth)

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    i = 0
    player_num = (i % 2) + 1
    other_player_num = ((i + 1) % 2) + 1
    while running:
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
            place_pos = (int((mouse_pos[1] - y_offset + CELL_SIZE / 2) // CELL_SIZE), int((mouse_pos[0] - x_offset + CELL_SIZE / 2) // CELL_SIZE))
        # elif player_num == 2 and mouse_pos:
        #     place_pos = (int((mouse_pos[1] - y_offset + CELL_SIZE / 2) // CELL_SIZE), int((mouse_pos[0] - x_offset + CELL_SIZE / 2) // CELL_SIZE))
        elif player_num == 2:
            # time.sleep(0.25)
            # place_pos = go_board.get_available_moves(player_num).pop()
            old_time = time.monotonic()
            place_pos = mcts_agent.get_move(go_board)
            print(f"MCTS time: {(time.monotonic() - old_time):.2f}")

        if place_pos:
            if go_board.place_piece(player_num, place_pos):
                if go_board.is_winning_state(player_num):
                    print(f"Player #{player_num} Wins!")
                    break
                elif go_board.is_winning_state(other_player_num):
                    print(f"Player #{other_player_num} Wins!")
                    break
                elif go_board.is_tie():
                    print(f"Game ended in a tie")
                    break
                print(f"Pieces captures: {go_board.captured_piece_counts}")
                i += 1
                player_num = (i % 2) + 1
                print(f"Player #{player_num}'s Turn")

        draw_grid(
            screen,
            GRID_COLOR,
            BOARD_WIDTH,
            BOARD_HEIGHT,
            CELL_SIZE,
            x_offset,
            y_offset
        )
        draw_board(
            go_board,
            screen,
            PLAYER_ONE_COLOR,
            PLAYER_ONE_OUTLINE_COLOR,
            PLAYER_TWO_COLOR,
            PLAYER_TWO_OUTLINE_COLOR,
            OPEN_SPOT_COLOR,
            BOARD_WIDTH,
            BOARD_HEIGHT,
            CELL_SIZE,
            x_offset,
            y_offset
        )
        font = pygame.font.Font(None, 36)
        draw_player_num(
            player_num,
            PLAYER_ONE_TEXT_COLOR,
            PLAYER_TWO_TEXT_COLOR,
            screen,
            font
        )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()