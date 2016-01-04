from serial     import Serial, SerialException
from threading  import Lock, Timer
from Queue      import Queue
from glob       import g
#from dispatcher import LBDispatcher
from sandbox    import LBSandbox
import sys, time, platform, json


def debug(s):
	print '>>>>>>>>>> ' + s

class LBSerialPort:
	"""
		Handles full duplex communication with the serial prot
		Support multiple platforms
		Pattern = singleton
	"""

	@staticmethod
	def get_params():
		if g.is_RPI:
			# Raspberry PI
			return ('/dev/ttyAMA0', 57600)
		elif g.is_OSX:
			# Mac OS X
			return ('/dev/cu.usbmodem1421', 115200)
	#
	def __init__(self):
		self.timeout = 5
		self.port, self.baudrate = LBSerialPort.get_params()
		self.serial = None
		self.is_open = False
  #
	def open(self):
		print '   serial port  = %s' % self.port
		print '   baudrate     = %d' % self.baudrate
		try:
			self.serial = Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
			self.serial.flushInput()
			self.serial.flushOutput()
			self.is_open = True
			Timer(1.0, g.api.reset_shield).start()
			debug('Serial port is open')
			return True
			#time.sleep(0.5)
		except OSError as e:
			debug('Cannot open the serial port: %s' % str(e))
			debug('Retrying in 5 sec...')
			self.is_open = False
			Timer(5.0, self.open).start()
			return False

	#
	def close(self):
		try:
			self.serial.close()
		except SerialException as e:
			debug('UART close failure: %s, (%s)' % (str(e), str(type(e))))
		finally:
			self.serial = None
			self.is_open = False
	#
	def write(self, cmd):
		try:
			if self.is_open:
				json_msg = 'json:' + json.dumps(cmd) + '\n'
				self.serial.write(json_msg)
				print 'Send serial_cmd %s' % json_msg
				return True
			else:
				return False
		except SerialException as e:
			debug('UART write failure')
			return False
	#
	def forever_loop(self):
		#
		def dispatch(json_msg):
			print 'dispatch %s' % json_msg
			msg = json.loads(json_msg)
			if msg.has_key('REQ_ID'): # regular command
				queue = LBSerialRequest.queue_store[msg['REQ_ID']]
				queue.put(msg)
			elif msg.has_key('SAMPLE_ID'): #data streaming
				# sandbox consumes objects
				g.sandbox.fire_event('SAMPLE', msg)
				# dispatcher consumes json messages
				g.dispatcher.fire_event(json_msg)
			else:
				raise SerialException('Response is missing a REQ_ID or SAMPLE_ID')
		#
		while g.alive:
			try:
				s = self.serial.readline()
				if len(s) > 0:
					dispatch(s.strip())
			except SerialException as e:
				debug('UART: Exception %s, (%s)' % (str(e), str(type(e))))
				self.close()
		#
		print 'Serial port thread ... done'


class LBSerialRequest:
	""" Synchronous request/response over serial """
	# static variables
	queue_store = {}
	count = 100 # for generating unique ids
	lock = Lock()

	@staticmethod
	def get_id():
		LBSerialRequest.lock.acquire()
		id = LBSerialRequest.count
		LBSerialRequest.count += 1
		LBSerialRequest.lock.release()
		return str(id)
	#
	def __init__(self, msg):
		self.id = LBSerialRequest.get_id()
		self.ack = None
		self.queue = Queue(1)
		LBSerialRequest.queue_store[self.id] = self.queue
		msg['REQ_ID'] = self.id
		status = g.serial.write(msg)
		self.is_ok = status
	#
	def get_ack(self):
		try:
			self.ack = self.queue.get(timeout=2)
		except Exception as e:
			self.ack = 'Request %d has timed out, %s' %  (self.id, str(e))
		finally:
			print 'Got ack for request %s: %s' % (self.id, self.ack)
			del LBSerialRequest.queue_store[self.id]
			return self.ack


""" Dispatch events from originating from the serial port """

class LBDispatcher:
	def __init__(self):
		self.listeners = []
  #
	def add_listener(self, queue):
		self.listeners.append(queue)
  #
	def remove_listener(self, queue):
		self.listeners.remove(queue)

	def fire_event(self, data):
		for q in self.listeners:
			q.put(data)
  #...


""" Global object Initialization """

g.dispatcher = LBDispatcher()
g.serial = LBSerialPort()
