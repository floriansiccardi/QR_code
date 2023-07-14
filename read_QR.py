from classes.QR import Manager, Reader
from classes.webcam import Webcam
from classes.tools import toBinary

manager = Manager()
reader = Reader()

print(reader.read())