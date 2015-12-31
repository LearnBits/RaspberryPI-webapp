// Project: Gauge demo
// Module: Gauge (main)
// Author: Sergey Shishigin (shishigin.sergey@gmail.com)

'use strict';

function Gauge(container, opts) {

    var value, angle, angleRangeSize,
        dialInd, svg, errList, NAMESPACE_URI, CLASS_NAME,
				needleElem, arc1Elem, arc2Elem, gaugeLabelElem;

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
        //return {x: Math.round(x), y: Math.round(y)};
				return {x: x, y: y};
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
        // An arc
				d = ["M",p1.x,",",p1.y," A", dialInd.r, ",", dialInd.r,
						 " 0, ", la_flag, ",1 ", p2.x, ",", p2.y];
				// A pie
				//d = ["M",p1.x,",",p1.y," A", dialInd.r, ",", dialInd.r,
				//		 " 0, ", la_flag, ",1 ", p2.x, ",", p2.y, " L",cx,",",cy, " Z"];
        return d.join("");
    }


		function drawGaugeBase() {
			// 1) Value
			arc1Elem = createElement('path', {}, 'arc_value');
			svg.appendChild(arc1Elem);

			// 2) Range
			arc2Elem = createElement('path', {}, 'arc_range');
			svg.appendChild(arc2Elem);

			// 3) Needle
			needleElem = createElement('polygon', {}, 'meter_needle');
			svg.appendChild(needleElem);

			// 4) Needle circle
			var attrs = {
				cx: dialInd.cx,
				cy: dialInd.cy,
				r: opts.meter_needle.circle_r
      };
			var circle = createElement('circle', attrs, 'needle_base');
			svg.appendChild(circle);

			// 5) Label
			gaugeLabelElem = createElement('text', {}, 'gauge_label');
			gaugeLabelElem.textContent = '';
			svg.appendChild(gaugeLabelElem);
		}

		function drawDynamicArc() {
			var arc_params = createArcParameters(dialInd.cx, dialInd.cy, dialInd.r, dialInd.sAngle, angle);
   		arc1Elem.setAttribute('d', arc_params);
			arc_params = createArcParameters(dialInd.cx, dialInd.cy, dialInd.r, angle, dialInd.eAngle);
   		arc2Elem.setAttribute('d', arc_params);
    }


    function drawMeterNeedle() {
        var p, p1, p2, points;
        p = polarToCartesian(dialInd.cx, dialInd.cy, dialInd.r + opts.meter_needle.interval, angle);
        p1 = polarToCartesian(dialInd.cx, dialInd.cy, opts.meter_needle.circle_r * 0.5, angle + 90);
        p2 = polarToCartesian(dialInd.cx, dialInd.cy, opts.meter_needle.circle_r * 0.5, angle - 90);
        // TODO: remove magic numbers ^^^
        points = [p.x, p.y, p1.x, p1.y, p2.x, p2.y ].join(",");
				needleElem.setAttribute('points', points);
        //polygon = createElement('polygon', attrs, 'meter_needle');
        //svg.appendChild(polygon);
    }

		function updateGaugeLabel() {
			var p = polarToCartesian(dialInd.cx, dialInd.cy,
															 dialInd.r + opts.meter_needle.interval + opts.tickLabel.interval, angle);
			gaugeLabelElem.setAttribute('x', dialInd.cx);
			gaugeLabelElem.setAttribute('y', dialInd.cy + 35);
			gaugeLabelElem.textContent = value;
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
				drawDynamicArc();
				drawMeterNeedle();
				updateGaugeLabel();
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
    /** Determine geometry of Gauge
        Assume that sAngle and eAngle are symetric
        cx, cy is a bit below center of gravity
        r is calculated so that the gauge displays an aestethics padding
    */
		var alpha = (opts.dial_indicator.sAngle - 180) * 3.1415 / 180;
    dialInd.cx = svg.clientWidth * 0.5;
		dialInd.cy = (svg.clientHeight + (opts.dial_indicator.r * (1 - Math.sin(alpha)))) * 0.5;
    var padding = 20;
    dialInd.r = svg.clientWidth / 2 - (padding + opts.meter_needle.interval);

		drawGaugeBase();
}

Gauge.svgMarkup = "<svg class='gauge'></svg>"


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

/* //Use Gradient
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
