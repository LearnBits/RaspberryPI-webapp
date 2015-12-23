from threading 	import Thread, Timer
from glob       import g
from flask      import Flask
from serialport import LBSerialPort
from camera     import LBVisionProcessor
from time       import strftime, sleep
from sys	    import exit
from webapp     import app
from requests   import post
from dateutil.relativedelta import relativedelta
import datetime



time_format = '%Y-%m-%d %H:%M:%S'

def print_uptime(start_uptime):
	# Pretty time print
	def pprint(diff, units):
		words = []
		for u in units:
			v = eval('diff.' + u + 's') # + 's' b/c it's diff.days (with an 's')
			if v > 0:
				words.append('%d %s' % (v, u if v == 1 else u + 's'))
		return ' '.join(words)
	#
	end_uptime = datetime.datetime.strptime(strftime(time_format), time_format)
	diff = relativedelta(end_uptime, start_uptime)
	print 'Total uptime: %s' % pprint(diff, ['month', 'day', 'hour', 'minute', 'second'])


def warm_up():
	''' Start all threads '''
	def start_web_app():
		app.run(host='0.0.0.0', port=8080, threaded=True, debug=True, use_evalex=False, use_reloader=False)
	#
	# Run serial port
	serial_port_thread = Thread(target=g.serial.forever_loop)
	serial_port_thread.start()
	#
	# Run web app
	web_app_thread = Thread(target=start_web_app)
	web_app_thread.start()
	#
	# Open video camera # (OS X bug: must be done in the main thread)
	g.camera.turn_on()


def cool_down():
	''' Gracefully terminate all running threads '''
	def stop_web_app():
		Timer(3.0, post, args=('http://localhost:8080/shutdown',)).start()
	#
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	print 'o                                           o'
	print 'o  Server shutdown, exiting in 5 secs ...   o'
	print 'o                                           o'
	print 'o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o'
	# Set global alive flag to false
	g.alive = False
	# End sandbox programs
	g.sandbox.fire_event('SHUTDOWN')
	# Release video camera
	g.camera.turn_off()
	# Shutdown web app 		
	stop_web_app()
	# wait 5 secs for all thread to terminate
	sleep(5.0)


# main starts here
if __name__ == '__main__':
	# Measure start time
	start_uptime = datetime.datetime.strptime(strftime(time_format), time_format)
	#
	warm_up()

	''' main idle loop '''
	try:
		while g.alive:
			sleep(1.0)
	except Exception as e:
		print 'Got exception %s' % str(e)
	finally:
		''' server shutdown	(^C)'''
		cool_down()
		# Uptime
		print_uptime(start_uptime)
		# Bye
		exit(0)
