import numpy as np
import random
import math

MAX_INT = 2147483647
MIN_INT = -2147483648


#  Data format helper functions

def serialize(l1,l2):
    return " ".join([str(i) for i in interleave(l1,l2)])

def interleave(l1,l2):
    return [val for pair in zip(l1,l2) for val in pair]

#  Generic data generators

def gen_random_ints(N):
    return [random.randint(MIN_INT,MAX_INT) for _ in range(N)]

def gen_normal_dist(N, std, mean=0):
    return [int(std*np.random.normal()) for _ in range(N)]

def gen_interval(N, tdelta=1, offset=0):
    return list(tdelta * np.array(range(N)) + offset)

#  Model data generators for timestamps

def gen_ts_random(N):
    return gen_random_ints(N)

def gen_ts_ideal(N):
    return gen_interval(N,MAX_INT/N)

def gen_ts_realistic(N,t):
    noise = np.array(gen_normal_dist(N,t/10))
    ts = np.array(gen_interval(N,t,100000)) + noise
    return list(ts)

def gen_ts_realistic_bad(N,t):
    noise = np.array(gen_normal_dist(N,t/2))
    ts = np.array(gen_interval(N,t,100000)) + noise
    return list(ts)

def gen_ts_realistic_20ms(N):
    return gen_ts_realistic(N,20)

def gen_ts_realistic_200ms(N):
    return gen_ts_realistic(N,200)

def gen_ts_realistic_1000ms(N):
    return gen_ts_realistic(N,1000)

def gen_ts_realistic_bad_20ms(N):
    return gen_ts_realistic(N,20)

def gen_ts_realistic_bad_200ms(N):
    return gen_ts_realistic(N,200)

def gen_ts_realistic_bad_1000ms(N):
    return gen_ts_realistic(N,1000)


# Model data generators for values

def gen_val_normal_dist(N):
    return gen_normal_dist(N, 250000)

def gen_val_uniform_dist(N):
    return gen_random_ints(N)

def gen_val_positive_dist(N):
    norm = gen_normal_dist(N,10000)
    positives = [min(MAX_INT,x*x) for x in norm]
    return positives

def gen_val_negative_dist(N):
    norm = gen_normal_dist(N,10000)
    negatives = [max(MIN_INT,-x*x) for x in norm]
    return negatives

def gen_val_moving_signal(N):
    delta = 10
    vals = [0]
    for _ in range(N-1):
        vals.append(vals[len(vals)-1] + int(delta))
        delta = delta + 2 * np.random.normal()
    return vals

def gen_val_random_spike(N):
    signal = gen_normal_dist(N,100)
    for i in range(N):
        if random.random() > 0.95:
            spike = np.random.normal()
            spike = int(1000 * spike * spike)
            signal[i] = spike
    return signal

def gen_val_noisy_periodic(N):
    noise = np.array(gen_normal_dist(N,1000))
    signal = np.array([int(10000*math.sin(n/100 * 2 * 3.1415)) for n in range(N)]) + noise
    return list(signal)




