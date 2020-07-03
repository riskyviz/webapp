$('.btn').on('click', function() {
    var x = document.getElementById("demo");
    var $this = $(this);
    var loadingText = '<i class="fa fa-circle-o-notch fa-spin"></i> Loading...';
    if ($(this).html() !== loadingText) {
        $this.data('original-text', $(this).html());
        $this.html(loadingText);
    }

});

async function boot() {
    var geojson = await fetch("Middle_Layer_Super_Output_Areas__December_2011__Boundaries.geojson");
    var geodata = await geojson.json();

    if ("geolocation" in navigator) {
        var that =this;

        this.watchID = navigator.geolocation.watchPosition(function(position) {
            var lon = position.coords.longitude;
            sessionStorage.setItem("longitude", lon);
            var lat = position.coords.latitude;
            sessionStorage.setItem("latitude", lat);
            var point1 = turf.point([lon,lat], { });//x,y



            var features = geodata.features;

            for (var i = 0, len = features.length; i < len; i++) {
                var isInside = turf.inside(point1,features[i]);
                if(isInside) {
                    var place = features[i].properties.msoa11nm;
                    place = place.replace(/[0-9]/g, '');
                    sessionStorage.setItem("location", place);
                    window.location.assign("local.html");
                }
            }
        },function(err) { alert(err); });
    } else {
        alert("no geolocation");
    }
}


