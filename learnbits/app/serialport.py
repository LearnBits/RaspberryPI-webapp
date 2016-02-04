from serial     import Serial, SerialException
from threading  import Thread, Lock, Timer, Event
from Queue      import Queue
from glob       import g
#from sandbox    import LBSandbox
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
		self.port, self.baudrate = LBSerialPort.get_params()
		self.serial_dev = None
		self.is_open = False
		self.prev_i2c_list = []
		self.i2c_scan_event = Event()
  #
	def open(self, timeout):
		print '   serial port  = %s' % self.port
		print '   baudrate     = %d' % self.baudrate
		try:
			self.serial_dev = Serial(port=self.port, baudrate=self.baudrate, timeout=timeout)
			self.serial_dev.flushInput()
			self.serial_dev.flushOutput()
			self.is_open = True
		except OSError as e:
			debug('Cannot open the serial port: %s' % str(e))
			debug('Retrying in 5 sec...')
			self.is_open = False
			if g.alive:
				Timer(5.0, self.open, args=[timeout]).start()
			return False
			#
		debug('Serial port is open')
		# Reset Shield
		Timer(1.0, self.reset_shield).start()
		return True
		#
	def reset_shield(self):
		req = LBSerialRequest({'CMD':'RESET'})
		ret_val = req.get_ack()
#
	def close(self):
		try:
			self.serial_dev.close()
		except SerialException as e:
			debug('UART close failure: %s, (%s)' % (str(e), str(type(e))))
		finally:
			self.serial_dev = None
			self.is_open = False
	#
	def write(self, cmd):
		try:
			if self.is_open:
				json_msg = 'json:' + json.dumps(cmd) + '\n'
				self.serial_dev.write(json_msg)
				#print 'Send serial_cmd %s' % json_msg
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
			#print 'dispatch %s' % json_msg
			msg = json.loads(json_msg)
			if msg.has_key('SAMPLE_ID'): #data streaming
				# sandbox consumes objects
				g.sandbox.fire_event(msg)
				# dispatcher consumes json messages
				g.dispatcher.fire_event(('SAMPLE', json_msg))
			elif msg.has_key('I2C_ADDR'):
				# Response to a SCAN command
				i2c_list = msg['I2C_ADDR']
				i2c_list.sort()
				if cmp(self.prev_i2c_list, i2c_list) != 0:
					# only fire an event if there was a change in i2c bus
					self.prev_i2c_list = i2c_list
					g.dispatcher.fire_event(('SCAN', json.dumps(i2c_list)))
			elif msg.has_key('REQ_ID'): # regular command
				queue = LBSerialRequest.queue_store[msg['REQ_ID']]
				queue.put(msg)
			else:
				raise SerialException('Bad response in serial port dispatch')
		#
		while g.alive:
			try:
				if self.serial_dev:
					s = self.serial_dev.readline() # timeout 5 secs
					if len(s) > 0:
						dispatch(s.strip())
			except SerialException as e:
				debug('UART: Exception %s, (%s)' % (str(e), str(type(e))))
				self.close()
		#
		# end i2c scan thread
		self.i2c_scan_event.set()
		print 'Serial port thread ... done'

	def scan_I2C(self, timeout):
		""" Forever loop: timed execution of I2C bus scan """
		while not self.i2c_scan_event.wait(timeout):
			if self.is_open:
				status = self.write({'CMD':'SCAN'})
				#debug('scanning I2C bus every %d sec' % timeout)
		#
		print 'I2C scan thread ... done'

	def get_I2C_list(self):
		return self.prev_i2c_list



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



class LBDispatcher:
	""" Dispatch events from originating from the serial port """

	def __init__(self):
		self.listeners = []
  	#
	def add_listener(self, queue):
		self.listeners.append(queue)
  	#
	def remove_listener(self, queue):
		self.listeners.remove(queue)
	#
	def fire_event(self, data):
		for q in self.listeners:
			q.put(data)
  	#


""" Global object Initialization """

g.dispatcher = LBDispatcher()
g.serial = LBSerialPort()
