from threading 	import Thread, Timer
from glob       import g
from api 		import pi
from flask      import Flask
from time       import strftime, sleep
from webapp     import app
import dateutil.relativedelta, datetime, requests, argparse, sys


# VARs
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
#

def start_server():
	g.start_uptime = datetime.datetime.strptime(strftime(TIME_FORMAT), TIME_FORMAT)
	g.check_supported_platform()
#
def warm_up():
	''' Start all threads '''
	#
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	print 'o                         o'
	print 'o  Learnbits application  o'
	print 'o                         o'
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	print '   platform     = %s' % ('OSX' if g.is_OSX else ('RPI' if g.is_RPI else 'Unsupported'))
	print '   use camera   = %s' % g.config.use_camera
	print '   use serial   = %s' % g.config.use_serial
	print '   server port  = %d' % g.config.port
	#
	# Run serial port
	if g.config.use_serial:
		from serialport import LBSerialPort
		g.serial.open(timeout=5.0)
		serial_port_thread = Thread(target=g.serial.forever_loop)
		i2c_scan_thread    = Thread(target=g.serial.scan_I2C, args=(5.0,))
		serial_port_thread.start()
		i2c_scan_thread.start()
	#
	print
	#
	# Run web app
	def start_web_app():
		app.run(host='0.0.0.0', port=g.config.port, threaded=True, debug=True, use_evalex=False, use_reloader=False)
	#
	web_app_thread = Thread(target=start_web_app)
	web_app_thread.start()
	#
	if g.config.use_camera and g.is_OSX:
		from camera import LBComputerVision
#
def cool_down():
	''' Gracefully terminate all running threads '''
	def stop_web_app():
		# wait 3 secs to give time to clients to close their connections
		Timer(3.0, requests.post, args=('http://localhost:%d/shutdown' % g.config.port,)).start()
		sleep(3.5) # wait until flask server shutdown
	#
	print
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	print 'o                                           o'
	print 'o  Learnbits shutdown, exiting in 3 secs .  o'
	print 'o                                           o'
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	#
	g.alive = False
	#
	g.sandbox.stop_program()
	#
	stop_web_app()
#
def shutdown():
	# Pretty time print
	def pprint(diff, units):
		words = []
		for u in units:
			v = eval('diff.' + u + 's') # + 's' b/c it's diff.days (with an 's')
			if v > 0:
				words.append('%d %s' % (v, u if v == 1 else u + 's'))
		return ' '.join(words)
	#
	end_uptime = datetime.datetime.strptime(strftime(TIME_FORMAT), TIME_FORMAT)
	diff = dateutil.relativedelta.relativedelta(end_uptime, g.start_uptime)
	print 'Total uptime: %s' % pprint(diff, ['month', 'day', 'hour', 'minute', 'second'])
	sys.exit(0)
#

def check_camera_flag_OSX():
	# Open video camera # (OS X bug: must be done in the main thread)
	if g.turn_on_camera_osx:
		pi.camera.turn_on()
	elif g.turn_off_camera_osx:
		pi.camera.turn_off()
#

def parse_args():
	parser = argparse.ArgumentParser(description='Learnbits application')
	parser.add_argument('--no-camera', dest='use_camera', action='store_false', default=True, help='disable the camera')
	parser.add_argument('--no-serial', dest='use_serial', action='store_false', default=True, help='disable the serial port')
	parser.add_argument('--port', dest='port',  action='store', type=int,       default=8080, help='http server port')
	return parser.parse_args()

# main starts here
if __name__ == '__main__':
	#
	g.config = parse_args()
	#
	start_server()
	#
	warm_up()
	#
	''' main idle loop '''
	try:
		while g.alive:
			if g.is_OSX and g.config.use_camera:
				check_camera_flag_OSX()
			sleep(1.0)
	except Exception as e:
		print 'main.py: got exception %s' % str(e)
	finally:
		''' server shutdown	(^C)'''
		cool_down()
		#
		shutdown()
