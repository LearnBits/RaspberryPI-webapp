from threading 	import Thread
from Queue 			import Queue
from flask      import Flask, request, Response, redirect
from serialport import LBSerialRequest, LBDispatcher
from cv         import LBVisionProcessor
from sandbox    import LBSandbox
from glob       import g
import time, flask.ext.cors, cv2

#--------------------

def debug(s):
	print >> stderr, '>>>>>>>>>> ' + s


HTTP_OK = 'OK', 200 
#
app = Flask(__name__)
app.debug = True
flask.ext.cors.CORS(app)
#-----------------------------


#---------------
# Flask routing
#---------------

@app.route('/')
def hello():
	return redirect('/static/main.html')

# Synchronous serial requests
def send_serial_request(data):
	req = LBSerialRequest(data)
	ack = req.get_ack()
	return ack

@app.route('/serial_scan')
def scan():
	return send_serial_request({'CMD':'SCAN'})

@app.route('/serial_cmd')
def serial_cmd():
	# we're going to add an REQ_ID therefore
	# a copy is needed b/c request.args is immutable
	return send_serial_request(request.args.copy()) 

# Streaming data request from serial port
# global variables for data streams
stream_count = 0
stream_alive = {}

@app.route('/start_sampling')
def start_sampling():
	def gen():
		# register listener
		sampling_queue = Queue()
		g.dispatcher.add_listener(sampling_queue)
		# stream_id
		global stream_count, stream_alive
		stream_id = stream_count
		yield 'event: start\n' + 'data: %d\n\n' % stream_id
		stream_alive[stream_id] = True
		stream_count +=1
		# sampling loop
		while g.app_is_running and stream_alive[stream_id]:
			json_sample = sampling_queue.get()
			print 'Sending SSE sample %s' % json_sample
			yield 'data: %s\n\n' % json_sample
		#
		# end of streaming thread
		yield 'event: close\n' + 'data: {"time": "now"}\n\n'
		print 'Data streaming thread .... done'
	#
	return Response(gen(), mimetype='text/event-stream')

@app.route('/stop_sampling')
def stop_sampling():
	global stream_alive
	stream_id = int(request.args['stream_id'])
	print 'got stop_Stampling request for %d' % stream_id
	stream_alive[stream_id] = False
	return HTTP_OK

# Video streaming from camera
@app.route('/camera_stream')
def video_feed():
	#			
	frame_gen = g.cv.get_jpeg_stream()
	return Response(frame_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Sandbox requests
@app.route('/run_program', methods=['POST'])
def run():
	# Format of /upload POST request 
	# author (str), date (str), program (str)
  #
	p = str(request.form['program'])
	g.sandbox.run_program(p)
	return HTTP_OK

@app.route('/stop_program')
def stop():
	g.sandbox.stop_program()
	return HTTP_OK

@app.route('/shutdown', methods=['POST'])
def shutdown():
	shutdown_func = request.environ.get('werkzeug.server.shutdown')
	if shutdown_func is None: raise RuntimeError('Not running with the Werkzeug Server')
	shutdown_func()
	print 'Web app thread ... done'
	return 'Shutting down Learnbits server...'


def start_web_app():
	app.run(host='0.0.0.0', port=8080, threaded=True,
					debug=True, use_evalex=False, use_reloader=False)
	
def stop_web_app():
	from requests import post
	from threading import Timer	
	Timer(3.0, post, args=('http://localhost:8080/shutdown',)).start()

# main starts here
if __name__ == '__main__':

	'''
		Map of all running threads
		1) serial port thread
		2) web app main threads + request threads
		3) sandbox thread (when running)
		4) main thread - dormant
	'''

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
	#g.cv.start()
	
	try:
		while g.app_is_running:
			time.sleep(1.0)
	except Exception as e:
		print 'Got exception %s' % str(e)
	finally:
		#
		# Gracefully terminate all running threads (after hitting Ctrl-C) 
		print '\nServer shutdown, exiting in 5 secs ...'
		g.app_is_running = False
		g.sandbox.fire_event('SHUTDOWN')
		# Release video camera
		#g.cv.stop()
		# Shutdown web app by sending a 		
		stop_web_app()
		time.sleep(5.0)
		from sys import exit
		exit(0)
