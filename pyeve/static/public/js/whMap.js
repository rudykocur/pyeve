
jsPlumb.bind("ready", function() {
    console.log('OMG READY');

    var defaults = {
        Container: 'wormholeMap',
        Endpoint : ["Dot", {radius:2}],

        Anchor:[ "Perimeter", { shape:"Rectangle" } ],

        Connector:[ "Straight" ],
//        ConnectorStyle:{ strokeStyle:"#5c96bc", strokeWidth:1, outlineColor:"transparent", outlineWidth:0 },

        PaintStyle:{
    lineWidth:3,
    strokeStyle:"#4CBCDA"
//    outlineColor:"black",
//    outlineWidth:0
  }

//        ConnectorStyle:{ strokeStyle:"#5c96bc", lineWidth:2, outlineColor:"transparent", outlineWidth:4 }
    };

    var plumb = jsPlumb.getInstance(defaults);

    plumb.connect({
      source:"sig-J098654",
      target:"sig-J432567",

        overlays:[
            [ "Label", { label:"foo", location:15, cssClass: 'connectorLabel' } ],
            [ "Label", { label:"bar", location:-15, cssClass: 'connectorLabel' } ]
        ]
    });

    plumb.connect({
      source:"sig-J432567",
      target:"sig-J111112",

        overlays:[
            [ "Label", { label:"foo", location:15, cssClass: 'connectorLabel' } ],
            [ "Label", { label:"bar", location:-15, cssClass: 'connectorLabel' } ]
        ]
    });

    plumb.connect({
      source:"sig-J432567",
      target:"sig-J111115"
    });

});
