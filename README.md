# lab2: Webcam image collection for finger counting classifier

## Ultimate goal
In the coming three labs, we would like to build a Tkinter GUI application that can recognize finger counting for digits from 1 to 5. The final applictation will capture images form a webcam and display the finger count as a string overlay. We will proceed in 3 steps:
1. Lab2: Data acquisition from webcam: Build a GUI application to acquire image data.
2. Lab3: Train a fastai learner to recognize the 5 finger counts.
3. Lab4: Wrap the model in a GUI application to predict digits from live webcam stream.

We will use the [American counting system](https://en.wikipedia.org/wiki/Finger-counting#Western_world)

## Lab2 Goal
In a first step, we would like to collect training image data for each of the 5 finger counts.

Implement a Tkinter GUI application with the following specifications:
1. The application is started from the command line, with the option to pass a path to the folder where images are saved. If this argument is missing, the current folder is used.
2. The application checks if folder exists and creates it if it does not exist.
3. The application opens the webcam (with OpenCV) and displays images in regular intervals.
4. The application has a 'Save' button. When clicked, the current image is saved to the destination folder using eight-place number format, e.g. `00000000.jpg`.
5. Subsequent images are saved by increasing the filename numbering by 1, e.g. `00000002.jpg` for the second image, etc.
6. When the application starts, the destination folder is searched for existing images. The highest number present (+1) initializes the counter. Consecutive use of the application with the same destination folder will not overwrite existing images.
7. (optional) The application has a 'burst' button that saves a series of 10 images in 1/2-second intervals.
8. (optional) Provide functionality to change destination folder from the running GUI.

The file `lab2_image_capture_gui.py` contains some starter code to be extended.

Collect at least 40 training, and 10 valiation images for each digit with variations. Use the following directory structure:
```
train
  |--one
  |  |-- 00000000.jpg
  |  ...
  |--two
  |  |-- 00000000.jpg
  |  ...
  ...
valid
  |--one
  |  |-- 00000000.jpg
  |  ...
  |--two
  |  |-- 00000000.jpg
  |  ...
  ...
```
To start the gui, you can run the program with the following command in a Jupyter notebook cell:
```
!python lab2_image_capture_gui.py -o digits/train/one/
```
This will save training images of finger count one.

All images will be used in Lab3 to train/validate your model.

In the notebook `lab2-display_batch.ipynb`, use a fastai `DataLoader()` to load in the data and display 25 images of a training and validation batch.

## What to hand in
- Complete implementation in `lab2_image_capture_gui.py` according to the specifications.
- In the Jupyter notebook `lab2-display_batch.ipynb`:
  - implement the steps indicated.
  - answer questions.
  - complete *Reflection*
- Keep code clean, comment/document and remove any unnecessary cells in the notebook.

During development, save progress with git and use descriptive commit messages.

Hand in: git push `lab2_image_capture_gui.py` and `lab2-display_batch.ipynb`, verify on github, submit url on D2L.

**Important:** Do **not** commit image data to github. Images do **not** need to be handed in.

## Rubric change for lab2
Because this lab has more coding, less interpretation, points from Section 4. Conclusion (3pt) will be reallocated to Section 2. Functionality for a total of 6pts in this category.
