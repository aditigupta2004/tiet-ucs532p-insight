from preprocess import Preprocessor
import cv2
from background_subtraction import BackgroundSubtractor

cap = cv2.VideoCapture("videos/video1.mp4")
preprocessor = Preprocessor()
bg_subtractor = BackgroundSubtractor()

cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
cv2.namedWindow("Processed", cv2.WINDOW_NORMAL)
cv2.namedWindow("Foreground Mask", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Original", 600, 400)
cv2.resizeWindow("Processed", 600, 400)
cv2.resizeWindow("Foreground Mask", 600, 400)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    processed = preprocessor.process(frame)
    fg_mask = bg_subtractor.apply(processed)

    cv2.imshow("Original", frame)
    cv2.imshow("Processed", processed)
    cv2.imshow("Foreground Mask", fg_mask)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
