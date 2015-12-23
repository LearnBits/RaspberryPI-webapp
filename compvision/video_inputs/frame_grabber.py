__author__ = 'amitay dobo'


def webcam_frame_grabber(process):

	import time, cv2

	def gen():
  		while not process.done():
			grabbed, frame = process.camera.read()
			frame = cv2.resize(frame, process.frameResize)
			yield frame

  	return gen


def picamera_frame_grabber(process):
	'''
	import time, cv2, numpy, picamera
	from picamera.array import PiRGBArray

	resolution = (1296, 730)
	frameRate = 20
	format = "bgr"
	imageSizeTuple = process.frameResize[::-1] + (3,)
	image = numpy.zeros(imageSizeTuple, dtype = "uint8")

	def gen(): #picamera.PiCamera
	    with process.camera as camera:
	    	camera.resolution = resolution
			#camera.framerate = frameRate
			with picamera.array.PiRGBArray(camera, size = process.frameResize) as rawCapture:
				for frame in camera.capture_continuous(rawCapture, format = format, resize = process.frameResize, use_video_port = True):
					# clear the stream in preparation for the next frame
					if process.done(): break
					rawCapture.truncate(0)
					# grab the raw NumPy array representing the image, then place it in pool
					yield = frame.array
					self.streamFrameNum += 1

  	return gen
	'''
