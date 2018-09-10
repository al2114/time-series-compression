import numpy as np
import random

MAX_INT = 2147483647
MIN_INT = -2147483648

def serialize(l1,l2):
    return " ".join([str(i) for i in interleave(l1,l2)])

def interleave(l1,l2):
    return [val for pair in zip(l1,l2) for val in pair]

def gen_random_ints(N):
    return [random.randint(MIN_INT,MAX_INT) for _ in range(N)]

def gen_interval(N, period=1, offset=0):
    return list(period * np.array(range(N)) + offset)
