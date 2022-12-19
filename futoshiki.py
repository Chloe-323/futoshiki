from pynput import keyboard
from collections import deque, namedtuple
from os import sys
import os
import copy
import time
from rich.console import Console

board_size = 5
State = namedtuple('State', 'board constraints row_constraints col_constraints')
console = Console()

#Non blocking keyboard input gets stored in a queue
keypresses = deque()
listener = keyboard.Listener(on_press=keypresses.append)
listener.start()

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

    def print(self, selected = None, err = False):
        #Clear screen if windows:
        if sys.platform == 'win32':
            os.system('cls')
            #print('\033[2J', end = '')
        elif sys.platform == 'linux':
            print('\033[2J', end = '')
            pass
        if selected == None:
            console.print(self)
        else:
            repr_string = str(self)
            #calculate offset of selected tile in string
            #X coordinate: 
            x_offset = 4 * selected[1]
            #Y coordinate:
            y_offset = 42 * selected[0]
            red_print = f'[bold red]{repr_string[x_offset + y_offset]}[/bold red]' if not err else f'[bold red]X[/bold red]'
            console.print(repr_string[:x_offset + y_offset] + red_print + repr_string[x_offset + y_offset + 1:])
            
    def play(self):
        initial_state = copy.deepcopy(self.state)
        immovable = set()
        for row in range(board_size):
            for col in range(board_size):
                if self.state.board[row][col] != 0:
                    immovable.add((row, col))
        selected = [0, 0]
        while True:
            self.print(selected = selected)
            input_key = None
            while input_key == None:

                if len(keypresses) > 0:
                    key = keypresses.popleft()
                    if key == keyboard.Key.esc:
                        sys.exit(0)
                    elif key == keyboard.KeyCode.from_char('s'):
                        solved_state = self.solve(initial_state)
                        if solved_state == None:
                            print('No solution found')
                            exit(1)
                        self.state = solved_state
                        self.print()
                        print('Solved!')
                        exit(0)
                    elif key == keyboard.Key.up:
                        selected[0] = max(0, selected[0] - 1)
                    elif key == keyboard.Key.down:
                        selected[0] = min(board_size - 1, selected[0] + 1)
                    elif key == keyboard.Key.left:
                        selected[1] = max(0, selected[1] - 1)
                    elif key == keyboard.Key.right:
                        selected[1] = min(board_size - 1, selected[1] + 1)
                    elif key == keyboard.KeyCode.from_char('1'):
                        input_key = 1
                        break
                    elif key == keyboard.KeyCode.from_char('2'):
                        input_key = 2
                        break
                    elif key == keyboard.KeyCode.from_char('3'):
                        input_key = 3
                        break
                    elif key == keyboard.KeyCode.from_char('4'):
                        input_key = 4
                        break
                    elif key == keyboard.KeyCode.from_char('5'):
                        input_key = 5
                        break
                    print('p')
                    self.print(selected = selected)

            #Draw board
            #Get player inputs
            is_valid = True
            is_overwrite = False
            if input_key in self.state.row_constraints[selected[0]] or input_key in self.state.col_constraints[selected[1]]:
                is_valid = False
                self.print(selected = selected, err = True)
                time.sleep(0.2)
                continue
            if  (selected[0], selected[1]) in immovable:
                is_valid = False
                self.print(selected = selected, err = True)
                time.sleep(0.2)
            elif self.state.board[selected[0]][selected[1]] != 0:
                is_overwrite = True
            if (selected[0], selected[1]) in self.state.constraints:
                for other_tile in self.state.constraints[(selected[0], selected[1])]:
                    if self.state.board[other_tile[0]][other_tile[1]] != 0:
                        if self.state.constraints[(selected[0], selected[1])][other_tile] == '<':
                            if self.state.board[other_tile[0]][other_tile[1]] < input_key:
                                is_valid = False
                                self.print(selected = selected, err = True)
                                time.sleep(0.2)
                                break
                        else:
                            if self.state.board[other_tile[0]][other_tile[1]] > input_key:
                                is_valid = False
                                self.print(selected = selected, err = True)
                                time.sleep(0.2)
                                break
            if is_valid:
                row = selected[0]
                col = selected[1]
                new_board = copy.deepcopy(self.state.board)
                new_board[row][col] = input_key
                new_row_constraints = copy.deepcopy(self.state.row_constraints)
                new_col_constraints = copy.deepcopy(self.state.col_constraints)
                if is_overwrite:
                    new_row_constraints[row].remove(self.state.board[row][col])
                    new_col_constraints[col].remove(self.state.board[row][col])
                new_row_constraints[row].add(input_key)
                new_col_constraints[col].add(input_key)
                
                new_state = State(new_board, self.state.constraints, new_row_constraints, new_col_constraints)
                self.state = new_state
                
            #Check if move is valid
            #If valid, update board
            #Else, flash the X
            #Check if board is solved
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
            #define degree as highest number of constraints on other tiless
            max_degree = 0
            max_degree_tiles = set()
            for tile in max_constraints_tiles:
                degree = 0
                for constraint in state.constraints[tile]:
                    if state.board[constraint[0]][constraint[1]] == 0:
                        degree += 1
                if degree > max_degree:
                    max_degree = degree
                    max_degree_tiles = {tile}
                elif degree == max_degree:
                    max_degree_tiles.add(tile)

            #Once we've finished, return any tile that works.
            return max_degree_tiles.pop()
    
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
            if self.output_file:
                with open(self.output_file, 'w') as f:
                    for row in state.board:
                        for col in row:
                            f.write(str(col) + " ")
                        f.write("\n")
            return state
        next_assignment = select_next_assignment(state)
        for move in get_legal_moves(state, next_assignment[0], next_assignment[1]):
            new_state = generate_new_state(state, next_assignment[0], next_assignment[1], move)
            result = self.solve(new_state)
            if result is not None:
                return result
        return None

input_file = None
output_file = None
auto_solve = False
for index, argument in enumerate(sys.argv):
    print(argument)
    if argument == "-i":
        input_file = sys.argv[index + 1]
    elif argument == "-o":
        output_file = sys.argv[index + 1]
    elif argument == '-s':
        auto_solve = True
    if input_file is None:
        print("Usage: python3 futoshiki.py -i <input_file> [-o <output_file>] [-s]")
        print("Note: The default python installation on Windows does not allow for command line arguments. You can enter them manually below.")
        input_file = input("Enter input file: ")
        output_file = input("Enter output file: ")
        if output_file == "":
            output_file = None
        auto_solve = input("Auto solve? (y/n): ") == 'y'
        keypresses.clear() #Clear this because if not it will read the keypresses from the input prompt
    p = Puzzle(input_file, output_file)
    if auto_solve:
        s = p.solve()
        if s is not None:
            p.state = s
            p.print()
            print("Solved!")
        else:
            print("No solution found")
    else:
        p.play()
