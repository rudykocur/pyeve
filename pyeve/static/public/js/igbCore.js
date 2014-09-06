/**
 * Created by Rudy on 2014-09-05.
 */

var IGBManager = (function() {
    var pub = {};

    pub.requestTrust = function() {
        CCPEVE.requestTrust('http://localhost:5000/');
        $('#untrusted').remove();

        return false;
    };

    pub.reload = function() {
        window.location = window.location;
        return false;
    };

    return pub;
})();
