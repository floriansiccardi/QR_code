from src.QR import Manager, Reader
from src.webcam import Webcam
from src.tools import toBinary

manager = Manager()
reader = Reader()

print(reader.read())
