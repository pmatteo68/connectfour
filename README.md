# Connect Four

> **Version:** 1.0.0
> **Date:** Oct. 20, 2026
> **Author:** Matteo P.
> **URL:** https://github.com/pmatteo68/connectfour
---

## Abstract

A desktop implementation of Connect Four built with Python and Tkinter.
Two players take turns dropping colored discs into a vertical grid.
Each disc falls to the lowest empty cell in the chosen column.
The first player to form a line of four (or more, as configured) consecutive discs --
horizontally, vertically, or diagonally -- wins.
If the board fills before either player connects, the game is a draw.

The computer opponent uses Minimax search with alpha-beta pruning.
An autoplay mode runs a fully unattended game from start to finish so
you can observe the complete flow, including the end-of-game statistics.

The game runs fully offline with no dependency on external services.

---

## Setup

### Prerequisites

Python is not assumed to be on the system PATH. The path to the Python
interpreter is configured in `bin\env.cmd` (Windows) or `bin/env.sh`
(Unix/macOS). Edit those files if your Python installation is in a
different location than the default recorded there before running any
script.

### 1. Create the virtual environment (once)

Open a terminal inside the `v1.0.0` directory and run the setup script.

**Windows:**

```
create_env.cmd
```

**Unix / macOS:**

```
bash create_env.sh
```

The script calls `bin\env` (or `bin/env.sh`) to put Python on the PATH,
then creates a virtual environment named `myenv`, activates it, and
installs the dependencies listed in `requirements.txt`.
If the virtual environment already exists the script simply activates it
without reinstalling anything.

### 2. Launch the game

Run the play script every time you want to start the game.

**Windows:**

```
play.cmd
```

**Unix / macOS:**

```
bash play.sh
```

The play script calls `bin\env` (or `bin/env.sh`) to set the Python PATH,
activates the virtual environment, and runs `src/main.py`.

### Optional: open an environment-ready shell (Windows only)

```
open_env.cmd
```

This opens a new CMD window with Python and the virtual environment
already on the PATH so you can run arbitrary Python commands manually,
inspect logs, or launch the game with `python src/main.py`.

---

## How to Play

### Start screen

Before a game begins you choose:

- **Who goes first** -- Human or Machine. When the human goes first the
  human is Player 1 (red discs by default). When the machine goes first
  the machine is Player 1 and the human is Player 2 (yellow discs by
  default).
- **Columns** -- the number of columns in the grid (default 7).
- **Rows** -- the number of rows in the grid (default 6).
- **Connect** -- the length of the winning strip (default 4).
  This is the "4" in "Connect Four"; you can change it to 3, 4, or 5.
- **Discs/player** -- the maximum number of discs each player may place
  (default 21). If both players exhaust their quota before anyone wins,
  the game is a draw. On the standard 7x6 board 21 discs per player is
  enough to fill the entire board, so the draw condition is equivalent to
  a full board.

The parameters chosen here are shown as a compact summary line
("7 cols | 6 rows | connect 4 | 21 discs each") that updates live as
you adjust the dropdowns.

Click **Start Game** to begin, or **Load Game** to resume a previously
saved game.

### Playing

On your turn the board is active. Hover the mouse over the grid to see
a ghost disc show the column you are pointing at. Click to drop your
disc into that column. The disc animates downward to the lowest empty
cell.

If the column you click is already full a message tells you to choose
another column.

The status bar at the bottom of the window tells you whose turn it is
and what the game expects you to do next.

### Computer turn

When it is the machine's turn the board is disabled and the status bar
shows "Machine is thinking...". The AI runs on a background thread so
the UI stays responsive. After a brief configurable pause the disc
drops with the same animation as a human move.

### Winning and draws

When a player connects the required number of discs in a row the
winning cells flash several times, the status bar shows the game result,
and after a short delay the **Game Summary** window appears.

A draw occurs if the board fills completely or both players exhaust
their disc quota without forming a winning line.

### Game Summary window

The summary window appears at the end of every game. It shows:

- **Result** -- who won (or draw).
- **Moves** -- moves by each player and the total.
- **Board** -- board coverage (percentage of cells used) and the number
  of the winning move.
- **Timing** -- total game duration and average time per move for each
  player.
- **Position advantage chart** (requires matplotlib) -- a line chart
  showing how the heuristic position score (from Player 1's perspective)
  evolved after each move. Positive values indicate an advantage for
  Player 1; negative values indicate an advantage for Player 2.
  The chart fills the positive area in Player 1's color and the negative
  area in Player 2's color so the momentum shifts are immediately visible.

The chart section is omitted silently if matplotlib is not installed.

### Saving and loading

Use the **Game** menu or the **Save Game** button in the status bar to
save the current game state to a JSON file at any point during play.
Load a saved game via the **Game** menu or the **Load Game** button on
the start screen. The loaded game resumes exactly where it was left off
with all previously placed discs visible on the board.

Saving a game that is already over is supported (for archival).
The stats window is not shown for loaded completed games because timing
data for moves played before the save are not preserved in the file.

---

## Configuration

All user-tunable parameters are isolated in dedicated files under
`src/`. No other file needs to be edited for typical customisation.

| File | Purpose |
|---|---|
| `src/config_game.py` | Gameplay rules: board dimension bounds and defaults, connect length, discs per player, AI algorithm selection, all animation and timing parameters, autoplay mode |
| `src/config_ui.py` | Active skin selection |
| `src/config_text.py` | Every user-visible string: button labels, menu items, status messages, dialog text, chart labels |
| `src/log_config.py` | Logging: output file path, console echo toggle, global log level |
| `bin\env.cmd` / `bin/env.sh` | Python installation path and environment variables |

### Gameplay parameters (config_game.py)

Every numeric constant in the game is a named variable in this file;
nothing is hardcoded anywhere in the source. Parameters include:

- **NUM_PLAYERS = 2** -- structural constant. The code relies on exactly
  two players; no other value is supported, but the constant is named
  and used wherever the code depends on the player count being two.
- **Board bounds** -- minimum, maximum, and default values for columns
  (4-12, default 7), rows (4-10, default 6), connect length (3-5,
  default 4), and discs per player (10-60, default 21). The hard limits
  and the reasoning behind them are documented as comments at the top of
  the file. Raising a maximum beyond its current value may require
  corresponding updates to skin files (see the Tech Notes section).
- **AI_ENGINE** -- the name of the engine module inside `src/ai_engines/`
  to load. Change this to switch the active AI without touching any
  other file.
- **AI_THINK_DELAY_MS** -- pause (ms) before the AI's disc drop animation
  begins. Gives the human time to see the board before the machine moves.
- **AI_INTER_MOVE_PAUSE_MS** -- pause (ms) after each committed move
  before the next phase begins.
- **DROP_ANIM_ENABLED** -- whether discs animate falling (True) or
  appear instantly (False).
- **DROP_ANIM_STEP_MS** -- duration (ms) of each row-step during the
  fall animation. Smaller = faster fall.
- **WIN_FLASH_COUNT** -- number of on/off half-cycles in the winning
  cell flash.
- **WIN_FLASH_INTERVAL_MS** -- duration (ms) of each half-cycle.
- **AUTOPLAY** -- when True both players are controlled by the AI with
  no human interaction (see the Autoplay section below).
- **AUTOPLAY_MOVE_DELAY_MS** -- pause (ms) before each move in autoplay
  mode.
- **AUTOPLAY_HANDOFF_SPLASH_MS** -- reserved timing constant for
  autoplay handoff pauses.
- **DEFAULT_FIRST_PLAYER** -- which option is pre-selected on the start
  screen ("human" or "ai").

### Visual themes (config_ui.py)

Set the `SKIN` constant to any of the names listed in the Available Skins
section, or use `"random"` to pick a different skin on every launch.
If a named skin cannot be loaded the application falls back to the
default skin automatically.

### Text and labels (config_text.py)

Every word the user sees lives in this file. Edit it to translate the
game, rebrand it, or adjust any label without touching the rest of the
code.

---

## Tech Notes

- **Language / GUI**: Python 3.8+, Tkinter (bundled with CPython). On
  Linux, install `python3-tk` via the package manager if it is not
  already present.

- **Threading**: AI move computation runs on a background daemon thread
  so the UI stays responsive while the engine thinks. The result is
  posted back to the main thread via `after(0, callback)` -- the only
  safe way to call Tkinter from a non-main thread. In autoplay mode two
  independent engine instances run, one per player, so their internal
  search state never interferes.

- **Board dimension ceilings**: each skin defines a fixed `CELL_SIZE`.
  Very wide or tall boards may overflow the window if `WINDOW_WIDTH` or
  the canvas height in the skin is not also increased. The hard limits
  and the reasoning behind them are documented as comments at the top of
  `src/config_game.py`. Read those before raising any maximum.

- **Connect length ceiling**: a winning strip longer than the shortest
  board dimension makes winning impossible on small boards and turns
  every game into a draw. `CONNECT_LENGTH_MAX = 5` is the enforced
  ceiling; values beyond 5 are rarely useful in practice.

- **Trajectory chart**: an optional matplotlib figure embedded in the
  stats window. The Y axis shows `evaluate_position()` from Player 1's
  perspective after each move. If matplotlib is not installed the chart
  section is omitted; the rest of the stats window is unaffected. The
  chart can also be disabled in any skin by setting
  `STATS_SHOW_CHART = False`.

- **Save / load format**: game state is stored as a human-readable JSON
  file. The format version is embedded in every file; a mismatch raises
  a clear error at load time.

- **ASCII policy**: every source file and this README contain only
  7-bit ASCII characters. This ensures compatibility with all terminals,
  editors, and diff tools regardless of locale settings.

---

## Autoplay Mode

The `AUTOPLAY` flag in `src/config_game.py` (default False) runs the
entire game without any human interaction. Useful for:

- Watching the complete game flow end-to-end including the win flash
  and the stats window.
- Stress-testing an AI engine implementation.
- Verifying that a new skin renders all states correctly.

When autoplay is enabled:

- Both players are controlled by two independent instances of the
  configured AI engine. The instances are created fresh at the start of
  each game via `ai_engine.create_fresh_instance()` so they never share
  internal search state.
- The start screen still appears so you can adjust parameters; clicking
  Start Game begins the automated run immediately.
- Each move is preceded by a configurable delay (`AUTOPLAY_MOVE_DELAY_MS`)
  so you can follow the game visually.
- All statistics are collected normally, so the Game Summary window at
  the end is fully populated with real data.

Set `AUTOPLAY = False` to return to normal interactive play.

---

## AI Engine Plugin System

The AI logic is fully encapsulated behind a plugin interface. The active
engine is selected with a single line in `src/config_game.py`:

```
AI_ENGINE = "minimax_alphabeta"
```

The value is the name of a module inside `src/ai_engines/`. The facade
`src/ai_engine.py` loads it at runtime via `importlib`. The rest of the
codebase imports only `ai_engine` and never depends on a specific
implementation.

### Contract

Every engine module must contain a class that subclasses
`ConnectFourAIEngine` (from `ai_engines/base.py`) and implements the
required methods, plus a module-level factory function named `create`.

| Method | What it must do |
|---|---|
| `get_name() -> str` | Return a short human-readable name (shown on the start screen and in logs) |
| `_compute_next_move(board, player, num_cols, num_rows, connect_length) -> int` | Compute and return the column index (0-based) to play next |
| `reset() -> None` | Reset all internal state so the engine is ready for a fresh game |

The public `next_move()` method is implemented by the base class and
must NOT be overridden. It calls `_compute_next_move()`, validates that
the returned column is in range and not full, falls back to the first
valid column if the implementation returns an invalid value (with a
warning log), and returns the result. This safety net applies to every
engine automatically.

### Board representation

The board is a list of lists: `board[row][col]`.

- Row 0 is the **top** of the visual board.
- Row `num_rows - 1` is the **bottom** (where discs accumulate).
- Cell values: `0` = empty, `1` = Player 1, `2` = Player 2.

Discs fall from row 0 downward; the lowest empty row in a column is
where the next disc will land.

### Writing a new engine -- step by step

1. Create `src/ai_engines/my_engine.py`.

2. Import the base class and subclass it:

   ```python
   from .base import ConnectFourAIEngine

   class MyEngine(ConnectFourAIEngine):
       ...
   ```

3. Implement `get_name()`:

   ```python
   def get_name(self) -> str:
       return "My Engine"
   ```

4. Implement `reset()` -- clear any internal state that accumulates
   across moves (transposition tables, move history caches, etc.):

   ```python
   def reset(self) -> None:
       self._transposition_table = {}
   ```

5. Implement `_compute_next_move(board, player, num_cols, num_rows,
   connect_length)`:

   - `board` is a snapshot (safe to mutate; it is a copy).
   - `player` is the player whose move to compute: `1` or `2`.
   - The opponent is `3 - player` (since `NUM_PLAYERS = 2`).
   - Return an integer column index in `range(num_cols)` for a column
     that is not full. The base class will fall back to the first valid
     column with a warning if an invalid index is returned.

   A minimal random engine:

   ```python
   import random
   from game_logic import get_valid_columns

   def _compute_next_move(self, board, player,
                          num_cols, num_rows, connect_length):
       valid = get_valid_columns(board, num_cols)
       return random.choice(valid)
   ```

6. Add the module-level factory at the bottom:

   ```python
   def create():
       return MyEngine()
   ```

7. Set `AI_ENGINE = "my_engine"` in `src/config_game.py`. No other file
   needs to change. The engine name from `get_name()` will appear on the
   start screen automatically.

### Useful helpers from game_logic.py

```python
from game_logic import (
    get_valid_columns,   # list of non-full column indices
    get_landing_row,     # lowest empty row in a column, or None if full
    find_winning_cells,  # None, or list of connect_length (row,col) tuples
    evaluate_position,   # heuristic score from a player's perspective
    OTHER_PLAYER,        # dict: OTHER_PLAYER[1] == 2, OTHER_PLAYER[2] == 1
    EMPTY, PLAYER_1, PLAYER_2,
)
```

A typical minimax engine will call `get_valid_columns` to enumerate
moves, `get_landing_row` to place a disc on a trial board, and
`find_winning_cells` to detect terminal states.

### Separate per-engine configuration

If your engine needs configuration constants, put them in a dedicated
file following the pattern used by the built-in engine:

```
src/ai_engines/my_engine_config.py
```

Import from there inside `my_engine.py`. This keeps tuning parameters
visible and separate from algorithmic logic.

### Available AI engines

| Name | Module | Strategy |
|---|---|---|
| Minimax Alpha-Beta | `minimax_alphabeta` | Depth-limited minimax with alpha-beta pruning. Evaluates all 4-length windows on the board and awards score bonuses for two-in-a-row, three-in-a-row, and winning positions. Move ordering (win-now first, block-opponent second, center-out third) improves pruning efficiency. Search depth and all score weights are configurable in `src/ai_engines/minimax_alphabeta_config.py`. |

---

## Skin Plugin System

The visual appearance is fully encapsulated behind a skin plugin
interface. The active skin is selected with a single line in
`src/config_ui.py`:

```
SKIN = "default"
```

The value is the name of a module inside `src/skins/`. If the module
cannot be loaded the default skin is used automatically.

### Writing a new skin

1. Copy `src/skins/default.py` to `src/skins/my_skin.py`.
2. Change `SKIN_NAME` near the top to a short descriptive label.
3. Edit colors, fonts, and dimension values to taste. Every constant in
   the default skin file must be present with the same name in your new
   file; do not remove any constant.
4. Set `SKIN = "my_skin"` in `src/config_ui.py`. No other file needs to
   change.

Key constants to understand when writing a skin:

| Constant | Meaning |
|---|---|
| `CELL_SIZE` | Width and height of each grid cell in pixels. Must equal `DISC_DIAMETER + 2 * DISC_MARGIN`. |
| `DISC_DIAMETER` | Diameter of each disc circle in pixels. |
| `DISC_MARGIN` | Gap between each disc edge and the cell boundary. |
| `BOARD_PADDING` | Pixel padding around the board frame on all sides. |
| `HEADER_HEIGHT` | Height of the ghost-disc drop zone above the board. |
| `BOARD_FRAME_COLOR` | Fill color of the board rectangle (the "board" itself). |
| `CELL_EMPTY_COLOR` | Fill color of an empty cell. |
| `PLAYER_1_COLOR` | Disc color for Player 1. |
| `PLAYER_2_COLOR` | Disc color for Player 2. |
| `PLAYER_1_GHOST_COLOR` | Hover ghost disc color for Player 1. |
| `PLAYER_2_GHOST_COLOR` | Hover ghost disc color for Player 2. |
| `WIN_FLASH_COLOR_P1` | Alternate color for Player 1's winning cells during the flash. |
| `WIN_FLASH_COLOR_P2` | Alternate color for Player 2's winning cells during the flash. |
| `STATS_SHOW_CHART` | Boolean; set to False to suppress the matplotlib chart in the stats window even when matplotlib is installed. |

### Available skins

| Name | Module | Description |
|---|---|---|
| Default | `default` | Classic blue board, red Player 1 vs yellow Player 2. |
| Midnight | `midnight` | Near-black canvas, neon electric discs, dark-mode feel. |
| Sunset | `sunset` | Amber and coral warm tones, gold accents. |
| Ocean | `ocean` | Deep navy canvas, cyan and teal discs. |
| Forest | `forest` | Mossy greens, bark browns, earthy palette. |
| Candy | `candy` | Soft pastel bubblegum palette. |
| Vivid-1 | `vivid_1` | Full-saturation primaries on white, high energy. |
| Vivid-2 | `vivid_2` | Electric cobalt and cyan on pale blue. |
| Mint-Gray | `mint_gray` | Cool gray canvas, mint-green accents. |
| Black-and-White | `black_and_white` | Pure monochrome grayscale, no color anywhere. |
| Random | `"random"` | Picks a different skin on every launch. |

---

## Debugging

### Log file

Every run appends to `connect_four.log` in the directory where the game
is launched (the `v1.0.0` directory when using the play scripts). The
log captures all DEBUG-level events by default: move decisions, AI
thread start/end, animation lifecycle, game-over transitions, and a
full game summary block at INFO level at the end of every game.

### Log level

The level is configured in `src/log_config.py` and can be overridden at
runtime by setting the `MEC_LOG_LEVEL` environment variable (already set
to `DEBUG` by `bin\env.cmd` / `bin/env.sh`). Valid values: `DEBUG`,
`INFO`, `WARNING`, `ERROR`, `CRITICAL`.

The start banner and game summary block are always logged at INFO level;
all other events are at DEBUG level so they can be filtered out by
setting the level to INFO for quieter output.

### Autoplay for end-to-end testing

Set `AUTOPLAY = True` in `src/config_game.py` to run a full game
without touching the mouse or keyboard. This is the fastest way to
verify that:

- The AI engine produces valid moves throughout the game.
- The win detection, flash animation, and stats window all work.
- A new skin renders every game state correctly.
- Save and load preserve all game state faithfully (save mid-autoplay,
  reload, and autoplay should continue seamlessly).

---

## Changelog

### 1.0.0 - 2026-10

- First release. Human vs. AI Connect Four with configurable board.
- Start screen with dropdowns for columns, rows, connect length, and
  discs per player; who-goes-first selector; live rules hint.
- Animated disc fall (row-by-row, configurable speed) and win-cell
  flash (configurable count and interval).
- Minimax with alpha-beta pruning AI; all weights and depth configurable
  in `src/ai_engines/minimax_alphabeta_config.py`.
- AI runs on a background thread; UI stays responsive during computation.
- Autoplay mode: two independent AI instances play a full game
  unattended end-to-end.
- Save / load game (JSON format with embedded format version).
- End-of-game statistics window: result, move counts, board coverage,
  winning move number, game duration, per-player average move time.
- Position advantage chart (requires matplotlib): heuristic score from
  Player 1's perspective after each move, with filled areas showing
  who was ahead and by how much.
- 10 visual skins plus random rotation; skin plugin system for adding
  new themes.
- AI engine plugin system for replacing or adding solver strategies.
- All gameplay parameters, all timings, all text labels, and all visual
  constants are configurable with no hardcoded magic numbers anywhere.
- Strict 7-bit ASCII policy throughout all source files and this README.
