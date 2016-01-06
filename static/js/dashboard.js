/* * * * * * * * * * * * * *
 *											   *
 * 	Class DashboardEntry   *
 *											   *
 * * * * * * * * * * * * * */


function DashboardEntry(sigID, signal) {
	// Name must be unique
	this.signal = signal;
	var sensorMarkup =
		`<tr><td><div class='label-div' id='label-${sigID}'>${signal.name}</div></td>` +
		`<td><div class='gauge-div' id='gauge-${sigID}'></div></td>` +
		//BUG in smoothie:  MUST provide width and height of the canvas
		`<td><canvas class='graph-canvas' id='canvas-${sigID}' ` +
		`width='400' height='150'></canvas></td></tr>`;
	//console.log(sensorMarkup);
	$('#sensors-table').append(sensorMarkup);
	// Graph
	var canvasElem = $(`#canvas-${sigID}`)[0];
	//console.log(canvasElem.toString());
	var range = { minValue: signal.range.min, maxValue: signal.range.max };
	this.graph = new SmoothieChart(this.graphOptions(range));
	this.graph.streamTo(canvasElem, 1000 /*delay*/);
	this.timeSeries = new TimeSeries();
  this.graph.addTimeSeries(this.timeSeries, this.timeSeriesOptions({}));
	// Gauge
	range = { 'range': [signal.range.min, signal.range.max] };
	var gaugeElem = $(`#gauge-${sigID}`)[0];
	this.gauge = new Gauge(gaugeElem, this.gaugeOptions(range));
}

DashboardEntry.prototype.setValue = function(value) {
	var computed_value = this.signal.graphFunc(value);
  this.timeSeries.append(new Date().getTime(), computed_value);
	this.gauge.setValue(computed_value);
}

DashboardEntry.prototype.graphOptions = function(opts) {
  var default_opts =  {
		//interpolation:'linear',
		scaleSmoothing: 0.179,
		grid: {
			fillStyle:'#0da1ba',
			strokeStyle:'rgba(119,119,119,0.24)'
		},
		labels: {
			fillStyle: 'rgba(255,255,255,0.6)',
			fontSize: 10,
			fontFamily: "Nunito"
		},
		maxValue: 32768,
		minValue: 0,
		timestampFormatter: SmoothieChart.timeFormatter
	};
	return this.setOptions(opts, default_opts);
}

DashboardEntry.prototype.timeSeriesOptions = function(opts) {
	var default_opts = {
		lineWidth:1.1,
		strokeStyle:'none',
		fillStyle:'rgba(6,117,135,0.36)'
	};
	return this.setOptions(opts, default_opts);
}

DashboardEntry.prototype.gaugeOptions = function(opts) {
	var default_opts = {
		value: 0,
		range: [0, 32768],
		zones: [{length_quota: 1.0, color: '#ffe0b3'}],
		dial_indicator: {
			cx: 0,cy: 0, r: 70, // cx and cy are computed automatically in the library
			sAngle: 210, eAngle: -30,
			stroke_width: 12
		},
		tickLabel: {interval: 16},     // between dial and tick label
		tickLine: {interval: 15 /* between dial and tick */, length: 15},
		meter_needle: {circle_r: 8, interval: 25} /* between dial and end of needle */
	};
	return this.setOptions(opts, default_opts);
}

DashboardEntry.prototype.setOptions = function(options, default_options) {
	for(var opt in default_options) {
		//if(default_options.hasOwnProperty(opt)) {
			//if(default_options.hasOwnProperty(opt) && !options.hasOwnProperty(opt)) {
			if(!options.hasOwnProperty(opt)) {
				options[opt] = default_options[opt];
			}
		//}
	}
	return options;
}

/* * * * * * * * * * * * *
 *											 *
 * 	Init								 *
 *											 *
 * * * * * * * * * * * * */

function initDashboard() {
}

var defaultOpts = {
		graph: {},
		timeSeries: {},
		gauge: {}
}

function createDashboardEntry(sensorID) {
	sensor = sensorPropsTable[sensorID];
	for(var i = 0; i < sensor.signal.length; i++) {
		var sigID = `${sensorID}-${sensor.signal[i].name}`;
		if(!(sigID in app.dashboard)) {
			app.dashboard[sigID] = new DashboardEntry(sigID, sensor.signal[i]);
			app.dashboard[sigID].setValue(0);
		}
		else
			console.log(`${sigID} already exists in the dashboard`);
	}
}

/* * * * * * * * * * * * *
 *											 *
 * 	Data streaming			 *
 *											 *
 * * * * * * * * * * * * */

function toggleSampling() {
	if(!app.sseSocket) {
		console.log('init sampling');
		initSensors(startSampling);
	}
	else
		stopSampling();
}

function plotDashboardSample(samplingData) {
	sensor = sensorPropsTable[samplingData.SAMPLE_ID];
	//console.log(`Sample: ${samplingData.SAMPLE_ID}, ${samplingData.VAL.toString()}`);
	for(var i = 0; i < sensor.signal.length; i++) {
		var sigID = `${samplingData.SAMPLE_ID}-${sensor.signal[i].name}`;
		app.dashboard[sigID].setValue(samplingData.VAL);
	}
}

function startSampling() {
	function startGraphs() {
		for(var i = 0; i < dashboard.length; i++)
			app.dashboard[i].graph.start();
	}

	app.sseSocket = new EventSource('/start_sampling');
	console.log('app.sseSocket created');

	app.sseSocket.onmessage = function(json_message) {
		samplingData = JSON.parse(json_message.data);
		if(samplingData.SAMPLE_ID != 'CAMERA')
			plotDashboardSample(samplingData);
	}
	app.sseSocket.addEventListener('start', function(message) {
		app.streamId = message.data;
		startGraphs();
	});
	app.sseSocket.addEventListener('close', function(message) {
		app.sseSocket.close();
		app.sseSocket = null;
		console.log(`close app.sseSocket for stream ${app.streamId}`);
	});
	app.sseSocket.onerror = function(e) {
		console.log(`Eventsource failed: ${e.type}`);
	}
}

function stopSampling() {
	function stopGraphs() {
		for(var i = 0; i < dashboard.length; i++)
			app.dashboard[i].graph.stop();
	}
	$.get('/stop_sampling', {STREAM_ID: app.streamId}).done(function (jsonResp) {
		console.log(`closing stream ${app.streamId}`);
	});
	stopGraphs();
}
