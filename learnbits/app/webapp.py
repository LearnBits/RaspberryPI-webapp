from Queue      import Queue, Empty
from flask      import Flask, request, Response, redirect, url_for
from serialport import LBSerialRequest, LBDispatcher
from camera     import LBVisionProcessor
from sandbox    import LBSandbox
from sse        import LBServerSideEvent
from glob       import g
from api        import pi
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
app = Flask('__name__', static_url_path='/learnbits/files', static_folder='files')
HTTP_OK = 'OK', 200
HTTP_ERROR = 'ERROR', 200
init_web_app()

#---------------
# Flask routing
#---------------

@app.route('/')
def hello():
	return redirect(url_for('static', filename='main.html'))


@app.route('/serial_cmd')
def serial_cmd():
	# we're going to add an REQ_ID therefore
	# a copy is needed b/c request.args is immutable
	ret_val = pi.send_serial_request(request.args.copy())
	return json.dumps(ret_val)

@app.route('/reset_shield')
def reset_shield():
	try:
		ret_val = g.api.reset_shield()
		return json.dumps(ret_val)
	except Exception as e:
		print 'Reset shield error'
		print 'Exception: %s' % str(e)
		return HTTP_ERROR

# /motor?right=32&left=32
@app.route('/motor')
def motor():
	right = left = None
	try:
		right = int(request.args['right'])
		left  = int(request.args['left'])
		ret_val = pi.motor(right, left)
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
		ret_val = pi.led_bar8(led_values)
		return json.dumps(ret_val)
	except Exception as e:
		print 'LED_BAR8 error: %s' % request.args
		print 'Exception: %s' % str(e)
		return json.dumps({'STATUS':'LED_BAR8_ERROR'})


@app.route('/connect')
def connect():
	sse = LBServerSideEvent()
	return Response(sse.generator(), mimetype=LBServerSideEvent.mimetype)

@app.route('/disconnect')
def disconnect():
	sse_id = int(request.args['SSE_ID'])
	print 'disconnecting sse_id %d' % sse_id
	LBServerSideEvent.state[sse_id] = False
	return HTTP_OK


# Video streaming from camera
@app.route('/start_camera')
def start_camera():
	print 'start_camera'
	pi.camera.start()
	return HTTP_OK

@app.route('/stop_camera')
def stop_camera():
	print 'stop_camera'
	pi.camera.stop()
	return HTTP_OK

@app.route('/camera_stream')
def video_feed():
	frame_gen = pi.camera.get_jpeg_stream_generator()
	return Response(frame_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Sandbox requests
@app.route('/run_program', methods=['POST'])
def run():
	# Format of /upload POST request
	# author (str), date (str), program (str)
	prog = str(request.form['program'])
	g.sandbox.spawn(prog)
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
