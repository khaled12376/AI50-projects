"""
Tic Tac Toe Player
"""

import math
from typing import List, Any

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def count_specific_element(arr, element):
    count = 0
    for row in arr:
        count += row.count(element)
    return count


def player(board):
    """
    Returns player who has the next turn on a board.
    X is first.
    """
    if count_specific_element(board, X) > count_specific_element(board, O):
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    rslt = [row[:] for row in board]
    i, j = action
    if (not (rslt[i][j] == EMPTY)) or (not (0 <= i <= 2 and 0 <= j <= 2)):
        raise Exception("Invalid Move")

    rslt[i][j] = player(board)
    return rslt


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for player in [X, O]:
        # Check rows, columns and diagonals
        for i in range(3):
            if all(board[i][j] == player for j in range(3)) or \
                    all(board[j][i] == player for j in range(3)):
                return player

        if all(board[i][i] == player for i in range(3)) or \
                all(board[i][2 - i] == player for i in range(3)):
            return player

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if not winner(board) == None:
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def maxval(board):
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, minval(result(board, action)))
    return v


def minval(board):
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, maxval(result(board, action)))
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        if player(board) == X:
            score = float("-inf")
            action = ()
            # print(actions(board))
            for a in actions(board):

                tempscore = minval(result(board, a))
                # print(tempscore)
                if tempscore > score:
                    score = tempscore
                    action = a

            return action
        else:
            score = float("inf")
            action = ()
            for a in actions(board):
                tempscore = maxval(result(board, a))
                if tempscore < score:
                    score = tempscore
                    action = a

            return action
