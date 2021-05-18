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
1) Convert the content of conll file to the MS Word document
```python
python DocumentWriter.py tiny-test.conll
```
The MS Word document will be created (the name of the .docx is according to the dataset name in **config.py**)

*Optional step:* Add different background -- in **.docx** change the background by adding a watermark (Design tab --> select Watermark and follow instructions)

2) Convert the MS Word document to JPEG images of individual pages
```python
python DocumentWriter.py example-dataset.docx
```
If the input file has .docx or .doc extenstion the program convert this document to JPEG images of individual pages (the name of the folder is based on the information in **config.py**)

*Optional step:* Apply **ImageDataAugmentor.py** to enrich the dataset. It creates a second folder with the same content, but random transformations will be performed (random blurring and rotating) which will make the dataset more difficult. 
```python
python3 ImageDataAugmentor.py example-dataset 
```
The folder example-dataset_trans will be created.

3) Perform the segmentation into a text line images by **SimpleDactsSegmenter**
```python
python3 SimpleDactsSegmenter.py example-dataset output
```  

In the output folder there will be text line images of individual utterances based on the input **conll file**.
