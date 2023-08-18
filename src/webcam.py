import numpy as np
import cv2

class Webcam:

    def __init__(self, index=0) -> None:
        self.open(index=index)
    
    def __del__(self):
        self.capture.release()

    def open(self, index=0):
        try:
            self.capture = cv2.VideoCapture(index)
        except:
            print('Camera not found')
    
    def image(self) -> np.array:
        ret, frame = self.capture.read()
        return frame
    
    def show(self):
        cv2.imshow("Camera", self.image())
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def save(self):
        cv2.imwrite("capture_000.jpg", self.image())

