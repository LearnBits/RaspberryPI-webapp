// Map between addresses and sensor data
function responseIsOK(resp, desc, cmd) {
	//console.log(typeof resp)
	if('STATUS' in resp && resp.STATUS in app.hwErrMessages) {
		console.log(`Could not complete ${desc}, serial error`);
		return false;
	}
	else if(cmd && 'RESP' in resp && resp.RESP != cmd) {
		console.log(`Bad ${cmd} message: ${resp}`);
		return false;
	}
	else
		return true;
}

function noSerial(resp) {
	return 'STATUS' in resp && resp.STATUS == 'NO_SERIAL';
}


function startSSE() {

	app.sseSocket = new EventSource('/connect');
	console.log('app.sseSocket created');

	// Start event
	app.sseSocket.addEventListener('start', function(message) {
		app.streamId = JSON.parse(message.data);
		//startGraphs();
	});

	// Sampling data (default)
	app.sseSocket.onmessage = function(json_message) {
		samplingData = JSON.parse(json_message.data);
		plotDashboardSample(samplingData);
	}

	app.sseSocket.addEventListener('scan', function(message) {
		scanList = JSON.parse(message.data);
		console.log(message.data);
		updateSensors(scanList);
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

function updateSensors(scanList) {

	function diff(a, b) {
		// return members of a that are not in b
		for(var i = 0, l = []; i < a.length; i++)
			if(b.indexOf(a[i]) == -1)
				l.push(a[i]);
		return l;
	}

	// addr ==> sensor_ID
	for(var i = 0; i < scanList.length; i++)
		scanList[i] = sensorIDTable[scanList[i]];
	console.log(scanList)

	removed = diff(app.sensorList, scanList);
	for(var i = 0; i < removed.length; i++) {
		var ID = removed[i];
		unselectSensorControl(ID);
		removeDashboardEntry(ID);
		console.log('Removed sensor ' + ID );
	}

	added = diff(scanList, app.sensorList)
	for(var i = 0; i < added.length; i++) {
		var ID = added[i];
		selectSensorControl(ID);
		createDashboardEntry(ID);
		sendSensorCommand(ID);
		app.samplingIsON = true;
		console.log('Added sensor ' + ID );
	}

	app.sensorList = scanList;
}


function sendSensorCommand(ID) {
	var sensorCmd = sensorPropsTable[ID].command;
	console.log(`send ${JSON.stringify(sensorCmd)}`);
	$.get('/serial_cmd', sensorCmd)
		.done(function (resp) {
			if(!responseIsOK(JSON.parse(resp), `${JSON.stringify(sensorCmd)}`)) {
				console.log(`resp=${resp}`);
			}
		})
		.fail(function () {
				console.log('Failed to send command to sensor ' + ID);
		});
}


var sensorIDTable = {
	'80' : 'SLIDEPOT',
	'104': 'MPU6050',
	'119': 'BMP180',
}

var sensorPropsTable = {

	'MPU6050': {
		command: {CMD: 'MPU6050', MSEC: 50},
		signal: [ {
			name: 'Accelerometer',
			graphFunc: function(val) {
				//return val == 0 ? 0 : Math.sqrt(val[0]*val[0] + val[1]*val[1] + val[2]*val[2]).toFixed(2);
				return val == 0 ? 0 : Math.round(Math.sqrt(val[0]*val[0] + val[1]*val[1] + val[2]*val[2])/100);
			},
			//range: { min: 0, max: 57000 } // > 2^15 (32768) * sqrt(3) (1.732)
			range: { min: 0, max: 100 } // > 2^15 (32768) * sqrt(3) (1.732)
		}, {
			name: 'Gyroscope',
			graphFunc: function(val) {
				//return val == 0 ? 0 : Math.sqrt(val[3]*val[3] + val[4]*val[4] + val[5]*val[5]).toFixed(2);
				return val == 0 ? 0 : Math.round(Math.sqrt(val[3]*val[3] + val[4]*val[4] + val[5]*val[5])/100);
			},
			//range: { min: 0, max: 57000 }
			range: { min: 0, max: 100 }
		} ]
	},

	'BMP180': {
		command: {CMD: 'BMP180', MSEC: 1000},
		signal: [ {
			name: 'Temperature',
			graphFunc: function(val) { return val == 0 ? 0 : val[0].toFixed(2); },
			range: { min: 0, max: 50 }
		}, {
			name: 'Pressure',
			graphFunc: function(val) { return val == 0 ? 0 : val[1].toFixed(2); },
			range: { min: 0, max: 1300 }
	 	} ]
 },

	'SLIDEPOT': { // Slider potentiometer
		command: {CMD: 'SLIDEPOT', MSEC: 300},
		signal: [ {
			name: 'Slider',
			graphFunc: function(val) { return val == 0 ? 0 : Math.round(val[0] * 100 / 2180); },
			range: { min: 0, max: 100 }
		} ]
	}

};

/*
function resetPeripherals() {
  var timer = window.setInterval( function() {
		$.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
			//resp = JSON.parse(JSON.parse(jsonResp));
			resp = JSON.parse(jsonResp);
			//console.log('serial_cmd resp=' + resp);
			if(responseIsOK(resp, 'Hardware reset') || noSerial(resp)) {
				console.log(resp);
				window.clearInterval(timer);
			}
		});
	}, 5000);
}
*/

/*
Color palette used in the shield

const uint32_t RGB_TABLE[RGB_TABLE_SIZE]={
0x800000,0x8B0000,0xA52A2A,0xB22222,0xDC143C,0xFF0000,0xFF6347,0xFF7F50,0xCD5C5C,0xF08080,0xE9967A,0xFA8072,
0xFFA07A,0xFF4500,0xFF8C00,0xFFA500,0xFFD700,0xB8860B,0xDAA520,0xEEE8AA,0xBDB76B,0xF0E68C,0x808000,0xFFFF00,
0x9ACD32,0x556B2F,0x6B8E23,0x7CFC00,0x7FFF00,0xADFF2F,0x006400,0x008000,0x228B22,0x00FF00,0x32CD32,0x90EE90,
0x98FB98,0x8FBC8F,0x00FA9A,0x00FF7F,0x2E8B57,0x66CDAA,0x3CB371,0x20B2AA,0x2F4F4F,0x008080,0x008B8B,0x00FFFF,
0x00FFFF,0xE0FFFF,0x00CED1,0x40E0D0,0x48D1CC,0xAFEEEE,0x7FFFD4,0xB0E0E6,0x5F9EA0,0x4682B4,0x6495ED,0x00BFFF,
0x1E90FF,0xADD8E6,0x87CEEB,0x87CEFA,0x191970,0x000080,0x00008B,0x0000CD,0x0000FF,0x4169E1,0x8A2BE2,0x4B0082,
0x483D8B,0x6A5ACD,0x7B68EE,0x9370DB,0x8B008B,0x9400D3,0x9932CC,0xBA55D3,0x800080,0xD8BFD8,0xDDA0DD,0xEE82EE,
0xFF00FF,0xDA70D6,0xC71585,0xDB7093,0xFF1493,0xFF69B4,0xFFB6C1,0xFFC0CB,0xFAEBD7,0xF5F5DC,0xFFE4C4,0xFFEBCD,
0xF5DEB3,0xFFF8DC,0xFFFACD,0xFAFAD2,0xFFFFE0,0x8B4513,0xA0522D,0xD2691E,0xCD853F,0xF4A460,0xDEB887,0xD2B48C,
0xBC8F8F,0xFFE4B5,0xFFDEAD,0xFFDAB9,0xFFE4E1,0xFFF0F5,0xFAF0E6,0xFDF5E6,0xFFEFD5,0xFFF5EE,0xF5FFFA,0x708090,
0x778899,0xB0C4DE,0xE6E6FA,0xFFFAF0,0xF0F8FF,0xF8F8FF,0xF0FFF0,0xFFFFF0,0xF0FFFF,0xFFFAFA,0x000000,0x696969,
0x808080,0xA9A9A9,0xC0C0C0,0xD3D3D3,0xDCDCDC,0xF5F5F5,0xFFFFFF};
*/
