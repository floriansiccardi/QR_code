import cv2

def toBinary(number: int, bits=64) -> str:
    if number == 0:
        return '0' * bits
    binary = []
    while number > 0:
        binary.append(str(number % 2))
        number //= 2
    
    return '0' * (bits - len(binary)) + ''.join(binary[::-1])

def toNumber(binary: str) -> int:
    number = 0
    for i, b in enumerate(binary[::-1]):
        number += int(b) * 2 ** i
    return number

def plot(image):
    cv2.imshow("", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()