class Global:
	
	def __init__(self):
		self.app        = None
		self.dispatcher = None
		self.sandbox    = None
		self.serial     = None
		self.camera     = None
		self.alive      = True

# initialization of global object
g = Global()