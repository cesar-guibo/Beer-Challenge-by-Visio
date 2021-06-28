import numpy as np
from .frequency import apply_on_freq_domain

def split_rgb_channels(img):
    return np.squeeze(np.split(img, 3, axis=-1), axis=-1)

def cross_correlate(img, filt):
    return apply_on_freq_domain(lambda x,y: x*np.conj(y), img, filt)

def convolve(img, filt):
    return apply_on_freq_domain(np.multiply, img, filt)

def generate_zero_centered_arange(size):
    center = size // 2
    return np.arange(size) - center

def compute_2d_gaussian(x, y, sigma):
    if sigma == 0:
        return np.ones_like(x)
    return 1 / (2 * np.pi * sigma2) * np.exp(x2 + y2 / (2 * sigma2))

def ensure_is_odd(value):
    return value + (1 - value % 2)

def compute_optimal_gaussian_filter_size(sigma):
    return ensure_is_odd(int(2 * sigma))

def generate_gaussian_filter(sigma=1):
    if sigma == 0:
        return np.array([[1]])
    filter_size = compute_optimal_gaussian_filter_size(sigma)
    zcrange = generate_zero_centered_arange(filter_size)
    x, y = np.meshgrid(zcrange, zcrange)
    filt = np.exp(-(np.square(x) + np.square(y)) / (2 * np.square(sigma)))
    return filt / np.sum(filt)

def apply_gaussian_filter(img, sigma=1):
    gaussian = generate_gaussian_filter(sigma=sigma)
    if img.ndim == 2:
        return convolve(img, gaussian)
    else:
        result = map(lambda channel: convolve(channel, gaussian), split_rgb_channels(img))
    return np.stack(tuple(result), axis=-1).astype(img.dtype)
