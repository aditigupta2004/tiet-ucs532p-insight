# Video Preprocessing Demo

This project demonstrates basic video frame preprocessing with OpenCV. It reads a video file, converts frames to grayscale, optionally applies CLAHE for contrast enhancement, and then applies Gaussian blur. The original and processed frames are displayed side by side.

## Files

- `main.py`: Runs the video loop and displays original vs processed frames.
- `preprocess.py`: Implements the `Preprocessor` class with grayscale, CLAHE, and blur steps.
- `videos/`: Place your input video files here (expects `video1.mp4`).

## Requirements

- Python 3.x
- OpenCV (`opencv-python`)

Install dependencies:

```bash
pip install opencv-python
```

## Usage

1. Put your video file at `videos/video1.mp4`.
2. Run the script:

```bash
python main.py
```

Controls:

- Press `q` to quit the video window.

## Configuration

You can change preprocessing settings by editing `Preprocessor` in `preprocess.py`:

- `blur_kernel`: Gaussian blur kernel size (default `(5, 5)`).
- `use_clahe`: Enable or disable CLAHE (default `True`).

Example:

```python
preprocessor = Preprocessor(blur_kernel=(7, 7), use_clahe=False)
```

## Notes

- If the video does not open, check the path and file name in `main.py`.
- Press `q` while the window is focused to exit.
