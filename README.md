# Beer-Challenge-by-Visio

## Abstract
Measuring the quality of beer is an important task in industrial
scale fermentation processes. To do that, a lot of times, the 
proportion of alive and dead yeast cells is used as the parameter 
that indicates this quality measurement quantitatively. The procedure 
utilized for analysing this number involves the dilution of a sample
of the fermentation with brothymol blue in a Neubauer's chamber and the 
posterior counting of the number of alive cells and the number of dead
cells through microscopic observation.

With that in mind, the objective of this challenge is to develop 
an image processing method that is capable of recieving as 
input the microscopic images taken from the Neubauer's chamber and
segment it so that alive and dead cells can be differentiated and counted.
Also, since a single microscopic image can't cover the entirety of the 
sample that is under observation, multiple images have to be taken with
different parts of the sample in the center of the chamber. Thus, to 
get a more accurate estimate of the beer quality, the images that 
were taken from the same sample must be used to reconstruct an image 
that represents the entire sample.
