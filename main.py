from preprocess import Preprocessor
import cv2
from background_subtraction import BackgroundSubtractor
import json
import numpy as np

cap = cv2.VideoCapture("videos/video1.mp4")
preprocessor = Preprocessor()
bg_subtractor = BackgroundSubtractor()

cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
cv2.namedWindow("Processed", cv2.WINDOW_NORMAL)
cv2.namedWindow("Foreground Mask", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Original", 600, 400)
cv2.resizeWindow("Processed", 600, 400)
cv2.resizeWindow("Foreground Mask", 600, 400)

with open("slots.json", "r") as f:
    slots = json.load(f)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    processed = preprocessor.process(frame)
    fg_mask = bg_subtractor.apply(processed)
    for slot in slots:
        mask = np.zeros_like(fg_mask)

        pts = np.array(slot, np.int32)

        # Fill slot area
        cv2.fillPoly(mask, [pts], 255)

        # Get only pixels inside slot
        slot_pixels = cv2.bitwise_and(fg_mask, fg_mask, mask=mask)

        # Calculate occupancy
        occupied_ratio = np.sum(slot_pixels) / (np.sum(mask) + 1)

        # Decide occupied or empty
        if occupied_ratio > 0.2:
            color = (0, 0, 255)  # Red = occupied
        else:
            color = (0, 255, 0)  # Green = empty

        # Draw slot
        cv2.polylines(frame, [pts], True, color, 2)


    cv2.imshow("Original", frame)
    cv2.imshow("Processed", processed)
    cv2.imshow("Foreground Mask", fg_mask)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
