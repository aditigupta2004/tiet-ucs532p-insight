<<<<<<< HEAD
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
# Option 1: Python simple server
python -m http.server 8000
# Then open http://localhost:8000

## Project Overview

This site documents a classical computer vision project for parking slot occupancy detection using a single camera feed, frame differencing, CLAHE preprocessing, and polygon-based ROI analysis.

# Option 2: VS Code Live Server extension
# Right-click index.html → Open with Live Server
```

---

## 📋 Features

- ✅ Dark / light mode toggle (persisted in localStorage)
- ✅ Sticky sidebar with scroll-spy active state
- ✅ Mobile responsive (hamburger menu)
- ✅ No build step — pure HTML/CSS/JS
- ✅ GitHub Actions auto-deploy
- ✅ SEO meta tags (title, description, OG)
- ✅ Code syntax blocks with monospace fonts
- ✅ Gantt timeline, SMART objective cards, risk management cards
- ✅ Architecture diagram, tech stack grid, data tables

---

## 📄 License

MIT — free to use and adapt for your own academic projects.
