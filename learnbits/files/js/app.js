/* * * * * * * * * * * * * *
 *											   *
 * 	Class LearnbitsApp   *
 *											   *
 * * * * * * * * * * * * * */

 function LearnbitsApp() {
   this.dashboard = {}
   this.cameraIsON = false;
   this.samplingIsON = true;
   this.sseSocket = null;
   this.sseStreamId = null;
   this.sensorList = [];
   this.hwErrMessages = {SERIAL_ERROR: '', NO_SERIAL: '', SERVER_SHUTDOWN: ''};
   this.defaultImage = 'media/photo.png';
   this.BlocklyWorkspace = null;
 }

 var app = new LearnbitsApp();
