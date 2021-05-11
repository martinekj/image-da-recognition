import matplotlib
import matplotlib.pyplot as plt

from skimage.data import page
from skimage.filters import (threshold_niblack, threshold_sauvola)
from skimage import io
matplotlib.rcParams['font.size'] = 12
import cv2


def binarize_sauvola(image):
    #binarized_filename = input_image_filename.split(".")[0] + "_bin.png"

    # image = page()
    # image binarized_filename
    # image = io.imread(input_image_filename)

    # opening and grayscaling the image
    #image = cv2.imread(input_image_filename, cv2.IMREAD_GRAYSCALE)

    #thresh_niblack = threshold_niblack(image, k=0.8)
    thresh_sauvola = threshold_sauvola(image)

    #binary_niblack = image > thresh_niblack
    binary_sauvola = image > thresh_sauvola

    #binary_niblack = binary_niblack.astype(int)
    binary_sauvola = binary_sauvola.astype(int)

    #binary_niblack *= 255
    binary_sauvola *= 255

    # applying the binarization
    # image_bin = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    #cv2.imwrite("niblack.png", binary_niblack)
    cv2.imwrite("sauvola.png", binary_sauvola)

    #print("Binarization completed! Binarized image saved into ", binarized_filename)
    #return binarized_filename