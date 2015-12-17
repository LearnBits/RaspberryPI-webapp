class Global:
	
	def __init__(self):
		self.dispatcher = None
		self.sandbox    = None
		self.serial     = None
		self.app_is_running = True

# initialization of global object
glob = Global()