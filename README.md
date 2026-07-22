# Jane Street July 2026: 'Pent-Up' Frustration 3 / Knight Moves 7

My solution to the [July 2026 Jane Street puzzle](https://www.janestreet.com/puzzles/archive/).

**Answer: 33609** (checkpoint interval K = 7, path length 54 moves)

## The puzzle

An 8x8 board is tiled by the 12 pentominoes plus a 2x2 tetromino into 13 regions.
Each region gets one "tower" (an extra unit cube on one of its squares), placed by
the solver. A knight starts at the bottom-left square with score 0 and makes 3D
knight moves: a legal move travels 0 units in one dimension, 1 in another, and 2
in the third, where the third dimension is altitude (height 1 for normal squares,
height 2 for towers). It never revisits a square and stops the moment it has
visited all 13 towers.

On move N the score changes by the move type: +N on a level move, xN moving up,
/N moving down (only legal if the score divides evenly). The knight recorded its
score every 3 moves through move 18, then every K moves for some unknown K > 3.
Eleven recorded scores are shown on the board. The task is to reconstruct the
unique path, then sum, over all unvisited squares, the scores of their orthogonally
adjacent visited squares.

## Approach

This is constraint-guided backtracking (DFS), not dynamic programming: the state
includes the full set of visited squares and the partial tower assignment, so
subproblems never repeat and there is nothing to memoize. The search is fast
because the constraints are brutal:

- Every checkpoint move must land exactly on a clue square with exactly the clue
  score, and clue squares cannot be visited at non-checkpoint times.
- Down moves require exact divisibility by N.
- Tower placement is decided lazily during the search: a square's height is fixed
  the first time the knight interacts with it, subject to one tower per region,
  and any region that runs out of unvisited squares without a tower kills the branch.
- A lookahead pruner enumerates the exact set of scores reachable in the moves
  remaining before the next checkpoint (a small set-valued sweep over move
  operations, ignoring position) and prunes if no remaining clue value is reachable.
  A relaxed all-pairs move-distance table prunes positionally.

The path length L must satisfy 18 + 5K <= L < 18 + 6K, since exactly five scores
were recorded after move 18. Searching K = 4 through 9 exhaustively finds exactly
one solution, at K = 7, in about a tenth of a second in Python.

The knight's opening is forced almost immediately by the arithmetic: 0, +1 = 1,
+2 = 3, /3 = 1, which means it climbs two towers in its first two moves and steps
down onto the "1" clue square at move 3.

## Files

- `solve.py` searches for the path from scratch and prints the unique solution.
- `verify.py` contains no solving logic. It hardcodes the found path and checks
  every rule independently (move geometry, score arithmetic, divisibility,
  tower placement, checkpoint schedule), then recomputes the final answer.

## Run

```
python3 solve.py --all   # exhaustive search over K, confirms uniqueness
python3 verify.py        # independent rule-by-rule verification
```

No dependencies beyond the standard library.

Note: this repo was kept private until Jane Street published the official
solution at the end of July 2026.
