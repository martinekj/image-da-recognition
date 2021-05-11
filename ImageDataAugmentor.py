import cv2
import numpy as np
import os
import img_utils
import sys


def create_augmented_folder(input_folder, output_folder):
    if os.path.exists(output_folder):
        print("Folder already exists!")
        exit(1)
    else:
        os.makedirs(output_folder)
        counter = 0
        for image_file in sorted(os.listdir(input_folder)):
            img = cv2.imread(os.path.join(input_folder, image_file), cv2.IMREAD_COLOR)
            img = img_utils.apply_random_rotation(img)
            img = img_utils.apply_blur(img)

            cv2.imwrite(os.path.join(output_folder, image_file), img)
            if counter % 100 == 0:
                print("Processed: ", counter, " (", counter / len(os.listdir(input_folder)), " % )")
            counter += 1



if __name__ == '__main__':
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    create_augmented_folder(input_folder=input_folder, output_folder=output_folder)