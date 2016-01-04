from Queue      import Queue, Empty
from flask      import Flask, request, Response, redirect
from serialport import LBSerialRequest, LBDispatcher
from camera     import LBVisionProcessor
from sandbox    import LBSandbox
from api		import LBShieldAPI
from glob       import g
import json, flask.ext.cors, math

#--------------------

def debug(s):
	print '>>>>>>>>>> ' + s

def init_web_app():
	app.debug = True
	app.config.update(PROPAGATE_EXCEPTIONS=True)
	flask.ext.cors.CORS(app)
	g.app = app

''' global var declarations '''
app = Flask('__name__')
HTTP_OK = 'OK', 200
HTTP_ERROR = 'ERROR', 200
init_web_app()

#---------------
# Flask routing
#---------------

@app.route('/')
def hello():
	return redirect('/static/main.html')

@app.route('/serial_scan')
def scan():
	ret_val = g.api.send_serial_request({'CMD':'SCAN'})
	return json.dumps(ret_val)

@app.route('/serial_cmd')
def serial_cmd():
	# we're going to add an REQ_ID therefore
	# a copy is needed b/c request.args is immutable
	ret_val = g.api.send_serial_request(request.args.copy())
	return json.dumps(ret_val)


# /motor?right=32&left=32
@app.route('/motor')
def motor():
	right = left = None
	try:
		right = int(request.args['right'])
		left  = int(request.args['left'])
		ret_val = g.api.motor(right, left)
		return json.dumps(ret_val)
	except Exception as e:
		print 'Motor error: %s' % str(request.args)
		print 'Exception: %s' % str(e)
		return json.dumps({'STATUS':'MOTOR_ERROR'})

# /led_bar8?values=11,12,13,14,15,16,17,18
@app.route('/led_bar8')
def led():
	led_values = None
	try:
		led_values = map(lambda x: int(x), request.args['values'].split(','))
		ret_val = g.api.led_bar8(led_values)
		return json.dumps(ret_val)
	except Exception as e:
		print 'LED_BAR8 error: %s' % request.args
		print 'Exception: %s' % str(e)
		return json.dumps({'STATUS':'LED_BAR8_ERROR'})


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
		while stream_alive[stream_id] and g.alive:
			try:
				json_sample = sampling_queue.get(timeout=5)
				#print 'Sending SSE sample %s' % json_sample
				yield 'data: %s\n\n' % json_sample
			except Empty as e:
				print 'Empty queue in streaming data %s. Possibly timed out (5s)' % str(e)
		#
		# end of streaming thread
		yield 'event: close\n' + 'data: {"time": "now"}\n\n'
		g.dispatcher.remove_listener(sampling_queue)
		print 'Data streaming thread .... done'
	#
	return Response(gen(), mimetype='text/event-stream')

@app.route('/stop_sampling')
def stop_sampling():
	global stream_alive
	stream_id = int(request.args['STREAM_ID'])
	print 'got stop_Stampling request for %d' % stream_id
	stream_alive[stream_id] = False
	return HTTP_OK


# Video streaming from camera
@app.route('/start_camera')
def start_camera():
	print 'start_camera'
	g.camera.start()
	return HTTP_OK

@app.route('/stop_camera')
def stop_camera():
	print 'stop_camera'
	g.camera.stop()
	return HTTP_OK

@app.route('/camera_stream')
def video_feed():
	frame_gen = g.camera.get_jpeg_stream_generator()
	return Response(frame_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Sandbox requests
@app.route('/run_program', methods=['POST'])
def run():
	# Format of /upload POST request
	# author (str), date (str), program (str)
	p = str(request.form['program'])
	g.sandbox.run_program(p)
	return HTTP_OK

@app.route('/stop_program')
def stop():
	g.sandbox.stop_program()
	return HTTP_OK

# Server shutdown_func
# Can only be done via a HTTP request
@app.route('/shutdown', methods=['POST'])
def shutdown():
	shutdown_func = request.environ.get('werkzeug.server.shutdown')
	if shutdown_func is None: raise RuntimeError('Not running with the Werkzeug Server')
	shutdown_func()
	print 'Web app thread ... done'
	return 'Shutting down Learnbits server...'
