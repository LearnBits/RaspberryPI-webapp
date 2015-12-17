// Project: Gauge demo
// Module: Gauge (main)
// Author: Sergey Shishigin (shishigin.sergey@gmail.com)

'use strict';

function Gauge(container, opts) {

    var value, angle, angleRangeSize,
        dialInd, svg, errList, NAMESPACE_URI, CLASS_NAME, needleElem;

    this.lastError = function () {
        return errList.join(";");
    };

    function checkIfGaugeExists() {
        var isExists = false, i;
        svg = container.getElementsByTagName("svg");
        if (svg.length > 0) {
            for (i = 0; i < svg.length; i++) {
                isExists = isExists || svg[i].getAttribute("class") === CLASS_NAME;
                if (isExists) {
                    break;
                }
            }
        }
        return isExists;
    }

    function checkOpts() {
        var key;
        errList = [];
        //check range
        if (opts.range[0] >= opts.range[1]) {
            errList.push(Gauge.errors.invalid_option_range);
        } else {
            //check labels
            for (key in opts.labels) {
                if (opts.labels.hasOwnProperty(key)) {
                    if (+key < opts.range[0] || +key > opts.range[1]) {
                        errList.push(Gauge.errors.invalid_option_labels);
                        break;
                    }
                }
            }
        }
        return errList;
    }
	
		
    function setOptions(default_opts) {
        var opt;
        opts = opts || {};
        for (opt in default_opts) {
            if (default_opts.hasOwnProperty(opt)) {
                if (default_opts.hasOwnProperty(opt) && !opts.hasOwnProperty(opt)) {
                    opts[opt] = default_opts[opt];
                }
            }
        }
        return opts;
    }

    function calcAngle(value) {
        if (+value < opts.range[0] || +value > opts.range[1]) {
            errList.push(Gauge.errors.invalid_tick_value);
            return -1;
        }
        var anglePerRange = angleRangeSize / (opts.range[1] - opts.range[0]);
        return opts.dial_indicator.sAngle - value * anglePerRange;
    }

    function polarToCartesian(cx, cy, r, a) {
        var x, y, angleRad;

        angleRad = a * Math.PI / 180.0;
        x = cx + r * Math.cos(angleRad);
        y = cy - r * Math.sin(angleRad);    // use "-", because we need to transform cy-axes
        return {x: Math.round(x), y: Math.round(y)};
        //TODO: maybe use array instead dict ^^^ (?)
    }

    function createElement(name, attrs, _class) { // class is a reserved token
        var attr, el;
        el = document.createElementNS(NAMESPACE_URI, name);
        if (_class !== undefined) {
            el.setAttribute('class', _class);
        }
        for (attr in attrs) {
            if (attrs.hasOwnProperty(attr)) {
                el.setAttribute(attr, attrs[attr]);
            }
        }
        return el;
    }

    function createArcParameters(cx, cy, r, sAngle, eAngle) {
        var p1, p2, la_flag, d;

        p1 = polarToCartesian(cx, cy, r, sAngle);
        p2 = polarToCartesian(cx, cy, r, eAngle);
        la_flag = (sAngle - eAngle) <= 180 ? 0 : 1;
        d = ["M",p1.x,",",p1.y," A", dialInd.r, ",", dialInd.r,
						 " 0, ", la_flag, ",1 ", p2.x, ",", p2.y];
        return d.join("");
    }

		/*
    function removeMeterNeedle() {
        var items, i;
        items = [].slice.call(svg.getElementsByClassName('meter_needle'));
        for (i = 0; i < items.length; i++) {
            items[i].parentNode.removeChild(items[i]);
        }
    }*/

    function drawDialIndicatorZones() {
        var arc, sZoneAngle, eZoneAngle, i;

        eZoneAngle = dialInd.sAngle;
        for (i = 0; i < opts.zones.length; i++) {
            sZoneAngle = eZoneAngle;
            eZoneAngle = sZoneAngle - angleRangeSize * opts.zones[i].length_quota;

            arc = createElement('path', {
							d: createArcParameters(dialInd.cx, dialInd.cy, dialInd.r, sZoneAngle, eZoneAngle),
							stroke: opts.zones[i].color,
							//stroke: 'url(#gaugegradient)',
							'stroke-width': opts.dial_indicator.stroke_width // Arrgh!! need to quote this attr!!
						}, 'dial_indicator');
            svg.appendChild(arc);   
					
        }
    }

    function drawTicks() {
        var text, line, sZoneAngle,  p, p1, p2, r1, r2, attrs, key;
				//console.log(opts.labels);
        for(key in opts.labels) {
            if (opts.labels.hasOwnProperty(key)) {
                sZoneAngle = calcAngle(key);
                p = polarToCartesian(dialInd.cx, dialInd.cy, 
																		dialInd.r - opts.dial_indicator.stroke_width *0.4 -
																		opts.tickLine.length - opts.tickLabel.interval, 
																		sZoneAngle);
                text = createElement('text', p, 'tick_label');
								// DK: the labels are computed automatically
								// It's not clear why the value is stored in a prop called 'value'. Maybe a bug
                text.textContent = opts.labels[key].value;
								var isSmallTick = (text.textContent == '.');
								var isMidTick   = (text.textContent == '..');
								if(text.textContent[0] == '.') text.textContent = '';
                svg.appendChild(text);

								/* * * * * * * * * * * * * * * * * * * * * * * * * * * *
								 * Modified by DK                                      *
								 * Added small intermediate ticks with no labels       *
								 * * * * * * * * * * * * * * * * * * * * * * * * * * * */
                //r1 = dialInd.r + opts.tickLine.interval + opts.tickLine.length; 
                //r2 = dialInd.r + opts.tickLine.interval + /* DK: added the following term */
                r1 = dialInd.r - opts.dial_indicator.stroke_width *0.4 - 5;
                r2 = r1  - opts.tickLine.length  * (isSmallTick ? 0.1 : (isMidTick ? 0.4 : 0.8 )); 
                p1 = polarToCartesian(dialInd.cx, dialInd.cy, r1, sZoneAngle);
                p2 = polarToCartesian(dialInd.cx, dialInd.cy, r2, sZoneAngle);
								//console.log(p1, p2);
                attrs = {"x1": p1.x, "y1": p1.y, "x2": p2.x, "y2": p2.y};
                line = createElement('line', attrs, isSmallTick || isMidTick? 'smalltick' : 'tick');
                svg.appendChild(line);
            }
        }
    }

    function drawMeterNeedle() {
        var circle, polygon, attrs, p, p1, p2, points;

        // draw circle in center
        attrs = {
            cx: dialInd.cx,
            cy: dialInd.cy,
            r: opts.meter_needle.circle_r
        };
        circle = createElement('circle', attrs, 'needle_base');
        svg.appendChild(circle);

        // draw meter_needle
        p = polarToCartesian(dialInd.cx, dialInd.cy, dialInd.r + opts.meter_needle.interval, angle);
        p1 = polarToCartesian(dialInd.cx, dialInd.cy, opts.meter_needle.circle_r * 0.5, angle + 90);
        p2 = polarToCartesian(dialInd.cx, dialInd.cy, opts.meter_needle.circle_r * 0.5, angle - 90);
        // TODO: remove magic numbers ^^^
        points = [p.x, p.y, p1.x, p1.y, p2.x, p2.y ].join(",");
        attrs = {
            "points": points
        };
				needleElem.setAttribute('points', points);
        //polygon = createElement('polygon', attrs, 'meter_needle');
        //svg.appendChild(polygon);
    }

    function render() {
        //removeMeterNeedle();
        drawDialIndicatorZones();
        drawMeterNeedle();
        drawTicks();
    }

    //Set angle value on dial indicator
    //angle: an angle in degrees
    function setAngle(a) {
        if (a > dialInd.sAngle || angle < dialInd.eAngle) {
            errList.push(Gauge.errors.invalid_angle);
        } else {
            angle = a;
        }
        //render();
				//removeMeterNeedle();
				drawMeterNeedle();
    }

    // Set tick value on dial indicator
    // value: tick value
    this.setValue = function (val) {
        errList = [];
        value = val;
        angle = calcAngle(value);
        if (angle !== -1) {
            setAngle(angle);
        }
    };
	
		/*
	 function printChildren(e) {
		 var child = e.children;
		 for (var i = 0; i < child.length; i++) {
    	 console.log(child[i].tagName);
			 if(child[i].tagName == 'defs')
				 printChildren(child[i]);
			 }
	 }*/

    // vars init
		opts = setOptions(Gauge.default_opts);
    NAMESPACE_URI = "http://www.w3.org/2000/svg";
    CLASS_NAME = "gauge";
    errList = [];
    if (checkOpts().size > 0) {
        return this;
    }

    if (checkIfGaugeExists()) {
        errList.push("gauge is already exists in container");
        return this;
    }

    dialInd = opts.dial_indicator; // we use dialInd instead opts.dial_indicator
    angleRangeSize = Math.abs(dialInd.eAngle - dialInd.sAngle);
    value = opts.value;
    angle = calcAngle(value);
    container.innerHTML = Gauge.svgMarkup;
    svg = container.getElementsByTagName("svg")[0];
		dialInd.cx = svg.clientWidth * 0.5;
		// Assume that sAngle and eAngle are symetric
		var alpha = (opts.dial_indicator.sAngle - 180) * 3.1415 / 180;
		dialInd.cy = (svg.clientHeight + (opts.dial_indicator.r * (1 - Math.sin(alpha)))) * 0.5;
	
		drawDialIndicatorZones();
		//drawMeterNeedle();
		drawTicks();
	  needleElem = createElement('polygon', {}, 'meter_needle');
		svg.appendChild(needleElem);
}

Gauge.svgMarkup = "<svg class='gauge'></svg>"
/*
Gauge.svgMarkup = "\
<svg class='gauge'>\
  <defs>\
    <linearGradient id='gaugegradient'>\
      <stop offset='5%'  stop-color='#ccff66'/>\
      <stop offset='40%'  stop-color='#ffff66'/>\
			<stop offset='80%'  stop-color='#ffcc66'/>\
	 	  <stop offset='100%' stop-color='#ff7733'/>\
    </linearGradient>\
  </defs>\
</svg>";*/

Gauge.default_opts = {
    value: 0,                           // default value
    range: [0, 6],                      // range
    labels: {0: '0',                    // labels
             1: '1',
             2: '2',
             3: '3',
             4: '4',
             5: '5',
             6: '6'},
    zones: [                              // color zones
        {   length_quota: 0.75,
            color: '#686868'
            },
        {   length_quota: 0.15,
            color: '#FFC458'
            },
        {   length_quota: 0.1,
            color: '#FF0000'
            }
    ],
    dial_indicator: {                     // dial indicator drawing parameters
        cx: 300,
        cy: 300,
        r: 200,
        sAngle: 210,
        eAngle: -30
    },
    tickLabel: {                          // tick label drawing parameters
        interval: 35                      // interval between dial indicator and tick label
    },
    tickLine: {                           // tick line drawing parameters
        interval: 10,                     // interval between dial indicator and tick line
        length: 10                        // length of tick line
    },
    meter_needle: {                       // meter needle drawing parameters
        circle_r: 10,
        interval: 10                      // interval between dial indicator and end of meter needle
    }
};

//TODO: make error strings parametrized
Gauge.errors = {
    'invalid_option_range': "Invalid range",
    'invalid_option_labels': "Invalid labels",
    'invalid_tick_value': "Invalid value",
    'invalid_angle': "Invalid angle"
};