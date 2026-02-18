from preprocess import Preprocessor
import cv2

cap = cv2.VideoCapture("videos\\video1.mp4")
preprocessor = Preprocessor()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    processed = preprocessor.process(frame)

    cv2.imshow("Original", frame)
    cv2.imshow("Processed", processed)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
