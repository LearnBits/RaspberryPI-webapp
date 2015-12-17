/* * * * * * * * * 
*
* Tabs handling
*
* * * * * * * * */
function initTabs() {
// Tabs initial state
	$('#tabs-div ul li').each(function() {
		unselectTab($(this));
	});														 
	// Tab selection
	$('#tabs-div ul li').click(function() {
		// (1) select me/show div (2) unselect others/hide other divs
		var clicked = $(this).attr('id');
		$('#tabs-div ul li').each(function() {
			var clickedMe = ($(this).attr('id') == clicked);
			if(clickedMe)
				selectTab($(this));
			else
				unselectTab($(this));
			showContentDiv($(this).attr('id'), clickedMe);
		});
	});
	// Tab hover
	$('#tabs-div ul li').mouseenter(function() {
		if($(this).hasClass('tab0'))
			hoverTab($(this));
	});
	$('#tabs-div ul li').mouseleave(function() {
		// Pay attention: selected tab also has class tab-hover, 
		if($(this).hasClass('tab-hover') && !$(this).hasClass('tab1'))
			unselectTab($(this));
	});
}

function selectTab($tab) {
	$tab.attr('class','tab1 tab-hover').children('img').attr('class', 'img1');
}
function unselectTab($tab) {
	$tab.attr('class','tab0').children('img').attr('class', 'img0');
}
function hoverTab($tab) {
	$tab.attr('class','tab-hover').children('img').attr('class', 'img1');
}

// handle toggling content-divs
function showContentDiv(content, show) {
	$('#' + content + '-div').css({visibility: show ? 'visible' : 'hidden'});
		
	/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
	 *               >>>>>   Unbelievable!!   <<<<<
	 *   Blockly silently creates elements under the document root
	 *            Need to manually make them invisible
	 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
	if(content == 'blockly-editor')
		$('[class*="blockly"]').each(function() {
			$(this).css({'visibility':  show ? 'visible' : 'hidden'});
		});
}

/* * * * * * * * * 
*
* Sensors handling
*
* * * * * * * * */
function initSensorControls() {
// Sensors initial state
	$('#sensors-div ul li').each(function() {
		unselectSensorControl($(this).attr('id'));
	});														 
	// Sensor selection
	$('#sensors-div ul li').click(function() {
		/*if(!$(this).hasClass('sensor-selected'))
			 selectSensorControl($(this).attr('id'));
		else
			unselectSensorControl($(this).attr('id'));*/
	});
}

function selectSensorControl(id) {
	$(`[id="${id}"]`).addClass('sensor-selected').children('img').attr('class', 'img1');
}
function unselectSensorControl(id) {
	$(`[id="${id}"]`).removeClass('sensor-selected').children('img').attr('class', 'img0');
}


/* * * * * * * * * 
*
* Buttons handling
*
* * * * * * * * */
function initButtons() {
$('[class="control-button"]').each(function() {
		$(this).attr('src', $(this).data('src') + '1.png');
		$(this).mouseenter(function() {
			var isOn = $(this).data('state') == 'on';			
			$(this).attr('src', $(this).data('src') + (isOn ? '2.png' : '1.png'));
			$(this).css({'cursor': isOn ? 'pointer' : 'default'});
		});
		$(this).mouseleave(function() {
			$(this).attr('src', $(this).data('src') + '1.png');
		});
	});
	//$('#play-button').click(runProgram);
	//$('#stop-button').click(stopProgram);
	$('#sample-button').click(toggleSampling);
}

function setButtonState(button, state) {
	$('#' + button).data('state', state);
	$('#' + button).css({'opacity': state == 'on' ? 1.0 : 0.5});
}
