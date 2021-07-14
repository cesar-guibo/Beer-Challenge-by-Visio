import numpy as np
from scipy.spatial import cKDTree
from functools import partial
from scipy.ndimage.morphology import(
    binary_opening,
    binary_closing,
    grey_dilation
)
from .morphology import disk_structure
from .transformations import scale_intensities
from .filters import apply_sobel, apply_gabor_annulus, apply_gaussian
from .features import apply_non_max_suppression, apply_hysteresis_threshold

GABOR_ANNULUS_CONFIG = {
    'kernel_size': 55,
    'radius0': 4,
    'sigma': 10,
    'freq0': 1/5
}

LOW_THRESHOLD = 1
HIGH_THRESHOLD = 3
RADIUS = 10
OVERLAP = 0.3
MAGNITUDE_THRESHOLD = 38
FILL_DISK_SIZE = 8
NOISE_RM_DISK_SIZE = 2
WHITE_RECTANGLES_THRESHOLD = 230
WHITE_RECTANGLES_STRUCTURE_SHAPE = (11, 11)
GAUSSIAN_SIGMA = 1.6

def remove_white_rectangles(gray_image):
    structure = np.ones(WHITE_RECTANGLES_STRUCTURE_SHAPE)
    dilated = grey_dilation(gray_image, footprint=structure)
    new_image = np.copy(gray_image)
    new_image[dilated > WHITE_RECTANGLES_THRESHOLD] = np.median(gray_image)
    return new_image

def threshold_cells(gray_image):
    blurred = apply_gaussian(gray_image, GAUSSIAN_SIGMA)
    Ix = apply_sobel(blurred, on_y_axis=False)
    Iy = apply_sobel(blurred, on_y_axis=True)
    magnitude = np.hypot(Ix, Iy)
    cell_edges = np.uint8(scale_intensities(magnitude) > MAGNITUDE_THRESHOLD)

    fill_structure = disk_structure(FILL_DISK_SIZE)
    cells_filled = binary_closing(cell_edges, fill_structure)
    noise_rm = disk_structure(NOISE_RM_DISK_SIZE)
    return binary_opening(cells_filled, noise_rm)

def filter_circle_overlaps(centers, radius, all_likelihoods, allowed_overlap):
    center_likelihoods = all_likelihoods[tuple(zip(*centers))]
    tree = cKDTree(centers)
    selected = np.ones(centers.shape[0], dtype=bool)
    diameter = 2 * radius
    pairs = list(tree.query_pairs(diameter - (diameter * allowed_overlap)))
    for (index1, index2) in pairs:
        likelihood1 = center_likelihoods[index1]
        likelihood2 = center_likelihoods[index2]
        selected[index2 if likelihood2 < likelihood1 else index1] = False
    return centers[selected]

def detect_cells(image):
    no_rect = remove_white_rectangles(image[:,:,0])
    th_cells = threshold_cells(no_rect)
    center_likelihood = apply_gabor_annulus(no_rect, **GABOR_ANNULUS_CONFIG)
    regional_likelihood = th_cells * np.abs(center_likelihood)
    peaks = apply_non_max_suppression(regional_likelihood, 3)
    th_peaks = apply_hysteresis_threshold(peaks, LOW_THRESHOLD, HIGH_THRESHOLD)
    potential_centers = np.argwhere(th_peaks)
    return filter_circle_overlaps(potential_centers, RADIUS, peaks, OVERLAP)
