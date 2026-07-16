import numpy as np

from go_group import GoGroup

class GoBoard():
    def __init__(self, initial_board: np.ndarray):
        self.board = initial_board
        self.height = initial_board.shape[0]
        self.width = initial_board.shape[1]
        self.captured_piece_counts = [0, 0]
        self.last_piece_placements = [None, None]
        self.groups: set[GoGroup] = set()

    def copy(self):
        new_board = GoBoard(self.board.copy())
        new_board.captured_piece_counts = self.captured_piece_counts.copy()
        new_board.last_piece_placements = self.last_piece_placements.copy()

        for group in self.groups:
            new_group = group.copy(new_board)
            new_board.groups.add(new_group)
            for position in new_group.piece_positions:
                new_board.board[position] = new_group

        return new_board

    def get_available_moves(self, player_num: int) -> set[tuple[int, int]]:
        available_moves = set()
        for y, x in np.argwhere(self.board == 0):
            pos = (int(y), int(x))
            if self.can_place_piece(player_num, pos):
                available_moves.add(pos)

        return available_moves

    # def get_piece_counts(self) -> tuple[int, int]:
    #     return (np.count_nonzero(self.board == 1), np.count_nonzero(self.board == 2))

    # TODO change winning state to be accurate to actual go games with territory captured? (calculated based on number of empty spots the enemy can't capture + your placed nodes)
    def is_winning_state(self, player_num: int) -> bool:
        return len(self.get_available_moves(self.other_player(player_num))) == 0 and self.captured_piece_counts[player_num - 1] > self.captured_piece_counts[self.other_player(player_num) - 1]

    def is_tie(self):
        return len(self.get_available_moves(1)) == 0 and len(self.get_available_moves(2)) == 0 and self.captured_piece_counts[0] == self.captured_piece_counts[1]

    def is_on_board(self, pos: tuple[int, int]):
        return 0 <= pos[1] < self.width and 0 <= pos[0] < self.height

    def can_place_piece(self, player_num: int, pos: tuple[int, int], verbose: bool = False) -> bool:
        if not self.is_on_board(pos):
            # raise Exception("Shouldn't be placing piece outside of bounds")
            return False

        if self.board[pos] != 0:
            return False

        # Can't place in the same spot twice in a row
        if self.last_piece_placements[player_num - 1] is not None and pos == self.last_piece_placements[player_num - 1]:
            if verbose:
                print("Can't place piece in same spot twice")
            return False

        # If there is at least one open spot, we know a piece can be placed for sure
        if len(self.get_surrounding_positions(pos, 0)) > 0:
            return True

        for position in self.get_surrounding_positions(pos):
            pos_group: GoGroup = self.board[position]
            # Can't place if it is the last open spot
            if pos_group == player_num:
                if len(pos_group.open_positions) > 1:
                    return True
            # Can place if it would kill an enemy group
            elif pos_group == self.other_player(player_num):
                if len(pos_group.open_positions) == 1:
                    return True

        return False

    def place_piece(self, player_num: int, pos: tuple[int, int]) -> bool:
        if not self.can_place_piece(player_num, pos, True):
            return False

        self.last_piece_placements[player_num - 1] = pos

        surrounding_groups: set[GoGroup] = {self.board[position] for position in self.get_surrounding_positions(pos, player_num)}
        if surrounding_groups:
            merge_group = surrounding_groups.pop()
            merge_group.merge_groups(surrounding_groups, pos)
            for position in merge_group.piece_positions:
                self.board[position] = merge_group
            self.groups -= surrounding_groups
        else:
            merge_group = GoGroup(self, player_num, pos)
            self.board[pos] = merge_group
            self.groups.add(merge_group)

        surrounding_enemy_groups: set[GoGroup] = {self.board[position] for position in self.get_surrounding_positions(pos, self.other_player(player_num))}
        groups_to_delete: set[GoGroup] = set()
        for group in surrounding_enemy_groups:
            group.update_open_positions(pos, False)
            if len(group.open_positions) == 0:
                groups_to_delete.add(group)

        self.groups -= groups_to_delete
        for group in groups_to_delete:
            for position in group.piece_positions:
                self.captured_piece_counts[player_num - 1] += 1
                # Update open positions for the removed piece
                for surrounding_position in self.get_surrounding_positions(position, player_num):
                    self.board[surrounding_position].open_positions.add(position)
                self.board[position] = 0

        return True

    def other_player(self, player_num: int):
        return 2 if player_num == 1 else 1

    def get_surrounding_positions(self, pos: tuple[int, int], num_filter: int|None = None):
        if num_filter is None:
            return [position for position in [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)] if self.is_on_board(position)]
        else:
            return [position for position in [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)] if self.is_on_board(position) and self.board[position] == num_filter]

    def __str__(self):
        return self.board.__str__()