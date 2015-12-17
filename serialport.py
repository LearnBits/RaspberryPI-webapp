from serial     import Serial, SerialException 
from threading  import Lock
from Queue      import Queue
from glob       import glob
from dispatcher import LBDispatcher
from sandbox    import LBSandbox
import sys, time, platform, json

#--------------------

def debug(s):
	print '>>>>>>>>>> ' + s

class LBSerialPort:
  #
	def __init__(self):
		self.serial = None
  #
	def open(self):
		#
		def serial_port_params():
			if platform.system() == 'Darwin':
				# Mac OS X
				return ('/dev/cu.usbmodem1421', 115200) 
			else:
				# Raspberry PI
				return ('/dev/ttyAMA0', 57600)
	  #
		try:
			(p, b) = serial_port_params()
			self.serial = Serial(port=p, baudrate=b)
		except Exception as e:
			debug('UART open failed: Exception ' + str(e))
			sys.exit(1)
	#
	def close(self):
		self.serial.close()
	#
	def send(self, cmd):
		json_msg = 'json:' + json.dumps(cmd) + '\n'
		self.serial.write(json_msg)
	#	
	def forever_loop(self):
		#
		debug_count = 0;
		while glob.app_is_running:
			try:
				json_msg = self.serial.readline().strip()
				msg = json.loads(json_msg)
				debug_count += 1
				#
				if msg.has_key('SENSOR_ID'):
					glob.sandbox.fire_event(msg)
					glob.dispatcher.fire_event(json_msg)
					if debug_count % 15 == 0: debug('Streaming from UART: %s' % json_msg)
				#
				elif msg.has_key('ID'):
					queue = LBSerialRequest.store[msg['ID']]
					queue.put(json_msg)
				#
			except Exception as e:
				debug('UART: Exception ' + str(e) + ' ' + str(type(e)))
#...

''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization 

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
glob.serial = LBSerialPort()


# LBSerialRequest	
	

class LBSerialRequest:
	# static variables
	store = {}
	count = 100 # for generating unique ids
	lock = Lock()
	
	@staticmethod 
	def get_id():
		LBSerialRequest.lock.acquire()
		id = LBSerialRequest.count
		LBSerialRequest.count += 1
		LBSerialRequest.lock.release()
		return str(id)

	def __init__(self, msg):
		self.id = LBSerialRequest.get_id()
		self.queue = Queue(1)
		self.resp = None
		LBSerialRequest.store[self.id] = self.queue
		msg['ID'] = self.id
		print 'Send serial_cmd %s' % json.dumps(msg)
		glob.serial.send(msg)
	#
	def get_response(self):
		try:
			self.resp = self.queue.get(timeout=2)
		except Exception as e:
			self.resp = 'Request %d has timed out, %s' %  (self.id, str(e))
			print self.resp
			self
		finally:
			del LBSerialRequest.store[self.id]
			return self.resp
	
			