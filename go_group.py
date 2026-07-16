from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from go_board import GoBoard

class GoGroup(int):
    def __new__(cls, _, player_num, __):
        return super().__new__(cls, player_num)

    def __init__(self, board: GoBoard, player_num: int, initial_position: tuple[int, int] | None = None):
        self.player_num = player_num
        self.piece_positions: set[tuple[int, int]] = set()
        self.open_positions: set[tuple[int, int]] = set()
        self.board = board
        if initial_position is not None:
            self._add_piece(initial_position)

    def __eq__(self, other):
        if isinstance(other, GoGroup):
            return self is other
        return int(self) == other

    def __hash__(self):
        return id(self)

    def copy(self, board: GoBoard) -> GoGroup:
        new_group = GoGroup(board, self.player_num, None)
        new_group.piece_positions = self.piece_positions.copy()
        new_group.open_positions = self.open_positions.copy()
        return new_group

    def merge_groups(self, groups: set[GoGroup], intersection_position: tuple[int, int]):
        for group in groups:
            self.piece_positions.update(group.piece_positions)
            self.open_positions.update(group.open_positions)

        self.add_piece(intersection_position)

    def add_piece(self, pos: tuple[int, int]):
        if pos not in self.open_positions:
            raise Exception("Can't place piece in group that isn't open")

        self._add_piece(pos)

    def _add_piece(self, pos: tuple[int, int]):
        self.piece_positions.add(pos)
        self.update_open_positions(pos, True)

    def update_open_positions(self, pos: tuple[int, int], is_friendly: bool):
        if pos in self.open_positions:
            self.open_positions.remove(pos)

        if is_friendly:
            self.open_positions.update(self.board.get_surrounding_positions(pos, 0))