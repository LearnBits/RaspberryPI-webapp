from Queue      import Queue, Empty
from flask      import Flask, request, Response, redirect
from serialport import LBSerialRequest, LBDispatcher
from camera     import LBVisionProcessor
from sandbox    import LBSandbox
from glob       import g
import json, flask.ext.cors

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
init_web_app()

#---------------
# Flask routing
#---------------

@app.route('/')
def hello():
	return redirect('/static/main.html')

# Synchronous serial requests
def send_serial_request(data):
	if g.alive:
		req = LBSerialRequest(data)
		return req.get_ack() if req.is_ok else json.dumps({'STATUS':'SERIAL_ERROR'})
	else:
		return json.dumps({'STATUS':'SERVER_SHUTDOWN'})

@app.route('/serial_scan')
def scan():
	if g.args.use_serial:
		return send_serial_request({'CMD':'SCAN'})
	else:
		return json.dumps({'STATUS':'NO_SERIAL'})

@app.route('/serial_cmd')
def serial_cmd():
	# we're going to add an REQ_ID therefore
	# a copy is needed b/c request.args is immutable
	if g.args.use_serial:
		return send_serial_request(request.args.copy())
	else:
		return json.dumps({'STATUS':'NO_SERIAL'})

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
		while stream_alive[stream_id] and g.serial.is_open and g.alive:
			try:
				json_sample = sampling_queue.get(timeout=5)
				print 'Sending SSE sample %s' % json_sample
				yield 'data: %s\n\n' % json_sample
			except Empty as e:
				print 'Queue error in streaming data %s' % str(e)
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
	stream_id = int(request.args['stream_id'])
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
