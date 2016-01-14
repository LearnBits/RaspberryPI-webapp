import numpy as np
import cv2
from imutils.object_detection import non_max_suppression


class pedestrian(object):
    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, img):
        pedestrians = []
        result = {
            "pedestrians": pedestrians
        }
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        orig = img.copy()

        (rects, weights) = self.hog.detectMultiScale(img, winStride = (4, 4),
                                                     padding = (8, 8), scale = 1.1)

        # draw the original bounding boxes
        for (x, y, w, h) in rects:
            cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # apply non-maxima suppression to the bounding boxes using a
        # fairly large overlap threshold to try to maintain overlapping
        # boxes that are still people
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        pick = non_max_suppression(rects, probs = None, overlapThresh = 0.65)

        # draw the final bounding boxes
        for (xA, yA, xB, yB) in pick:
            cv2.rectangle(img, (xA, yA), (xB, yB), (0, 255, 0), 2)
            pedestrians.append({"xA": int(xA), "yA": int(yA), "xB": int(xB), "yB": int(yB)})


        # show some information on the number of bounding boxes
        # show the output images
        # cv2.imshow("Before NMS", orig)
        # cv2.imshow("After NMS", img)

        return (img, result)


