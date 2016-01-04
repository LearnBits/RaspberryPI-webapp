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

/**
  Commands: motor and led
  */

function initCommands() {
  initMotorSliders();
  initColorPicker();
}

function initMotorSliders() {
  $('input[type="range"]').rangeslider({
      polyfill: false,
      onInit: function () {
        // Note this is the original function. Works only for Init (not sure how)
        var $handle = $('.rangeslider__handle', this.$range);
        $handle[0].textContent = this.value;
      }
  })
  .on('input', function () {
    /**
     * AAAAAAARRRRRRRRGGGGGGGGHHHHHHHH !!!!!
     * This function was AWEFULLY buggy [when 2 sliders were used only it would only update the first one]
     * Here's the fix:
        - in the library rangslider.js I added an id to the slider value element
        - note that in this function 'this' points to the original range input DOM element
        - therefore I retrieve the slider value element by ID and updates its Value
     **/
    slider_val_id = $(this).attr('id') + '-val';
    $('#' + slider_val_id).text(this.value);
  });
}

function initColorPicker() {

  function TagConvertor(chaine, TagList, joker) {
    var _mask = (joker == undefined)? "#":joker;
    for (var val in TagList) chaine = chaine.replace(new RegExp(_mask+val+_mask, "g"), TagList[val]);
    return chaine;
  }
  // LED palette is taked from http://www.rapidtables.com/web/color/RGB_Color.htm

  function BuildPalette(contentTemplateLine, contentTemplate) { //méthode construisant la palette
    var content = ""
    var values = ['#FF4500', '#FFD700', '#32CD32', '#8A2BE2', '#00BFFF', '#FF1493', '#F4A460', '#FFFFFF', '#000000'];
    for (i = 0; i < values.length; i++) {
        content += TagConvertor(contentTemplateLine,{"color":values[i]});
    }
    //Warning : tag starts and ends with #
    content = contentTemplate.replace("#contentLineTemplate#",content);
    return content;
  }

  //initialisation of AntColorPicker with customisation of labels
  $("#led1").AntColorPicker( {//Custom parameters
    //labelClose: "Close color picker",
    //labelRAZColor: "Clear field",
    builder: BuildPalette
  });
  $("#led2").AntColorPicker( {builder: BuildPalette});
  $("#led3").AntColorPicker( {builder: BuildPalette});
  $("#led4").AntColorPicker( {builder: BuildPalette});
  $("#led5").AntColorPicker( {builder: BuildPalette});
  $("#led6").AntColorPicker( {builder: BuildPalette});
  $("#led7").AntColorPicker( {builder: BuildPalette});
  $("#led8").AntColorPicker( {builder: BuildPalette});
}

LED_BAR_COLOR_PALETTE = [
'#800000','#8B0000','#A52A2A','#B22222','#DC143C','#FF0000','#FF6347','#FF7F50','#CD5C5C','#F08080','#E9967A','#FA8072',
'#FFA07A','#FF4500','#FF8C00','#FFA500','#FFD700','#B8860B','#DAA520','#EEE8AA','#BDB76B','#F0E68C','#808000','#FFFF00',
'#9ACD32','#556B2F','#6B8E23','#7CFC00','#7FFF00','#ADFF2F','#006400','#008000','#228B22','#00FF00','#32CD32','#90EE90',
'#98FB98','#8FBC8F','#00FA9A','#00FF7F','#2E8B57','#66CDAA','#3CB371','#20B2AA','#2F4F4F','#008080','#008B8B','#00FFFF',
'#00FFFF','#E0FFFF','#00CED1','#40E0D0','#48D1CC','#AFEEEE','#7FFFD4','#B0E0E6','#5F9EA0','#4682B4','#6495ED','#00BFFF',
'#1E90FF','#ADD8E6','#87CEEB','#87CEFA','#191970','#000080','#00008B','#0000CD','#0000FF','#4169E1','#8A2BE2','#4B0082',
'#483D8B','#6A5ACD','#7B68EE','#9370DB','#8B008B','#9400D3','#9932CC','#BA55D3','#800080','#D8BFD8','#DDA0DD','#EE82EE',
'#FF00FF','#DA70D6','#C71585','#DB7093','#FF1493','#FF69B4','#FFB6C1','#FFC0CB','#FAEBD7','#F5F5DC','#FFE4C4','#FFEBCD',
'#F5DEB3','#FFF8DC','#FFFACD','#FAFAD2','#FFFFE0','#8B4513','#A0522D','#D2691E','#CD853F','#F4A460','#DEB887','#D2B48C',
'#BC8F8F','#FFE4B5','#FFDEAD','#FFDAB9','#FFE4E1','#FFF0F5','#FAF0E6','#FDF5E6','#FFEFD5','#FFF5EE','#F5FFFA','#708090',
'#778899','#B0C4DE','#E6E6FA','#FFFAF0','#F0F8FF','#F8F8FF','#F0FFF0','#FFFFF0','#F0FFFF','#FFFAFA','#000000','#696969',
'#808080','#A9A9A9','#C0C0C0','#D3D3D3','#DCDCDC','#F5F5F5','#FFFFFF'];
