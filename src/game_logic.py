"""
Core Connect Four game logic. No UI imports.

Board layout:
  board[row][col]  -- row 0 is the TOP of the visual board,
                      row (num_rows-1) is the BOTTOM (where discs stack).
  Values: EMPTY=0, PLAYER_1=1, PLAYER_2=2.

Discs fall from the top: drop_disc(col) places the disc in the
lowest empty row of that column.

Game phases:
  PHASE_PLAYER1_TURN -- Player 1 is about to move
  PHASE_PLAYER2_TURN -- Player 2 is about to move
  PHASE_DONE         -- game over (win or draw)
"""
import logging
from config_game import (
    NUM_COLS_DEFAULT,
    NUM_ROWS_DEFAULT,
    CONNECT_LENGTH_DEFAULT,
    NUM_DISCS_PER_PLAYER_DEFAULT,
    NUM_PLAYERS,
)

logger = logging.getLogger(__name__)

EMPTY    = 0
PLAYER_1 = 1
PLAYER_2 = 2

OTHER_PLAYER = {PLAYER_1: PLAYER_2, PLAYER_2: PLAYER_1}

PHASE_PLAYER1_TURN = "player1_turn"
PHASE_PLAYER2_TURN = "player2_turn"
PHASE_DONE         = "done"

DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def make_board(num_rows: int, num_cols: int) -> "list[list[int]]":
    return [[EMPTY] * num_cols for _ in range(num_rows)]


def get_valid_columns(board: "list[list[int]]", num_cols: int) -> "list[int]":
    return [c for c in range(num_cols) if board[0][c] == EMPTY]


def get_landing_row(board: "list[list[int]]", col: int, num_rows: int) -> "int | None":
    """Return row index where disc lands in col, or None if column is full."""
    for row in range(num_rows - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row
    return None


def find_winning_cells(board: "list[list[int]]",
                       row: int, col: int, player: int,
                       num_rows: int, num_cols: int,
                       connect_length: int) -> "list[tuple] | None":
    """
    After placing player's disc at (row, col), check all four directions.
    Returns the winning cell list if connect_length in a row is found, else None.
    The returned list contains exactly connect_length (row, col) tuples.
    """
    for dr, dc in DIRECTIONS:
        backward = []
        r, c = row - dr, col - dc
        while 0 <= r < num_rows and 0 <= c < num_cols and board[r][c] == player:
            backward.append((r, c))
            r -= dr
            c -= dc

        forward = []
        r, c = row + dr, col + dc
        while 0 <= r < num_rows and 0 <= c < num_cols and board[r][c] == player:
            forward.append((r, c))
            r += dr
            c += dc

        run = list(reversed(backward)) + [(row, col)] + forward
        if len(run) >= connect_length:
            return run[:connect_length]

    return None


def count_open_threats(board: "list[list[int]]",
                       player: int,
                       num_rows: int, num_cols: int,
                       connect_length: int) -> "dict[int, int]":
    """
    Count unblocked windows by how many of player's discs they contain.
    Returns {k: count} where k is the number of player discs in the window
    (the rest of the cells are empty; any window containing the opponent is ignored).
    """
    opponent = OTHER_PLAYER[player]
    counts: "dict[int, int]" = {}

    def _check_window(cells):
        player_n  = sum(1 for r, c in cells if board[r][c] == player)
        opponent_n = sum(1 for r, c in cells if board[r][c] == opponent)
        if opponent_n == 0 and player_n > 0:
            counts[player_n] = counts.get(player_n, 0) + 1

    for row in range(num_rows):
        for col in range(num_cols - connect_length + 1):
            cells = [(row, col + i) for i in range(connect_length)]
            _check_window(cells)

    for col in range(num_cols):
        for row in range(num_rows - connect_length + 1):
            cells = [(row + i, col) for i in range(connect_length)]
            _check_window(cells)

    for row in range(num_rows - connect_length + 1):
        for col in range(num_cols - connect_length + 1):
            cells = [(row + i, col + i) for i in range(connect_length)]
            _check_window(cells)

    for row in range(connect_length - 1, num_rows):
        for col in range(num_cols - connect_length + 1):
            cells = [(row - i, col + i) for i in range(connect_length)]
            _check_window(cells)

    return counts


def evaluate_position(board: "list[list[int]]",
                      player: int,
                      num_rows: int, num_cols: int,
                      connect_length: int) -> int:
    """
    Heuristic position score from player's perspective.
    Positive = good for player, negative = bad.
    Used by game_stats to build the advantage trajectory.
    """
    opponent = OTHER_PLAYER[player]

    SCORE_WIN   = 1000000
    SCORE_THREE = 100
    SCORE_TWO   = 10

    def _score_window(cells):
        p_cnt   = sum(1 for r, c in cells if board[r][c] == player)
        opp_cnt = sum(1 for r, c in cells if board[r][c] == opponent)
        empty_n = connect_length - p_cnt - opp_cnt
        if opp_cnt > 0:
            return 0
        if p_cnt == connect_length:
            return SCORE_WIN
        if p_cnt == connect_length - 1 and empty_n == 1:
            return SCORE_THREE
        if p_cnt == connect_length - 2 and empty_n >= 2:
            return SCORE_TWO
        return 0

    def _opp_score_window(cells):
        p_cnt   = sum(1 for r, c in cells if board[r][c] == player)
        opp_cnt = sum(1 for r, c in cells if board[r][c] == opponent)
        empty_n = connect_length - p_cnt - opp_cnt
        if p_cnt > 0:
            return 0
        if opp_cnt == connect_length:
            return SCORE_WIN
        if opp_cnt == connect_length - 1 and empty_n == 1:
            return SCORE_THREE
        if opp_cnt == connect_length - 2 and empty_n >= 2:
            return SCORE_TWO
        return 0

    total = 0

    for row in range(num_rows):
        for col in range(num_cols - connect_length + 1):
            cells = [(row, col + i) for i in range(connect_length)]
            total += _score_window(cells) - _opp_score_window(cells)

    for col in range(num_cols):
        for row in range(num_rows - connect_length + 1):
            cells = [(row + i, col) for i in range(connect_length)]
            total += _score_window(cells) - _opp_score_window(cells)

    for row in range(num_rows - connect_length + 1):
        for col in range(num_cols - connect_length + 1):
            cells = [(row + i, col + i) for i in range(connect_length)]
            total += _score_window(cells) - _opp_score_window(cells)

    for row in range(connect_length - 1, num_rows):
        for col in range(num_cols - connect_length + 1):
            cells = [(row - i, col + i) for i in range(connect_length)]
            total += _score_window(cells) - _opp_score_window(cells)

    return total


class GameState:
    """Full Connect Four game state."""

    def __init__(self,
                 first_player: int,
                 num_cols: int = NUM_COLS_DEFAULT,
                 num_rows: int = NUM_ROWS_DEFAULT,
                 connect_length: int = CONNECT_LENGTH_DEFAULT,
                 num_discs_per_player: int = NUM_DISCS_PER_PLAYER_DEFAULT):
        self.num_cols             = num_cols
        self.num_rows             = num_rows
        self.connect_length       = connect_length
        self.num_discs_per_player = num_discs_per_player

        self.board          = make_board(num_rows, num_cols)
        self.move_history   : "list[tuple[int, int, int]]" = []  # (player, col, row)
        self.discs_placed   = {PLAYER_1: 0, PLAYER_2: 0}
        self.winner         : "int | None" = None
        self.winning_cells  : "list[tuple[int, int]] | None" = None
        self.game_over      = False

        self.current_player = first_player
        self.phase = PHASE_PLAYER1_TURN if first_player == PLAYER_1 else PHASE_PLAYER2_TURN

        logger.debug(
            "GameState init: cols=%d rows=%d connect=%d discs=%d first=%d",
            num_cols, num_rows, connect_length, num_discs_per_player, first_player,
        )

    def get_valid_columns(self) -> "list[int]":
        return get_valid_columns(self.board, self.num_cols)

    def get_landing_row(self, col: int) -> "int | None":
        return get_landing_row(self.board, col, self.num_rows)

    def drop_disc(self, col: int) -> int:
        """
        Place current player's disc in col.
        Returns the landing row index.
        Raises ValueError if column is full or column index is invalid.
        """
        if col < 0 or col >= self.num_cols:
            raise ValueError(f"Column {col} out of range [0, {self.num_cols - 1}]")
        row = self.get_landing_row(col)
        if row is None:
            raise ValueError(f"Column {col} is full")

        player = self.current_player
        self.board[row][col] = player
        self.discs_placed[player] += 1
        self.move_history.append((player, col, row))
        logger.debug("Player %d drops in col %d -> row %d (disc #%d)",
                     player, col, row, self.discs_placed[player])

        winning_cells = find_winning_cells(
            self.board, row, col, player,
            self.num_rows, self.num_cols, self.connect_length,
        )

        if winning_cells:
            self.winner        = player
            self.winning_cells = winning_cells
            self.game_over     = True
            self.phase         = PHASE_DONE
            logger.debug("Player %d wins! Winning cells: %s", player, winning_cells)
        elif self._is_draw():
            self.game_over = True
            self.phase     = PHASE_DONE
            logger.debug("Draw: no valid moves or disc quota reached")
        else:
            next_player = OTHER_PLAYER[player]
            self.current_player = next_player
            self.phase = (PHASE_PLAYER1_TURN if next_player == PLAYER_1
                          else PHASE_PLAYER2_TURN)

        return row

    def _is_draw(self) -> bool:
        if not self.get_valid_columns():
            return True
        discs_p1 = self.discs_placed.get(PLAYER_1, 0)
        discs_p2 = self.discs_placed.get(PLAYER_2, 0)
        both_exhausted = (discs_p1 >= self.num_discs_per_player and
                          discs_p2 >= self.num_discs_per_player)
        return both_exhausted
