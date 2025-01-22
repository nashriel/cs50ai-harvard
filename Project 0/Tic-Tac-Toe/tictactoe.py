"""
Tic Tac Toe Player
"""

import math
import copy

MAX = float('inf')
MIN = float('-inf')
X = "X"
O = "O"
EMPTY = None
N = 3


def initial_state():
    """
    Returns the initial state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Determines which player has the next turn.
    """
    count_x = sum(row.count(X) for row in board)
    count_o = sum(row.count(O) for row in board)
    return X if count_x <= count_o else O


def actions(board):
    """
    Generates all possible actions (i, j) for the current board state.
    """
    return {(r, c) for r in range(N) for c in range(N) if board[r][c] == EMPTY}


def result(board, action):
    """
    Produces the resulting board after applying the specified action.
    """
    r, c = action
    if board[r][c] != EMPTY or not (0 <= r < N and 0 <= c < N):
        raise ValueError("Invalid action: position is either occupied or out of bounds.")

    updated_board = copy.deepcopy(board)
    updated_board[r][c] = player(board)
    return updated_board


def winner(board):
    """
    Determines the winner of the game, if any.
    """
    rows = [set(row) for row in board]
    cols = [set(board[r][c] for r in range(N)) for c in range(N)]
    diags = [
        {board[i][i] for i in range(N)},
        {board[i][N - 1 - i] for i in range(N)}
    ]

    for group in rows + cols + diags:
        if len(group) == 1 and EMPTY not in group:
            return next(iter(group))

    return None


def terminal(board):
    """
    Checks if the game is over.
    """
    return winner(board) is not None or all(EMPTY not in row for row in board)


def utility(board):
    """
    Evaluates the board state: 1 if X wins, -1 if O wins, 0 otherwise.
    """
    result = winner(board)
    return 1 if result == X else -1 if result == O else 0


def minimax(board):
    """
    Determines the optimal action for the current player.
    """
    if player(board) == X:
        _, best_action = maxvalue(board, MIN, MAX)
    else:
        _, best_action = minvalue(board, MIN, MAX)

    return best_action


def maxvalue(board, alpha, beta):
    """
    Computes the maximum score for the maximizing player.
    """
    if terminal(board):
        return utility(board), None

    max_score = MIN
    best_action = None

    for action in actions(board):
        score, _ = minvalue(result(board, action), alpha, beta)
        if score > max_score:
            max_score = score
            best_action = action

        alpha = max(alpha, max_score)
        if alpha >= beta:
            break

    return max_score, best_action


def minvalue(board, alpha, beta):
    """
    Computes the minimum score for the minimizing player.
    """
    if terminal(board):
        return utility(board), None

    min_score = MAX
    best_action = None

    for action in actions(board):
        score, _ = maxvalue(result(board, action), alpha, beta)
        if score < min_score:
            min_score = score
            best_action = action

        beta = min(beta, min_score)
        if beta <= alpha:
            break

    return min_score, best_action
