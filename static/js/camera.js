function toggleCamera() {
  console.log(`togglecamera: camera=${app.cameraIsON}`);
  if(app.cameraIsON)
    stop_camera();
  else
    start_camera();
}

function start_camera() {
  console.log('start_camera');
  $.get('/start_camera').done(function (msg) {
		if(msg == 'OK' ) {
      $('#video-stream-img').attr('src', '/camera_stream');
      $('#camera-button').text('Stop');
      app.cameraIsON = true;
    }
	});
}

function stop_camera() {
  console.log('stop_camera');
  $.get('/stop_camera').done(function (msg) {
		if(msg == 'OK' ) {
      $('#camera-button').text('Start');
      app.cameraIsON = false;
      $('#video-stream-img').attr('src', '');
      /*window.setTimeout( function() {
        $('#video-stream-img').attr('src', '');
      }, 1000);*/
    }
	});
}

function printComputerVisionResults(samplingData) {
  console.log(samplingData);
}
