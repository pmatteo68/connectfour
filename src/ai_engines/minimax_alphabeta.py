"""
Minimax with alpha-beta pruning for Connect Four.

The engine always plays as `player` (PLAYER_1 or PLAYER_2) and maximises its
own position score minus the opponent's position score.

Move ordering: center-first column search order + killer-move heuristic
(try immediately winning or blocking moves before the rest).
"""
import math
import random
import logging
from .base import ConnectFourAIEngine
from .minimax_alphabeta_config import (
    SEARCH_DEPTH,
    CENTER_WEIGHT,
    SCORE_WIN,
    SCORE_THREE,
    SCORE_TWO,
    KILLER_MOVE_ENABLED,
)

logger = logging.getLogger(__name__)

_EMPTY = 0
_P1    = 1
_P2    = 2
_OTHER = {_P1: _P2, _P2: _P1}


def _landing_row(board, col, num_rows):
    for row in range(num_rows - 1, -1, -1):
        if board[row][col] == _EMPTY:
            return row
    return None


def _make_move(board, col, player, num_rows, num_cols):
    row = _landing_row(board, col, num_rows)
    if row is None:
        return None, board
    new_board = [r[:] for r in board]
    new_board[row][col] = player
    return row, new_board


def _check_win_at(board, row, col, player, num_rows, num_cols, connect_length):
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    for dr, dc in directions:
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < num_rows and 0 <= c < num_cols and board[r][c] == player:
            count += 1
            r += dr; c += dc
        r, c = row - dr, col - dc
        while 0 <= r < num_rows and 0 <= c < num_cols and board[r][c] == player:
            count += 1
            r -= dr; c -= dc
        if count >= connect_length:
            return True
    return False


def _is_terminal(board, num_cols, num_rows, connect_length):
    valid = [c for c in range(num_cols) if board[0][c] == _EMPTY]
    if not valid:
        return True
    for row in range(num_rows):
        for col in range(num_cols):
            p = board[row][col]
            if p != _EMPTY:
                if _check_win_at(board, row, col, p, num_rows, num_cols, connect_length):
                    return True
    return False


def _winner(board, num_rows, num_cols, connect_length):
    for row in range(num_rows):
        for col in range(num_cols):
            p = board[row][col]
            if p != _EMPTY:
                if _check_win_at(board, row, col, p, num_rows, num_cols, connect_length):
                    return p
    return None


def _score_window(window, player, opponent, L):
    p_cnt   = window.count(player)
    opp_cnt = window.count(opponent)
    empty_n = window.count(_EMPTY)
    if opp_cnt > 0 and p_cnt > 0:
        return 0
    if p_cnt == L:
        return SCORE_WIN
    if opp_cnt == L:
        return -SCORE_WIN
    score = 0
    if p_cnt == L - 1 and empty_n >= 1:
        score += SCORE_THREE
    elif p_cnt == L - 2 and empty_n >= 2:
        score += SCORE_TWO
    if opp_cnt == L - 1 and empty_n >= 1:
        score -= SCORE_THREE
    elif opp_cnt == L - 2 and empty_n >= 2:
        score -= SCORE_TWO
    return score


def _evaluate(board, player, opponent, num_rows, num_cols, connect_length):
    L = connect_length
    total = 0

    mid_col = num_cols // 2
    center_count = sum(
        1 for row in range(num_rows) if board[row][mid_col] == player
    )
    total += center_count * CENTER_WEIGHT

    for row in range(num_rows):
        for col in range(num_cols - L + 1):
            window = [board[row][col + i] for i in range(L)]
            total += _score_window(window, player, opponent, L)

    for col in range(num_cols):
        for row in range(num_rows - L + 1):
            window = [board[row + i][col] for i in range(L)]
            total += _score_window(window, player, opponent, L)

    for row in range(num_rows - L + 1):
        for col in range(num_cols - L + 1):
            window = [board[row + i][col + i] for i in range(L)]
            total += _score_window(window, player, opponent, L)

    for row in range(L - 1, num_rows):
        for col in range(num_cols - L + 1):
            window = [board[row - i][col + i] for i in range(L)]
            total += _score_window(window, player, opponent, L)

    return total


def _order_moves(valid, board, player, opponent, num_rows, num_cols, connect_length):
    """Return valid columns ordered: win-now first, then block-opponent, then center-out."""
    wins   = []
    blocks = []
    rest   = []

    for col in valid:
        row, nb = _make_move(board, col, player, num_rows, num_cols)
        if row is not None and _check_win_at(nb, row, col, player, num_rows, num_cols, connect_length):
            wins.append(col)
            continue
        row2, nb2 = _make_move(board, col, opponent, num_rows, num_cols)
        if row2 is not None and _check_win_at(nb2, row2, col, opponent, num_rows, num_cols, connect_length):
            blocks.append(col)
            continue
        rest.append(col)

    mid = num_cols // 2
    rest.sort(key=lambda c: abs(c - mid))
    return wins + blocks + rest


def _minimax(board, depth, alpha, beta, maximizing,
             player, opponent,
             num_rows, num_cols, connect_length):
    valid = [c for c in range(num_cols) if board[0][c] == _EMPTY]

    w = _winner(board, num_rows, num_cols, connect_length)
    if w == player:
        return SCORE_WIN + depth
    if w == opponent:
        return -(SCORE_WIN + depth)
    if not valid:
        return 0
    if depth == 0:
        return _evaluate(board, player, opponent, num_rows, num_cols, connect_length)

    if KILLER_MOVE_ENABLED:
        ordered = _order_moves(valid, board, player if maximizing else opponent,
                               opponent if maximizing else player,
                               num_rows, num_cols, connect_length)
    else:
        mid = num_cols // 2
        ordered = sorted(valid, key=lambda c: abs(c - mid))

    if maximizing:
        value = -math.inf
        for col in ordered:
            _, nb = _make_move(board, col, player, num_rows, num_cols)
            child = _minimax(nb, depth - 1, alpha, beta, False,
                             player, opponent, num_rows, num_cols, connect_length)
            if child > value:
                value = child
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        return value
    else:
        value = math.inf
        for col in ordered:
            _, nb = _make_move(board, col, opponent, num_rows, num_cols)
            child = _minimax(nb, depth - 1, alpha, beta, True,
                             player, opponent, num_rows, num_cols, connect_length)
            if child < value:
                value = child
            if value < beta:
                beta = value
            if alpha >= beta:
                break
        return value


class MinimaxAlphaBetaEngine(ConnectFourAIEngine):

    def get_name(self) -> str:
        return f"Minimax Alpha-Beta (depth {SEARCH_DEPTH})"

    def reset(self) -> None:
        logger.debug("MinimaxAlphaBetaEngine reset")

    def _compute_next_move(self, board, player, num_cols, num_rows, connect_length):
        opponent = _OTHER[player]
        valid = [c for c in range(num_cols) if board[0][c] == _EMPTY]
        if not valid:
            return 0

        if KILLER_MOVE_ENABLED:
            ordered = _order_moves(valid, board, player, opponent,
                                   num_rows, num_cols, connect_length)
        else:
            mid = num_cols // 2
            ordered = sorted(valid, key=lambda c: abs(c - mid))

        best_col   = ordered[0]
        best_score = -math.inf

        for col in ordered:
            _, nb = _make_move(board, col, player, num_rows, num_cols)
            score = _minimax(nb, SEARCH_DEPTH - 1, -math.inf, math.inf,
                             False, player, opponent,
                             num_rows, num_cols, connect_length)
            logger.debug("AI col=%d score=%d", col, score)
            if score > best_score:
                best_score = score
                best_col   = col

        logger.debug("AI chose col=%d (score=%d)", best_col, best_score)
        return best_col


def create() -> MinimaxAlphaBetaEngine:
    return MinimaxAlphaBetaEngine()
