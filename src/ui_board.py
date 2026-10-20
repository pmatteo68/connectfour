"""BoardCanvas -- Tkinter canvas widget that renders the Connect Four grid."""

import tkinter as tk
import logging

import config_ui   as UI
import config_game as CG
from game_logic import PLAYER_1, PLAYER_2, EMPTY

log = logging.getLogger(__name__)

_NO_COLUMN  = -1   # sentinel: no column highlighted / no ghost


class BoardCanvas(tk.Frame):
    """
    Displays the Connect Four board grid.

    Layout (top to bottom on the canvas):
      - Header row (HEADER_HEIGHT px): ghost-disc drop zone.
      - Board rows (NUM_ROWS * CELL_SIZE px): the actual grid.

    Row indices in this class:
      row 0 = top of the board (discs arrive here first when the column fills up)
      row (num_rows-1) = bottom of the board

    Usage:
      canvas.set_on_column_click(callback)   -- called with col index on click
      canvas.set_current_player(player)      -- updates ghost disc colour
      canvas.set_enabled(True/False)         -- enable/disable user interaction
      canvas.set_disc(row, col, player)      -- paint a disc without animation
      canvas.clear_all()                     -- remove all discs (reset visuals)
      canvas.animate_drop(col, landing_row, player, on_done)
      canvas.flash_win(cells, player, on_done)
      canvas.replay_from_history(history)    -- paint committed moves silently
    """

    def __init__(self, parent, num_cols: int, num_rows: int, **kwargs):
        super().__init__(parent, bg=UI.BG_COLOR, **kwargs)
        self._num_cols       = num_cols
        self._num_rows       = num_rows
        self._enabled        = True
        self._current_player = PLAYER_1
        self._ghost_col      = _NO_COLUMN
        self._on_col_click   = None

        self._cell_ovals   : "dict[tuple, int]" = {}   # (row, col) -> canvas id
        self._ghost_oval   : "int | None"       = None  # header ghost disc id
        self._col_rects    : "dict[int, int]"   = {}    # col -> hover rect id
        self._canvas       : "tk.Canvas | None" = None

        self._build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_on_column_click(self, callback) -> None:
        """Register a callback(col: int) fired when user clicks a column."""
        self._on_col_click = callback

    def set_current_player(self, player: int) -> None:
        self._current_player = player
        self._refresh_ghost()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self._hide_ghost()

    def set_disc(self, row: int, col: int, player: "int | None") -> None:
        """Paint (or clear) the disc at (row, col). player=None clears to empty."""
        oid = self._cell_ovals.get((row, col))
        if oid is None:
            return
        if player == PLAYER_1:
            color = UI.PLAYER_1_COLOR
        elif player == PLAYER_2:
            color = UI.PLAYER_2_COLOR
        else:
            color = UI.CELL_EMPTY_COLOR
        self._canvas.itemconfigure(oid, fill=color)
        log.debug("set_disc row=%d col=%d player=%s", row, col, player)

    def clear_all(self) -> None:
        """Reset all cells to empty colour."""
        for (row, col), oid in self._cell_ovals.items():
            self._canvas.itemconfigure(oid, fill=UI.CELL_EMPTY_COLOR)
        self._hide_ghost()

    def replay_from_history(self, history: "list[tuple[int,int,int]]") -> None:
        """Paint all (player, col, row) moves without animation."""
        self.clear_all()
        for player, col, row in history:
            self.set_disc(row, col, player)

    def animate_drop(self, col: int, landing_row: int, player: int,
                     on_done) -> None:
        """
        Animate a disc falling from row 0 to landing_row in column col.
        Calls on_done() when the animation completes.
        If DROP_ANIM_ENABLED is False, paints directly and calls on_done.
        """
        self._hide_ghost()
        self.set_enabled(False)

        if not CG.DROP_ANIM_ENABLED or landing_row == 0:
            self.set_disc(landing_row, col, player)
            self._canvas.after(0, on_done)
            return

        color = UI.PLAYER_1_COLOR if player == PLAYER_1 else UI.PLAYER_2_COLOR
        r = UI.DISC_DIAMETER // 2

        x1, y1 = self._cell_center(0, col)
        self._anim_oval = self._canvas.create_oval(
            x1 - r, y1 - r, x1 + r, y1 + r,
            fill=color, outline=UI.DISC_OUTLINE_COLOR,
            width=UI.DISC_OUTLINE_WIDTH,
            tags="anim_disc",
        )
        log.debug("animate_drop col=%d landing=%d player=%d", col, landing_row, player)
        self._canvas.after(CG.DROP_ANIM_STEP_MS,
                           lambda: self._anim_step(col, 0, landing_row, player, on_done))

    def flash_win(self, cells: "list[tuple[int,int]]", player: int,
                  on_done) -> None:
        """Flash winning cells WIN_FLASH_COUNT times then call on_done."""
        flash_color = (UI.WIN_FLASH_COLOR_P1 if player == PLAYER_1
                       else UI.WIN_FLASH_COLOR_P2)
        disc_color  = (UI.PLAYER_1_COLOR if player == PLAYER_1
                       else UI.PLAYER_2_COLOR)
        self._flash_step(cells, disc_color, flash_color, CG.WIN_FLASH_COUNT, True, on_done)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self) -> None:
        s    = UI
        cols = self._num_cols
        rows = self._num_rows

        canvas_w = cols * s.CELL_SIZE + 2 * s.BOARD_PADDING
        canvas_h = s.HEADER_HEIGHT + self._num_rows * s.CELL_SIZE + 2 * s.BOARD_PADDING

        self._canvas = tk.Canvas(
            self,
            width=canvas_w,
            height=canvas_h,
            bg=s.BG_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack()

        self._draw_board_frame(canvas_w, canvas_h)
        self._draw_cells()
        self._draw_ghost()
        self._draw_col_hit_areas(canvas_w, canvas_h)

        self._canvas.bind("<Motion>",   self._on_mouse_move)
        self._canvas.bind("<Button-1>", self._on_mouse_click)
        self._canvas.bind("<Leave>",    self._on_mouse_leave)

    def _draw_board_frame(self, canvas_w: int, canvas_h: int) -> None:
        s   = UI
        pad = s.BOARD_PADDING
        self._canvas.create_rectangle(
            pad,
            pad + s.HEADER_HEIGHT,
            canvas_w - pad,
            canvas_h - pad,
            fill=s.BOARD_FRAME_COLOR,
            outline="",
        )

    def _draw_cells(self) -> None:
        s = UI
        r = s.DISC_DIAMETER // 2
        for row in range(self._num_rows):
            for col in range(self._num_cols):
                cx, cy = self._cell_center(row, col)
                oid = self._canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=s.CELL_EMPTY_COLOR,
                    outline=s.CELL_OUTLINE_COLOR,
                    width=s.CELL_OUTLINE_WIDTH,
                    tags=(f"cell_{row}_{col}",),
                )
                self._cell_ovals[(row, col)] = oid

    def _draw_ghost(self) -> None:
        s  = UI
        r  = s.DISC_DIAMETER // 2
        hx, hy = self._header_center(0)
        self._ghost_oval = self._canvas.create_oval(
            hx - r, hy - r, hx + r, hy + r,
            fill=s.PLAYER_1_GHOST_COLOR,
            outline=s.GHOST_OUTLINE_COLOR,
            width=s.GHOST_OUTLINE_WIDTH,
            state="hidden",
            tags="ghost",
        )

    def _draw_col_hit_areas(self, canvas_w: int, canvas_h: int) -> None:
        s = UI
        for col in range(self._num_cols):
            x1 = s.BOARD_PADDING + col * s.CELL_SIZE
            x2 = x1 + s.CELL_SIZE
            y1 = s.BOARD_PADDING
            y2 = canvas_h - s.BOARD_PADDING
            rid = self._canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="", outline="",
                tags=f"hit_{col}",
            )
            self._col_rects[col] = rid

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _cell_center(self, row: int, col: int) -> "tuple[int, int]":
        s  = UI
        cx = s.BOARD_PADDING + col * s.CELL_SIZE + s.CELL_SIZE // 2
        cy = s.BOARD_PADDING + s.HEADER_HEIGHT + row * s.CELL_SIZE + s.CELL_SIZE // 2
        return cx, cy

    def _header_center(self, col: int) -> "tuple[int, int]":
        s  = UI
        cx = s.BOARD_PADDING + col * s.CELL_SIZE + s.CELL_SIZE // 2
        cy = s.BOARD_PADDING + s.HEADER_HEIGHT // 2
        return cx, cy

    def _col_from_x(self, x: int) -> int:
        col = (x - UI.BOARD_PADDING) // UI.CELL_SIZE
        return max(0, min(self._num_cols - 1, col))

    def _is_over_board(self, x: int, y: int) -> bool:
        s = UI
        return (s.BOARD_PADDING <= x < s.BOARD_PADDING + self._num_cols * s.CELL_SIZE
                and s.BOARD_PADDING <= y)

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def _on_mouse_move(self, event: tk.Event) -> None:
        if not self._enabled:
            return
        if not self._is_over_board(event.x, event.y):
            self._hide_ghost()
            return
        col = self._col_from_x(event.x)
        if col != self._ghost_col:
            self._ghost_col = col
            self._refresh_ghost()

    def _on_mouse_leave(self, event: tk.Event) -> None:
        self._ghost_col = _NO_COLUMN
        self._hide_ghost()

    def _on_mouse_click(self, event: tk.Event) -> None:
        if not self._enabled:
            return
        if not self._is_over_board(event.x, event.y):
            return
        col = self._col_from_x(event.x)
        log.debug("Board click col=%d", col)
        if self._on_col_click:
            self._on_col_click(col)

    # ------------------------------------------------------------------
    # Ghost disc helpers
    # ------------------------------------------------------------------

    def _refresh_ghost(self) -> None:
        if self._ghost_col == _NO_COLUMN or not self._enabled:
            self._hide_ghost()
            return
        s   = UI
        col = self._ghost_col
        hx, hy = self._header_center(col)
        r   = s.DISC_DIAMETER // 2
        self._canvas.coords(
            self._ghost_oval,
            hx - r, hy - r, hx + r, hy + r,
        )
        ghost_color = (s.PLAYER_1_GHOST_COLOR if self._current_player == PLAYER_1
                       else s.PLAYER_2_GHOST_COLOR)
        self._canvas.itemconfigure(
            self._ghost_oval,
            fill=ghost_color,
            state="normal",
        )

    def _hide_ghost(self) -> None:
        if self._ghost_oval is not None:
            self._canvas.itemconfigure(self._ghost_oval, state="hidden")

    # ------------------------------------------------------------------
    # Drop animation
    # ------------------------------------------------------------------

    def _anim_step(self, col: int, current_row: int, landing_row: int,
                   player: int, on_done) -> None:
        s   = UI
        r   = s.DISC_DIAMETER // 2

        if current_row >= landing_row:
            self._canvas.delete("anim_disc")
            self.set_disc(landing_row, col, player)
            self.set_enabled(True)
            on_done()
            return

        next_row = current_row + 1
        nx, ny = self._cell_center(next_row, col)
        self._canvas.coords(
            self._anim_oval,
            nx - r, ny - r, nx + r, ny + r,
        )
        self._canvas.after(CG.DROP_ANIM_STEP_MS,
                           lambda: self._anim_step(col, next_row, landing_row,
                                                   player, on_done))

    # ------------------------------------------------------------------
    # Win flash animation
    # ------------------------------------------------------------------

    def _flash_step(self, cells, disc_color: str, flash_color: str,
                    remaining: int, flash_on: bool, on_done) -> None:
        color = flash_color if flash_on else disc_color
        for row, col in cells:
            oid = self._cell_ovals.get((row, col))
            if oid is not None:
                self._canvas.itemconfigure(oid, fill=color)

        if remaining == 0:
            for row, col in cells:
                oid = self._cell_ovals.get((row, col))
                if oid is not None:
                    self._canvas.itemconfigure(oid, fill=disc_color)
            on_done()
            return

        self._canvas.after(
            CG.WIN_FLASH_INTERVAL_MS,
            lambda: self._flash_step(cells, disc_color, flash_color,
                                     remaining - 1, not flash_on, on_done),
        )
