function runProgram() {
	var program = aceEditor.getValue();
	console.log('run program ' + program);
  $.post('/run_program', { 
	    author: 'david',
	    date: new Date(),
	    program: program,
	})
	.done(function (msg) {
		if(msg == 'OK' )
			setButtonState('stop-button', 'on');
	  var s1 = 'Program uploaded successfully'
		var s2 = 'Error uploading program'
		console.log( msg == 'OK' ? s1 : s2)
	});
}

function stopProgram() {
	$.get('/stop_program').done(function (msg) {
		if(msg == 'OK' )
			setButtonState('stop-button', 'off');
		console.log( msg == 'OK' ? 'OK' : 'Error could not issue a stop command');
	});
}



/* * * * * * * * * * * * * * * * * *
 *																 *	
 *  Ace code									 *
 *																 *	
 * * * * * * * * * * * * * * * * * */
var aceEditor = null;

function initAceEditor() {
    var prog = $('#init_program').text().trim()+'\n';
    $('#ace-editor-div').text(prog);
    aceEditor = ace.edit("ace-editor-div");
    aceEditor.setTheme("ace/theme/clouds");
    aceEditor.getSession().setMode("ace/mode/python");
		aceEditor.setShowPrintMargin(false);
}


/* * * * * * * * * * * * * * * * * *
 *																 *	
 *  Blockly code									 *
 *																 *	
 * * * * * * * * * * * * * * * * * */

function generatePythonSourceCode() {
  var pythonSourceCode = Blockly['Python'].workspaceToCode(workspace);
  var sourceCodePanel = document.getElementById('pythonSourceCode');
	sourceCodePanel.value = pythonSourceCode;

	console.log(pythonSourceCode);
	$.ajax({
		type: "POST", url: "/upload",
		data: JSON.stringify({code: pythonSourceCode}),
		contentType: "application/json",
		success: function (msg) {
			console.log(msg);
		}
	});
	/*
	var charCodesText = document.getElementById('charCodes');
	var _strcode = '';
	for(var i=0; i<_code.length; i++) {
		var c = _code.charCodeAt(i)
		_strcode += c==32 ? '..' : (c==10 ? '\n' : c+'.');
	}
	charCodesText.value = _strcode;
	*/
}



// Depending on the URL argument, render as LTR or RTL.

function initBlockly() {
	var workspace = Blockly.inject(
		'blockly-editor-div', 
		{
			comments: true,
			disable: true,
			collapse: true,
			grid: {
				spacing: 25,
				length: 3,
				colour: '#ddd', // DK: customize
				snap: true },
			maxBlocks: Infinity,
			media: 'lib/blockly/media/',
			rtl: (document.location.search == '?rtl'),
			scrollbars: true,
			toolbox: document.getElementById('toolbox'),
			zoom: {
				controls: true,
				wheel: true,
				startScale: 1.0,
				maxScale: 4,
				minScale: .25,
				scaleSpeed: 1.1
			},
		});
}

/*
var workspace = null;

function toXml() {
  var output = document.getElementById('importExport');
  var xml = Blockly.Xml.workspaceToDom(workspace);
  output.value = Blockly.Xml.domToPrettyText(xml);
  output.focus();
  output.select();
}

function fromXml() {
  var input = document.getElementById('importExport');
  var xml = Blockly.Xml.textToDom(input.value);
  Blockly.Xml.domToWorkspace(workspace, xml);
}
*/

