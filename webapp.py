from threading 	import Thread
from Queue 			import Queue
from flask      import Flask, request, Response, redirect
from serialport import LBSerialRequest
from dispatcher import LBDispatcher
from sandbox    import LBSandbox
from glob       import glob
import time, flask.ext.cors

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
	json_resp = req.get_response()
	return json_resp

@app.route('/scan')
def scan():
	return send_serial_request({'CMD':'SCAN'})

@app.route('/serial_cmd')
def serial_cmd():
	# we're going to add an ID therefore
	# a copy is needed b/c args is immutable
	return send_serial_request(request.args.copy()) 

# Streaming request 
@app.route('/start_sampling')
def sample():
	def gen():
		# init
		sampling_queue = Queue()
		glob.dispatcher.add_listener(sampling_queue)
		# sampling loop
		while glob.app_is_running:
			json_sampling_msg = sampling_queue.get()
			print 'Sending SSE sample %s' % json_sampling_msg
			yield 'data: %s\n\n' % json_sampling_msg
		#
		yield 'event: shutdown\n' + 'data: {"time": "now"}\n\n'
		print 'Data streaming thread .... done'
	#
	return Response(gen(), mimetype='text/event-stream')

# Sandbox requests
@app.route('/run_program', methods=['POST'])
def run():
	# Format of /upload POST request 
	# author (str), date (str), program (str)
  #
	p = str(request.form['program'])
	glob.sandbox.run_program(p)
	return HTTP_OK

@app.route('/stop_program')
def stop():
	glob.sandbox.stop_program()
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
	serial_port_thread = Thread(target=glob.serial.forever_loop)
	serial_port_thread.start()
	
	#
	# Run web app
	web_app_thread = Thread(target=start_web_app)
	web_app_thread.start()

	try:
		while glob.app_is_running:
			time.sleep(1.0)
	except Exception as e:
		print 'Got exception %s' % str(e)
	finally:
		#
		# Gracefully terminate all running threads (after hitting Ctrl-C) 
		print '\nServer shutdown, exiting in 5 secs ...'
		glob.app_is_running = False
		glob.sandbox.fire_event('SHUTDOWN')
		# Shutdown web app by sending a 		
		stop_web_app()
		time.sleep(5.0)
		from sys import exit
		exit(0)
