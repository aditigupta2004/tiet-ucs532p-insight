# Parking Slot Occupancy Detection Using Classical Computer Vision

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

This project detects whether parking slots are free or occupied from a fixed CCTV-style video feed, using image processing only (no deep learning model).

The system works by comparing each slot region in the current frame with a stored reference image that represents that slot when it is empty.

---

## What You Get

- Manual slot annotation tool with occupancy labeling
- Frame preprocessing for stable comparison
- Slot-wise occupancy detection and on-screen HUD
- Debug runtime to inspect slot references and pixel differences

---

## End-to-End Pipeline

1. Load video frame.
2. Preprocess frame (grayscale, CLAHE, blur).
3. For each annotated slot polygon:
   - Create binary mask for that slot area.
   - Compare current processed frame against that slot's stored empty reference.
   - Count changed pixels inside the slot mask.
   - Convert changed pixels to ratio of slot area.
4. If ratio is above threshold, mark slot as occupied, else free.
5. Draw slot outlines and show overall counts.

---

## Project Files Explained

### preprocess.py

Contains class `Preprocessor`.

Frame operations:
- Convert BGR to grayscale
- Apply CLAHE for local contrast improvement
- Apply Gaussian blur to reduce high-frequency noise

Output:
- One processed single-channel image used by detection logic.

### background_subtraction.py

Contains class `BackgroundSubtractor`.

Operations:
- MOG2 foreground extraction
- Shadow removal (thresholding)
- Morphological cleanup (open + dilate)

Current status:
- Implemented and usable, but not currently consumed in the `main.py` and `main_ref.py` runtime decision path.

### slot_annotation.py

Interactive annotation tool for creating parking slots from the first frame of `videos/video1.mp4`.

Workflow:
1. Click 4 points for one slot polygon.
2. Press `1` if currently occupied or `0` if currently empty.
3. Repeat for all slots.
4. Press `s` to save into `slots.json`.

Controls:
- Left click: add point (up to 4 for current slot)
- `u`: undo last point
- `d`: delete last saved slot
- `r`: reset all slots
- `s`: save slots
- `q`: quit

Saved format per slot:
- `points`: list of 4 `[x, y]` coordinates
- `occupied`: initial state (`0` free, `1` occupied)

### slots.json

Persistent storage of all annotated slots.

Used by:
- `main.py`
- `main_ref.py`

### main.py

Primary runtime application.

What it does:
- Opens `videos/video1.mp4`
- Loads slots from `slots.json`
- Initializes slot reference frames
- Runs occupancy detection every frame
- Draws color-coded slot boundaries and HUD counts

Color convention:
- Green: free
- Red: occupied

Reference initialization logic:
- If a slot is initially marked free in `slots.json`, first processed frame is used as empty reference.
- If a slot is initially marked occupied, reference starts as `None` and fallback state is used until logic updates.

### main_ref.py

Debug version of `main.py` with extra windows for explainability.

Additional windows:
- `Reference Frames`: current stored empty reference image for each slot
- `Diff View`: amplified absolute difference against reference for each slot

Use this file when tuning thresholds or diagnosing wrong occupancy behavior.

### videos/

Input video folder.
Expected default file: `videos/video1.mp4`.

### screenshots/

Reference outputs used in documentation.

---

## Occupancy Decision Rule

Both `main.py` and `main_ref.py` use these constants:

- `DIFF_THRESHOLD = 30`
- `OCCUPANCY_RATIO = 0.25`

Per slot:

1. `diff = abs(current_processed - slot_reference)`
2. Keep only slot pixels using mask.
3. `changed_pixels = count(diff > DIFF_THRESHOLD)`
4. `ratio = changed_pixels / slot_area`
5. Occupied if `ratio > OCCUPANCY_RATIO`

---

## Installation

Requirements:
- Python 3.x
- OpenCV
- NumPy

Install:

```bash
pip install opencv-python numpy
```

---

## Run Guide

### 1) Prepare video

Place your footage at:

```text
videos/video1.mp4
```

### 2) Annotate slots

```bash
python slot_annotation.py
```

After annotation, save with `s`.

### 3) Run main detector

```bash
python main.py
```

### 4) Run debug detector (optional)

```bash
python main_ref.py
```

Quit windows with `q`.

---

## Known Limitations

- Camera shake or large lighting changes can affect pixel-difference logic.
- Slots initially marked occupied do not begin with an empty reference image.
- Annotation point order is user-dependent; inconsistent ordering can degrade ROI quality.
