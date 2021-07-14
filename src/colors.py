import numpy as np

def split_channels(img):
    return np.squeeze(np.split(img, img.shape[-1], axis=-1), axis=-1)\
        if img.ndim > 2 else np.expand_dims(img, axis=0)

def rgb_to_gray(img):
    weights = np.array([0.144, 0.299, 0.587])
    return (img @ weights).astype(img.dtype) if img.ndim > 2 else img
