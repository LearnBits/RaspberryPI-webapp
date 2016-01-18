import numpy as np
import cv2
from os import path

cur_path = path.dirname(path.abspath(__file__))
fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.3
text_bg_color = (244, 244, 244)


class haar_cascade():
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(path.join(cur_path, 'haarcascades', 'haarcascade_frontalface_default.xml'))
        #self.eye_cascade =cv2.CascadeClassifier(path.join(cur_path, 'haarcascades', 'haarcascade_eye.xml'))

    def process(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(img_gray, 1.3, 5)
        self.decorate(img, faces)
        return (img, faces.tolist()[0] if len(faces) > 0 else [])

    def decorate(self, img, faces):
        def put_boxed_text(text, x, y, color):
            size, baseline = cv2.getTextSize(text, fontFace, fontScale, 1)
            x -= size[0]/2
            y += size[1]/2
            cv2.rectangle(img, (x, y + baseline), (x + size[0], y - size[1]), text_bg_color, -1)
            cv2.putText(img, text, (x, y), fontFace, fontScale, color, 1)
        #
        for (x, y, w, h) in faces:
            # bounding rectangle
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # write rectangle info
            put_boxed_text('(%d,%d)' % (x,y), x, y, (139, 0, 139))
            put_boxed_text(str(w), x+w/2, y+h, (0, 0, 255))
            put_boxed_text(str(h), x+w, y+h/2, (0, 0, 255))


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
