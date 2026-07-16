import numpy as np
import random

from go_board import GoBoard
from go_agent import GoAgent

class MCTSNode:
    def __init__(self, board: GoBoard, player_num: int, parent, c=np.sqrt(2)):
        self.board = board
        self.player_num = player_num
        self.other_player_num = 1 if player_num == 2 else 2
        self.parent: MCTSNode = parent
        self.moves = board.get_available_moves(player_num)
        self.terminal = len(self.moves) == 0
        self.children: dict[tuple[int, int], MCTSNode] = dict()
        for m in self.moves:
            self.children[m] = None

        self.num_visits = 0
        self.num_wins = 0

        #c value to be used in the UCB calculation
        self.c = c

    def max_child(self):
        max_num_visits = 0
        max_move = None

        for m in self.moves:
            if self.children[m] is not None and self.children[m].num_visits > max_num_visits:
                max_num_visits = self.children[m].num_visits
                max_move = m
        return max_move

    def upper_bound(self, N: int):
        bound = (self.num_wins / self.num_visits) + (self.c * np.sqrt(np.log(N) / self.num_visits))
        return bound

    def select(self):
        max_ub = -np.inf
        max_child = None

        if self.terminal:
            return self

        for m in self.moves:
            if self.children[m] is None:
                new_board = self.board.copy()
                new_board.place_piece(self.player_num, m)

                self.children[m] = MCTSNode(new_board, self.other_player_num, self, self.c) #Create the child node
                return self.children[m]

            #Child already exists, get it's UCB value
            current_ub = self.children[m].upper_bound(self.num_visits)

            #Compare to previous best UCB
            if current_ub > max_ub:
                max_ub = current_ub
                max_child = m

        #Recursively return the select result for the best child
        return self.children[max_child].select()


    def simulate(self, max_simulation_depth: int) -> int:
        result = None
        if self.board.is_winning_state(self.player_num):
            result = -1

        # self.terminal (no moves for self.player_num) plus the capture comparison
        # is exactly is_winning_state(other_player_num), without rescanning the board
        elif self.terminal and self.board.captured_piece_counts[self.other_player_num - 1] > self.board.captured_piece_counts[self.player_num - 1]:
            result = 1

        else:
            valid_moves = set(self.moves)
            new_board = self.board.copy()
            players = [self.player_num, self.other_player_num]
            i = 0
            while len(valid_moves) != 0 and result is None and i < max_simulation_depth:
                cur_player = players[i % 2]

                move = random.choice(list(valid_moves))
                valid_moves.discard(move)
                if not new_board.place_piece(cur_player, move):
                    raise Exception("Failed to place a piece in simulation")

                i += 1
                valid_moves = new_board.get_available_moves(players[i % 2])

            player_piece_count = new_board.captured_piece_counts[self.player_num - 1]
            other_player_piece_count = new_board.captured_piece_counts[self.other_player_num - 1]
            result = other_player_piece_count - player_piece_count

        self.num_wins += result
        self.num_visits += 1

        self.parent.back_prop(-result)

    def back_prop(self, score):
        self.num_visits += 1
        self.num_wins += score
        if self.parent is not None:
            self.parent.back_prop(-score)

class MCTSAgent(GoAgent):
    def __init__(self, player_num: int, max_iterations: int, max_simulation_depth: int, c: float = 1.41):
        self.player_num = player_num
        self.max_iterations = max_iterations
        self.max_simulation_depth = max_simulation_depth
        self.c = c

    def get_move(self, board):
        """
        Use MCTS to get the next move
        """
        root = MCTSNode(board, self.player_num, None, self.c)

        for _ in range(self.max_iterations):
            cur_node = root.select()
            cur_node.simulate(self.max_simulation_depth)

        return root.max_child()