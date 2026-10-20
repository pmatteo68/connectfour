"""Default skin -- classic blue board, red vs yellow discs."""

SKIN_NAME = "Default"

# -- Window -------------------------------------------------------------------
WINDOW_WIDTH         = 680
WINDOW_HEIGHT        = 600
LAYOUT_INIT_DELAY_MS = 10

# -- General background -------------------------------------------------------
BG_COLOR             = "#f0f4f8"
PANEL_BG             = "#f0f4f8"
PANEL_DIVIDER_COLOR  = "#c0ccd8"

# -- Board canvas -----------------------------------------------------------
# CELL_SIZE must equal DISC_DIAMETER + 2 * DISC_MARGIN for consistent spacing.
# At DISC_DIAMETER=50 and DISC_MARGIN=7 the formula gives CELL_SIZE=64.
DISC_DIAMETER        = 50
DISC_MARGIN          = 7
CELL_SIZE            = 64      # == DISC_DIAMETER + 2 * DISC_MARGIN
BOARD_PADDING        = 24      # outer margin around the full grid
HEADER_HEIGHT        = 64      # height of the ghost-disc drop zone (== CELL_SIZE)

BOARD_FRAME_COLOR    = "#1565c0"   # classic Connect Four blue frame
BOARD_FRAME_PAD      = 6          # inner padding of the blue frame rectangle
CELL_EMPTY_COLOR     = "#e8edf2"
CELL_OUTLINE_COLOR   = "#ffffff"
CELL_OUTLINE_WIDTH   = 2

PLAYER_1_COLOR       = "#e53935"   # red
PLAYER_2_COLOR       = "#fdd835"   # yellow
PLAYER_1_GHOST_COLOR = "#f48fb1"   # light red for hover ghost
PLAYER_2_GHOST_COLOR = "#fff176"   # light yellow for hover ghost
GHOST_OUTLINE_WIDTH  = 2
GHOST_OUTLINE_COLOR  = "#888888"

WIN_FLASH_COLOR_P1   = "#ff8a80"   # bright flash for player 1 winning cells
WIN_FLASH_COLOR_P2   = "#ffff8d"   # bright flash for player 2 winning cells

DISC_OUTLINE_WIDTH   = 1
DISC_OUTLINE_COLOR   = "#00000033"  # very faint outline on placed discs (tk may ignore alpha)
# Use a fallback solid color since tkinter does not support alpha in color strings:
DISC_OUTLINE_COLOR   = "#888888"

# -- Column hover highlight ---------------------------------------------------
COL_HOVER_COLOR      = "#ffffff44"
COL_HOVER_ALPHA_COLOR = "#dde5f0"  # visible tint on hover column background

# -- Status bar ---------------------------------------------------------------
STATUS_BAR_HEIGHT    = 44
STATUS_BG            = "#dde5f0"
STATUS_FONT          = ("Helvetica", 12)
STATUS_COLOR         = "#1a3a5c"
STATUS_LABEL_PADX    = 12
STATUS_BTN_PADX      = 4
STATUS_BTN_PADX_END  = 8
STATUS_BTN_PADY      = 4
STATUS_BTN_FONT      = ("Helvetica", 9)

# -- Side panel (player info strip) ------------------------------------------
SIDE_PANEL_WIDTH     = 0    # set to 0 to disable the side panel; info fits in status bar

# -- Buttons ------------------------------------------------------------------
BTN_BG          = "#1565c0"
BTN_FG          = "#ffffff"
BTN_ACTIVE_BG   = "#1976d2"
BTN_FONT        = ("Helvetica", 11, "bold")
BTN_RELIEF      = "flat"
BTN_PADX        = 14
BTN_PADY        = 6
BTN_BD          = 0
MENU_BD         = 0

# -- Start screen -------------------------------------------------------------
START_TITLE_FONT      = ("Helvetica", 30, "bold")
START_TITLE_COLOR     = "#1565c0"
START_SUBTITLE_FONT   = ("Helvetica", 14)
START_SUBTITLE_COLOR  = "#455a64"
START_ENGINE_PADY     = 8
START_TITLE_PADY      = 6
START_SUBTITLE_PADY   = 22
START_WHO_FIRST_PADY  = 14
START_BTN_PADX        = 8
START_RULES_PADY      = 18
START_BOTTOM_ROW_PADY = 14
START_SECTION_PADY    = 16
START_ENGINE_LABEL_PADY_TOP = 2

LABEL_FONT  = ("Helvetica", 11)
LABEL_COLOR = "#455a64"

# -- Menu colors --------------------------------------------------------------
MENU_FG              = "#1a3a5c"

# -- Turn indicator in status bar ---------------------------------------------
TURN_COLOR_P1   = "#e53935"
TURN_COLOR_P2   = "#b79400"
TURN_COLOR_DRAW = "#607d8b"

# -- About / Rules dialogs ----------------------------------------------------
ABOUT_WRAP_WIDTH          = 380
ABOUT_PADX                = 24
ABOUT_PADY                = 8
ABOUT_TITLE_PADY_TOP      = 20
ABOUT_DIVIDER_PADX        = 20
ABOUT_HEADER_DIVIDER_PADY = 10
ABOUT_BODY_DIVIDER_PADY   = 6
ABOUT_CLOSE_PADY_TOP      = 10
ABOUT_CLOSE_PADY_BOT      = 20
BOARD_BORDER              = "#b0bec5"

RULES_WRAP_WIDTH  = 400
RULES_LABEL_PADX  = 24
RULES_LABEL_PADY  = 16
RULES_CLOSE_PADY_BOT = 16

# -- Stats window -------------------------------------------------------------
STATS_WINDOW_WIDTH    = 540
STATS_PADDING         = 18
STATS_TITLE_PADY_BOT  = 10
STATS_CLOSE_SPACER_H  = 6
STATS_SECTION_BG      = BTN_BG
STATS_SECTION_FG      = BTN_FG
STATS_SECTION_FONT    = ("Helvetica", 10, "bold")
STATS_SECTION_PADY    = 6
STATS_ROW_LABEL_FONT  = ("Helvetica", 11)
STATS_ROW_VALUE_FONT  = ("Helvetica", 11, "bold")
STATS_ROW_LABEL_COLOR = STATUS_COLOR
STATS_ROW_VALUE_COLOR = "#1565c0"
STATS_ROW_PADX        = 14
STATS_ROW_PADY        = 2
STATS_DIVIDER_COLOR   = BOARD_BORDER
STATS_TITLE_FONT      = START_TITLE_FONT
STATS_TITLE_COLOR     = START_TITLE_COLOR
STATS_DELAY_MS        = 800

STATS_TABLE_PADY_TOP    = 4
STATS_TABLE_PADY_BOT    = 2
STATS_TABLE_COL_PAD     = 24
STATS_TABLE_DIVIDER_PADY = 3

STATS_SHOW_CHART        = True
STATS_CHART_HEIGHT_IN   = 2.6
STATS_CHART_DPI         = 90
STATS_CHART_BG          = BG_COLOR
STATS_CHART_P1_COLOR    = "#e53935"
STATS_CHART_P2_COLOR    = "#fdd835"
STATS_CHART_LINE_COLOR  = "#455a64"
STATS_CHART_ZERO_COLOR  = "#b0bec5"
STATS_CHART_GRID_COLOR  = "#d0dae6"
STATS_CHART_FILL_ALPHA  = 0.20
STATS_CHART_LINE_WIDTH  = 1.8
STATS_CHART_ZERO_WIDTH  = 1.0
STATS_CHART_FONT_SIZE   = 7
STATS_CHART_LABEL_PAD   = 2
STATS_CHART_TICK_LENGTH = 3
STATS_CHART_TICK_PAD    = 2
STATS_CHART_SPINE_WIDTH = 0.8
STATS_CHART_GRID_WIDTH  = 0.5
STATS_CHART_LAYOUT_PAD  = 0.6

STATS_SECTION_PACK_PADY_TOP = 8
STATS_SECTION_PACK_PADY_BOT = 2
STATS_CLOSE_BTN_PADY_TOP    = 8
STATS_CHART_PACK_PADY_TOP   = 8
