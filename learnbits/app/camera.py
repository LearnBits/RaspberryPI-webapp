#from imutils.video.videostream import VideoStream
from compvision.lb_face_detector import haar_cascade
from compvision.lb_object_tracker import color_tracker
#from compvision.lb_digits_classifier import svm_digits_classifier
from compvision.video_inputs.frame_grabber import *
from compvision.jpeg import *
from threading import Thread, Event, Timer
from glob import g
from api import pi
from flask import jsonify
from time import sleep
import cv2, platform, json

fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.4


class LBComputerVision:

	class CVProcessor:
		def __init__(self, processor, event_id):
			self.processor = processor
			self.event_id = event_id

	def __init__(self):
		self.camera = None
		self.face_detector = LBComputerVision.CVProcessor(haar_cascade(), 'FACE_DETECTION')
		self.ball_tracker = LBComputerVision.CVProcessor(color_tracker(), 'BALL_TRACKING')
		self.digits_classifier = None #LBComputerVision.CVProcessor(svm_digits_classifier(), 'DIGITS_CLASSIFIER')
		self.processor = None
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
		# TODO also define isRPI

	def turn_on(self):
		if g.is_OSX:
			''' NOTE: On Mac OS X this command must run in main thread!! '''
			self.camera = cv2.VideoCapture(0)
			g.turn_on_camera_osx = False
			g.osx_camera_notifier.set()
		elif g.is_RPI:
			# Raspberry PI
			import picamera
			self.camera = picamera.PiCamera()
		sleep(1.0)

	def turn_off(self):
		if self.camera != None:
			if g.is_OSX:
				self.camera.release()
				g.turn_off_camera_osx = False
				g.osx_camera_notifier.set()
			elif g.is_RPI:
				self.camera.close()

	def start(self, option):
		self.alive = True
		if g.is_OSX:
			# Due to OSX known bug
			# actual turn_off is done from the main thread
			g.turn_on_camera_osx = True
			g.osx_camera_notifier.clear()
			g.osx_camera_notifier.wait()
		elif g.is_RPI:
			self.turn_on()
		self.set_processor(option)
		Thread(target = self.camera_get_frame).start()
		Thread(target = self.camera_process_frame).start()

	def stop(self):
		self.alive = False
		if g.is_OSX:
			# Due to OSX known bug
			# actual turn_off is done from the main thread
			g.turn_off_camera_osx = True
			g.osx_camera_notifier.clear()
			g.osx_camera_notifier.wait()
		elif g.is_RPI:
			Timer(1.0, self.turn_off).start()

	def done(self):
		return not (self.alive and g.alive)

	def set_processor(self, option):
		if option == 'face detection':
			self.processor = self.face_detector
		elif option == 'ball tracking':
			self.processor = self.ball_tracker
		elif option == 'digits recognition':
			self.processor = self.digits_classifier
		else:
			self.processor = self.face_detector

	def get_frame_generator(self):
		if g.is_OSX:
			return webcam_frame_grabber(self)
		elif g.is_RPI:
			return picamera_frame_grabber(self)
		else:
			print 'Camera frame gen: unsupported platform'


	def camera_get_frame(self):
		grab_frame = self.get_frame_generator()
		for frame in grab_frame():
			self.new_frame = frame
			self.raw_frame_count += 1
			self.new_frame_event.set()
			if self.done():
				break
		print 'Thread camera_get_frame done.'

	def camera_process_frame(self):
		while not self.done():
			self.new_frame_event.wait()
			self.new_frame_event.clear()
			self.processed_frame, self.result = self.processor.processor.process(self.new_frame)
			self.drawInfo()
			self.processed_count += 1
			self.processed_frame_event.set()
			if len(self.result) > 0:
				g.sandbox.fire_event({'SAMPLE_ID': self.processor.event_id, 'VAL': self.result})
		print 'Thread camera_process_frame done.'

	def drawInfo(self):
		if self.decorate:
			# background white rectangle (I measured the box manually :-)
			# cv2.rectangle(self.processed_frame, (5, 1), (265, 13), (244, 244, 244), -1)
			# frame number and % of dropped frames
			processed_rate = round(100.0 * self.processed_count / self.raw_frame_count, 2)
			displayed_rate = round(100.0 * self.displayed_count / self.raw_frame_count ,2)
			text = ' frame:%d  proc:%.2f%%  disp:%.2f%% ' % (self.raw_frame_count, processed_rate, displayed_rate)
			size, baseline = cv2.getTextSize(text, fontFace, fontScale, thickness=1)
			cv2.rectangle(self.processed_frame, (30, 10+baseline), (30+size[0], 10-size[1]), (100, 220, 220), -1)
			cv2.putText(self.processed_frame, text = text, org = (30, 10), fontFace=fontFace, fontScale=fontScale, color = (139, 139, 0), thickness = 1)
			# running marker on frame, useful for debugging
			cv2.putText(self.processed_frame, text = "||", org = (10, 15 + 10 * ((self.raw_frame_count % 15) + 1)), fontFace=fontFace, fontScale = 0.3, color = (0, 0, 255))

	def get_jpeg_stream_generator(self):
		#
		def gen():
			while not self.done():
				self.processed_frame_event.wait()
				self.processed_frame_event.clear()
				jpeg_buf = array2jpegBuffer(self.processed_frame)
				stream_data = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg_buf+ b'\r\n'
				yield stream_data
				self.displayed_count += 1
			print 'jpeg streaming done'
		#
		return gen

''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
pi.camera = LBComputerVision()
