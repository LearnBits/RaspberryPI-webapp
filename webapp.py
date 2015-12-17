from threading 	import Thread
from Queue 			import Queue
from flask      import Flask, request, Response, redirect
from serialport import LBSerialRequest
from dispatcher import LBDispatcher
from sandbox    import LBSandbox
from glob       import glob
import json, sys, flask.ext.cors

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
		print 'streaming .... done'
	#
	print 'Got sample request, start streaming'
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


###############################################
import random, time
def dummy():
	while glob.app_is_running:
		time.sleep(2+0.005 + random.random()*1.5)
		print('%%%%%%%%%%%%%%%%%%%%%%%%% dummy')
##############################################

# main starts here
if __name__ == '__main__':
  #
	glob.serial.open()
	Thread(target=glob.serial.forever_loop).start()
	
	
	#
	# Run Flask server
	app.run(host='0.0.0.0', port=8080, threaded=True,
					debug=True, use_evalex=False, use_reloader=False)
	#
	# Gracefully terminate all running threads (after hitting Ctrl-C) 
	glob.app_is_running = False
	print 'Exiting learnbit server....'
	sys.exit(0)


