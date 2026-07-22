"""Jane Street July 2026: 'Pent-Up' Frustration 3 / Knight Moves 7.

Coordinates: x=0..7 left->right, y=0..7 bottom->top. Start (0,0), score 0.
Heights: every square height 1, except each region's tower square (height 2).
Moves: (dx,dy,dz) a permutation of {0,1,2} in absolute value.
  dz=0  -> standard knight (1,2): score += N
  dz=1  -> straight (2,0):        up: score *= N ; down: score /= N (exact)
Checkpoints at moves 3,6,9,12,15,18, then 18+K, 18+2K, ... (K>3).
Exactly 11 clue squares; knight stops on the move that visits the 13th tower.
"""
import sys, json
from functools import lru_cache

region_img = [
[ 0, 0, 0, 0, 0, 1, 1, 1],
[ 2, 2, 2, 3, 3, 4, 4, 1],
[ 2, 5, 2, 3, 3, 3, 4, 1],
[ 6, 5, 5, 7, 7, 8, 4, 4],
[ 6, 6, 5, 7, 7, 8, 8, 9],
[ 6,10, 5,11, 8, 8,12, 9],
[ 6,10,11,11,11,12,12, 9],
[10,10,10,11,12,12, 9, 9]]
REG = [[0]*8 for _ in range(8)]  # REG[x][y]
for r in range(8):
    for c in range(8):
        REG[c][7-r] = region_img[r][c]

CLUES = {(0,4):528,(1,2):750,(1,3):449,(3,2):88,(3,5):23,(4,3):16,
         (5,2):272,(5,5):138,(5,7):37,(6,2):1,(7,7):1100}
CLUE_CELLS = set(CLUES)
NREG = 13
REGION_CELLS = [[] for _ in range(NREG)]
for x in range(8):
    for y in range(8):
        REGION_CELLS[REG[x][y]].append((x,y))

FLAT = [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]
STRAIGHT = [(2,0),(-2,0),(0,2),(0,-2)]

# relaxed all-pairs distance (any move type, ignoring heights) for pruning
import collections
ALLM = FLAT + STRAIGHT
DIST = {}
for sx in range(8):
    for sy in range(8):
        d = {(sx,sy):0}
        q = collections.deque([(sx,sy)])
        while q:
            x,y = q.popleft()
            for dx,dy in ALLM:
                nx,ny = x+dx,y+dy
                if 0<=nx<8 and 0<=ny<8 and (nx,ny) not in d:
                    d[(nx,ny)] = d[(x,y)]+1
                    q.append((nx,ny))
        DIST[(sx,sy)] = d

SCORE_CAP = 5_000_000

def checkpoint_times(K, upto):
    ts = set(range(3,19,3))
    t = 18+K
    while t <= upto:
        ts.add(t); t += K
    return ts

def next_cp(m, K):
    if m < 18:
        return ((m//3)+1)*3
    r = (m-18) % K
    return m + (K - r if r else K)

def score_reach(v, m, t, targets):
    """Exact set of scores reachable from v after moves m+1..m+t; check any target hit."""
    cur = {v}
    for i in range(1, t+1):
        N = m+i
        nxt = set()
        for s in cur:
            a = s+N
            if a <= SCORE_CAP: nxt.add(a)
            a = s*N
            if a <= SCORE_CAP: nxt.add(a)
            if N and s % N == 0: nxt.add(s//N)
        cur = nxt
        if not cur: return False
    return bool(cur & targets)

def solve(K, find_all=False):
    sols = []
    Lmin, Lmax = 18+5*K, 18+6*K-1
    visited = [[False]*8 for _ in range(8)]
    reg_tower = [None]*NREG
    reg_unvis = [len(REGION_CELLS[i]) for i in range(NREG)]
    path = []  # (x,y,h,score)
    clue_left = set(CLUE_CELLS)

    def feasible_regions():
        for i in range(NREG):
            if reg_tower[i] is None and reg_unvis[i] == 0:
                return False
        return True

    def cp_prune(x, y, m, v):
        cp = next_cp(m, K)
        t = cp - m
        if cp > Lmax:  # no further checkpoints required; but path must end by Lmax
            return True
        # positional: some remaining clue square within t relaxed moves
        cand = {CLUES[c] for c in clue_left if DIST[(x,y)][c] <= t and (DIST[(x,y)][c] % 1 == 0)}
        if not cand: return False
        return score_reach(v, m, t, cand)

    def dfs(x, y, h, m, v):
        towers_done = all(t is not None for t in reg_tower)
        if towers_done:
            # knight stops NOW (this arrival completed the towers)
            if Lmin <= m <= Lmax and not clue_left:
                sols.append((K, m, list(path)))
                return not find_all
            return False
        if m >= Lmax:  # must have stopped by now
            return False
        # remaining towers <= remaining moves
        rem_t = sum(1 for t in reg_tower if t is None)
        if rem_t > Lmax - m: return False
        if len(clue_left) and not cp_prune(x, y, m, v):
            return False
        N = m+1
        cp = next_cp(m, K)
        for dx, dy in FLAT + STRAIGHT:
            nx, ny = x+dx, y+dy
            if not (0 <= nx < 8 and 0 <= ny < 8): continue
            if visited[nx][ny]: continue
            straight = (dx == 0 or dy == 0)
            rg = REG[nx][ny]
            # height options for destination
            if straight:
                hopts = []
                if h == 1:
                    if reg_tower[rg] is None: hopts = [2]
                else:
                    hopts = [1]
            else:
                hopts = [h] if (h == 1 or reg_tower[rg] is None) else []
                # h==2 flat needs dest tower in its (different) region
                if h == 2 and rg == REG[x][y]: hopts = []
            for nh in hopts:
                if straight:
                    if nh == 2:
                        nv = v*N
                        if nv > SCORE_CAP: continue
                    else:
                        if N == 0 or v % N != 0: continue
                        nv = v//N
                else:
                    nv = v+N
                    if nv > SCORE_CAP: continue
                is_cp = (N == cp) if N <= Lmax else False
                if (nx,ny) in CLUE_CELLS:
                    if not is_cp or CLUES[(nx,ny)] != nv: continue
                else:
                    if is_cp: continue
                # apply
                visited[nx][ny] = True
                reg_unvis[rg] -= 1
                placed = False
                if nh == 2:
                    reg_tower[rg] = (nx,ny); placed = True
                if (nx,ny) in CLUE_CELLS: clue_left.discard((nx,ny))
                ok_reg = feasible_regions()
                path.append((nx,ny,nh,nv))
                if ok_reg and dfs(nx, ny, nh, N, nv):
                    return True
                path.pop()
                if (nx,ny) in CLUE_CELLS: clue_left.add((nx,ny))
                if placed: reg_tower[rg] = None
                reg_unvis[rg] += 1
                visited[nx][ny] = False
        return False

    # start at (0,0): branch start height
    for h0 in (1, 2):
        visited[0][0] = True
        rg0 = REG[0][0]
        reg_unvis[rg0] -= 1
        if h0 == 2: reg_tower[rg0] = (0,0)
        path.append((0,0,h0,0))
        if feasible_regions():
            if dfs(0, 0, h0, 0, 0) and not find_all:
                return sols
        path.pop()
        if h0 == 2: reg_tower[rg0] = None
        reg_unvis[rg0] += 1
        visited[0][0] = False
    return sols

if __name__ == "__main__":
    import time
    find_all = "--all" in sys.argv
    allsols = []
    for K in range(4, 10):
        t0 = time.time()
        s = solve(K, find_all=find_all)
        print(f"K={K}: {len(s)} solution(s) in {time.time()-t0:.1f}s", flush=True)
        allsols += s
    for K, L, path in allsols:
        print("SOLUTION K=", K, "L=", L)
        for i,(x,y,hh,vv) in enumerate(path):
            print(f"  move {i}: ({x},{y}) h={hh} score={vv}")
    if allsols:
        json.dump([{"K":K,"L":L,"path":p} for K,L,p in allsols], open("sols.json","w"))
