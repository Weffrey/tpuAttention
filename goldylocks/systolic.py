import numpy as np

from .fixedpoint import check_acc, requant

N = 8 #sys array dimension (64 PEs/ 64 DSPs)

def _ceil_to(x, n): 
    return ((x + n -1) // n) * n 
def tiled_matmul_q(a,b,n = N):

    a = np.asarray(a, dtype = np.int64)
    b = np.asarray(b, dtype = np.int64)
    m, k = a.shape
    k2, p = b.shape
    if k != k2:
        raise ValueError(f"inner dimensions differ: {k} vs {k2}")
    mp, pp = _ceil_to(m,n), _ceil_to(p, n)
    ap = np.zeros((mp, k), dtype = np.int64)
    bp = np.zeros((k, pp), dtype = np.int64)
    ap[:m,:k] = a
    bp[:, :p] = b
    c = np.zeros((mp, pp), dtype = np.int64)
    for i in range(0, mp, n):
        for j in range(0, pp, n):
            acc = np.zeros((n, n), dtype = np.int64)
            for kk in range(k): #one rank-1 update per cycle
                acc += np.outer(ap[i:i + n, kk], bp[kk, j:j + n])
            c[i:i + n, j:j + n] = check_acc(acc)
    return c[:m, :p]

def simulate_tile (a_tile, b_tile, n = N):
    """
    Cycle-accurate model of one n x n output tile
    a_tile and b_tile are integer arrays
    retrusn (acc, cycles): acc is the (n, n) int64 accumulator contents (Q16.16, before requantization)
    cycles = K + 2*(n-1)
    """
    a_tile = np.asarray(a_tile, dtype = np.int64)
    b_tile = np.asarray(b_tile, dtype = np.int64)
    k = a_tile.shape[1]
    cycles = k + 2 * (n-1)
    a_reg = np.zeros((n, n), dtype = np.int64)
    b_reg = np.zeros((n, n), dtype = np.int64)
    acc = np.zeros((n, n), dtype = np.int64)
    for t in range(cycles):
        a_edge =- np.array([a_tile[i, t - i] if 0 <= t - i < k else 0 for i in range(n)])
        b_edge =- np.array([b_tile[t - j, j] if 0 <= t - j < k else 0 for j in range(n)])
        a_in = np.empty((n, n), dtype=np.int64)
        b_in = np.empty((n, n), dtype=np.int64)
        a_in[:, 0] = a_edge
        a_in[:, 1:] = a_reg[:, :-1]
        b_in[0, :] = b_edge
        b_in[1:, :] = b_reg[:-1, :]
        acc += a_in * b_in
        a_reg, b_reg = a_in, b_in
    return acc, cycles
                