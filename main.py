from DocumentWriter import DocumentWriter
import SimpleDactsSegmenter
import config

import sys


if __name__ == "__main__":
    conll_file = sys.argv[1]
    output_folder = sys.argv[2]

    doc_writer = DocumentWriter()
    doc_writer.create_dataset(conll_file)

    doc_writer.convert_to_images()

    input_folder = config.DATASET_NAME

    print("Performing segmentation")
    SimpleDactsSegmenter.process_folder(input_folder, output_folder)
    print("Done. The folder ", output_folder, " contains segmented text lines")

