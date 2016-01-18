from collections import deque
import numpy as np
import imutils
import cv2

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
BUFFER_SIZE = 32

class color_tracker:

	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space

	def __init__(self):
		# initialize the list of tracked points, the img self.counter,
		# and the coordinate deltas
		self.pts = deque(maxlen=BUFFER_SIZE)
		self.counter = 0
		(self.dX, self.dY) = (0, 0)
		self.direction = ""

	def process(self, img):

		# resize the img, blur it, and convert it to the HSV
		# color space
		#img = imutils.resize(img, width=600)
		blurred = cv2.GaussianBlur(img, (11, 11), 0)
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the img,
				# then update the list of tracked points
				cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 2)
				cv2.circle(img, center, 5, (0, 0, 255), -1)
				self.pts.appendleft(center)

		# loop over the set of tracked points
		for i in np.arange(1, len(self.pts)):
			# if either of the tracked points are None, ignore
			# them
			if self.pts[i - 1] is None or self.pts[i] is None:
				continue

			# check to see if enough points have been accumulated in
			# the buffer
			''' DK fixed a bug : added and len(self.pts) >= 10 '''
			#if self.counter >= 10 and i == 1 and self.pts[-10] is not None:
			if self.counter >= 10 and len(self.pts) >= 10 and i == 1 and len(self.pts) >= 10:
				# compute the difference between the x and y
				# coordinates and re-initialize the self.direction
				# text variables
				self.dX = self.pts[-10][0] - self.pts[i][0]
				self.dY = self.pts[-10][1] - self.pts[i][1]

				'''
				(dirX, dirY) = ("", "")

				# ensure there is significant movement in the
				# x-self.direction
				if np.abs(self.dX) > 20:
					dirX = "East" if np.sign(self.dX) == 1 else "West"

				# ensure there is significant movement in the
				# y-self.direction
				if np.abs(self.dY) > 20:
					dirY = "North" if np.sign(self.dY) == 1 else "South"

				# handle when both self.directions are non-empty
				if dirX != "" and dirY != "":
					self.direction = "{}-{}".format(dirY, dirX)

				# otherwise, only one self.direction is non-empty
				else:
					self.direction = dirX if dirX != "" else dirY
				'''
			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			#thickness = int(np.sqrt(BUFFER_SIZE / float(i + 1)) * 2.5)
			#cv2.line(img, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

		# show the movement deltas and the self.direction of movement on
		# the img
		#cv2.putText(img, self.direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 1)
		#cv2.putText(img, "dx: {}, dy: {}".format(self.dX, self.dY), (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		# show the img to our screen and increment the img self.counter
		self.counter += 1

		return (img, [self.dX, self.dY])
