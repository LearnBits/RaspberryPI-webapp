
$(document).ready(function() {
	initTabs();
	initButtons();
	initSensorControls();
	initAceEditor();
	initBlockly();
	initDashboard();

	/* * * * * * * * *
	 * Initial state
	 * * * * * * * * */
	selectTab($('#blockly-editor'));
	showContentDiv('blockly-editor', true);
	setButtonState('play-button', 'on');
	setButtonState('stop-button', 'off');
	setButtonState('sample-button', 'on');

	//resetPeripherals();
	scanSensors();
});
