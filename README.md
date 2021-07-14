# Beer-Challenge-by-Visio

## Abstract
Measuring the quality of beer is an important task in industrial scale
fermentation processes. To do that, a lot of times, the proportion of
alive and dead yeast cells is used as the parameter that indicates this
quality measurement quantitatively. The procedure utilized for analyzing
this number involves diluting a fermentation sample with bromothymol blue
inside a Neubauer chamber and counting the numbers of alive and dead cells
through microscopic observation.

With that in mind, the objective of this challenge is to develop an image
processing method that calculates the amounts of both alive and dead cells
in a yeast sample. For that, one problem that needs to be tackled is that
since a single microscopic image can't cover the entirety of the observed
sample, images of its different parts must be used. Thus, to get a more
accurate estimate of the beer quality, the images of a partitioned sample
must be used to reconstruct an image that represents an entire sample.  The
other one is that the reconstructed image of a sample must be segmented in
such a way that the cells can be not only recognized, but also differentiated
as either dead or alive. 

## Objectives
- Merge the grid of images into a single image through Image Stitching methods
	- For this, Image enhancement methods, key points detection, image segmentation methods and binary images processing were also utilized.
- Recognize cells in images through segmentation and circle detection.
	- For this, image enhancement methods, edge detection methods, image segmentation methods and mathematical morphology and feature matching were also used
- Count the number of cells with a blue color and the number of cells with a gray color
	- For this color feature matching was used. 	

## Pipeline utilized

### Brief description
First, thresholding segmentation is applied to distinguish the background
grids from the rest of the images and the rotations are corrected by minimizing
a loss funciton. After that, the corners of the three line grids are found
and through that, the grid of images is stitched together. Then, the white 
rectangles on the borders of the images are removed and the cells are segmented
through thresholding the magnitude of the image gradient and applying a 
morphological close operation to this binary immage to fill the circles. Following
this, a gabor annulus is applied to the stitched image and the result is multiplied
by the binary mask formed by the previous operations and not only peak detection,
but also hysterisis thresholding and overlay exclusion are applied to the 
result of this multiplications to detect the centers of the cells. At last,
color features are utilized to classify cells as either alive or dead. This
whole process is tuned on the images present in the directory sequencia_1 and
are afterwards tested in th images of the directory sequencia_2.

### Analysis of the images
The images that must be stitched together form the following grid

    
![png](./report_images/output_4_0.png)
    


From this simple visual analysis, we can see that detecting keypoints through 
either blob or edge detection would be really dificult, there are no particularly
unique points in those images. That being the case, it is best to ignore the 
content of the images themselves and just look at the background grid to compute
the transformations that can be used to merge all images into a single one 
with minimum overlap. Thus, thresholding is going to be applied to each image 
for the purpose of isolating the grid as a binary image.

### Image stitching
#### Thresholding segmentation

Before the thresholding is applied, the images need to be downsampled, otherwise
the computational cost will be too big with the current resolutions.

    
![png](./report_images/output_9_0.png)
    


After performing this downsampling, the images are converted from rgb to 
a grayscale and its color histograms are analyzed


    
![png](./report_images/output_12_0.png)
    


    
![png](./report_images/output_14_1.png)
    


With this histogram, it can be seen that since the grid has the brightest color in the monochromatic image, its gray level is probably within the following interval:

    
![png](./report_images/output_16_1.png)
    


To find the probability associated with this interval, we compute the cumulative
histogram and obtain the following percentile as a threshold

    
![png](./report_images/output_18_1.png)
    


Now, thresholding the images to values higher than the 85th percentile results in

    
![png](./report_images/output_21_0.png)
    


Which properly isolates the grid. But with a closer inspection, we can see that
it ends up leaving a good number of imperfections on the grid lines

    
![png](./report_images/output_23_1.png)
    


#### Correcting rotation

Now that the grid has been isolated, we have that the textura along its rows
$f_i$ can described through the maximum probability value $\max_\{P_{f_i}\}$
in its color histogram $P_{f_i}$, or in other words, the measure of how much
participation the dominant color has in the row. We also have that the distance
between any two row texture descriptors $P_g$ and $P_h$ can be calculated as
$$|P_g - P_h|.$$ 

When a grid horizontal $P_i$ line is perfectly aligned with the axis, the dominant
color of the rows that represent it should have a histogram with a probability
of each pixel in that row having value one very close to the maximum. For rows
that do not represent horizontal lines, in an ideal thresholded grid image,
there should be a negligeble probability $c$ that a pixel has value zero 
(part of a vertical line) and a probability $1 - c$ that a pixel has value one.

In this case, $P_i - P_g$ will be positive for any rotated lien and approximately
0 otherwise. This makes this distance function almost linear, so $c$ is ignored,
and the row texture descriptor of an ideal thresholded grid image that is aligned
with the xy-axis is defined as row in which the color histogram has a maximum
probability value of one. Now using this row texture as a reference point, we
minimize the sum of the distances between the row textures of an image and the
row textures of an ideal grid through iterative rotations to obtain an estimator
of the angle that must be used by a rotation to align the image lines to the x axis. 

    
![png](./report_images/output_29_0.png)
    


#### Key points detection

Now, for the key points detection, since the images don't have a lot of 
distinguishing features, the idea is to use the grid to detect the points 
that can be matched to the adjacent images, more precisely, the four groups of
three lines that are very close together can be used to estimate four corner
points on the image that can be matched to other images through ther spatial 
positions on the images. 

To find those points, we must first blurr the image so that the three lines that
are close together get merged into a single rectangle. For that a gaussian 
filter is applyed before thresholding for a lower percentile

    
![png](./report_images/output_32_0.png)
    


Now, thresholding the row and column percentages of white pixels to detect lines,
we can find the two biggest areas of rows of the image filled with white pixels and
estimate their centers. The same thing can be done for the image columns. After
detecting those centers, their intersections give a very good estimate of the
corners of the central big square

    
![png](./report_images/output_35_0.png)
    


Then computing the transformations that allow us to stitch them together, we
obtain the following results

    
![png](./report_images/output_38_1.png)
    


### Cell detection

After stitching the grid of images into a single image, the cells must be 
detected within it. To do that, since the cells have a circular shape, circle
detection is going to be used.

#### Gabor Annulus

This circle detection is performed by applying a Gabor Annulus filter to the 
image. This filter can be described by the following two equations

$G(r) = \frac{1}{2 \pi \sigma r_0}
e^{-\pi\left[\frac{(r-r_0)^2}{\sigma^2}\right]}e^{i2\pi f_0(r-r_0)}$

$r = \sqrt{{(x - x_0)}^2 {(y-y_0)}^2}$

and their visualization gives us

    
![png](./report_images/output_42_1.png)
    


After convolving it with the red channel of the image (The red channel is the 
one in which the cells are better highlighted) and taking the absolute values
of the complex evaluations of the image after this operation, it is possible
to see that the centers of the potetntial cells are depicted as particularly
bright points in the following heat map

    
![png](./report_images/output_44_1.png)
    


By looking at this image, it can be seen that through it the centers can be
detected through non maximum suppression an hysteresis threshold but the problem
is that together with the cells, there is still some noise from the background
grid and from the small white rectangles. 


This could interfere with the detection, so before applying the gabor annulus, 
the image is dilated with the following structure to obtain a binary mask that
will allow us to substitute the white color for the standard background color 
of the image.

    
![png](./report_images/output_46_1.png)
    

    
![png](./report_images/output_47_1.png)
    


After getting rid of the white rectangle, it is necessary to deal with the noise
caused by the background grid. For that, the magnitude of the gradient is 
thresholded to obtain the edges of the cells. Then, a close operation is executed
on the binary image with a big disk structure and, afterwards, a closing operation
is performed with a small disk structure to eliminate points that are too small
to be a circle. This way, we obtain the following binary mask.


    
![png](./report_images/output_49_1.png)
    


Which when multiplied by the result from the convolution of the gabor anulus and
the image without the white rectangle, returns only the regions that are of 
interest for the circle detection

    
![png](./report_images/output_51_1.png)
    


Thus, after applying non max suppression, hysteresis threshold and filtering
excessive overlays, we obtain the following detected cells

    
![png](./report_images/output_53_0.png)
    


### Cell classification

After detecting the cells, since the feature that better distinguishes the 
different cells is their color, only the mean pixel value of each RGB channel is 
utilized to build a features vector that represents how much each channel 
participates in the color of the cell. For that each features vector is divided
by the sum of its components.

This mean pixel value is taken over a window of radius 2 to make sure that the 
background colors aren't being too expressive on the values for smaller cells.
That is also the reason why a complete color histogram isn't utilized. The 
histogram would take into acoount the colors that are present in the background
and thus would end up adding noise to the feature we actually want to use for 
classification. 

For the classification algorithm, k-means cluster is utilized. To train it, the 
image formed by the grid stored in sequencia_1 is used as a training set and 
the test is done on the cells of the image taken from sequencia_2.

This way, in the end, the following results are obtained

#### sequencia_1

```
    ----------------------------------------------
    Estimated 838 (84.73%) Dead cells
    Silhouette coefficient: 0.7255728855941194
    ----------------------------------------------
    Estimated 151 (15.27%) Healthy cells
    Silhouette coefficient: 0.6717842143644754
```

![png](./outputs/training_set_result.jpg)


#### sequencia_2

```
----------------------------------------------
Estimated 133 (20.52%) Dead cells
Silhouette coefficient: 0.7043450440511143
----------------------------------------------
Estimated 515 (79.48%) Healthy cells
Silhouette coefficient: 0.8571111647946725
```

![png](./outputs/test_set_result.jpg)

It can be seen that almost all cells were detected and even though some dead
cells were recognized as alive cells, for the most part, the classification 
also obtained acceptable results.

## Runing the program
```
python program.py <images_grid_directory> <output_image_file_path>
```

## Dependencies
* numpy
* scipy
* cv2
* sklearn
* pickle
* pillow
