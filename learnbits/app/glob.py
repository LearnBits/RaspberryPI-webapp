import sys, re, platform
from threading import Event


def check_RPI():
	"""Detect the version of the Raspberry Pi.  Returns either 1, 2 or
	None depending on if it's a Raspberry Pi 1 (model A, B, A+, B+),
	Raspberry Pi 2 (model B+), or not a Raspberry Pi.
	"""
	with open('/proc/cpuinfo', 'r') as infile:
		cpuinfo = infile.read()
	# Match a line like 'Hardware   : BCM2709'
	match = re.search('^Hardware\s+:\s+(\w+)$', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)
	is_RPI1 = True if (match and match.group(1) == 'BCM2708') else False
	is_RPI2 = True if (match and match.group(1) == 'BCM2709') else False
	return is_RPI1 or is_RPI2
#
def check_OSX():
	return (platform.system() == 'Darwin')
#

class LBGlob:

    def __init__(self):
        self.args         = None
        self.app          = None
        self.dispatcher   = None
        self.sandbox      = None
        self.alive        = True
        self.start_uptime = 0
        self.is_OSX       = check_OSX()
        self.is_RPI       = not check_OSX() and check_RPI
        self.turn_on_camera_osx = False
        self.turn_off_camera_osx = False
        self.osx_camera_notifier = Event()

    def check_supported_platform(self):
        if not self.is_RPI and not self.is_OSX:
            print '>>>>>>>>> Unsupported platform'
            print '>>>>>>>>> Aborting !!!'
            print
            sys.exit(1)

# initialization of global object
g = LBGlob()
