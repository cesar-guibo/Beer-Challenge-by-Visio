import numpy as np
from .aux import create_zero_centered_radius_2d_range

def disk_structure(radius):
    kernel_size = (radius * 2) + 1
    all_radius = create_zero_centered_radius_2d_range(kernel_size)
    return np.uint8(all_radius <= radius)
