import cv2
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import img_utils
import shutil
from binarizer import binarize_sauvola

### simple dacts segmenter based on profile algorithm

bounding_box_vertical_margin = 5
connected_components_area_threshold = 500
da_separator_white_margin = 60

global last_component_y_coord

def is_filtered_out(component, whole_img):
    area = component[cv2.CC_STAT_AREA]

    # filter out too small components
    if area < connected_components_area_threshold:
        return True

    # filter out components with height >raw width and also height should be around 50
    if component[cv2.CC_STAT_WIDTH] < component[cv2.CC_STAT_HEIGHT]:
        return True

    #print("Component height: ", component[cv2.CC_STAT_HEIGHT])
    if component[cv2.CC_STAT_HEIGHT] < 10 or component[cv2.CC_STAT_HEIGHT] > 70:
        #print(component[cv2.CC_STAT_HEIGHT])
        return True

    # filter out corner (left/top) component
    # print(component[cv2.CC_STAT_LEFT])
    if component[cv2.CC_STAT_LEFT] < 10:
        return True

    # remove components where the any pixel of bottom (top) border is black (noisy component)
    start_point = (component[cv2.CC_STAT_LEFT], component[cv2.CC_STAT_TOP] - bounding_box_vertical_margin)
    end_point = (component[cv2.CC_STAT_LEFT] + component[cv2.CC_STAT_WIDTH],
                 component[cv2.CC_STAT_TOP] + component[cv2.CC_STAT_HEIGHT] + bounding_box_vertical_margin)

    start_cropped_bounding_box = whole_img[start_point[1]:end_point[1], start_point[0]:end_point[0]].copy()
    # cv2.imshow("problematic component", start_cropped_bounding_box)
    # cv2.waitKey(0)

    start_cropped_bounding_box[start_cropped_bounding_box == 0] = 1
    start_cropped_bounding_box[start_cropped_bounding_box == 255] = 0
    bottom_border_black_pixels = np.sum(start_cropped_bounding_box[-1], axis=0)
    # print(bottom_border_black_pixels)
    if area < connected_components_area_threshold * 1.25 and bottom_border_black_pixels > 10:
        return True

    return False


class SimpleDactsSegmenter:
    def __init__(self, input_img_path, output_folder):
        self.input_img_path = input_img_path
        self.output_folder = output_folder
        # load grayscale image
        self.grayscale_img = cv2.imread(self.input_img_path, cv2.IMREAD_GRAYSCALE)
        self.colored_img = cv2.imread(self.input_img_path, cv2.IMREAD_COLOR)


    def segment(self):
        # print("Performing segmentation")
        # binarize image
        # cv2.imshow("Grayscale img", self.img)
        # cv2.waitKey(0)
        # _, bin_img = cv2.threshold(self.grayscale_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        binarize_sauvola(self.grayscale_img)
        bin_sauvola = cv2.imread("sauvola.png", cv2.IMREAD_GRAYSCALE)

        # cv2.imshow("Binarized image Sauvola",  bin_sauvola)
        # cv2.waitKey(0)

        inverted_bin_img = cv2.bitwise_not(bin_sauvola)
        cv2.imwrite("components_binarized_image.png", inverted_bin_img)
        # cv2.imshow("Binarized image", inverted_bin_img)
        # cv2.waitKey(0)

        #kernel = np.ones((1, 5), 'uint8')
        kernel = np.ones((1, 12))
        dilated_img = cv2.dilate(inverted_bin_img, kernel, iterations=2)

        original_masked_image = np.zeros(shape=dilated_img.shape)
        masked_image = np.zeros(shape=dilated_img.shape)

        # Labels is a matrix the size of the input image where each element has a value equal to its label.
        # Stats is a matrix of the stats that  the function  calculates.It has a length equal to the number of
        # labels and a width equal to the  number of stats.

        nb_components, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated_img, connectivity=8)
        counter = 0

        i = 0
        while i < nb_components:
            if i == 0:
                i += 1
                continue
            # lets label the mask
            original_masked_image[labels == i] = 255
            i += 1

        # filter out component, then do process
        valid_component_list = []
        valid_label_list = []
        for i in range(0, nb_components):
            component = stats[i]
            if is_filtered_out(component, bin_sauvola):
                # mark component in label matrix
                labels[labels == i] = 0
                continue
            else:
                valid_component_list.append(component)

        # determine if any valid components need to be merged (two divided components)
        previous_y_coord = -1
        for component in valid_component_list:
            if previous_y_coord == -1:
                previous_y_coord = component[cv2.CC_STAT_TOP]
                continue
            # if abs(previous_y_coord - component[cv2.CC_STAT_TOP]) < 40:
                #print("Find candidate for merging. Skipping")
                #print(self.input_img_path)
            else:
                previous_y_coord = component[cv2.CC_STAT_TOP]

        nb_components = len(valid_component_list)
        stats = valid_component_list

        i = 0
        while i < nb_components:
            labels[labels == i] = 0
            # lets label the mask
            masked_image[labels == i] = 255
            i += 1

        i = 0
        while i < nb_components:
            sub_counter = 1
            multiple_rows_da = False
            start_point = (stats[i][cv2.CC_STAT_LEFT], stats[i][cv2.CC_STAT_TOP] - bounding_box_vertical_margin)
            end_point = (stats[i][cv2.CC_STAT_LEFT] + stats[i][cv2.CC_STAT_WIDTH], stats[i][cv2.CC_STAT_TOP] + stats[i][cv2.CC_STAT_HEIGHT] + bounding_box_vertical_margin)

            # check if it is only one component -- aka utterance in page
            if i + 1 >= len(stats):
                output_img_filename = os.path.join(self.output_folder, os.path.basename(self.input_img_path).replace(".jpg", "_") + str(counter).zfill(3) + ".png")
                start_cropped_bounding_box = self.grayscale_img[start_point[1]:end_point[1],start_point[0]:end_point[0]].copy()
                cv2.imwrite(output_img_filename, start_cropped_bounding_box)
                # draw bounding boxes
                img_utils.draw_bounding_box(self.colored_img, start_point, end_point)
                # draw start point
                img_utils.draw_point(self.colored_img, x=start_point[0], y=start_point[1])

            # check also following (i+1)th component if and check y coords distance difference --> DACTS continue
            # watch the last item in the list
            j = i + 1
            while j < nb_components:
                # filter out too small components
                following_area = stats[j][cv2.CC_STAT_AREA]

                #print("Component i: ", i, "Component j: ", j)
                # cv2.imshow("Start bounding box", start_cropped_bounding_box)
                # cv2.waitKey(0)

                if sub_counter == 1:
                    current_start_point = start_point
                    current_end_point = end_point
                else:
                    current_start_point = (stats[j - 1][cv2.CC_STAT_LEFT], stats[j - 1][cv2.CC_STAT_TOP] - bounding_box_vertical_margin)
                    current_end_point = (stats[j - 1][cv2.CC_STAT_LEFT] + stats[j - 1][cv2.CC_STAT_WIDTH], stats[j - 1][cv2.CC_STAT_TOP] + stats[j - 1][cv2.CC_STAT_HEIGHT ]+ bounding_box_vertical_margin)

                following_start_point = (stats[j][cv2.CC_STAT_LEFT], stats[j][cv2.CC_STAT_TOP] - bounding_box_vertical_margin)
                following_end_point = (stats[j][cv2.CC_STAT_LEFT] + stats[j][cv2.CC_STAT_WIDTH], stats[j][cv2.CC_STAT_TOP] + stats[j][cv2.CC_STAT_HEIGHT] + bounding_box_vertical_margin)

                # check y-coord difference (cca 65 px next da and 35 px same da) and/or x-coord of current and following start point
                # print(following_start_point[1] - current_start_point[1])
                # if abs(following_start_point[0] - current_start_point[0]) > 6:
                if (following_start_point[1] - current_start_point[1] < da_separator_white_margin):

                    #always store first
                    # draw bounding box and start_poin
                    img_utils.draw_bounding_box(self.colored_img, current_start_point, current_end_point)
                    img_utils.draw_point(self.colored_img, x=current_start_point[0], y=current_start_point[1])
                    output_img_filename = os.path.join(self.output_folder, os.path.basename(self.input_img_path).replace(".jpg", "_") + str(counter).zfill(3) + "_part" + str(0).zfill(3) + ".png")
                    cv2.imwrite(output_img_filename, self.grayscale_img[current_start_point[1]:current_end_point[1], current_start_point[0]:current_end_point[0]].copy())

                    # da continue
                    multiple_rows_da = True
                    start_cropped_bounding_box = self.grayscale_img[following_start_point[1]:following_end_point[1], following_start_point[0]:following_end_point[0]].copy()
                    # draw bounding box and start_poin
                    img_utils.draw_bounding_box(self.colored_img, following_start_point, following_end_point)
                    img_utils.draw_point(self.colored_img, x=following_start_point[0], y=following_start_point[1])
                    output_img_filename = os.path.join(self.output_folder, os.path.basename(self.input_img_path).replace(".jpg", "_")+ str(counter).zfill(3)+"_part"+str(sub_counter).zfill(3)+ ".png")
                    i = j

                    cv2.imwrite(output_img_filename, start_cropped_bounding_box)
                    sub_counter += 1

                else:
                    # crop boudning boxes and store them as individual images
                    cropped_bounding_box = self.grayscale_img[start_point[1]:end_point[1],start_point[0]:end_point[0]].copy()
                    # draw bounding boxes
                    img_utils.draw_bounding_box(self.colored_img, start_point, end_point)
                    # draw start point
                    img_utils.draw_point(self.colored_img, x=start_point[0], y=start_point[1])

                    if multiple_rows_da:
                        # save the beggining part of da.
                        output_img_filename = os.path.join(self.output_folder, os.path.basename(self.input_img_path).replace(".jpg", "_")+ str(counter).zfill(3) + "_part000.png")
                    else:
                        output_img_filename = os.path.join(self.output_folder, os.path.basename(self.input_img_path).replace(".jpg", "_")+ str(counter).zfill(3) + ".png")
                    cv2.imwrite(output_img_filename, cropped_bounding_box)
                    # cv2.imshow("Cropped bounding box", cropped_bounding_box)
                    # cv2.waitKey(0)

                    break
                j += 1
            i += 1
            counter += 1

            #print("Component -- Start point: ", start_point, " End point: ", end_point, " Area: ", area)



        cv2.imwrite("components_bounding_boxes.png", self.colored_img)
        cv2.imwrite("components.png", masked_image)
        cv2.imwrite("components_original.png", original_masked_image)

        return self.colored_img

def process_folder(input_folder, output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        os.makedirs(output_folder)
    else:
        os.makedirs(output_folder)

    counter = 1
    for image_file in sorted(os.listdir(input_folder)):
        #print(image_file)
        # print(os.path.join(input_folder, image_file))
        segmenter = SimpleDactsSegmenter(os.path.join(input_folder, image_file), output_folder)
        bounding_box_image = segmenter.segment()

        if counter % 10 == 0:
            print("File: ", image_file)
            print("Current number of segmented utterances:", str(len(os.listdir(output_folder))))
        counter += 1

    print("-------------------------------------------")
    print("Number of segmented utterances: ", str(len(os.listdir(output_folder))))


if __name__ == '__main__':

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    print(input_folder)
    process_folder(input_folder, output_folder)



