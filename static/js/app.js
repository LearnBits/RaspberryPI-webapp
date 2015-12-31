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
 }

 var app = new LearnbitsApp();
