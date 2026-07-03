import numpy as np

class GoBoard():
    def __init__(self, initial_board: np.ndarray):
        self.board = initial_board
        self.height = initial_board.shape[0]
        self.width = initial_board.shape[1]
        self.captured_piece_counts = [0, 0]
        self.last_piece_placements = [None, None]

    def copy(self):
        return GoBoard(self.board.copy())

    def get_available_moves(self, player_num: int) -> set[tuple[int, int]]:
        available_moves = set()
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == 0:
                    if self.place_piece(player_num, (y, x), True):
                        available_moves.add((y, x))

        return available_moves

    # def get_piece_counts(self) -> tuple[int, int]:
    #     return (np.count_nonzero(self.board == 1), np.count_nonzero(self.board == 2))

    # TODO change winning state to be accurate to actual go games with area captured?
    def is_winning_state(self, player_num: int) -> bool:
        return len(self.get_available_moves(self.other_player(player_num))) == 0 and self.captured_piece_counts[player_num - 1] > self.captured_piece_counts[self.other_player(player_num) - 1]

    def is_tie(self):
        return len(self.get_available_moves(1)) == 0 and len(self.get_available_moves(2)) == 0 and self.captured_piece_counts[0] == self.captured_piece_counts[1]

    def is_on_board(self, pos: tuple[int, int]):
        return 0 <= pos[1] < self.width and 0 <= pos[0] < self.height

    def place_piece(self, player_num: int, pos: tuple[int, int], is_test_only: bool = False) -> bool:
        if not self.is_on_board(pos):
            # raise Exception("Shouldn't be placing piece outside of bounds")
            return False

        if self.board[pos] != 0:
            return False

        # Can't place in the same spot twice in a row
        if self.last_piece_placements[player_num - 1] is not None and pos == self.last_piece_placements[player_num - 1]:
            if not is_test_only:
                print("Can't place piece in same spot twice")
            return False

        # If there is at least one open spot, we know a piece can be placed for sure
        if is_test_only and len(self.get_surrounding_positions(pos, 0)) > 0:
            return True

        self.board[pos] = player_num

        other_player_num = self.other_player(player_num)
        did_kill_group = False
        for position in self.get_surrounding_positions(pos):
            if self.board[position] == other_player_num:
                is_group_dead, group_set = self.is_group_dead(position)
                if is_group_dead:
                    did_kill_group = True
                    if not is_test_only:
                        for group_pos in group_set:
                            self.board[group_pos] = 0
                            self.captured_piece_counts[player_num - 1] += 1

        if did_kill_group:
            if is_test_only:
                self.board[pos] = 0
            else:
                self.last_piece_placements[player_num - 1] = pos
            return True

        is_group_dead, group_set = self.is_group_dead(pos)
        if is_group_dead:
            self.board[pos] = 0
            return False

        if is_test_only:
            self.board[pos] = 0
        else:
            self.last_piece_placements[player_num - 1] = pos
        return True

    def other_player(self, player_num: int):
        return 2 if player_num == 1 else 1

    def get_surrounding_positions(self, pos: tuple[int, int], num_filter: int|None = None):
        if num_filter is None:
            return [position for position in [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)] if self.is_on_board(position)]
        else:
            return [position for position in [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)] if self.is_on_board(position) and self.board[position] == num_filter]

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