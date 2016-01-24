from sklearn.externals import joblib
from pyimagesearch.hog import HOG
from pyimagesearch import dataset
import mahotas
import cv2
from os import path

# load the model
cur_path = path.dirname(path.abspath(__file__))

class svm_digits_classifier:
	def __init__(self):
		self.model = joblib.load(path.join(cur_path, 'digit-svm-model', 'svm.cpickle.dk'))
		# initialize the HOG descriptor
		self.hog = HOG(orientations = 18, pixelsPerCell = (10, 10), cellsPerBlock = (1, 1), normalize = True)

	def process(self, img):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		# blur the image, find edges, and then find contours along the edged regions
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
		edged = cv2.Canny(blurred, 30, 150)
		(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# sort the contours by their x-axis position, ensuring
		# that we read the numbers from left to right
		cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in cnts], key = lambda x: x[1])

		# loop over the contours
		res = []
		for (c, _) in cnts:
			# compute the bounding box for the rectangle
			(x, y, w, h) = cv2.boundingRect(c)
			#print('Started contour %d' % digit_count)

			# if the width is at least 7 pixels and the height
			# is at least 20 pixels, the contour is likely a digit
			if w >= 7 and h >= 20:
				# crop the ROI and then threshold the grayscale
				# ROI to reveal the digit
				roi = gray[y:y + h, x:x + w]
				thresh = roi.copy()
				T = mahotas.thresholding.otsu(roi)
				thresh[thresh > T] = 255
				thresh = cv2.bitwise_not(thresh)
				# deskew the image center its extent
				thresh = dataset.deskew(thresh, 20)
				thresh = dataset.center_extent(thresh, (20, 20))

				#cv2.imshow("thresh", thresh)

				# extract features from the image and classify it
				hist = hog.describe(thresh)
				digit = model.predict(hist)[0]
				res.append((digit, (x,y,w,h)))
				#print("I think that number is: {}".format(digit))

		self.decorate(img, res)
		return res

	def decorate(self, img, res):
		for d in res:
			digit = d[0]
			(x,y,w,h) = d[1]
			# draw a rectangle around the digit, the show what the digit was classified as
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
			cv2.putText(image, str(digit), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
