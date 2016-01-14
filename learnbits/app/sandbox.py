from __future__ import with_statement
from threading  import Thread, Event, RLock
from time       import sleep
from glob		import g
import json

class LBSamplingEvent:
  	#
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
		self.program = ''
		self.pid = 0 # the current running program
		self.running = {self.pid:False}
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
		#	Must lock this critical portion
		# to make sure that only one program runs at a given time
		with self.rlock:
			self.stop_program()
			self.program = program
			self.pid += 1
			self.running[self.pid] = False
			Thread(target=self.run_program, args=(self.pid,)).start()
			self.wait_for_new_program_thread()
			print 'program %d confirmed' % self.pid
	#
	def wait_for_new_program_thread(self):
		while not self.running[self.pid]:
			sleep(0.1)
	#
	def run_program(self, prog_id):
		print 'program %d started' % prog_id
		self.running[prog_id] = True
		self.flush() # not sure if it's needed
		bytecode = compile(self.program, '<string>', 'exec')
		# main loop
		self.forever_loop(prog_id, bytecode)
		# garbage collection
		del self.running[prog_id]
		print 'program %d ended' % prog_id
  	#
	def forever_loop(self, prog_id, bytecode):
		# local registers
		r1 = r2 = r3 = None
		#
		while self.running[prog_id] and g.alive:
			__event__ = self.get_event()
			if __event__:
				exec(bytecode)

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
