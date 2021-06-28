from stitching.transformations import downsample_img
from stitching.stitching import stitch_images
import imageio as im
import os

if __name__ == '__main__':
    base_dir = './sequencia_1/'
    image_paths = sorted(os.listdir(base_dir))[1:]
    images = [im.imread(f'{base_dir}{path}') for path in image_paths]
    downsampled = list(map(lambda img: downsample_img(img, 10), images))
    imgs_grid = [
        downsampled[:5],
        downsampled[5:10],
        downsampled[10:15],
        downsampled[15:20],
        downsampled[20:25],
    ]
    stitched_image = stitch_images(imgs_grid)
    im.imwrite('../stitching_resul.jpg', stitched_image)
