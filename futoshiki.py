from pynput import keyboard
from collections import deque, namedtuple
from os import sys
import heapq
import copy
import time
from rich.console import Console

board_size = 5
State = namedtuple('State', 'board constraints row_constraints col_constraints')

class Puzzle:
    def __init__(self, input_file, output_file):

        board = None
        constraints = {}
        row_constraints = [set() for _ in range(board_size)]
        col_constraints = [set() for _ in range(board_size)]

        hconstraints = None
        vconstraints = None
        with open(input_file, 'r') as f:
            board = [[int(i) for i in f.readline().strip().split(' ')] for j in range(board_size)]
            f.readline()
            hconstraints = [[i for i in f.readline().strip().split(' ')] for j in range(board_size)]
            f.readline()
            vconstraints = [[i for i in f.readline().strip().split(' ')] for j in range(board_size)]
        self.output_file = output_file

        #Initialize all individual constraints to empty and add row and column constraints
        for row in range(board_size):
            for col in range(board_size):
                constraints[(row, col)] = {}
                if board[row][col] != 0:
                    row_constraints[row].add(board[row][col])
                    col_constraints[col].add(board[row][col])


        #Add horizontal inequality constraints
        for row in range(board_size):
            for col in range(board_size - 1):
                if hconstraints[row][col] != '0':
                    left = (row, col)
                    right = (row, col + 1)

                    constraint = hconstraints[row][col]
                    inv_constraint = '<' if constraint == '>' else '>'

                    constraints[left][right] = constraint

                    constraints[right][left] = inv_constraint

        #Add vertical inequality constraints
        for row in range(board_size - 1):
            for col in range(board_size):
                if vconstraints[row][col] != '0':
                    left = (row, col)
                    right = (row + 1, col)

                    constraint = '<' if vconstraints[row][col] == '^' else '>'
                    inv_constraint = '<' if constraint == '>' else '>'

                    constraints[left][right] = constraint
                    constraints[right][left] = inv_constraint

        self.state = State(board, constraints, row_constraints, col_constraints)
        print(self)
#       for k in constraints:
#           print(k, constraints[k])
#       print()
        finished = self.solve()
        if finished:
            self.state = finished
            print(self)
            print('Solved!')


    def __str__(self):
        string = []
        for row in range(board_size):
            v_string = []
            for col in range(board_size):
                nxt = (row, col + 1)
                below = (row + 1, col)
                if self.state.board[row][col] == 0:
                    string.append('_')
                else:
                    string.append(str(self.state.board[row][col]))
                string.append(' ')
                if (row, col) in self.state.constraints and nxt in self.state.constraints[(row, col)]:
                    string.append(self.state.constraints[(row, col)][nxt])
                else:
                    string.append(' ')
                if (row, col) in self.state.constraints and below in self.state.constraints[(row, col)]:
                    v_string.append('^' if self.state.constraints[(row, col)][below] == '<' else 'v')
                else:
                    v_string.append(' ')
                v_string.append('   ')
                string.append(' ')
            string.append('\n')
            string.extend(v_string)
            string.append('\n')
        return ''.join(string)

    def play(self):
        pass

    def solve(self, state = None):

        if state is None:
            state = self.state
        #So for this, we do backtracking search
        #The current state of the board is stored in a 2D array, and the individual constraints will not change. 
        #So we do best first where the heuristic is number of constraints, and degree is the tie breaker
        #Each iteration, we pick the unassigned tile with the most constraints. If there are multiple, we pick the one with the highest degree
        #We then assign it a legal value, and continue with this new state
        #If we reach a dead end, we backtrack until there are other legal moves that we didn't try, then we try those.

        #We need a few helper functions:
        # select_next_assignment() - returns the next assignment to try
            #I think this should keep track of the number of constraints for each tile, and the degree of each tile. Maybe some way to initialize it? Make it a generator?
            #We should also consider that the number of constraints will change as the tiles around the number get filled. So we should update the number of constraints for each tile as we go
            #This should return the next tile to try.
        # get_legal_moves(row, col) - returns a list of legal moves for the given tile
            #This needs to be in the order that we want to try the moves. So we should try the moves in order of the number of constraints they will create
        # update_constraints(row, col) - updates the number of constraints for each tile

        def get_legal_moves(state, row, col):
            all_moves = {1, 2, 3, 4, 5}
            moves = set()
            for move in all_moves:
                if move in state.row_constraints[row] or move in state.col_constraints[col]:
                    continue
                is_valid = True
                for constraint in state.constraints[(row, col)]:
                    if state.board[constraint[0]][constraint[1]] == 0:
                        continue
                    if state.constraints[(row, col)][constraint] == '>':
                        if move <= state.board[constraint[0]][constraint[1]]:
                            is_valid = False
                            break
                    else:
                        if move >= state.board[constraint[0]][constraint[1]]:
                            is_valid = False
                            break
                if is_valid:
                    moves.add(move)
            return moves

        def select_next_assignment(state):
            max_constraints = 0
            max_constraints_tiles = set()
            #Find the tiles with the most constraints
            for row in range(board_size):
                for col in range(board_size):
                    if state.board[row][col] != 0:
                        continue

                    num_constraints = 5 - len(get_legal_moves(state, row, col))

                    if num_constraints > max_constraints:
                        max_constraints = num_constraints
                        max_constraints_tiles = {(row, col)}
                    elif num_constraints == max_constraints:
                        max_constraints_tiles.add((row, col))
            if len(max_constraints_tiles) == 0:
                return None #Need to backtrack
            elif len(max_constraints_tiles) == 1:
                return max_constraints_tiles.pop()

            #Find tile with highest degree
            #define degree as highest number of constraints on other tiles

            #Once we've finished, return any tile that works.
            return max_constraints_tiles.pop()
    
        def generate_new_state(state, row, col, move):
            #return a new state with the next assignment, and with update row and column constraints
            new_board = copy.deepcopy(state.board)
            new_board[row][col] = move
            new_row_constraints = copy.deepcopy(state.row_constraints)
            new_col_constraints = copy.deepcopy(state.col_constraints)
            new_row_constraints[row].add(move)
            new_col_constraints[col].add(move)
            new_state = State(new_board, state.constraints, new_row_constraints, new_col_constraints)
            return new_state
            pass
        
        def is_finished(state):
            for row in range(board_size):
                for col in range(board_size):
                    if state.board[row][col] == 0:
                        return False
            return True
            #return true if the board is filled in and legal
            pass


        if is_finished(state):
            return state
        next_assignment = select_next_assignment(state)
        for move in get_legal_moves(state, next_assignment[0], next_assignment[1]):
            new_state = generate_new_state(state, next_assignment[0], next_assignment[1], move)
            result = self.solve(new_state)
            if result is not None:
                return result
        return None


p = Puzzle("SampleInput.txt", "SampleOutput.txt")
p = Puzzle("Input1.txt", "Output1.txt")
p = Puzzle("Input2.txt", "Output2.txt")
p = Puzzle("Input3.txt", "Output3.txt")
