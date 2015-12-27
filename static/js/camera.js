var camera = false;

function toggleCamera() {
  console.log(`togglecamera: camera=${camera}`);
  if(camera)
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
      camera = true;
    }
	});
}

function stop_camera() {
  console.log('stop_camera');
  $.get('/stop_camera').done(function (msg) {
		if(msg == 'OK' ) {
      $('#video-stream-img').attr('src', '');
      $('#camera-button').text('Start');
      camera = false;
    }
	});
}
