import cv2
import numpy as np
import config
import random
import imutils

def add_white_padding(img):
    h, w = img.shape[0:2]
    padded_img_width = config.DACTS_IMG_WIDTH - w
    if padded_img_width <= 0:
        # print("Return none (", w, "  --  ", padded_img_width)
        return None
    else:
        padded_img = np.ones(shape=(config.DACTS_IMG_HEIGHT, padded_img_width))
        padded_img *= 255
        padded_img = np.concatenate((img, padded_img), axis=1)

        return padded_img


def resize_image(img):
    h, w = img.shape[0:2]
    newH = config.DACTS_IMG_HEIGHT
    ratio = newH / h
    newW = int(w * ratio)
    img = cv2.resize(img, dsize=(newW, newH))
    return img

def draw_point(img, x, y):
    cv2.line(img, (int(x)-10,int(y)-10), (int(x)+10, int(y)+10), (0, 0, 255), 1)
    cv2.line(img, (int(x) - 10, int(y) + 10), (int(x) + 10, int(y) - 10), (0, 0, 255), 1)


def draw_bounding_box(img, start_point, end_point, random_color=True):
    if random_color:
        color = list(np.random.random(size=3) * 255)
    else:
        color = (0, 255, 0)
    cv2.rectangle(img, start_point, end_point, color=color, thickness=1)


def apply_blur(img):
    #img = cv2.imread("EN_test_dataset_noise_3\\image00001.jpg", cv2.IMREAD_GRAYSCALE)
    median_blur = cv2.medianBlur(img, ksize=3)
    combined_blur = cv2.GaussianBlur(median_blur, (9, 9), 0)
    return combined_blur

def apply_random_rotation(img):
    rdn = random.random()
    if rdn >= 0.5:
        degrees = 0.5
        if rdn >= 0.75:
            img = imutils.rotate(img, angle=degrees)
        else:
            img = imutils.rotate(img, angle=-degrees)
    return img

def canny_edge_detection(img):
    print(img.shape)
    edges = cv2.Canny(img.astype(np.uint8), 100, 200)
    show_image(edges)

def apply_sobel_filter(img):
    ddepth = cv2.CV_8U
    scale = 1
    delta = 0

    grad_x = cv2.Sobel(img, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    # Gradient-Y
    # grad_y = cv.Scharr(gray,ddepth,0,1)
    grad_y = cv2.Sobel(img, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)


    #converting back to  CV_8U
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    #gradient approximation
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

    sobel_image = grad
    #_, sobel_image = cv2.threshold(sobel_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return sobel_image


def show_image(img):
    cv2.imshow("image", img)
    cv2.waitKey(0)


def createProfileVisualization(profile):
    visu = np.zeros((200, profile.shape[0]), dtype=np.uint8)
    mmin = np.min(profile)
    mmax = np.max(profile)
    print("mmax, mmin:", mmax, mmin)
    if mmax - mmin == 0:
        return visu
    prof = (profile - mmin) * 200 / (mmax - mmin)
    for i in range(prof.shape[0]):
        for j in range(int(prof[i])):
            visu[199 - j, i] = 255
    return visu