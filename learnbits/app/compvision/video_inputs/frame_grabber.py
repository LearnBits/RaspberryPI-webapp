__author__ = 'amitay dobo'


def webcam_frame_grabber(process):

	import cv2

	def gen():
  		while not process.done():
			grabbed, frame = process.camera.read()
			frame = cv2.resize(frame, process.frameResize)
			frame = cv2.flip(frame, 1)
			yield frame

  	return gen


def picamera_frame_grabber(process):

	import picamera, cv2
	from picamera.array import PiRGBArray

	process.camera.resolution = (1296, 730) # (640, 480)
	process.camera.frameRate = 20 # 32
	imageResize = (324, 182)
	imageSizeTuple = imageResize[::-1] + (3,)
	#image = numpy.zeros(imageSizeTuple, dtype = "uint8")
	rawCapture = PiRGBArray(process.camera, size = imageResize)

	def gen():
		for frame in process.camera.capture_continuous(rawCapture, format='bgr', resize=imageResize, use_video_port=True):
			# clear the stream in preparation for the next frame
			if process.done(): break
			rawCapture.truncate(0)
			# grab the raw NumPy array representing the image, then place it in pool
			frame = cv2.flip(frame.array, 1)
			yield frame

  	return gen
