import numpy as np
from .filters import apply_gaussian
from .transformations import threshold
from .colors import rgb_to_gray
from scipy.ndimage import rotate
from scipy.optimize import minimize_scalar
from scipy.stats import mode
from itertools import starmap, chain
from functools import reduce
import operator
import re

def binary_value_max_probability(array):
    probability_of_1 = np.sum(array) / np.prod(array.shape)
    return max(probability_of_1, 1 - probability_of_1)

def loss_function(thresholded_img):
    row_max_probabilites = list(map(binary_value_max_probability, thresholded_img))
    return thresholded_img.shape[0] - np.sum(row_max_probabilites)

def correct_image_rotation_angle(thresholded_img):
    def rotation(ang):
        return loss_function(rotate(thresholded_img, angle=ang))
    result = minimize_scalar(rotation, tol=1e-8)
    return result.x

def find_major_grid_lines(image, axis):
    is_line = np.sum(image, axis=1-axis) / image.shape[1 - axis] > 0.7
    splitted_chars = np.split(is_line.astype(int).astype(str), 2, axis=0)
    strs = list(map(lambda strings: ''.join(strings), splitted_chars))
    patterns = map(lambda s: max(re.findall(r'1+', s), key=len), strs)
    idx1, idx2 = starmap(lambda p, s: s.find(p) + len(p) // 2, zip(patterns, strs))
    return (idx1, idx2 + splitted_chars[0].shape[0])

def find_major_grid_corners(image):
    x_u, x_d = find_major_grid_lines(image, axis=0)
    y_l, y_r = find_major_grid_lines(image, axis=1)
    return np.array([
        [[x_u, y_l], [x_u, y_r]],
        [[x_d, y_l], [x_d, y_r]]
    ])

def configured_rotate(img, angle):
    return rotate(img, angle, mode='reflect', reshape=False)

def compute_angles(imgs_grid):
    preprocess = lambda img: threshold(apply_gaussian(img, 2), 0.8)
    used_imgs_grid = list(map(lambda row: list(map(preprocess, row)), imgs_grid))
    angles = np.array(list(map(
        lambda row: list(map(correct_image_rotation_angle, row)),
        used_imgs_grid
    )))
    return angles

def compute_translations(imgs_grid):
    preprocess = lambda img: threshold(apply_gaussian(img, 3), 0.7)
    used_imgs_grid = list(map(lambda row: list(map(preprocess, row)), imgs_grid))
    corners = np.array(list(map(
        lambda row: list(map(find_major_grid_corners, row)),
        used_imgs_grid
    )))
    first_row_translations = np.concatenate(
        (np.zeros((1,2), dtype=int),
        np.add.accumulate(
            np.sum(corners[0,:-1,:,1] - corners[0,1:,:,0], axis=1) / 2 + 0.5
        ).astype(int))
    )
    cols_translations = np.concatenate(
        (np.zeros((1, corners.shape[1], 2), dtype=int),
        np.add.accumulate(
            np.sum(corners[:-1,:,1,:] - corners[1:,:,0,:], axis=2) / 2 + 0.5
        ).astype(int)),
        axis=0
    )
    return first_row_translations + cols_translations

def compute_transformations(gray_imgs_grid):
    angles = compute_angles(gray_imgs_grid)
    rotated_imgs_grid = list(starmap(
        lambda imgs, angles: list(starmap(configured_rotate, zip(imgs, angles))),
        zip(gray_imgs_grid, angles)
    ))
    return compute_translations(rotated_imgs_grid), angles

def preprocess(img):
    return threshold(apply_gaussian(rgb_to_gray(img), 3), 0.7)

def stitch_images(imgs_grid):
    gray_imgs_grid = list(map(
        lambda row: list(map(rgb_to_gray, row)),
        imgs_grid
    ))
    translations, angles = compute_transformations(gray_imgs_grid)
    first_quadrant_translations = translations + np.tile(
        np.array([-np.min(translations[0,:,0]), -np.min(translations[:,0,1])]),
        (translations.shape[0], 1)
    )
    images_shape = imgs_grid[0][0].shape
    rbackground = np.median(imgs_grid[0][0][:,:,0])
    gbackground = np.median(imgs_grid[0][0][:,:,1])
    bbackground = np.median(imgs_grid[0][0][:,:,2])
    stitched_img = np.zeros(
        (np.max(first_quadrant_translations[-1,:,0]) + images_shape[0],
         np.max(first_quadrant_translations[:,-1,1]) + images_shape[1],
         images_shape[2]),
        dtype=np.uint8
    )
    stitched_img[:,:,0] = rbackground
    stitched_img[:,:,1] = gbackground
    stitched_img[:,:,2] = bbackground
    imgs_list = chain.from_iterable(imgs_grid)
    translations_raveled = np.vstack(first_quadrant_translations)
    angles_list = chain.from_iterable(angles)
    for img, translation, angle in zip(imgs_list, translations_raveled, angles_list):
        dx, dy = translation
        rotated_img = configured_rotate(img, angle)
        stitched_img[dx:dx+img.shape[0],dy:dy+img.shape[1]] = rotated_img
    return stitched_img
