import numpy as np
from itertools import repeat

def ensure_is_odd(value):
    return value + (1 - value % 2)

def create_zero_centered_arange(size):
    center = size // 2
    return np.arange(size) - center

def create_zero_centered_radius_2d_range(size):
    zcrange = create_zero_centered_arange(size)
    return np.hypot(*np.meshgrid(*repeat(zcrange, 2)))

PI2 = 2 * np.pi
