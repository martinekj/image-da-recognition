# Image DA Recognition
This repository contains the scripts for the dataset creation for dialogue acts recognition using visual information. 
In this current form, the creation of 8 datasets with different background is supported.
The scripts are meant to support dialogue acts recognition, but they can be used for other text classification dataset as well (provided CONLL format).

## Requirements
- **python 3.x**
- text dataset (since datasets for DA recognition are often in CONLL files, the CONLL format is required)
### Libraries
- opencv-python
- skimage (skimage.filters for performing Sauvola thresholding)
- docx
- docx2pdf (only for Windows)
- pdf2image
- shutil


## Scripts

### Fundamental scripts and files
- main.py
- SimpleDactsSegmenter
- 

Some scripts may produce auxiliary and temporary files such as visualization images etc.

## SimpleDactsSegmenter
Simple yet efficient segmenter of utterances based on profile algorithm
The segmenter can be run independently as follows:
```python
python3 SimpleDactsSegmenter.py <path_to_corpus> <output_folder>
```


## How to Run
```python
python main.py
