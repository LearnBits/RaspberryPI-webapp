// Map between addresses and sensor data

var sensorAddrMap = {
	'104': {name: 'Accelerometer', id: 'MPU6050', cmd: {CMD: 'MPU6050', MSEC: 500} }
};

var initCommand = null;

function resetHardware() {
  $.get('/serial_cmd', {CMD: 'RESET'}).done(function (jsonResp) {
		console.log(jsonResp);
	});
}

function scanHardware() {
  $.get('/scan').done(function (jsonResp) {
		
		console.log(jsonResp);
		scanResult = JSON.parse(jsonResp);

		if(!('RESP' in scanResult && scanResult.RESP == 'SCAN'))
			console.log('Bad SCAN message: ' + jsonResp);

		initCommand = []
		for(var i = 0; i < scanResult.I2C_ADDR.length; i++) {
			var addr = scanResult.I2C_ADDR[i];
			var sensor = sensorAddrMap[addr];
			selectSensorControl(sensor.id);
			createDashboardEntry(sensor);
			initCommand.push(sensor.cmd);
		}
	});
}

function initSensors(startSamplingFunc) {
	var count = 0;
	console.log(`Initializing ${initCommand.length} sensors`);
	for(var i = 0; i < initCommand.length; i++) {
		console.log(`send ${JSON.stringify(initCommand[i])}`);
		$.get('/serial_cmd', initCommand[i])
  		.done(function (resp) {
				console.log(`resp=${resp}`);
				count += 1;
				if(count == initCommand.length)
					startSamplingFunc();
			});
	}
}