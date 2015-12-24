import numpy as np
import cv2
from os import path
cur_path = path.dirname(path.abspath(__file__))


class haar_cascade():
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(path.join(cur_path, 'haarcascades', 'haarcascade_frontalface_default.xml'))
        #self.eye_cascade =cv2.CascadeClassifier(path.join(cur_path, 'haarcascades', 'haarcascade_eye.xml'))

    def detect(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(img_gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return (img, faces)

        '''	# I removed the eyes detector #
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            result_faces.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

        result = {
            "faces": result_faces
        }'''
