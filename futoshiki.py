from pynput import keyboard
from collections import deque
from os import sys
import heapq
import copy
import time
from rich.console import Console

board_size = 5

class Puzzle:
    def __init__(self, input_file, output_file):
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.board = None
        self.hconstraints = None
        self.vconstraints = None
        self.constraints = {}
        with open(input_file, 'r') as f:
            self.board = [[int(i) for i in f.readline().strip().split(' ')] for j in range(board_size)]
            f.readline()
            self.hconstraints = [[i for i in f.readline().strip().split(' ')] for j in range(board_size)]
            f.readline()
            self.vconstraints = [[i for i in f.readline().strip().split(' ')] for j in range(board_size)]
        self.output_file = output_file
        for row in range(board_size):
            for col in range(board_size - 1):
                if self.hconstraints[row][col] != '0':
                    left = (row, col)
                    right = (row, col + 1)

                    constraint = self.hconstraints[row][col]
                    inv_constraint = '<' if constraint == '>' else '>'

                    if left not in self.constraints:
                        self.constraints[left] = {}
                    self.constraints[left][right] = constraint

                    if right not in self.constraints:
                        self.constraints[right] = {}
                    self.constraints[right][left] = inv_constraint

        for row in range(board_size - 1):
            for col in range(board_size):
                if self.vconstraints[row][col] != '0':
                    left = (row, col)
                    right = (row + 1, col)

                    constraint = '<' if self.vconstraints[row][col] == '^' else '>'
                    inv_constraint = '<' if constraint == '>' else '>'

                    if left not in self.constraints:
                        self.constraints[left] = {}
                    self.constraints[left][right] = constraint

                    if right not in self.constraints:
                        self.constraints[right] = {}
                    self.constraints[right][left] = inv_constraint
        print(self)
        for key in self.constraints:
            print(key, '-', self.constraints[key])


    def __str__(self):
        string = []
        for row in range(board_size):
            v_string = []
            for col in range(board_size):
                nxt = (row, col + 1)
                below = (row + 1, col)
                if self.board[row][col] == 0:
                    string.append('_')
                else:
                    string.append(str(self.board[row][col]))
                string.append(' ')
                if (row, col) in self.constraints and nxt in self.constraints[(row, col)]:
                    string.append(self.constraints[(row, col)][nxt])
                else:
                    string.append(' ')
                if (row, col) in self.constraints and below in self.constraints[(row, col)]:
                    v_string.append('^' if self.constraints[(row, col)][below] == '<' else 'v')
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
        pass

p = Puzzle("SampleInput.txt", "SampleOutput.txt")
