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
var dashboard = {}

function createDashboardEntry(sensorID) {
	sensor = sensorPropsTable[sensorID];
	for(var i = 0; i < sensor.signal.length; i++) {
		var sigID = `${sensorID}-${sensor.signal[i].name}`;
		if(!(sigID in dashboard)) {
			dashboard[sigID] = new DashboardEntry(sigID, sensor.signal[i]);
			dashboard[sigID].setValue(0);
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

var sse = null;
var stream_id = null;

function toggleSampling() {
	if(!sse) {
		console.log('init sampling');
		initSensors(startSampling);
	}
	else
		stopSampling();
}

function plotSample(json_data) {
	samplingData = JSON.parse(json_data);
	sensor = sensorPropsTable[samplingData.SAMPLE_ID];
	console.log(`Sample: ${samplingData.SAMPLE_ID}, ${samplingData.VAL.toString()}`);
	for(var i = 0; i < sensor.signal.length; i++) {
		var sigID = `${samplingData.SAMPLE_ID}-${sensor.signal[i].name}`;
		dashboard[sigID].setValue(samplingData.VAL);
	}
}

function startSampling() {
	sse = new EventSource('/start_sampling');
	console.log('sse created');
	sse.onmessage = function(message) {
		plotSample(message.data);
	}
	sse.addEventListener('start', function(message) {
		//console.log(`message.data=${message.data}`);
		stream_id = message.data;
		//console.log(`stream_id=${stream_id}`);
	});
	sse.addEventListener('close', function(message) {
		sse.close();
		sse = null;
		console.log(`close sse for stream ${stream_id}`);
	});
	sse.onerror = function(e) {
		console.log(`Eventsource failed: ${e.type}`);
	}
}

function stopSampling() {
	$.get('/stop_sampling', {stream_id: stream_id}).done(function (jsonResp) {
		console.log(`closing stream ${stream_id}`);
	});
}



/*
	var sensor = [
		new Sensor('accelerometer', '1', defaultOpts),
		new Sensor('gyroscope', '2', defaultOpts)
	];

	var ccc = 0;
	setInterval( function() {
		var a = ccc * Math.PI / 180;
		//sensor[0].setValue(Math.round(40 * Math.sin(a+5) + 30 * Math.abs(Math.cos(19 * a))) + 20);
		sensor[0].setValue(Math.round(40 * Math.cos(a) + 30 * Math.abs(Math.cos(15 * a))) + 20);
		sensor[1].setValue(Math.round(40 * Math.cos(a) + 30 * Math.abs(Math.cos(15 * a))) + 20);
		ccc += 18;
	}, 500);
	*/
