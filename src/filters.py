import numpy as np
from scipy.signal import fftconvolve
from itertools import repeat, product, starmap
from functools import partial
from .colors import split_channels
from .aux import (
    ensure_is_odd,
    create_zero_centered_arange,
    create_zero_centered_radius_2d_range,
    PI2
)

def create_gaussian_kernel(sigma):
    if sigma == 0:
        return np.array([[1]])
    kernel_size = ensure_is_odd(int(2 * sigma))
    zcrange = create_zero_centered_arange(kernel_size)
    x, y = np.meshgrid(zcrange, zcrange)
    kernel = np.exp(-(np.square(x) + np.square(y)) / (2 * np.square(sigma)))
    return kernel / np.sum(kernel)

def apply_gaussian(img, sigma):
    kernel = create_gaussian_kernel(sigma)
    channels = split_channels(img)
    result = tuple(map(lambda img: fftconvolve(img, kernel, mode='same'), channels))
    return np.squeeze(np.stack(result, axis=-1).astype(img.dtype))

SOBEL_KERNELS = [
    np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ]),
    np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ])
]

def apply_sobel(img, on_y_axis=False):
    return fftconvolve(img, SOBEL_KERNELS[int(on_y_axis)], mode='same')

def create_gabor_annulus_kernel(kernel_size, radius0, sigma, freq0):
    kernel_size = kernel_size + 1 - (kernel_size % 2)
    zero_centered_range = np.arange(kernel_size) - (kernel_size // 2)
    radius = create_zero_centered_radius_2d_range(kernel_size)
    radius_diff = radius - radius0
    multiplier = 1 / (PI2 * sigma * radius0)
    r_exponent = - (np.pi / np.square(sigma)) * np.square(radius_diff)
    i_exponent = (1j * PI2 * freq0) * radius_diff
    return multiplier * np.exp(r_exponent + i_exponent)

def apply_gabor_annulus(img, kernel_size, radius0, sigma, freq0):
    kernel = create_gabor_annulus_kernel(kernel_size, radius0, sigma, freq0)
    return fftconvolve(img, kernel, mode='same')
