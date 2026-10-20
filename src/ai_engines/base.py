"""Abstract base class for all Connect Four AI engine plugins."""
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ConnectFourAIEngine(ABC):
    """
    Plugin interface for Connect Four AI engines.

    Implement _compute_next_move() in your subclass and add a module-level
    factory function create().  The public next_move() wrapper validates the
    result and falls back gracefully so the game can always continue.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Short identifier shown on the start screen and in logs."""

    def next_move(self,
                  board: "list[list[int]]",
                  player: int,
                  num_cols: int,
                  num_rows: int,
                  connect_length: int) -> int:
        """
        Public entry point -- do NOT override in subclasses.

        Validates the column returned by _compute_next_move() and substitutes
        the first valid column if the engine returns an invalid or full column.

        board          : board[row][col], row 0 = top, 0=empty/1=P1/2=P2
        player         : PLAYER_1 or PLAYER_2
        num_cols       : board width
        num_rows       : board height
        connect_length : winning strip length
        Returns        : column index in [0, num_cols-1]
        """
        valid = [c for c in range(num_cols) if board[0][c] == 0]
        if not valid:
            logger.error("next_move called with no valid columns -- returning 0")
            return 0

        col = self._compute_next_move(board, player, num_cols, num_rows, connect_length)

        if col in valid:
            return col

        logger.warning(
            "%s._compute_next_move returned invalid/full column %d -- "
            "substituting first valid column %d",
            self.__class__.__name__, col, valid[0],
        )
        return valid[0]

    @abstractmethod
    def _compute_next_move(self,
                           board: "list[list[int]]",
                           player: int,
                           num_cols: int,
                           num_rows: int,
                           connect_length: int) -> int:
        """
        Implement the move-selection algorithm here.

        Must return a column index in [0, num_cols-1] whose top cell is empty
        (i.e., the column is not full).  next_move() verifies this and
        auto-corrects silently if violated.

        board[row][col] -- 0=empty, 1=player1, 2=player2, row 0 = top
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset any internal state for a fresh game."""
