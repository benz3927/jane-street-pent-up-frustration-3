"""Independent verifier for Jane Street July 2026:
'Pent-Up' Frustration 3 / Knight Moves 7.

This file contains NO solving logic. It hardcodes the found solution and
checks every puzzle rule against it, then recomputes the final answer.

Coordinates: x = 0..7 (left -> right), y = 0..7 (bottom -> top).
The knight starts at (0,0), the bottom-left square, with score 0.

Run:  python3 verify.py
"""

# ---------------------------------------------------------------- board ----
# Region ids per square, given as image rows (top row first).
REGION_ROWS_TOP_DOWN = [
    [ 0, 0, 0, 0, 0, 1, 1, 1],   # y = 7
    [ 2, 2, 2, 3, 3, 4, 4, 1],   # y = 6
    [ 2, 5, 2, 3, 3, 3, 4, 1],   # y = 5
    [ 6, 5, 5, 7, 7, 8, 4, 4],   # y = 4
    [ 6, 6, 5, 7, 7, 8, 8, 9],   # y = 3
    [ 6,10, 5,11, 8, 8,12, 9],   # y = 2
    [ 6,10,11,11,11,12,12, 9],   # y = 1
    [10,10,10,11,12,12, 9, 9],   # y = 0
]
REG = {(x, 7 - r): REGION_ROWS_TOP_DOWN[r][x] for r in range(8) for x in range(8)}
N_REGIONS = 13

# Clue squares: score the knight wrote there (start square (0,0) shows 0).
CLUES = {(0,4):528, (1,2):750, (1,3):449, (3,2):88, (3,5):23, (4,3):16,
         (5,2):272, (5,5):138, (5,7):37, (6,2):1, (7,7):1100}

K = 7                       # late-phase checkpoint interval
# ------------------------------------------------------------- solution ----
# (x, y, height) for each position, moves 0..54. height 2 = tower square.
PATH = [
    (0,0,2),(2,1,2),(4,2,2),(6,2,1),(7,0,1),(5,1,1),(4,3,1),(4,5,2),
    (4,7,1),(3,5,1),(2,7,1),(0,6,1),(0,4,2),(1,6,2),(3,7,2),(5,7,1),
    (3,6,1),(2,4,1),(3,2,1),(1,1,1),(0,3,1),(2,3,2),(4,4,2),(5,6,2),
    (7,6,1),(5,5,1),(3,4,1),(2,2,1),(0,1,1),(2,0,1),(4,0,2),(6,0,1),
    (5,2,1),(7,2,2),(7,4,1),(6,6,1),(5,4,1),(4,6,1),(2,5,1),(1,3,1),
    (0,5,1),(2,6,1),(1,4,1),(0,2,1),(1,0,1),(3,1,1),(1,2,1),(3,3,1),
    (4,1,1),(5,3,1),(6,1,1),(7,3,1),(6,5,1),(7,7,1),(7,5,2),
]

def fail(msg):
    raise SystemExit(f"VERIFICATION FAILED: {msg}")

def main():
    L = len(PATH) - 1                                   # number of moves
    squares = [(x, y) for x, y, _ in PATH]

    # -- basic path sanity ---------------------------------------------------
    if PATH[0][:2] != (0, 0):
        fail("path does not start at the bottom-left square")
    if len(set(squares)) != len(squares):
        fail("a square is visited twice")
    for x, y, h in PATH:
        if not (0 <= x < 8 and 0 <= y < 8) or h not in (1, 2):
            fail(f"bad entry ({x},{y},h={h})")

    # -- towers: exactly one per region, all on the path ---------------------
    towers = [(x, y) for x, y, h in PATH if h == 2]
    if len(towers) != N_REGIONS:
        fail(f"{len(towers)} towers on path, need {N_REGIONS}")
    if len({REG[t] for t in towers}) != N_REGIONS:
        fail("two towers share a region")
    height = {sq: 1 for sq in REG}
    for t in towers:
        height[t] = 2
    for x, y, h in PATH:                                # declared == implied
        if h != height[(x, y)]:
            fail(f"height mismatch at ({x},{y})")
    if PATH[-1][2] != 2:
        fail("knight must stop on the move that visits the final tower")
    if PATH[-2][:2] in towers and len({t for t in towers}) == N_REGIONS:
        pass  # (final tower is the 54th entry; earlier squares checked below)
    # the 13th tower must be visited exactly at the end:
    seen_t = 0
    for i, (x, y, h) in enumerate(PATH):
        seen_t += (h == 2)
        if seen_t == N_REGIONS and i != L:
            fail("all towers were visited before the final move")

    # -- checkpoint schedule -------------------------------------------------
    cps = set(range(3, 19, 3)) | {18 + K * j for j in range(1, 6)}
    if not (18 + 5 * K <= L < 18 + 6 * K):
        fail(f"path length {L} inconsistent with K={K} and 11 recorded scores")

    # -- replay every move ---------------------------------------------------
    score = 0
    for m in range(1, L + 1):
        x0, y0, h0 = PATH[m - 1]
        x1, y1, h1 = PATH[m]
        dx, dy, dz = abs(x1 - x0), abs(y1 - y0), abs(h1 - h0)
        if sorted((dx, dy, dz)) != [0, 1, 2]:
            fail(f"move {m}: displacement ({dx},{dy},{dz}) is not a knight move")
        if dz == 0:
            score += m                                  # level: add N
        elif h1 > h0:
            score *= m                                  # up: multiply by N
        else:
            if score % m != 0:
                fail(f"move {m}: score {score} not divisible by {m}")
            score //= m                                 # down: divide by N
        at_clue = (x1, y1) in CLUES
        if m in cps:
            if not at_clue:
                fail(f"move {m} is a checkpoint but ({x1},{y1}) has no clue")
            if CLUES[(x1, y1)] != score:
                fail(f"move {m}: score {score} != clue {CLUES[(x1,y1)]}")
        elif at_clue:
            fail(f"clue square ({x1},{y1}) visited off-checkpoint at move {m}")

    # every clue square must actually be on the path
    if not set(CLUES) <= set(squares):
        fail("some clue square was never visited")

    # -- final answer --------------------------------------------------------
    score = 0
    val = {}
    for m, (x, y, h) in enumerate(PATH):
        if m == 0:
            val[(x, y)] = 0
            continue
        x0, y0, h0 = PATH[m - 1]
        if h == h0:
            score += m
        elif h > h0:
            score *= m
        else:
            score //= m
        val[(x, y)] = score

    unvisited = [sq for sq in REG if sq not in val]
    total = 0
    print("All rule checks passed.  K = 7, path length = 54 moves.\n")
    print("Unvisited squares and their neighbor sums:")
    for x, y in sorted(unvisited):
        s = sum(val.get(n, 0) for n in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)))
        total += s
        print(f"  ({x},{y}): {s}")
    print(f"\nANSWER = {total}")

if __name__ == "__main__":
    main()
