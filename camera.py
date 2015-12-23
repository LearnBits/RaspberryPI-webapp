#from imutils.video.videostream import VideoStream
from compvision.face_detector import haar_cascade
from compvision.video_inputs.frame_grabber import *
from compvision.jpeg import *
from threading import Thread, Event
from glob import g
import cv2, time, platform

fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5

class LBVisionProcessor:

	def __init__(self):
		self.camera = None
		self.face_detector = haar_cascade()
		self.frameResize = (324, 182)
		self.decorate = True
		self.alive = True
		self.last_processed_frame = None
		self.last_result = None
		self.raw_frame_count = 0
		self.processed_count = 0
		self.displayed_count  = 0
		self.processed_frame_event = Event()
		self.new_frame_event = Event()
		self.isOSX = True if platform.system() == 'Darwin' else False

	def turn_on(self):
		if self.isOSX:
			''' NOTE: On Mac OS X this command must run in main thread!! '''
			self.camera = cv2.VideoCapture(0)
		else:
			# Raspberry PI
			import picamera
			self.camera = picamera.PiCamera()
		self.start()

	def turn_off(self):
		if self.camera != None:
			self.stop()
			if self.isOSX:
				self.camera.release()
			else:
				self.camera.close()

	def start(self):
		self.alive = True
		Thread(target = self.camera_input  ).start()
		Thread(target = self.camera_process).start()

	def stop(self):
		self.alive = False

	def done(self):
		return not (self.alive and g.alive)

	def get_frame_generator(self):
		if self.isOSX:
			return webcam_frame_grabber(self)
		else:
			return picamera_frame_grabber(self)

	def camera_input(self):
		time.sleep(1)
		grab_frame = self.get_frame_generator()
		for frame in grab_frame():
			self.new_frame = frame
			self.raw_frame_count += 1
			self.new_frame_event.set()
			if self.done():
				break

	def camera_process(self):
		time.sleep(1)
		while not self.done():
			self.new_frame_event.wait()
			self.new_frame_event.clear()
			self.processed_frame, self.result = self.face_detector.detect(self.new_frame)
			self.drawInfo()
			self.processed_count += 1
			self.processed_frame_event.set()
			#if (self.capturer.frame_counter % 100) == 0:
			#	print 'Processor FPS=%f [%d / %d]' % ((self.raw_frame_counter / 100.0), self.raw_frame_counter, self.capturer.frame_counter)
			#	self.raw_frame_counter = 0
			#self.new_frame.set()

	def drawInfo(self):
		if self.decorate:
			text = 'frame: %d' % self.raw_frame_count
			cv2.putText(self.processed_frame, text = text, org = (10, 10), fontFace = fontFace, fontScale = fontScale, color = (0, 255, 0), thickness = 1)

			#text = '%f - %f' %((self.processed_count / 300.0),(self.display_count / 300.0))
			cv2.putText(self.processed_frame, text = "||", org = (10 + 10 * ((self.raw_frame_count % 10) + 1), 30 + 10 * ((self.raw_frame_count % 10) + 1)), fontFace = fontFace, fontScale = 0.3, color = (0, 0, 255))

	def get_jpeg_stream_func(self):
		#
		def gen_jpeg_frames():
			while not self.done():
				self.processed_frame_event.wait()
				self.processed_frame_event.clear()
				#jpeg = cv2.imencode('.jpg', self.processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])[1].toString()
				# NEED to take care of Raspberry PI
				jpeg_buf = array2jpegBuffer(self.processed_frame)
				stream_data = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg_buf+ b'\r\n'
				yield stream_data
				self.displayed_count += 1
		#
		return gen_jpeg_frames

''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
g.camera = LBVisionProcessor()
