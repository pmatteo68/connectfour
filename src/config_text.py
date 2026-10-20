"""All user-visible text for Connect Four -- change here to localise or rebrand."""

from sw_metadata import getSWName, getVersion
from config_game import (
    NUM_COLS_DEFAULT,
    NUM_ROWS_DEFAULT,
    CONNECT_LENGTH_DEFAULT,
    NUM_DISCS_PER_PLAYER_DEFAULT,
    NUM_PLAYERS,
)
import ai_engine

# -- Window -------------------------------------------------------------------
WINDOW_TITLE = getSWName() + " v. " + getVersion()

# -- Start screen -------------------------------------------------------------
START_TITLE         = getSWName()
def make_start_subtitle(connect_length):
    return "Drop your disc, connect " + str(connect_length) + " in a row!"

START_SUBTITLE = make_start_subtitle(CONNECT_LENGTH_DEFAULT)
START_ENGINE_LABEL  = "AI engine:"
START_WHO_FIRST     = "Who goes first?"
START_FIRST_HUMAN   = "  Human  "
START_FIRST_AI      = "  Machine  "

START_COLS_LABEL    = "Columns:"
START_ROWS_LABEL    = "Rows:"
START_CONNECT_LABEL = "Connect:"
START_DISCS_LABEL   = "Discs/player:"

def make_rules_hint(num_cols, num_rows, connect_length, num_discs_per_player):
    return (
        str(num_cols) + " cols  |  "
        + str(num_rows) + " rows  |  "
        + "connect " + str(connect_length) + "  |  "
        + str(num_discs_per_player) + " discs each"
    )

# -- Buttons ------------------------------------------------------------------
BTN_START     = "  Start Game  "
BTN_CLOSE     = "  Close  "
BTN_NEW_GAME  = "New Game"
BTN_SAVE_GAME = "Save Game"
BTN_LOAD_GAME = "Load Game"
BTN_AUTOPLAY  = "  Auto Play  "
BTN_EXIT      = "Exit"
BTN_QUIT      = "Quit"

# -- Status messages ----------------------------------------------------------
STATUS_HUMAN_TURN     = "Your turn -- click a column to drop your disc"
STATUS_HUMAN_COL_HINT = "Column {col} selected -- click again to drop"
STATUS_AI_TURN        = "Machine is thinking..."
STATUS_ANIMATING      = "..."

# -- Player names (used in status bar, stats, and chart) ----------------------
PLAYER_1_NAME = "Player 1"
PLAYER_2_NAME = "Player 2"
PLAYER_HUMAN  = "Human"
PLAYER_AI     = "Machine"

# -- Phase / turn header labels -----------------------------------------------
TURN_HEADER_P1 = "Player 1's turn"
TURN_HEADER_P2 = "Player 2's turn"

# -- Game-over messages -------------------------------------------------------
GAMEOVER_P1_WINS  = "Player 1 wins!"
GAMEOVER_P2_WINS  = "Player 2 wins!"
GAMEOVER_HUMAN_WINS = "You win!"
GAMEOVER_AI_WINS    = "Machine wins!"
GAMEOVER_DRAW       = "Draw -- board full!"

# -- Autoplay handoff splash (auto-dismiss, no button) ------------------------
AUTOPLAY_SPLASH_THINKING = "Machine is thinking..."

# -- Menu labels --------------------------------------------------------------
MENU_GAME  = "Game"
MENU_NEW   = "New Game"
MENU_SAVE  = "Save Game..."
MENU_LOAD  = "Load Game..."
MENU_QUIT  = "Quit"
MENU_HELP  = "Help"
MENU_RULES = "Rules"
MENU_ABOUT = "About..."

# -- Dialog messages ----------------------------------------------------------
MSG_NO_GAME      = "No game in progress."
MSG_SAVED        = "Game saved to:\n{path}"
MSG_SAVE_ERROR   = "Could not save game:\n{err}"
MSG_LOAD_ERROR   = "Could not load game:\n{err}"
MSG_COL_FULL     = "That column is full -- please choose another."
SAVE_FILETYPE    = "Connect Four saved games (*.json)"

# -- Rules text ---------------------------------------------------------------
RULES_TEXT = (
    getSWName() + "  --  Rules\n\n"
    "Two players alternate dropping colored discs into the grid.\n"
    "Discs fall to the lowest empty cell in the chosen column.\n\n"
    "The first player to form a line of "
    + str(CONNECT_LENGTH_DEFAULT) + " discs --\n"
    "horizontal, vertical, or diagonal -- wins.\n\n"
    "The game is a draw if the board fills completely\n"
    "or both players exhaust their disc quota.\n\n"
    "Default board: " + str(NUM_COLS_DEFAULT) + " columns x "
    + str(NUM_ROWS_DEFAULT) + " rows, "
    + str(NUM_DISCS_PER_PLAYER_DEFAULT) + " discs per player."
)

# -- About dialog -------------------------------------------------------------
ABOUT_TITLE = "About " + getSWName()
ABOUT_SUBTITLE = getSWName()
ABOUT_BODY  = (
    getSWName() + " v. " + getVersion() + "\n\n"
    "A classic strategy game.\n\n"
    "AI: " + ai_engine.get_name() + "."
)

# -- Stats window -------------------------------------------------------------
STATS_TITLE                 = "Game Summary"
STATS_SECTION_RESULT        = "RESULT"
STATS_SECTION_MOVES         = "MOVES"
STATS_SECTION_TIMING        = "TIMING"
STATS_SECTION_BOARD         = "BOARD"

STATS_WINNER_LABEL          = "Winner"
STATS_WINNER_P1             = PLAYER_1_NAME
STATS_WINNER_P2             = PLAYER_2_NAME
STATS_WINNER_HUMAN          = PLAYER_HUMAN
STATS_WINNER_AI             = PLAYER_AI
STATS_WINNER_DRAW           = "Draw"

STATS_ROW_MOVES_P1          = PLAYER_1_NAME + " moves"
STATS_ROW_MOVES_P2          = PLAYER_2_NAME + " moves"
STATS_ROW_TOTAL_MOVES       = "Total moves"
STATS_ROW_WINNING_MOVE      = "Winning move"
STATS_ROW_BOARD_COVERAGE    = "Board coverage"
STATS_ROW_AVG_TIME_P1       = PLAYER_1_NAME + " avg time"
STATS_ROW_AVG_TIME_P2       = PLAYER_2_NAME + " avg time"
STATS_DURATION_LABEL        = "Game duration"
STATS_NA                    = "--"

STATS_CHART_P1_LABEL        = PLAYER_1_NAME
STATS_CHART_P2_LABEL        = PLAYER_2_NAME
STATS_CHART_X_LABEL         = "Move #"
STATS_CHART_Y_LABEL         = "Position advantage (P1)"
STATS_CHART_ZERO_LABEL      = "Equal"
