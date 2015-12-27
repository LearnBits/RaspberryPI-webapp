// Map between addresses and sensor data

var initCommand = null;
var errMessages = {SERIAL_ERROR: '', NO_SERIAL: '', SERVER_SHUTDOWN: ''}

function responseIsOK(resp, desc) {
	if('STATUS' in resp && resp.STATUS in errMessages ) {
		console.log(`Could not complete ${desc}, serial error`);
		return false;
	}
	else
		return true;
}

function noSerial(resp) {
	return 'STATUS' in resp && resp.STATUS == 'NO_SERIAL';
}

function resetPeripherals() {
  var timer = window.setInterval( function() {
		$.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
			resp = JSON.parse(jsonResp);
			if(responseIsOK(resp, 'Hardware reset') || noSerial(resp)) {
				console.log(jsonResp);
				window.clearInterval(timer);
			}
		});
	}, 5000);
}

function scanPeripherals(fCounter) {
	var timer = window.setInterval(function () {
		$.get('/serial_scan').done(function (jsonResp) {
			scanResult = JSON.parse(jsonResp);
			if(responseIsOK(scanResult, 'Hardware scan')) {
				if(!('RESP' in scanResult && scanResult.RESP == 'SCAN'))
					console.log('Bad SCAN message: ' + jsonResp);
				else {
					initCommand = [];
					for(var i = 0; i < scanResult.I2C_ADDR.length; i++) {
						var addr = scanResult.I2C_ADDR[i];
						var ID = sensorIDTable[addr];
						console.log('in scan found ID=' + ID );
						selectSensorControl(ID);
						sensor = sensorPropsTable[ID];
						createDashboardEntry(ID);
						initCommand.push(sensor.command);
					}
				}
			}
		 	if('STATUS' in scanResult && scanResult.STATUS == 'NO_SERIAL' )
				window.clearInterval(timer);
		});
	}, 5000);
}


function initSensors(startSamplingFunc) {
	var count = 0;
	console.log(`Initializing ${initCommand.length} sensors`);
	for(var i = 0; i < initCommand.length; i++) {
		console.log(`send ${JSON.stringify(initCommand[i])}`);
		$.get('/serial_cmd', initCommand[i])
  		.done(function (resp) {
				if(responseIsOK(JSON.parse(resp), `${JSON.stringify(initCommand[i])}`)) {
					console.log(`resp=${resp}`);
					count += 1;
					if(count == initCommand.length)
						startSamplingFunc();
				}
			});
	}
}

var sensorIDTable = {
	'80' : 'SLIDEPOT',
	'104': 'MPU6050',
	'119': 'BMP180',
}

var sensorPropsTable = {

	'MPU6050': {
		command: {CMD: 'MPU6050', MSEC: 30},
		signal: [ {
			name: 'Accelerometer',
			graphFunc: function(val) {
				return val == 0 ? 0 : Math.sqrt(val[0]*val[0] + val[1]*val[1] + val[2]*val[2]).toFixed(2);
			},
			range: { min: 0, max: 57000 } // > 2^15 (32768) * sqrt(3) (1.732)
		}, {
			name: 'Gyroscope',
			graphFunc: function(val) {
				return val == 0 ? 0 : Math.sqrt(val[3]*val[3] + val[4]*val[4] + val[5]*val[5]).toFixed(2);
			},
			range: { min: 0, max: 57000 }
		} ]
	},

	'BMP180': {
		command: {CMD: 'BMP180', MSEC: 200},
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

	'SLIDEPOT': {
		command: {CMD: 'SLIDEPOT', MSEC: 100},
		signal: [ {
			name: 'Slider',
			graphFunc: function(val) { return val == 0 ? 0 : Math.round(val[0] * 100 / 2180); },
			range: { min: 0, max: 100 }
		} ]
	}

};
