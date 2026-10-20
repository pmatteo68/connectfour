"""Main application window and controller for Connect Four."""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

import config_game   as CG
import config_text   as CT
import config_ui     as UI
import ai_engine     as AE
from game_logic       import (GameState, PLAYER_1, PLAYER_2,
                               PHASE_PLAYER1_TURN, PHASE_PLAYER2_TURN, PHASE_DONE)
from game_persistence import save_game, load_game
from game_stats       import GameStats
from ui_board         import BoardCanvas
from ui_stats         import StatsWindow

log = logging.getLogger(__name__)

_FIRST_HUMAN = "human"
_FIRST_AI    = "ai"


# ---------------------------------------------------------------------------
# Start screen
# ---------------------------------------------------------------------------

class StartScreen(tk.Frame):
    """
    The initial screen shown at launch or after New Game.
    Provides dropdowns for all board parameters, a who-goes-first selector,
    a Start button, and a Load button.
    """

    def __init__(self, parent, on_start, on_load, on_quit, on_autoplay):
        """
        on_start(num_cols, num_rows, connect_length, num_discs_per_player,
                 first_player)  -- first_player is "human" or "ai"
        on_load()              -- triggers open-file dialog in App
        on_quit()              -- exits the application
        on_autoplay(num_cols, num_rows, connect_length, num_discs_per_player)
                               -- starts a fully automated game (no human)
        """
        super().__init__(parent, bg=UI.BG_COLOR)
        self._on_start    = on_start
        self._on_load     = on_load
        self._on_quit     = on_quit
        self._on_autoplay_cb = on_autoplay
        self._build()

    # ------------------------------------------------------------------

    def _build(self) -> None:
        s = UI

        # Title + subtitle
        tk.Label(self, text=CT.START_TITLE,
                 font=s.START_TITLE_FONT, fg=s.START_TITLE_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_TITLE_PADY, 0))

        self._subtitle_var = tk.StringVar(
            value=CT.make_start_subtitle(CG.CONNECT_LENGTH_DEFAULT)
        )
        tk.Label(self, textvariable=self._subtitle_var,
                 font=s.START_SUBTITLE_FONT, fg=s.START_SUBTITLE_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_SUBTITLE_PADY, 0))

        # AI engine info line
        tk.Label(
            self,
            text=CT.START_ENGINE_LABEL + "  " + AE.get_name(),
            font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
        ).pack(pady=(s.START_ENGINE_PADY, 0))

        # Parameter dropdowns (2-column grid)
        grid_frame = tk.Frame(self, bg=s.BG_COLOR)
        grid_frame.pack(pady=(s.START_SECTION_PADY, 0))

        self._cols_var    = tk.StringVar(value=str(CG.NUM_COLS_DEFAULT))
        self._rows_var    = tk.StringVar(value=str(CG.NUM_ROWS_DEFAULT))
        self._connect_var = tk.StringVar(value=str(CG.CONNECT_LENGTH_DEFAULT))
        self._discs_var   = tk.StringVar(value=str(CG.NUM_DISCS_PER_PLAYER_DEFAULT))

        cols_opts    = [str(v) for v in range(CG.NUM_COLS_MIN,    CG.NUM_COLS_MAX + 1)]
        rows_opts    = [str(v) for v in range(CG.NUM_ROWS_MIN,    CG.NUM_ROWS_MAX + 1)]
        connect_opts = [str(v) for v in range(CG.CONNECT_LENGTH_MIN,
                                               CG.CONNECT_LENGTH_MAX + 1)]
        discs_opts   = [str(v) for v in range(CG.NUM_DISCS_PER_PLAYER_MIN,
                                               CG.NUM_DISCS_PER_PLAYER_MAX + 1)]

        params = [
            (CT.START_COLS_LABEL,    self._cols_var,    cols_opts),
            (CT.START_ROWS_LABEL,    self._rows_var,    rows_opts),
            (CT.START_CONNECT_LABEL, self._connect_var, connect_opts),
            (CT.START_DISCS_LABEL,   self._discs_var,   discs_opts),
        ]

        for idx, (label, var, opts) in enumerate(params):
            tk.Label(grid_frame, text=label, font=s.LABEL_FONT,
                     fg=s.LABEL_COLOR, bg=s.BG_COLOR, anchor="e",
                     ).grid(row=idx, column=0, sticky="e", padx=(0, 8), pady=3)
            om = tk.OptionMenu(grid_frame, var, *opts)
            om.config(
                bg=s.BTN_BG, fg=s.BTN_FG,
                activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                highlightthickness=0, font=s.BTN_FONT,
                relief=s.BTN_RELIEF, bd=s.MENU_BD, width=5,
            )
            om["menu"].config(
                bg=s.BTN_BG, fg=s.BTN_FG,
                activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            )
            om.grid(row=idx, column=1, sticky="w", pady=3)
            var.trace_add("write", lambda *_: self._update_rules_hint())

        # Who goes first
        tk.Label(self, text=CT.START_WHO_FIRST,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_WHO_FIRST_PADY, 0))

        radio_frame = tk.Frame(self, bg=s.BG_COLOR)
        radio_frame.pack()

        self._first_var = tk.StringVar(
            value=_FIRST_HUMAN if CG.DEFAULT_FIRST_PLAYER == _FIRST_HUMAN else _FIRST_AI
        )
        for value, text in ((_FIRST_HUMAN, CT.START_FIRST_HUMAN),
                             (_FIRST_AI,    CT.START_FIRST_AI)):
            tk.Radiobutton(
                radio_frame, text=text,
                variable=self._first_var, value=value,
                font=s.BTN_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                activebackground=s.BG_COLOR, selectcolor=s.BG_COLOR,
                indicatoron=True,
            ).pack(side="left", padx=s.START_BTN_PADX)

        # Rules hint (auto-updated on dropdown change)
        self._rules_hint_var = tk.StringVar()
        tk.Label(self, textvariable=self._rules_hint_var,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_RULES_PADY, 0))
        self._update_rules_hint()

        # Start and Load buttons
        tk.Button(
            self, text=CT.BTN_START,
            font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            relief=s.BTN_RELIEF, bd=s.BTN_BD,
            padx=s.BTN_PADX, pady=s.BTN_PADY,
            command=self._on_start_clicked,
        ).pack(pady=(s.START_BOTTOM_ROW_PADY, 0),
               padx=s.START_BTN_PADX, fill="x", ipadx=10)

        tk.Button(
            self, text=CT.BTN_LOAD_GAME,
            font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            relief=s.BTN_RELIEF, bd=s.BTN_BD,
            padx=s.BTN_PADX, pady=s.BTN_PADY,
            command=self._on_load,
        ).pack(pady=(s.START_BOTTOM_ROW_PADY // 2, 0),
               padx=s.START_BTN_PADX, fill="x", ipadx=10)

        tk.Button(
            self, text=CT.BTN_AUTOPLAY,
            font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            relief=s.BTN_RELIEF, bd=s.BTN_BD,
            padx=s.BTN_PADX, pady=s.BTN_PADY,
            command=self._on_autoplay_clicked,
        ).pack(pady=(s.START_BOTTOM_ROW_PADY // 2, 0),
               padx=s.START_BTN_PADX, fill="x", ipadx=10)

        tk.Button(
            self, text=CT.BTN_QUIT,
            font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            relief=s.BTN_RELIEF, bd=s.BTN_BD,
            padx=s.BTN_PADX, pady=s.BTN_PADY,
            command=self._on_quit,
        ).pack(pady=(s.START_BOTTOM_ROW_PADY // 2, s.START_BOTTOM_ROW_PADY),
               padx=s.START_BTN_PADX, fill="x", ipadx=10)

    def _update_rules_hint(self) -> None:
        try:
            connect = int(self._connect_var.get())
            self._subtitle_var.set(CT.make_start_subtitle(connect))
            self._rules_hint_var.set(
                CT.make_rules_hint(
                    int(self._cols_var.get()),
                    int(self._rows_var.get()),
                    connect,
                    int(self._discs_var.get()),
                )
            )
        except (ValueError, tk.TclError):
            pass

    def _on_start_clicked(self) -> None:
        try:
            self._on_start(
                int(self._cols_var.get()),
                int(self._rows_var.get()),
                int(self._connect_var.get()),
                int(self._discs_var.get()),
                self._first_var.get(),
            )
        except (ValueError, tk.TclError) as exc:
            log.error("Start screen bad input: %s", exc)

    def _on_autoplay_clicked(self) -> None:
        try:
            self._on_autoplay_cb(
                int(self._cols_var.get()),
                int(self._rows_var.get()),
                int(self._connect_var.get()),
                int(self._discs_var.get()),
            )
        except (ValueError, tk.TclError) as exc:
            log.error("Auto play bad input: %s", exc)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class App(tk.Tk):
    """
    Top-level Tkinter window.  Manages the start screen and game screen,
    drives game phase transitions, and owns the AI background thread.
    """

    def __init__(self):
        super().__init__()
        self.title(CT.WINDOW_TITLE)
        self.configure(bg=UI.BG_COLOR)
        self.resizable(False, False)

        # Game state (None when on start screen)
        self._gs           : "GameState | None" = None
        self._human_player : "int | None"       = None
        self._stats        : "GameStats | None" = None

        # Frame pointers
        self._start_frame  : "StartScreen | None" = None
        self._game_frame   : "tk.Frame | None"    = None

        # Board canvas and status label (alive only while game frame is live)
        self._board_canvas : "BoardCanvas | None" = None
        self._status_label : "tk.Label | None"    = None

        # Autoplay: two independent engine instances, one per player
        self._autoplay_engines: "dict[int, object]" = {}

        # True when the current (or next) game runs in fully automated mode.
        # Set by _on_start_autoplay; reset to False by _on_start_normal.
        self._autoplay = False

        # Generation counter -- incremented on each new game to discard
        # stale AI results that arrive after the user started a new game.
        self._game_id = 0

        # Minimum window width enforced while the game screen is shown.
        # Zero means: fit to content (used on the start screen).
        self._min_width = 0

        self._build_menu()
        self._show_start()

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------

    def _show_start(self) -> None:
        log.debug("Navigating to start screen")
        self._min_width = 0
        self._teardown_game()
        if self._start_frame:
            self._start_frame.destroy()
        self._start_frame = StartScreen(self, self._on_start_normal,
                                        self._on_load_game, self.quit,
                                        self._on_start_autoplay)
        self._start_frame.pack(fill="both", expand=True,
                                padx=UI.BOARD_PADDING, pady=UI.BOARD_PADDING)
        self.after(UI.LAYOUT_INIT_DELAY_MS, self._fit_window)

    def _show_game(self, state: GameState, human_player: "int | None") -> None:
        log.debug("Navigating to game screen (human_player=%s, autoplay=%s)",
                  human_player, self._autoplay)
        if self._start_frame:
            self._start_frame.pack_forget()
            self._start_frame.destroy()
            self._start_frame = None
        self._teardown_game()

        self._gs           = state
        self._human_player = human_player
        self._stats        = GameStats()
        self._stats._stats_num_cols = state.num_cols
        self._stats._stats_num_rows = state.num_rows
        self._game_id     += 1

        # Autoplay engines (fresh instances so they don't share state)
        if self._autoplay:
            self._autoplay_engines = {
                PLAYER_1: AE.create_fresh_instance(),
                PLAYER_2: AE.create_fresh_instance(),
            }
            log.debug("Autoplay engines created for both players")
        else:
            self._autoplay_engines = {}
            AE.reset()

        self._min_width = UI.MIN_WINDOW_WIDTH
        self._game_frame = tk.Frame(self, bg=UI.BG_COLOR)
        self._game_frame.pack(fill="both", expand=True)

        self._board_canvas = BoardCanvas(
            self._game_frame, state.num_cols, state.num_rows
        )
        self._board_canvas.pack()
        self._board_canvas.set_on_column_click(self._on_human_col_click)

        if state.move_history:
            self._board_canvas.replay_from_history(state.move_history)

        self._build_status_bar(self._game_frame)

        self.after(UI.LAYOUT_INIT_DELAY_MS, self._fit_window)

        if state.game_over:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._on_loaded_game_over)
        else:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._begin_phase)

    def _teardown_game(self) -> None:
        if self._game_frame:
            self._game_frame.destroy()
            self._game_frame   = None
            self._board_canvas = None
            self._status_label = None
        self._gs              = None
        self._autoplay_engines = {}

    def _build_status_bar(self, parent: tk.Frame) -> None:
        s = UI
        bar = tk.Frame(parent, bg=s.STATUS_BG, height=s.STATUS_BAR_HEIGHT)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        btn_frame = tk.Frame(bar, bg=s.STATUS_BG)
        btn_frame.pack(side="right", padx=s.STATUS_BTN_PADX_END,
                       pady=s.STATUS_BTN_PADY)

        for label, cmd in (
            (CT.BTN_NEW_GAME,  self._on_new_game),
            (CT.BTN_SAVE_GAME, self._on_save_game),
            (CT.BTN_LOAD_GAME, self._on_load_game),
            (CT.BTN_QUIT,      self.quit),
        ):
            tk.Button(
                btn_frame, text=label,
                font=s.STATUS_BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
                activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                relief=s.BTN_RELIEF, bd=s.BTN_BD,
                padx=s.STATUS_BTN_PADX, pady=s.STATUS_BTN_PADY,
                command=cmd,
            ).pack(side="left", padx=s.STATUS_BTN_PADX // 2)

        self._status_label = tk.Label(
            bar, text="",
            font=s.STATUS_FONT, fg=s.STATUS_COLOR, bg=s.STATUS_BG,
            anchor="w", padx=s.STATUS_LABEL_PADX,
        )
        self._status_label.pack(side="left", fill="x", expand=True)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        s = UI
        menubar = tk.Menu(
            self, bg=s.BG_COLOR, fg=s.MENU_FG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            bd=s.MENU_BD,
        )

        game_menu = tk.Menu(
            menubar, tearoff=0, bg=s.BG_COLOR, fg=s.MENU_FG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
        )
        game_menu.add_command(label=CT.MENU_NEW,  command=self._on_new_game)
        game_menu.add_command(label=CT.MENU_SAVE, command=self._on_save_game)
        game_menu.add_command(label=CT.MENU_LOAD, command=self._on_load_game)
        game_menu.add_separator()
        game_menu.add_command(label=CT.MENU_QUIT, command=self.quit)
        menubar.add_cascade(label=CT.MENU_GAME, menu=game_menu)

        help_menu = tk.Menu(
            menubar, tearoff=0, bg=s.BG_COLOR, fg=s.MENU_FG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
        )
        help_menu.add_command(label=CT.MENU_RULES, command=self._show_rules)
        help_menu.add_command(label=CT.MENU_ABOUT, command=self._show_about)
        menubar.add_cascade(label=CT.MENU_HELP, menu=help_menu)

        self.config(menu=menubar)

    # ------------------------------------------------------------------
    # Phase management
    # ------------------------------------------------------------------

    def _begin_phase(self) -> None:
        if self._gs is None:
            return
        if self._gs.game_over:
            self._on_game_over()
            return

        player = self._gs.current_player
        self._board_canvas.set_current_player(player)

        if self._autoplay:
            self._board_canvas.set_enabled(False)
            self._set_status(CT.STATUS_AI_TURN, player)
            engine = self._autoplay_engines[player]
            self.after(CG.AUTOPLAY_MOVE_DELAY_MS,
                       lambda: self._schedule_ai_move(player, engine, self._game_id))
        elif player == self._human_player:
            self._board_canvas.set_enabled(True)
            self._set_status(CT.STATUS_HUMAN_TURN, player)
        else:
            self._board_canvas.set_enabled(False)
            self._set_status(CT.STATUS_AI_TURN, player)
            self.after(CG.AI_THINK_DELAY_MS,
                       lambda: self._schedule_ai_move(player, None, self._game_id))

    def _on_human_col_click(self, col: int) -> None:
        if self._gs is None or self._gs.game_over:
            return
        if self._gs.current_player != self._human_player:
            return
        if self._gs.get_landing_row(col) is None:
            messagebox.showinfo(CT.WINDOW_TITLE, CT.MSG_COL_FULL)
            return
        self._board_canvas.set_enabled(False)
        self._commit_move(col)

    def _commit_move(self, col: int) -> None:
        if self._gs is None:
            return
        player = self._gs.current_player
        row    = self._gs.drop_disc(col)
        self._stats.record_move(
            player, col, self._gs.board,
            self._gs.num_rows, self._gs.num_cols, self._gs.connect_length,
        )
        self._set_status(CT.STATUS_ANIMATING)
        self._board_canvas.animate_drop(
            col, row, player,
            lambda: self._after_animation(col, row, player),
        )

    def _after_animation(self, col: int, row: int, player: int) -> None:
        if self._gs is None:
            return
        if self._gs.game_over:
            if self._gs.winner is not None:
                self._board_canvas.flash_win(
                    self._gs.winning_cells, player,
                    self._on_game_over,
                )
            else:
                self._on_game_over()
        else:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._begin_phase)

    # ------------------------------------------------------------------
    # AI thread
    # ------------------------------------------------------------------

    def _schedule_ai_move(self, player: int, engine, game_id: int) -> None:
        if game_id != self._game_id:
            return
        if self._gs is None or self._gs.game_over:
            return

        board_copy = [r[:] for r in self._gs.board]
        num_cols   = self._gs.num_cols
        num_rows   = self._gs.num_rows
        connect    = self._gs.connect_length

        def _run() -> None:
            if engine is None:
                col = AE.next_move(board_copy, player, num_cols, num_rows, connect)
            else:
                col = engine.next_move(board_copy, player, num_cols, num_rows, connect)
            self.after(0, lambda: self._on_ai_result(col, player, game_id))

        t = threading.Thread(target=_run, daemon=True, name=f"AI-P{player}")
        t.start()

    def _on_ai_result(self, col: int, player: int, game_id: int) -> None:
        if game_id != self._game_id:
            log.debug("Discarding stale AI result (game changed)")
            return
        if self._gs is None or self._gs.game_over:
            return
        if self._gs.current_player != player:
            log.debug("Discarding stale AI result (player mismatch)")
            return
        self._commit_move(col)

    # ------------------------------------------------------------------
    # Game over
    # ------------------------------------------------------------------

    def _on_game_over(self) -> None:
        if self._gs is None or self._stats is None:
            return
        winner = self._gs.winner
        reason = "win" if winner is not None else "draw"
        self._stats.finalise(winner, reason, self._human_player)

        if winner == PLAYER_1:
            msg   = (CT.GAMEOVER_HUMAN_WINS if self._human_player == PLAYER_1
                     else CT.GAMEOVER_P1_WINS)
            color = UI.TURN_COLOR_P1
        elif winner == PLAYER_2:
            if self._human_player == PLAYER_2:
                msg = CT.GAMEOVER_HUMAN_WINS
            elif self._human_player == PLAYER_1:
                msg = CT.GAMEOVER_AI_WINS
            else:
                msg = CT.GAMEOVER_P2_WINS
            color = UI.TURN_COLOR_P2
        else:
            msg   = CT.GAMEOVER_DRAW
            color = UI.TURN_COLOR_DRAW

        self._set_status(msg)
        if self._status_label:
            self._status_label.configure(fg=color)
        self._board_canvas.set_enabled(False)
        log.debug("Game over handler: winner=%s reason=%s", winner, reason)

        self.after(UI.STATS_DELAY_MS, self._show_stats)

    def _on_loaded_game_over(self) -> None:
        if self._gs is None:
            return
        winner = self._gs.winner
        if winner == PLAYER_1:
            msg   = CT.GAMEOVER_P1_WINS
            color = UI.TURN_COLOR_P1
        elif winner == PLAYER_2:
            msg   = CT.GAMEOVER_P2_WINS
            color = UI.TURN_COLOR_P2
        else:
            msg   = CT.GAMEOVER_DRAW
            color = UI.TURN_COLOR_DRAW
        self._set_status(msg)
        if self._status_label:
            self._status_label.configure(fg=color)
        self._board_canvas.set_enabled(False)
        if self._gs.winner is not None and self._gs.winning_cells:
            self._board_canvas.flash_win(
                self._gs.winning_cells, self._gs.winner, lambda: None
            )

    def _show_stats(self) -> None:
        if self._stats is None:
            return
        if self._stats.total_moves == 0:
            log.debug("Skipping stats window (no moves recorded)")
            return
        StatsWindow(self, self._stats, self._human_player)

    # ------------------------------------------------------------------
    # Menu / button handlers
    # ------------------------------------------------------------------

    def _on_new_game(self) -> None:
        log.debug("New game requested")
        self._game_id += 1
        self._show_start()

    def _on_save_game(self) -> None:
        if self._gs is None:
            messagebox.showinfo(CT.WINDOW_TITLE, CT.MSG_NO_GAME)
            return
        path = filedialog.asksaveasfilename(
            title=CT.MENU_SAVE,
            defaultextension=".json",
            filetypes=[(CT.SAVE_FILETYPE, "*.json")],
        )
        if not path:
            return
        try:
            save_game(self._gs, self._human_player, path)
            messagebox.showinfo(CT.WINDOW_TITLE,
                                CT.MSG_SAVED.format(path=path))
        except Exception as exc:
            messagebox.showerror(CT.WINDOW_TITLE,
                                 CT.MSG_SAVE_ERROR.format(err=exc))

    def _on_load_game(self) -> None:
        path = filedialog.askopenfilename(
            title=CT.MENU_LOAD,
            filetypes=[(CT.SAVE_FILETYPE, "*.json")],
        )
        if not path:
            return
        try:
            state, human_player = load_game(path)
        except Exception as exc:
            messagebox.showerror(CT.WINDOW_TITLE,
                                 CT.MSG_LOAD_ERROR.format(err=exc))
            return
        self._game_id += 1
        self._show_game(state, human_player)

    def _on_start_normal(self, num_cols: int, num_rows: int,
                         connect_length: int, num_discs_per_player: int,
                         first_player: str) -> None:
        self._autoplay = False
        self._on_start_new_game(num_cols, num_rows, connect_length,
                                num_discs_per_player, first_player)

    def _on_start_autoplay(self, num_cols: int, num_rows: int,
                           connect_length: int, num_discs_per_player: int) -> None:
        self._autoplay = True
        self._on_start_new_game(num_cols, num_rows, connect_length,
                                num_discs_per_player, _FIRST_HUMAN)

    def _on_start_new_game(self, num_cols: int, num_rows: int,
                           connect_length: int, num_discs_per_player: int,
                           first_player: str) -> None:
        log.debug(
            "Start new game: cols=%d rows=%d connect=%d discs=%d first=%s "
            "autoplay=%s",
            num_cols, num_rows, connect_length, num_discs_per_player,
            first_player, self._autoplay,
        )

        if self._autoplay:
            human_player = None
            first_pid    = PLAYER_1
        elif first_player == _FIRST_HUMAN:
            human_player = PLAYER_1
            first_pid    = PLAYER_1
        else:
            human_player = PLAYER_2
            first_pid    = PLAYER_1

        state = GameState(
            first_player         = first_pid,
            num_cols             = num_cols,
            num_rows             = num_rows,
            connect_length       = connect_length,
            num_discs_per_player = num_discs_per_player,
        )
        self._show_game(state, human_player)

    # ------------------------------------------------------------------
    # Help dialogs
    # ------------------------------------------------------------------

    def _show_rules(self) -> None:
        s   = UI
        dlg = tk.Toplevel(self)
        dlg.title(CT.MENU_RULES)
        dlg.configure(bg=s.BG_COLOR)
        dlg.resizable(False, False)
        dlg.grab_set()
        tk.Label(
            dlg, text=CT.RULES_TEXT,
            font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
            wraplength=s.RULES_WRAP_WIDTH, justify="left",
            padx=s.RULES_LABEL_PADX, pady=s.RULES_LABEL_PADY,
        ).pack()
        tk.Button(
            dlg, text=CT.BTN_CLOSE,
            font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            relief=s.BTN_RELIEF, bd=s.BTN_BD, padx=s.BTN_PADX, pady=s.BTN_PADY,
            command=dlg.destroy,
        ).pack(pady=(0, s.RULES_CLOSE_PADY_BOT))
        self._center_dialog(dlg)

    def _show_about(self) -> None:
        s   = UI
        dlg = tk.Toplevel(self)
        dlg.title(CT.ABOUT_TITLE)
        dlg.configure(bg=s.BG_COLOR)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text=CT.ABOUT_SUBTITLE,
                 font=s.START_TITLE_FONT, fg=s.START_TITLE_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.ABOUT_TITLE_PADY_TOP, 0), padx=s.ABOUT_PADX)

        tk.Frame(dlg, height=1, bg=s.PANEL_DIVIDER_COLOR).pack(
            fill="x", padx=s.ABOUT_DIVIDER_PADX,
            pady=(s.ABOUT_HEADER_DIVIDER_PADY, 0),
        )

        tk.Label(
            dlg, text=CT.ABOUT_BODY,
            font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
            wraplength=s.ABOUT_WRAP_WIDTH, justify="center",
            padx=s.ABOUT_PADX, pady=s.ABOUT_PADY,
        ).pack()

        tk.Frame(dlg, height=1, bg=s.PANEL_DIVIDER_COLOR).pack(
            fill="x", padx=s.ABOUT_DIVIDER_PADX,
            pady=(s.ABOUT_BODY_DIVIDER_PADY, 0),
        )

        tk.Button(
            dlg, text=CT.BTN_CLOSE,
            font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            relief=s.BTN_RELIEF, bd=s.BTN_BD, padx=s.BTN_PADX, pady=s.BTN_PADY,
            command=dlg.destroy,
        ).pack(pady=(s.ABOUT_CLOSE_PADY_TOP, s.ABOUT_CLOSE_PADY_BOT))

        self._center_dialog(dlg)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _set_status(self, text: str, player: "int | None" = None) -> None:
        if self._status_label is None:
            return
        if player == PLAYER_1:
            color = UI.TURN_COLOR_P1
        elif player == PLAYER_2:
            color = UI.TURN_COLOR_P2
        else:
            color = UI.STATUS_COLOR
        self._status_label.configure(text=text, fg=color)
        log.debug("Status bar: %r", text)

    def _fit_window(self) -> None:
        self.update_idletasks()
        w  = max(self.winfo_reqwidth(), self._min_width)
        h  = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = max(0, (sw - w) // 2)
        y  = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _center_dialog(self, dlg: tk.Toplevel) -> None:
        dlg.update_idletasks()
        pw = self.winfo_width()
        ph = self.winfo_height()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        w  = dlg.winfo_reqwidth()
        h  = dlg.winfo_reqheight()
        x  = px + (pw - w) // 2
        y  = py + (ph - h) // 2
        dlg.geometry(f"+{x}+{y}")
