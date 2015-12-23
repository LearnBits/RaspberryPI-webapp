// Map between addresses and sensor data

var sensorAddrMap = {
	'104': {name: 'Accelerometer', id: 'MPU6050', cmd: {CMD: 'MPU6050', MSEC: 500} }
};

var initCommand = null;
var errMessages = {SERIAL_ERROR: '', SERVER_SHUTDOWN: ''}

function checkError(resp, desc) {
	if('STATUS' in resp && resp.STATUS in errMessages ) {
		console.log(`Could not complete ${desc}, serial error`);
		return true;
	}
	else
		return false;
}

function resetHardwarePoll() {
  var timer = window.setInterval( function() {
		$.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
			if(!checkError(JSON.parse(jsonResp), 'Hardware reset')) {
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
			if(!checkError(scanResult, 'Hardware scan')) {
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
	var timer = window.setInterval(scanHardware, 5000);
}

	/*
function resetHardware(fCounter) {
  $.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
		if(!checkSerialError(JSON.parse(jsonResp), 'Hardware reset')) {
			console.log(jsonResp);
			if(fCounter == 1) fCounter -= 1;
	});
}

function scanHardware(fCounter) {
  $.get('/serial_scan').done(function (jsonResp) {		
		scanResult = JSON.parse(jsonResp);
		if(!checkSerialError(scanResult, 'Hardware scan')) {
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
				if(!checkSerialError(JSON.parse(resp), `${JSON.stringify(initCommand[i])}`)) {
					console.log(`resp=${resp}`);
					count += 1;
					if(count == initCommand.length)
						startSamplingFunc();
				}
			});
	}
}
