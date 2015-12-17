// Project: Gauge demo
// Module: gauge-plugin (jQuery plugin)
// Author: Sergey Shishigin (shishigin.sergey@gmail.com)

/*jslint todo: true */
/*jslint browser:true */
/*jslint plusplus: true */

(function ($) {
    'use strict';
    var gauge, methods;
    methods = {
        init: function (opts1) {
            var opts = $.extend({}, Gauge.default_opts, opts1);
            if (this.get().length === 1) {
                gauge = new Gauge(this.get(0), opts);
            } else {
                console.log("container must be only one");
                //TODO: handle error
            }
            return this;
        },
        setvalue: function (value) {
            gauge.setValue(value);
            return this;
        },
        geterror: function () {
            return gauge.lastError();
        }
    };

    $.fn.gauge = function (method) {
        if ( methods[method] ) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Метод с именем ' +  method + ' не существует для jQuery.gauge');
        }
    };
})(jQuery);