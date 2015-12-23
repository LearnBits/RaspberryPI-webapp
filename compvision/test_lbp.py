import os
import numpy as np
import cv2


class lbp_cascade():
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier('video_base/video_pkg/app/lbpcascades/lbpcascade_frontalface.xml')
        print os.getcwd()

    def detect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)


        result = {}
        return (img, result)
