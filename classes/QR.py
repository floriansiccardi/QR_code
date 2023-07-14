import numpy as np
import random as rd
from .tools import toBinary, toNumber, plot
from .webcam import Webcam
import cv2

class QR:

    def __init__(self, name: str, key: int) -> None:
        self.name = name
        self.key = key
        self.binary = toBinary(number=self.key, bits=64)
        self._initImage()
    
    def _initImage(self, resolution=(600, 600)):
        self.image = np.ones(resolution, dtype=np.uint8) * 255
        step = (resolution[0] // 10, resolution[1] // 10)
        for i in range(1, 9):
            for j in range(1, 9):
                if self.binary[(i-1)*8+(j-1)] == '0':
                    self.image[i*step[0]:(i+1)*step[0], j*step[1]:(j+1)*step[1]] = 0
        start, stop = (round(step[1]/2), round(step[0]/2)), (round(9.5*step[1]), round(9.5*step[0]))
        for side in [start[0], stop[0]]:
            self.image[start[1]:stop[1], side-2:side+2] = 0
        for side in [start[1], stop[1]]:
            self.image[side-2:side+2, start[0]:stop[0]] = 0
    
    def show(self):
        cv2.imshow("QR code", self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save(self):
        cv2.imwrite(f"QR_{self.name}.jpg", self.image)


class Manager:

    def __init__(self, path='./data.txt', separator=':___:') -> None:
        self.path = path
        self.separator = separator
        self.existingKeys = []
        self._update()
    
    def _update(self):
        self.existingKeys = []
        with open(self.path, 'r') as file:
            for line in file:
                self.existingKeys.append(int(line.split(self.separator)[1]))
    
    def _add(self, qr: QR, data: str):
        existingLines = []
        with open(self.path, 'r') as file:
            for line in file:
                existingLines.append(line)
        with open(self.path, 'w') as file:
            for line in existingLines:
                file.write(line)
            file.write(f'\n{qr.name}{self.separator}{qr.key}{self.separator}{data}')
        self.existingKeys.append(qr.key)
    
    def _remove(self, key: int):
        existingLines, key = [], int(key)
        with open(self.path, 'r') as file:
            for line in file:
                if line.split(self.separator)[1] != key:
                    existingLines.append(line)
        with open(self.path, 'w') as file:
            for line in existingLines:
                file.write(line)
        self.existingKeys.remove(key)

    def _generateKey(self, bits=64) -> int:
        key = rd.randint(1, 2**bits)
        while key in self.existingKeys:
            key = rd.randint(1, 2**bits)
        self.existingKeys.append(key)
        return key

    def new(self, name, data):
        qr = QR(name=name, key=self._generateKey())
        self._add(qr=qr, data=data)
        return qr
    

class Reader:

    def __init__(self, webcam_index=0) -> None:
        self.webcam = Webcam(index=webcam_index)
    
    def _isolate(self, image: np.array) -> tuple:
        size = image.shape
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(image_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        size_min, sections, accuracy, rectangle = (size[0] // 6, size[1] // 6), [], [], []
        threshold = 0.02
        if len(contours) == 0:
            return None, None, None
        for ctr in contours:
            x, y, w, h = cv2.boundingRect(ctr)
            if w > size_min[0] and h > size_min[1]:
                section = image_gray[y:y+h, x:x+w]
                white = len(section[section > (1-threshold)*255])
                black = len(section[section < threshold*255])
                sections.append(section)
                accuracy.append((white + black) / (h*w))
                rectangle.append((x, y, w, h))
        
        i_max = np.array(accuracy).argmax()
        return sections[i_max], accuracy[i_max], rectangle[i_max]
    
    def _decode(self, image, shape=(8, 8)) -> str:
        binary = ''
        size = image.shape
        step = (size[0] // (shape[0]+1), size[1] // (shape[1]+1))
        image = image[step[1]//2:-step[1]//2, step[0]//2:-step[0]//2]
        for i in range(shape[0]):
            for j in range(shape[1]):
                rect = image[i*step[0]:(i+1)*step[0], j*step[1]:(j+1)*step[1]]
                binary += str(round(np.average(rect[2:-2, 2:-2]) / 255))
        return binary
                
        
    
    def read(self):
        found = False
        while not found:
            image = self.webcam.image()
            section, acc, rect = self._isolate(image=image)
            if not section is None:
                print(f"Précision = {round(100*acc)} %")
                x, y, w, h = rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow('Webcam', image)
        cv2.destroyAllWindows()
        return toNumber(self._decode(image=section))
