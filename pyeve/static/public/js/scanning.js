/**
 * Created by Rudy on 2014-09-06.
 */


DateFormatters = (function () {
	var pad = function(val) {
		if(val < 10) {
			return '0' + val;
		}

		return val;
	};

	var getDayPart = function(now) {
		return now.getFullYear() + "-" + pad(now.getMonth()) + "-" + pad(now.getDate()) + " ";
	};

	var getTimePart = function(now) {
		return pad(now.getHours()) + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds());
	};

	var getMiliPart = function(now) {
		return "." + now.getMilliseconds();
	};

	var pub = {};

	pub.withMilis = function() {
		var now = new Date();

		return getDayPart(now) + getTimePart(now) + getMiliPart(now);
	};

	pub.hoursWithMilis = function() {
		var now = new Date();

		return getTimePart(now) + getMiliPart(now);
	};

	pub.withSeconds = function() {
		var now = new Date();

		return getDayPart(now) + getTimePart(now);
	};

	return pub;
})();

_toArray = function(arr) {
	return Array.prototype.slice.call(arr);
};

BookmarkManager = (function() {
	var pub = {};

	var container = null;

	var knownSignatures = [];

    var currentSystem = null;

    var checkSystem = function() {
        $.ajax('?call=getSystem', {
            type: 'POST',
            processData: false,
            contentType: "application/json; charset=utf-8",
            complete: function(req) {

                if(req.responseJSON.systemName != currentSystem) {
                    window.location = window.location;
                }
            }
        });
    };

    var saveSignatures = function() {
        $.ajax('?call=saveSignatures', {
            type: 'POST',
            processData: false,
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(knownSignatures),
            complete: function(req) {

                container.empty();
                container.append(req.responseJSON.html);
            }
        });
    };

	var processSignatures = function(data) {
		var rows = data.split('\n');

		var processed = [];

		rows.forEach(function(row) {

			if(!row) {
				return;
			}

			var parts = row.split('\t');

			processed.push({
				updated: DateFormatters.withSeconds(),
				key: parts[0],
				group: parts[1],
				type: parts[2],
				name: parts[3],
				strength: parts[4]
			});

		});

		updateSignatures(processed);
	};

	var updateSignatures = function(newSignatures) {
		var keyCache = {};

        var oldSignatures = knownSignatures;
        knownSignatures = [];

        oldSignatures.forEach(function(row) {
			keyCache[row.key] = row;

			var strFloat = parseFloat(row.strength.substr(0, row.strength.length-1).replace(',', '.'));
			row.strengthFloat = strFloat;
		});

		newSignatures.forEach(function(row) {
			var strFloat = parseFloat(row.strength.substr(0, row.strength.length-1).replace(',', '.'));
			row.strengthFloat = strFloat;

            if(!keyCache[row.key]) {

                knownSignatures.push(row);
            }
            else {
                var old = keyCache[row.key];

                if(old.strengthFloat < row.strengthFloat) {

                    for(k in row) {
                        old[k] = row[k];
                    }
                }

                // always update group type and name
                old.group = row.group || old.group;
                old.type = row.type || old.type;
                old.name = row.name || old.name;

                knownSignatures.push(old);
            }

		});

	};

    /**
     *
     * @param {Object} params
     */
	pub.init = function(params) {
		container = $(params.container);
        currentSystem = params.systemName;
        knownSignatures = params.savedSignatures;

		params.processButton.addEventListener('click', function(e) {
			e.stopPropagation();
			e.preventDefault();

			processSignatures(params.signaturesInput.value);
            params.signaturesInput.value = "";
            saveSignatures();
		});

        setInterval(checkSystem, 5000);
	};

	pub.showSignatures = function(signatures) {
		updateSignatures(signatures);
	};

	return pub;
})();