"""In-game statistics collector for Connect Four."""
import time
import logging
from game_logic import PLAYER_1, PLAYER_2, evaluate_position

logger = logging.getLogger(__name__)


class GameStats:

    def __init__(self):
        self._start_time        = time.monotonic()
        self._game_duration     = None

        self.winner             = None        # PLAYER_1 | PLAYER_2 | None (draw)
        self.game_over_reason   = None        # "win" | "draw"
        self.human_player       = None        # PLAYER_1 | PLAYER_2 | None (autoplay)

        self._move_times        : "list[float]"     = []   # wall time per move
        self._move_players      : "list[int]"       = []   # player per move
        self._move_cols         : "list[int]"       = []   # column per move
        self._position_scores   : "list[int]"       = []   # eval after each move (P1 perspective)

        self._total_moves       = 0
        self._last_move_ts      = time.monotonic()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_move(self, player: int, col: int,
                    board, num_rows: int, num_cols: int,
                    connect_length: int) -> None:
        now = time.monotonic()
        elapsed = now - self._last_move_ts
        self._last_move_ts = now

        self._move_players.append(player)
        self._move_cols.append(col)
        self._move_times.append(elapsed)
        self._total_moves += 1

        score = evaluate_position(
            board, PLAYER_1, num_rows, num_cols, connect_length
        )
        self._position_scores.append(score)

        logger.debug(
            "Stats: move #%d player=%d col=%d elapsed=%.2fs pos_score=%d",
            self._total_moves, player, col, elapsed, score,
        )

    def finalise(self, winner: "int | None", game_over_reason: str,
                 human_player: "int | None") -> None:
        self._game_duration   = time.monotonic() - self._start_time
        self.winner           = winner
        self.game_over_reason = game_over_reason
        self.human_player     = human_player
        self._log_summary()

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def game_duration(self) -> float:
        return self._game_duration or 0.0

    @property
    def total_moves(self) -> int:
        return self._total_moves

    @property
    def player1_moves(self) -> int:
        return sum(1 for p in self._move_players if p == PLAYER_1)

    @property
    def player2_moves(self) -> int:
        return sum(1 for p in self._move_players if p == PLAYER_2)

    def player_move_count(self, player: int) -> int:
        return sum(1 for p in self._move_players if p == player)

    def avg_move_time(self, player: int) -> float:
        times = [t for p, t in zip(self._move_players, self._move_times)
                 if p == player]
        return sum(times) / len(times) if times else 0.0

    @property
    def position_score_trajectory(self) -> "list[int]":
        """Position score from Player 1's perspective after each move."""
        return list(self._position_scores)

    @property
    def move_cols(self) -> "list[int]":
        return list(self._move_cols)

    @property
    def move_players(self) -> "list[int]":
        return list(self._move_players)

    def winning_move_number(self) -> "int | None":
        """1-based index of the move that ended the game, or None for draws."""
        if self.game_over_reason == "win" and self._total_moves > 0:
            return self._total_moves
        return None

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_summary(self) -> None:
        dur = self.game_duration
        m, s = divmod(int(dur), 60)
        dur_str = f"{m}m{s:02d}s" if m else f"{s}s"

        if self.winner == PLAYER_1:
            w_str = "Player 1"
        elif self.winner == PLAYER_2:
            w_str = "Player 2"
        else:
            w_str = "Draw"

        logger.info("=== GAME SUMMARY ===")
        logger.info(
            "[OUTCOME] result=%s reason=%s duration=%s",
            w_str, self.game_over_reason, dur_str,
        )
        logger.info(
            "[MOVES] total=%d p1=%d p2=%d",
            self._total_moves, self.player1_moves, self.player2_moves,
        )
        logger.info(
            "[TIMING] avg_p1=%.2fs avg_p2=%.2fs",
            self.avg_move_time(PLAYER_1),
            self.avg_move_time(PLAYER_2),
        )
        logger.info("[TRAJECTORY] pos_scores=%s", self._position_scores)
