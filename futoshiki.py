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
        for key in self.state.constraints:
            print(key, '-', self.state.constraints[key])


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

    def play():
        pass
    def solve():
        #So for this, we do backtracking search
        #The current state of the board is stored in a 2D array, and the individual constraints will not change. 
        #So we do best first where the heuristic is number of constraints, and degree is the tie breaker
        #Each iteration, we pick the unassigned tile with the most constraints. If there are multiple, we pick the one with the highest degree
        #We then assign it a legal value, and continue with this new state
        #If we reach a dead end, we backtrack until there are other legal moves that we didn't try, then we try those.

        #So the datastructures:
        #The board is a 2D array of ints

        #We need a few helper functions:
        # select_next_assignment() - returns the next assignment to try
            #I think this should keep track of the number of constraints for each tile, and the degree of each tile. Maybe some way to initialize it? Make it a generator?
            #We should also consider that the number of constraints will change as the tiles around the number get filled. So we should update the number of constraints for each tile as we go
            #This should return the next tile to try.
            #This is the most important function because it determines the order in which we try the assignments;
            #the rest is just checking and backtracking if we reach a dead end
        # get_legal_moves(row, col) - returns a list of legal moves for the given tile
            #This needs to be in the order that we want to try the moves. So we should try the moves in order of the number of constraints they will create
        # update_constraints(row, col) - updates the number of constraints for each tile

        def get_legal_moves(state, row, col):
            legal_moves = {1, 2, 3, 4, 5}
            for move in legal_moves:
                if move in state.row_constraints[row] or move in state.col_constraints[col]:
                    legal_moves.remove(move)
                for constraint in state.constraints[(row, col)]:
                    if state.constraints[(row, col)][constraint] == '>':
                        if move <= board[constraint[0]][constraint[1]]:
                            legal_moves.remove(move)
                    else:
                        if move >= board[constraint[0]][constraint[1]]:
                            legal_moves.remove(move)
            return legal_moves

        def select_next_assignment(state):
            max_constraints = 0
            max_constraints_tiles = set()
            #Find the tiles with the most constraints
            for row in range(board_size):
                for col in range(board_size):
                    if state.board[row][col] != 0:
                        continue

                    num_constraints = 5 - get_legal_moves(state, row, col)

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
            pass
    
        def generate_new_state(state, row, col, move):
            #return a new state with the next assignment, and with update row and column constraints
            pass
        pass

p = Puzzle("SampleInput.txt", "SampleOutput.txt")
