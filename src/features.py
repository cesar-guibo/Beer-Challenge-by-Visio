import numpy as np
from scipy.ndimage import maximum_filter

def apply_non_max_suppression(image, kernel_size):
    maxs = maximum_filter(image, size=kernel_size)
    return image * (image == maxs)

def apply_hysteresis_threshold(image, low, high):
    not_low_mask = np.uint8(image > low)
    maxs = maximum_filter(image, size=3)
    return np.uint8(maxs >= high) & not_low_mask
