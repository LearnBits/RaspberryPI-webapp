from __future__ import with_statement
from threading  import Thread, Event, RLock
from time       import sleep
from glob import glob

class LBSamplingEvent:
  #
	def __init__(self):
		self.event =  Event()
		self.event.clear()
		self.result = None
  #
	def set(self, sample):
		self.result = sample
		self.event.set()
  #
	def get(self):
		self.event.wait(3.0) # 3 secs timeout
		self.event.clear()
		return self.result
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
	def fire_event(self, sample):
		self.event.set(sample)
  #
	def get_sample(self):
		return self.event.get()
  #
	def run_program(self, program):
		#	Must lock this critical portion
		# to make sure that only one program runs at a given time 
		with self.rlock:
			self.stop_program()
			self.program = program
			self.pid += 1
			self.running[self.pid] = False
			Thread(target=self.program_loop, args=(self.pid,)).start()
			self.wait()
			print 'program %d confirmed' % self.pid
	#
	def wait(self):		# wait for new thread to start
		while not self.running[self.pid]:
			sleep(0.1)
	#
	def program_loop(self, my_pid):
		bytecode = compile(self.program, '<string>', 'exec')
		self.running[my_pid] = True
		print 'program %d started' % my_pid
		#
		# main loop
		while self.running[my_pid] and glob.app_is_running:
			__sample__ = self.get_sample()
			if __sample__: exec(bytecode)
		#
		# garbage collection
		del self.running[my_pid]
		print 'program %d ended' % my_pid
  #
	def stop_program(self):
		with self.rlock:
			self.running[self.pid] = False
#...

''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization 

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
glob.sandbox = LBSandbox()
