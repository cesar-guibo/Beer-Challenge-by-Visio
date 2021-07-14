import imageio as im
import numpy as np
import matplotlib.pyplot as plt
from PIL import ImageColor
import cv2 as cv
import pickle
import os
import sys
from src.transformations import downsample_img
from src.stitching import stitch_images
from src.cell_detection import detect_cells
from src.cell_classification import classify_cells

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('The program must be run with:')
        print('python program.py <inputs_directory> <output_file_path>')
    base_dir = sys.argv[1]
    if base_dir[:-1] != '/':
        base_dir += '/'
    image_paths = sorted(os.listdir(base_dir))[1:]
    images = [im.imread(f'{base_dir}{path}') for path in image_paths]
    downsampled = list(map(lambda img: downsample_img(img, 6), images))
    imgs_grid = [
        downsampled[:5],
        downsampled[5:10],
        downsampled[10:15],
        downsampled[15:20],
        downsampled[20:25],
    ]
    stitched_image = stitch_images(imgs_grid)
    centers = detect_cells(stitched_image)
    with open("classifier.pkl", "rb") as f:
        classifier = pickle.load(f)
    with open("label_meanings.pkl", "rb") as f:
        label_meanings = pickle.load(f)
    labels, metrics = classify_cells(stitched_image, centers, model=classifier)

    label1, label1_points, label1_silhouette = metrics[0]
    label2, label2_points, label2_silhouette = metrics[1]
    total_points = label1_points + label2_points
    label1_probability = np.round(100 * label1_points / total_points, 2)
    label2_probability = np.round(100 * label2_points / total_points, 2)
    print('----------------------------------------------')
    print(f'Estimated {label1_points} ({label1_probability}%) {label_meanings[label1]}')
    print(f'Silhouette coefficient: {label1_silhouette}')
    print('----------------------------------------------')
    print(f'Estimated {label2_points} ({label2_probability}%) {label_meanings[label2]}')
    print(f'Silhouette coefficient: {label2_silhouette}')

    print('\nWriting image with detected cells to disk...')
    colors = ['red', 'green']
    for i, (x, y) in enumerate(centers):
        color = ImageColor.getrgb(colors[labels[i]])
        cv.rectangle(stitched_image, (y-10, x-10), (y + 10, x + 10), color, 1)
    im.imwrite(sys.argv[2], stitched_image)
