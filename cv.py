from imutils.video.videostream import VideoStream
from glob import g
import cv2, time

class LBVisionProcessor:
	def __init__(self):
		self.video_stream = None
		
	def start(self):	
		self.video_stream = VideoStream()
		self.video_stream.start()
		
	def stop(self):
		self.video_stream.stop()
		
	def get_jpeg_stream(self):
		#
		def gen_video_frames():
			image_resize_size = (324, 182)
			FRAMES_PER_SECOND = 24
			start_time = time.time()
			frame_count = 0
			while g.app_is_running:
				frame = self.video_stream.read()
				frame = cv2.resize(frame, image_resize_size)
				jpeg =  cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])[1].tostring()
				frame_count += 1
				yield (b'--frame\r\n'
							 b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
				#time.sleep(1.0 / FRAMES_PER_SECOND)
					#print 'grabbed frame'
				#else:
				#	print 'missed frame at %d, frame_num=%d' % (int(time.time() - start_time), frame_count)
				#	time.sleep(0.1)
		#	
		return gen_video_frames
				
''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization 

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
g.cv = LBVisionProcessor()

