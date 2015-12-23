import sys
import time
import numpy as np
import cv2
import picamera
from picamera.array import PiRGBArray

# camera parameters
camResolution = (1296, 730)
camFrameRate = 20
camFormat = "bgr"

def frame_grabber(imageResizeSize):
    imageSizeTuple = imageResizeSize[::-1] + (3,)
    image = np.zeros(imageSizeTuple, dtype = "uint8")

    print "pi_camera_thread started"
    # capture frames from the camera

    def gen():

    with picamera.PiCamera() as camera:
        camera.resolution = camResolution
        camera.framerate = camFrameRate

        # Allow camera to wake up
        time.sleep(0.1)

        with picamera.array.PiRGBArray(camera, size = imageResizeSize) as rawCapture:
            for frame in camera.capture_continuous(rawCapture, format = camFormat, resize = imageResizeSize, use_video_port = True):
                # clear the stream in preparation for the next frame
                rawCapture.truncate(0)
                self.streamFrameNum += 1

                # grab the raw NumPy array representing the image, then place it in pool
                image = frame.array
                yield image


    return gen