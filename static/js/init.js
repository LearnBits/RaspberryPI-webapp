
$(document).ready(function() {
	initTabs();
	initButtons();
	initSensorControls();
	initAceEditor();
	initBlockly();
	initDashboard();
	initCommands();

	/* * * * * * * * *
	 * Initial state
	 * * * * * * * * */
	//selectTab($('#blockly-editor'));
 	//showContentDiv('blockly-editor', true);
  /* TEMP */
	selectTab($('#commands'));
	showContentDiv('commands', true);
	showContentDiv('blockly-editor', false);
	/* TEMP */
	setButtonState('play-button', 'on');
	setButtonState('stop-button', 'off');
	setButtonState('sample-button', 'on');

	//resetPeripherals();
	//scanSensors();
});
