"""Entry point for Connect Four."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# DPI awareness on Windows (must be called before Tkinter is imported)
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

import logging
import log_config
import sw_metadata as META

log_config.setup()
log = logging.getLogger(__name__)


def main() -> None:
    import config_game as CG
    import config_ui   as CUI
    import ai_engine   as AE

    log.info("=" * 60)
    log.info("%s  v. %s  --  starting", META.getSWName(), META.getVersion())
    log.info("Python %s  |  platform: %s", sys.version.split()[0], sys.platform)
    log.info("AI: %s  |  Skin: %s", AE.get_name(), CUI.get_name())
    log.info(
        "Board defaults: %dx%d  connect=%d  discs=%d  (autoplay via start screen)",
        CG.NUM_COLS_DEFAULT, CG.NUM_ROWS_DEFAULT,
        CG.CONNECT_LENGTH_DEFAULT, CG.NUM_DISCS_PER_PLAYER_DEFAULT,
    )
    log.info("=" * 60)

    from ui_main import App
    app = App()
    app.mainloop()

    log.info("=" * 60)
    log.info("%s  --  exited normally", META.getSWName())
    log.info("=" * 60)


if __name__ == "__main__":
    main()
