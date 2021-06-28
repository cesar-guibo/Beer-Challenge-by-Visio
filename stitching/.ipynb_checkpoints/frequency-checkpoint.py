import numpy as np
import operator

def calculate_bounding_shape(arrays):
    shapes = map(np.shape, arrays)
    dimension_sizes = zip(*shapes)
    return tuple(map(max, dimension_sizes))

def pad_symmetrically_to_shape(arr, shape):
    differences = map(lambda x: operator.sub(*x), zip(shape, arr.shape))
    paddings = tuple(map(lambda x: (x // 2, int(np.ceil(x / 2))), differences))
    return np.pad(arr, paddings)

def pad_symmetrically_to_same_shape(arrays):
    target_shape = calculate_bounding_shape(arrays)
    equalize_shapes = lambda arr: pad_symmetrically_to_shape(arr, target_shape)
    return list(map(equalize_shapes, arrays))

def apply_on_freq_domain(function, *args):
    frequencies = np.fft.rfft2(pad_symmetrically_to_same_shape(args))
    return np.fft.fftshift(np.fft.irfft2(function(*frequencies)))
