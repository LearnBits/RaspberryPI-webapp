/* * * * * * * * * * * * * *
 *											   *
 * 	Class LearnbitsApp   *
 *											   *
 * * * * * * * * * * * * * */

 function LearnbitsApp() {
   this.dashboard = {}
   this.cameraIsON = false;
   this.sseSocket = null;
   this.sseStreamId = null;
   this.hwInitCommand = [];
   this.hwErrMessages = {SERIAL_ERROR: '', NO_SERIAL: '', SERVER_SHUTDOWN: ''};
   this.defaultImage = 'media/photo.png';
   this.BlocklyWorkspace = null;
 }

 var app = new LearnbitsApp();
