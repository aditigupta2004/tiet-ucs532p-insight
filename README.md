# Smart Parking Detection using Classical Computer Vision

This project aims to detect empty and occupied parking spaces using CCTV video feeds using classical computer vision techniques (no deep learning).

The system processes video frames, detects foreground objects (vehicles), and will further classify parking slots as occupied or vacant.

---

## STEP 1: VIDEO PREPROCESSING

This step performs basic preprocessing on video frames.

### Approach

- Convert frames to grayscale
- Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for contrast enhancement
- Apply Gaussian blur to reduce noise

### Output

- Original video frames
- Processed frames (grayscale + contrast enhanced + blurred)

### Files

- `main.py`: Runs the video loop and displays frames
- `preprocess.py`: Implements the preprocessing pipeline
- `videos/`: Contains input video (`video1.mp4`)

---

## STEP 2: BACKGROUND SUBTRACTION

This step detects moving objects (vehicles) using classical computer vision.

### Approach

- Uses MOG2 background subtraction
- Applies thresholding to remove shadows
- Applies morphological operations (opening and dilation) to remove noise

### Output

- Foreground mask:
  - White pixels represent moving objects (vehicles)
  - Black pixels represent background

### Files

- `background_subtraction.py`: Implements foreground detection
- Updated `main.py`: Integrates preprocessing with background subtraction

---

## PROJECT PIPELINE

Video Input  
Preprocessing  
Background Subtraction  
Parking Slot Detection (next step)  
Occupancy Classification  

---

## REQUIREMENTS

- Python 3.x
- OpenCV (`opencv-python`)

Install dependencies:

```bash
pip install opencv-python
```

---

## USAGE

1. Place your video file in:

```
videos/video1.mp4
```

2. Run the program:

```bash
python main.py
```

3. Controls:

- Press `q` to quit

---

## FUTURE WORK

- Parking slot detection using ROI (Region of Interest)
- Slot-wise occupancy classification
- Nearest parking slot recommendation
- Multi-camera support

---

## NOTES

- Ensure correct video path in `main.py`
- Works best with static CCTV cameras
- Uses only classical computer vision techniques
