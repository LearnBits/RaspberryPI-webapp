from PIL import Image
import numpy as np
import cv2

__author__ = 'yonatan'
__project__ = 'video_base'


#class image_converter(object):
#    def __init__(self):
#        pass

def array2jpegBuffer(image):
    img_str = cv2.imencode('.jpg', image)[1].tostring()
    return img_str

def array2PIL(arr, size):
    mode = 'RGBA'
    arr = arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])
    if len(arr[0]) == 3:
        arr = np.c_[arr, 255 * np.ones((len(arr), 1), np.uint8)]
    return Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)
