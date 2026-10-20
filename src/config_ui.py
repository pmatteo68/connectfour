"""
UI skin selector.
Set SKIN to the name of a module inside src/skins/ to switch the active skin.
"""
import importlib
import logging
import random

logger = logging.getLogger(__name__)

SKINS = (
    "default",       # Default         - classic blue board, red vs yellow
    "midnight",      # Midnight        - near-black, neon electric discs
    "sunset",        # Sunset          - amber/coral warm tones
    "ocean",         # Ocean           - deep navy, teal and cyan
    "forest",        # Forest          - mossy greens, bark browns
    "candy",         # Candy           - pastel bubblegum palette
    "vivid_1",       # Vivid-1         - full-saturation primaries on white
    "vivid_2",       # Vivid-2         - electric cobalt+cyan on pale blue
    "mint_gray",     # Mint-Gray       - cool gray canvas, mint accents
    "black_and_white", # B&W           - pure monochrome grayscale
)

# Active skin -- replace "default" with any name above, or use "random"
SKIN = "default"

try:
    SKIN = random.choice(SKINS) if SKIN == "random" else SKIN
    _skin = importlib.import_module(f"skins.{SKIN}")
except (ImportError, ValueError) as _err:
    logger.error("Skin '%s' could not be loaded (%s) -- falling back to default", SKIN, _err)
    from skins import default as _skin


def get_name() -> str:
    return _skin.SKIN_NAME


# Layout constants not defined per-skin; skins may override any of these.
_DEFAULTS = {
    "START_ENGINE_LABEL_PADY_TOP": 2,
    "RULES_WRAP_WIDTH":            400,
    "RULES_LABEL_PADX":            24,
    "RULES_LABEL_PADY":            16,
    "RULES_CLOSE_PADY_BOT":        16,
    "STATS_SECTION_PACK_PADY_TOP": 8,
    "STATS_SECTION_PACK_PADY_BOT": 2,
    "STATS_CLOSE_BTN_PADY_TOP":    8,
    "STATS_CHART_PACK_PADY_TOP":   8,
    "STATS_TABLE_PADY_TOP":        4,
    "STATS_TABLE_PADY_BOT":        2,
    "STATS_TABLE_COL_PAD":         24,
    "STATS_TABLE_DIVIDER_PADY":    3,
    "STATUS_BTN_FONT":             ("Helvetica", 9),
    "MIN_WINDOW_WIDTH":            680,
}


def __getattr__(name: str):
    try:
        return getattr(_skin, name)
    except AttributeError:
        if name in _DEFAULTS:
            return _DEFAULTS[name]
        raise
