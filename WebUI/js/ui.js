$(function() {

    //Set test of nlp_unput if an example is clicked
    $(".example").click(function(e){
        $("#nlp_input").val($(this).text());
    });


    var map = new ol.Map({
        target: 'openlayers-map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM({
                    attributions: [
                        new ol.Attribution({
                            html: 'All maps &copy; ' +
                            '<a href="http://www.openstreetmap.org/">OpenstreetMap</a>'
                        }),
                        ol.source.OSM.ATTRIBUTION
                    ],
                })
            })
            // new ol.layer.Vector({
            //     source: featureSource
            // })
        ],
        view: new ol.View({
                center: ol.proj.fromLonLat([ 5.399167, 52.150836]),
                zoom: 6
            })

        });

    //proj4.defs('EPSG:3857', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs');
    // proj4.defs('EPSG:3857', '+proj=merc +ellps=WGS84 +datum=WGS84 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs');
    $("#parse").click( function() {
        $("#parse").prop("disabled",true);
        loc = map.getView().getCenter().map(String);
        loc.push("3857");
        data = {
            'sentence': $('#nlp_input').val(),
            'location': loc
        }

        data = JSON.stringify(data)

        $.ajax({
            type:"POST",
            url:"http://192.168.24.148:8085/parse_and_run_query",
            data: data,
            contentType: "application/json",

            success: function (result) {
                console.log(result)
                if (result["type"] == "error") {
                    $("#parse").prop("disabled",false);
                    window.alert(result["error_message"])
                    return
                }
                geojson = JSON.parse(result["result"])

                var features = new ol.format.GeoJSON().readFeatures(geojson);
                var vectorSource = new ol.source.Vector({
                  features: features
                });
                var vectorLayer = new ol.layer.Vector({
                    source: vectorSource
                });
                map.addLayer(vectorLayer)

                $("#parse").prop("disabled",false);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                window.alert(errorThrown)
                $("#parse").prop("disabled",false);
            }
        });
       }
    );


});
