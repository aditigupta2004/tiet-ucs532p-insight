import cv2


class Preprocessor:

    def __init__(self, blur_kernel=(5, 5), use_clahe=True):
        self.blur_kernel = blur_kernel
        self.use_clahe = use_clahe

    def apply_clahe(self, gray_frame):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray_frame)

    def process(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.use_clahe:
            gray = self.apply_clahe(gray)

        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)

        return blurred
