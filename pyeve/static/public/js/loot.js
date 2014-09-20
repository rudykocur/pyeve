/**
 * Created by Rudy on 2014-09-16.
 */

LootUI = (function() {
    var pub = {};

    pub._initUI = function() {
        this.modalRequested = Observable();

        $('.lootModalToggle').on('click', function(e) {
            e.preventDefault();

            this.modalRequested.fire(e.target.getAttribute('data-key'));
        }.bind(this));
    };

    pub.createModal = function(modalHtml, metadata) {
        return LootModalUI(modalHtml, metadata);
    };



    return function() {
        var obj = Object.create(pub);

        obj._initUI();

        return obj;
    }
})();

LootModalUI = (function() {
    var cls = {};

    cls._initUI = function(root) {

        this.modal = root.modal({show: false});
        this.uiContentPaste = $(this.modal).find('#contentPaste');
        this.uiContentPasteSubmit = $(this.modal).find('#contentPaste button');
        this.uiLoader = $(this.modal).find('.ajaxLoader');
        this.rowBlueprint = $(this.modal).find('.container-list .blueprint')[0];

        $(this.modal).find('.buttons button').on('click', this._handleNewContainerClick.bind(this));
        this.uiContentPasteSubmit.on('click', this._handleContentSubmit.bind(this));

        this.uiContentPaste.hide();
        this.modal.modal('show');
        this.uiLoader.hide();
    };

    cls._handleNewContainerClick = function(e) {
        e.preventDefault();
        e.stopPropagation();

        var level = e.target.getAttribute('data-level');

        console.log('clicked', e.target, '::', level);

        this.selectedLevel = level;

        this.uiContentPaste.slideDown();
    };

    cls._handleContentSubmit = function(e) {
        console.log('OMG OMG CLICK', e);

        this.onContainerSubmitted.fire(this.selectedLevel, this.uiContentPaste.find('textarea').val());
    };

    cls.hidePasteArea = function() {
        this.uiContentPaste.slideUp();
        this.uiContentPaste.find('textarea').val('');
    };

    cls.setProcessing = function(isProcessing) {
        if(isProcessing) {
            this.uiLoader.show();
        }
        else{
            this.uiLoader.hide();
        }
    };

    cls.showNextContainer = function(level, totalWorth) {
        var newRow = $(this.rowBlueprint.cloneNode(true));
        newRow.removeClass('blueprint');
        newRow.find('img').attr('src', this.metadata.levels[level].image);
        newRow.find('strong').text(this.metadata.levels[level].label);
        newRow.find('.totalWorth').text(totalWorth);

        $(this.rowBlueprint).before(newRow);
    };

    return function(root, metadata) {
        var obj = Object.create(cls);

        obj.selectedLevel = null;
        obj.modal = null;
        obj.uiContentPaste = null;
        obj.uiContentPasteSubmit = null;
        obj.uiLoader = null;
        obj.rowBlueprint = null;
        obj.metadata = metadata;

        obj.onContainerSubmitted = Observable();

        $(document.body).append(root);

        obj._initUI($(root));

        return obj;
    }
})();

LootInterface = (function() {
    var pub = {};

    var ui = null;

    pub.init = function() {
        ui = LootUI();

        ui.modalRequested.observe(function(signatureKey) {
            console.log('Requested modal for sig', signatureKey);

            loadLootForSignature(signatureKey);

        });

    };

    var loadLootForSignature = function(key) {
        $.ajax('?call=getLoot&key='+key, {
            type: 'POST',
            processData: false,
            //contentType: "application/json; charset=utf-8",
            //data: signatures,
            complete: function(req) {
                console.log('GOT RESPONSE', req);

                var data = req.responseJSON;

                var modal = ui.createModal(data.html, data.metadata);

                modal.onContainerSubmitted.observe(function(level, content) {
                    console.log('New content, level', level, ' with ', content);

                    modal.setProcessing(true);

                    $.ajax('?call=addContainer&key='+key+'&level='+level, {
                        type: 'POST',
                        processData: false,
                        //contentType: "application/json; charset=utf-8",
                        data: content,
                        complete: function (req) {
                            console.log('Container added!!');

                            modal.setProcessing(false);
                            modal.hidePasteArea();
                            modal.showNextContainer(level, req.responseJSON.totalWorth)
                        }
                    });

                });
            }
        });
    };

    return pub;
})();