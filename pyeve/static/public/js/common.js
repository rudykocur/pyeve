/**
 * Created by Rudy on 2014-09-16.
 */


if (typeof Object.create != 'function') {
    Object.create = (function () {
        var Object = function () {
        };
        return function (prototype) {
            if (arguments.length > 1) {
                throw Error('Second argument not supported');
            }
            if (typeof prototype != 'object') {
                throw TypeError('Argument must be an object');
            }
            Object.prototype = prototype;
            var result = new Object();
            Object.prototype = null;
            return result;
        };
    })();
}


if (!Function.prototype.bind) {
    Function.prototype.bind = function (oThis) {
        if (typeof this !== "function") {
            // closest thing possible to the ECMAScript 5
            // internal IsCallable function
            throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
        }

        var aArgs = Array.prototype.slice.call(arguments, 1),
            fToBind = this,
            fNOP = function () {
            },
            fBound = function () {
                return fToBind.apply(this instanceof fNOP && oThis
                        ? this
                        : oThis,
                    aArgs.concat(Array.prototype.slice.call(arguments)));
            };

        fNOP.prototype = this.prototype;
        fBound.prototype = new fNOP();

        return fBound;
    };
}


Observable = (function() {
    var pub = {};

    /**
     * Add listener function that is called when the event is fired.
     *
     * @param {Function} listener Listener callback
     */
    pub.observe = function(listener) {
        this._listeners.push(listener);
    };

    /**
     * Fire an event. One can add arguments that are passed to the listeners.
     */
    pub.fire = function() {
        var args = arguments;
        this._listeners.forEach(function(listener) {
            listener.apply(null, args);
        });
    };

    pub.clearListeners = function() {
        this._listeners = [];
    };

    return function() {
        var obj = Object.create(pub);
        obj._listeners = [];
        return obj;
    };
})();
