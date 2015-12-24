// Map between addresses and sensor data

var initCommand = null;
var errMessages = {SERIAL_ERROR: '', SERVER_SHUTDOWN: ''}

function responseIsOK(resp, desc) {
	if('STATUS' in resp && resp.STATUS in errMessages ) {
		console.log(`Could not complete ${desc}, serial error`);
		return false;
	}
	else
		return true;
}

function resetHardwarePoll() {
  var timer = window.setInterval( function() {
		$.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
			if(responseIsOK(JSON.parse(jsonResp), 'Hardware reset')) {
				console.log(jsonResp);
				window.clearInterval(timer);
			}
		});
	}, 5000);
}

function scanHardwarePoll(fCounter) {
	function scanHardware() {
		$.get('/serial_scan').done(function (jsonResp) {
			scanResult = JSON.parse(jsonResp);
			if(responseIsOK(scanResult, 'Hardware scan')) {
				if(!('RESP' in scanResult && scanResult.RESP == 'SCAN'))
					console.log('Bad SCAN message: ' + jsonResp);
				else {
					initCommand = []
					for(var i = 0; i < scanResult.I2C_ADDR.length; i++) {
						var addr = scanResult.I2C_ADDR[i];
						var sensor = sensorAddrMap[addr];
						selectSensorControl(sensor.id);
						createDashboardEntry(sensor);
						initCommand.push(sensor.init_cmd);
					}
				}
			}
		});
	}
	var timer = window.setInterval(scanHardware, 5000);
}

	/*
function resetHardware(fCounter) {
  $.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
		if(responseIsOK(JSON.parse(jsonResp), 'Hardware reset')) {
			console.log(jsonResp);
			if(fCounter == 1) fCounter -= 1;
	});
}

function scanHardware(fCounter) {
  $.get('/serial_scan').done(function (jsonResp) {
		scanResult = JSON.parse(jsonResp);
		if(responseIsOK(scanResult, 'Hardware scan')) {
			if(!('RESP' in scanResult && scanResult.RESP == 'SCAN'))
				console.log('Bad SCAN message: ' + jsonResp);
			else {
				initCommand = []
				for(var i = 0; i < scanResult.I2C_ADDR.length; i++) {
					var addr = scanResult.I2C_ADDR[i];
					var sensor = sensorAddrMap[addr];
					selectSensorControl(sensor.id);
					createDashboardEntry(sensor);
					initCommand.push(sensor.cmd);
				}
			}
		}
	});
}
*/
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

var sensorAddrMap = {
	'104': {
		name: 'Accelerometer',
		id: 'MPU6050',
		init_cmd: {CMD: 'MPU6050', MSEC: 500},
		dashboard_func: function(arr) {
			return arr.length == undefined ? arr /* scalar */
				: Math.sqrt(arr[0]*arr[0] + arr[1]*arr[1] + arr[2]*arr[2]);
		}
	 }
};
