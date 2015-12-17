from glob import glob 

class LBDispatcher:
  #
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

''' ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	Global object Initialization 

 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ '''
glob.dispatcher = LBDispatcher()