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

        this.modal.on('hidden.bs.modal', function() {
            $(root).remove();
        });

        this.uiContentPaste.hide();
        this.modal.modal('show');
        this.uiLoader.hide();
    };

    cls._handleNewContainerClick = function(e) {
        e.preventDefault();
        e.stopPropagation();

        var level = e.target.getAttribute('data-level');
        this.selectedLevel = level;

        this.uiContentPaste.slideDown();
    };

    cls._handleContentSubmit = function(e) {
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

    cls.showNextContainer = function(id, level, totalWorth) {
        var newRow = $(this.rowBlueprint.cloneNode(true));
        newRow.removeClass('blueprint');
        newRow.find('img').attr('src', this.metadata.levels[level].image);
        newRow.find('strong').text(this.metadata.levels[level].label);
        newRow.find('.totalWorth').text(totalWorth);

        $(this.rowBlueprint).before(newRow);

        return LootContainerUI(id, newRow);
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

        obj._initUI($(root));

        return obj;
    }
})();

LootContainerUI = (function() {
    var cls = {};

    cls._initUI = function(root) {
        this.uiCloseButton = $(this.element).find('a');

        this.uiCloseButton.on('click', function(e) {
            e.preventDefault();

            this.onContainerDeleteRequest.fire(this.containerId);
        }.bind(this));

        $(this.uiCloseButton).tooltip();
    };

    cls.remove = function() {
        this.element.remove();
    };

    return function(containerId, root) {
        var obj = Object.create(cls);

        obj.element = root;
        obj.containerId = containerId;
        obj.onContainerDeleteRequest = Observable();

        obj.uiCloseButton = null;

        obj._initUI(root);

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

            var d = requestLootForSignature(signatureKey);

            d.done(function(data) {handleModalWindow(signatureKey, data)});
        });
    };

    var handleModalWindow = function(signatureKey, data) {
        var modal = ui.createModal(data.html, data.metadata);

        modal.onContainerSubmitted.observe(function(level, content) {
            modal.setProcessing(true);

            var d2 = requestContainerAdd(signatureKey, level, content);

            d2.done(function(containerData) {
                modal.setProcessing(false);
                modal.hidePasteArea();
                var container = modal.showNextContainer(containerData.id, level, containerData.totalWorth);

                container.onContainerDeleteRequest.observe(function(id) {
                    console.log('Container', id, 'is about to be deleted');

                    setTimeout(function() {container.remove()}, 1000);
                })
            })
        });
    };

    var requestLootForSignature = function(key) {
        return $.ajax('?call=getLoot&key='+key, {
            type: 'POST',
            processData: false
        });
    };

    var requestContainerAdd = function(key, level, content) {
        return $.ajax('?call=addContainer&key='+key+'&level='+level, {
            type: 'POST',
            processData: false,
            contentType: "text/plain; charset=utf-8",
            data: content
        });
    };

    return pub;
})();