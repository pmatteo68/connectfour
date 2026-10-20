"""
Configuration for the Minimax Alpha-Beta Connect Four engine.

SEARCH_DEPTH controls the number of half-moves (plies) the engine looks ahead.
Higher depth produces stronger play at the cost of computation time.

Typical depth vs. compute time on a standard desktop (7x6 board):
  depth=4  -- < 0.1 s  (very fast, moderate strength)
  depth=6  -- 0.1-0.5 s  (good balance)
  depth=7  -- 0.5-2 s    (strong; noticeable pause on first move)
  depth=8+ -- several seconds; use only if you don't mind waiting

CENTER_WEIGHT controls how much the engine values center-column placement.
The center columns of a Connect Four board have the most connectivity and
are typically the strongest opening moves.

SCORE_WIN, SCORE_THREE, SCORE_TWO are the raw heuristic weights per window.
Ratios matter more than absolute values: SCORE_WIN >> SCORE_THREE >> SCORE_TWO.

KILLER_MOVE_ENABLED: try immediately-winning and immediately-blocking moves
first during search to improve alpha-beta cutoffs (move ordering heuristic).
"""

SEARCH_DEPTH   = 6

CENTER_WEIGHT  = 3      # bonus score per center-column disc

SCORE_WIN      = 1000000
SCORE_THREE    = 100
SCORE_TWO      = 10

KILLER_MOVE_ENABLED = True
