/**
 * Created by Rudy on 2014-09-06.
 */

BookmarkManager = (function() {
	var pub = {};

	var container = null;
    var currentSystem = null;
    var ajaxLoader = null;

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

    var submitSignatures = function(signatures) {
        ajaxLoader.css('display', 'inline');

        $.ajax('?call=saveSignatures', {
            type: 'POST',
            processData: false,
            contentType: "application/json; charset=utf-8",
            data: signatures,
            complete: function(req) {
                ajaxLoader.css('display', '');

                container.empty();
                container.append(req.responseJSON.html);
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
        ajaxLoader = $(params.ajaxLoader);

		params.processButton.addEventListener('click', function(e) {
			e.stopPropagation();
			e.preventDefault();

			var signatures = params.signaturesInput.value;
            params.signaturesInput.value = "";
            submitSignatures(signatures);
		});

        setInterval(checkSystem, 5000);
	};

	return pub;
})();