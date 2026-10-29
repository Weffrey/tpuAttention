

import numpy as np

FRAC = 8
WORD = 16
ACC_W = 32 #multiplying two 
QMIN = -(1 << (WORD - 1))
QMAX = (1 << (WORD - 1))
ACC_MIN = -(1 << (ACC_W - 1))
ACC_MAX = (1 << (ACC_W - 1)) - 1

def sat16(x):
    return np.clip(x, QMIN, QMAX).astype(np.int16)

def to_q(x):
    x = np.asarray(x, dtype=np.float64)
    return sat16(np.floor(x * (1 << FRAC) + 0.5))

def from_q(q):
    return np.asarray(q, dtype=np.float64) / (1 << FRAC)

def requant(acc):
    """ Q16.16 accumulator to Q8.8 with round-half-up and saturation """
    acc = np.asarray(acc, dtype=np.int64)
    return sat16((acc + (1 << (FRAC - 1))) >> FRAC)

def check_acc(acc):
    acc = np.asarray(acc, dtype=np.int64)
    if acc.min() < ACC_MIN or acc.max() > ACC_MAX:
        raise OverflowError("32-bit accumulator overflow: reduce K or rescale inputs")
    return acc

def matmul_q(a,b):
    acc = check_acc(np.asarray(a, dtype=np.int64) @ np.asarray(b, dtype=np.int64))
    return requant(acc)