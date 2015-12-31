class Global:

	def __init__(self):
		self.app        = None
		self.args       = None
		self.dispatcher = None
		self.sandbox    = None
		self.api = None
		self.serial     = None
		self.camera     = None
		self.alive      = True
		self.is_RPI      = False
		self.is_OSX     = False

# initialization of global object
g = Global()
