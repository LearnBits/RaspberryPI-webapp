import hardware, sys

class Global:

	def __init__(self):
		self.app        = None
		self.args       = None
		self.dispatcher = None
		self.sandbox    = None
		self.api 		= None
		self.serial     = None
		self.camera     = None
		self.alive      = True
		self.is_OSX     = hardware.is_OSX()
		self.is_RPI     = (not self.is_OSX) and (hardware.pi_version() is not None)

	def check_supported_platform(self):
	    if not self.is_RPI and not self.is_OSX:
	        print '>>>>>>>>> Unsupported platform'
	        print '>>>>>>>>> Aborting !!!'
	        print
	        sys.exit(1)

# initialization of global object
g = Global()
