from threading 	import Thread, Timer
from glob       import g
from flask      import Flask
#from serialport import LBSerialPort
#from camera     import LBVisionProcessor
from time       import strftime, sleep
from sys	    import exit
from webapp     import app
from datetime   import datetime
from dateutil.relativedelta import relativedelta
import requests, argparse, hardware


# VARs
time_format = '%Y-%m-%d %H:%M:%S'
start_uptime = None
#

def start_server():
	global start_uptime
	start_uptime = datetime.strptime(strftime(time_format), time_format)

def end_server():
	# Pretty time print
	def pprint(diff, units):
		words = []
		for u in units:
			v = eval('diff.' + u + 's') # + 's' b/c it's diff.days (with an 's')
			if v > 0:
				words.append('%d %s' % (v, u if v == 1 else u + 's'))
		return ' '.join(words)
	#
	global start_uptime
	end_uptime = datetime.strptime(strftime(time_format), time_format)
	diff = relativedelta(end_uptime, start_uptime)
	print 'Total uptime: %s' % pprint(diff, ['month', 'day', 'hour', 'minute', 'second'])


def server_warm_up(args):
	''' Start all threads '''
	#
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	print 'o                         o'
	print 'o  Learnbits application  o'
	print 'o                         o'
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	print '   use_camera  = %s' % args.use_camera
	print '   use_serial  = %s' % args.use_serial
	print '   server port = %d' % args.port
	print '   platform    = %s' % ('OSX' if g.is_OSX else ('RPI' if g.is_RPI else 'Unsupported'))
	print
	#
	# Run serial port
	if args.use_serial:
		from serialport import LBSerialPort
		serial_port_thread = Thread(target=g.serial.forever_loop)
		serial_port_thread.start()
	#
	# Run web app
	def start_web_app():
		app.run(host='0.0.0.0', port=args.port, threaded=True, debug=True, use_evalex=False, use_reloader=False)
	#
	web_app_thread = Thread(target=start_web_app)
	web_app_thread.start()
	#
	# Open video camera # (OS X bug: must be done in the main thread)
	if args.use_camera:
		from camera import LBVisionProcessor
		g.camera.turn_on()


def server_cool_down(args):
	''' Gracefully terminate all running threads '''
	def stop_web_app():
		# wait 3 secs to give time to clients to close their connections
		Timer(3.0, requests.post, args=('http://localhost:%d/shutdown' % args.port,)).start()
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
	g.sandbox.fire_event('SHUTDOWN')
	#
	if args.use_camera:
		g.camera.turn_off()
	#
	stop_web_app()


def parse_args():
	parser = argparse.ArgumentParser(description='Learnbits application')
	parser.add_argument('--no-camera', dest='use_camera', action='store_false', default=True, help='disable the camera')
	parser.add_argument('--no-serial', dest='use_serial', action='store_false', default=True, help='disable the serial port')
	parser.add_argument('--port', dest='port',  action='store', type=int,       default=8080, help='http server port')
	args = parser.parse_args()
	return args

# main starts here
if __name__ == '__main__':
	#
	args = parse_args()
	g.args = args
	#
	start_server()
	#
	server_warm_up(args)
	#
	''' main idle loop '''
	try:
		while g.alive:
			sleep(1.0)
	except Exception as e:
		print 'Got exception %s' % str(e)
	finally:
		''' server shutdown	(^C)'''
		server_cool_down(args)
		#
		end_server()
		#
		exit(0)
