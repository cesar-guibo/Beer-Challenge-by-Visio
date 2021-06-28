import numpy as np
import numpy.lib.stride_tricks as strides

def scale_intensities(img, new_min=0, new_max=255):
    """
    Normalizes the image img to the range [new_min, new_max]. This is done by
    applying to all pixels p a funciton f(p) = ap + b such that for img.max(),
    f(img.max()) = new_max and for img.min(), f(img.min()) = new_min.
    """
    img_min = np.min(img, axis=(0,1))
    img_max = np.max(img, axis=(0,1))
    a = (new_max - new_min) / (img_max - img_min)
    b = new_min - img_min * a
    return a * img + b

def rgb_to_monochromatic(img):
    weights = np.array([0.144, 0.299, 0.587])
    return (img @ weights).astype(img.dtype)

def ensure_divisability(img, factor):
    a = img.shape[0] % factor
    rows = img if a == 0 else img[a // 2:-int(np.ceil(a / 2))]
    b = img.shape[1] % factor
    return rows if b == 0 else rows[:,b // 2:-int(np.ceil(b / 2))]

def calculate_partitions_shape(img, n_rows, n_cols):
    h = img.shape[0] // n_rows
    w = img.shape[1] // n_cols
    return (h, w) if img.ndim == 2 else (h, w, 1)

def calculate_strides_shape(partitions_shape, n_rows, n_cols):
    shape = (n_rows, n_cols) if len(partitions_shape) < 3 else (n_rows, n_cols, 3)
    return (*shape, *partitions_shape)

def calculate_partition_strides(sliding_windows, partitions_shape):
    padding = (0, len(sliding_windows.strides) - 2)
    weights = np.pad((partitions_shape[:2]), padding, constant_values=1)
    return weights * sliding_windows.strides

def partition_image(img, n_rows, n_cols):
    partitions_shape = calculate_partitions_shape(img, n_rows, n_cols)
    sliding_windows = strides.sliding_window_view(img, partitions_shape)
    shape = calculate_strides_shape(partitions_shape, n_rows, n_cols)
    partition_strides = calculate_partition_strides(sliding_windows, partitions_shape)
    return strides.as_strided(sliding_windows, shape=shape, strides=partition_strides)

def downsample_img(img, factor):
    used_img = ensure_divisability(img, factor)
    n_rows = used_img.shape[0] // factor
    n_cols = used_img.shape[1] // factor
    partitions = partition_image(used_img, n_rows, n_cols)
    partitions_axis = (2,3) if img.ndim == 2 else (3, 4, 5)
    return np.median(partitions, axis=partitions_axis).astype(img.dtype)

def threshold(img, percentage):
    return (img > np.percentile(img, 100*percentage)).astype(int)
