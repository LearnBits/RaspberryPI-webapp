from __future__ import with_statement
from threading  import Thread, Event, RLock
from time       import sleep
from glob		import g
from api		import pi
import math, json, event_handlers
import numpy as np

class LBSamplingEvent:
	def __init__(self):
		self.event =  Event()
		self.event.clear()
		self.data  = None
  	#
	def set(self, data):
		self.data = data
		self.event.set()
  	#
	def get(self):
		self.event.wait()
		self.event.clear()
		return self.data
#...

class LBSandbox:
	#
	def __init__(self):
		self.pid = 0 # the current running program
		self.running = {0: False}
		self.event = LBSamplingEvent()
		self.rlock = RLock()
	#
	def fire_event(self, data):
		if self.running[self.pid]:
			self.event.set(data)
  	#
	def get_event(self):
		return self.event.get()
	#
	def flush(self):
		self.get_event()
  	#
	def spawn(self, program):
		def wait_for_new_program_thread():
			while not self.running[self.pid]:
				sleep(0.1)
		#	Must lock this critical portion
		# to make sure that only one program runs at a given time
		with self.rlock:
			self.stop_program()
			self.pid += 1
			self.running[self.pid] = False # before starting new thread
			Thread(target=self.run_program, args=(self.pid, program,)).start()
			wait_for_new_program_thread()
			print 'program %d confirmed' % self.pid
	#
	def run_program(self, prog_id, program):
		print 'program %d started' % prog_id
		self.running[prog_id] = True
		self.flush() # not sure if it's needed
		# main loop
		self.forever_loop(prog_id, program)
  	#

	def forever_loop(self, __prog_id__, __program__):
		'''
			NOTE:
			The following sections (#1, #2, #3)
			must run within the same scope
			The 'exec' statement cannot run in nested functions (Python limitation)
		'''
		# 1 - run user code and make it part of the local scope of this function
		#	  - function definitions
		#	  - variables
		#	  - statements
		exec(__program__)

		# 2 - add event listeners
		event_handler = event_handlers.get_signatures()
		def do_nothing(): pass

		for __handler__ in event_handler.itervalues():
			''' Take advantage of the NameError exception
				in order to find out if the handler exists in user code
				i.e. in the scope of this function
			'''
			try:
				exec('__handler__.func = %s' % __handler__.name)
			except NameError:
				__handler__.func = do_nothing
		# 3 - forever event loop
		#
		event_handler['INIT'].func()
		#
		while True:
			__event__ = self.get_event()
			#
			if self.running[__prog_id__] and g.alive:
				#
				# pre-processor
				event_handler['PRE_PROCESS'].func()
				#
				# Run event handler
				__handler__ = event_handler[__event__['SAMPLE_ID']]
				if __handler__.func is not do_nothing:
					# __f__ and __p__ must be declared ** HERE **
					# so the invoke_statement can be executed (see event_handlers.py)
					__f__ = __handler__.func
					__p__ = __event__['VAL']
					exec(__handler__.invoke_statement)
				#
				# post-processor
				event_handler['POST_PROCESS'].func()
				#
			else:
				#
				event_handler['CLEANUP'].func()
				break
		#
		# garbage collection
		del self.running[__prog_id__]
		print 'program %d ended' % __prog_id__
	#
	#
	def stop_program(self):
		with self.rlock:
			self.running[self.pid] = False
			# unblock waiting for event
			self.fire_event(None)


#...

''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
g.sandbox = LBSandbox()
