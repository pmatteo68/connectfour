"""
Game logic configuration for Connect Four.
All gameplay-affecting parameters live here.

Hard limits on board parameters:
  NUM_COLS_MAX <= 12: each skin defines CELL_SIZE for the canvas; very wide
    boards may overflow the window unless CELL_SIZE is reduced in the skin.
    At 12 cols x default CELL_SIZE=64 + 2*BOARD_PADDING=24 the canvas is
    816 px wide, comfortably below any modern display.
  NUM_ROWS_MAX <= 10: similarly constrained by canvas height.  At 10 rows the
    canvas height is about 712 px (HEADER_HEIGHT + 10*CELL_SIZE + 2*BOARD_PADDING);
    exceeding that risks clipping on low-res displays.
  CONNECT_LENGTH_MAX <= NUM_COLS_DEFAULT and <= NUM_ROWS_DEFAULT: a winning
    strip longer than the shortest board dimension makes winning impossible and
    turns the game into a draw-fest. Values > 5 are rarely useful in practice.
  NUM_DISCS_PER_PLAYER_MAX <= (NUM_COLS_MAX * NUM_ROWS_MAX) // NUM_PLAYERS:
    each player can place at most half the cells; exceeding that is nonsensical.
    At max board (12x10=120 cells) the theoretical max is 60 per player.

Structural constant: only 2 players are supported. The constant NUM_PLAYERS=2
is referenced wherever the code relies on exactly two players.
"""

# -- Number of players (structural constant; only 2 is supported) ---------------
NUM_PLAYERS = 2

# -- Board column parameters ---------------------------------------------------
NUM_COLS_MIN     = 4
NUM_COLS_MAX     = 12
NUM_COLS_DEFAULT = 7

# -- Board row parameters ------------------------------------------------------
NUM_ROWS_MIN     = 4
NUM_ROWS_MAX     = 10
NUM_ROWS_DEFAULT = 6

# -- Winning strip length ------------------------------------------------------
CONNECT_LENGTH_MIN     = 3
CONNECT_LENGTH_MAX     = 5
CONNECT_LENGTH_DEFAULT = 4

# -- Discs per player ----------------------------------------------------------
# Standard game: 21 per player on a 7x6 board (42 cells total, fully fillable).
# Minimum is enough to theoretically win; maximum is half the largest board.
NUM_DISCS_PER_PLAYER_MIN     = 10
NUM_DISCS_PER_PLAYER_MAX     = 60
NUM_DISCS_PER_PLAYER_DEFAULT = 21

# -- AI engine -----------------------------------------------------------------
AI_ENGINE = "minimax_alphabeta"   # module name inside ai_engines/

# -- AI animation timing -------------------------------------------------------
AI_THINK_DELAY_MS       = 400   # pause before the AI drop animation begins
AI_INTER_MOVE_PAUSE_MS  = 300   # pause after each committed move before next phase

# -- Disc drop animation -------------------------------------------------------
# Each step moves the falling disc down one row.
DROP_ANIM_ENABLED   = True
DROP_ANIM_STEP_MS   = 50        # ms per row during the fall animation

# -- Win flash animation -------------------------------------------------------
WIN_FLASH_COUNT       = 6       # number of on/off half-cycles
WIN_FLASH_INTERVAL_MS = 150     # ms per half-cycle (on OR off)

# -- Autoplay (testing / demo) -------------------------------------------------
# AUTOPLAY is no longer read at runtime; autoplay mode is now activated by the
# "Auto Play" button on the start screen. The flag is kept here for reference only.
# AUTOPLAY = False
AUTOPLAY_MOVE_DELAY_MS     = 600    # delay before each autoplay move
AUTOPLAY_HANDOFF_SPLASH_MS = 1500   # how long the auto-dismiss splash stays visible

# -- Start-screen defaults (pre-selection on the start screen) -----------------
# "human" = human goes first (as Player 1); "ai" = AI goes first (as Player 1)
DEFAULT_FIRST_PLAYER = "human"
