function boot() {
    window.location.assign("local.html");
    var geojson = fetch("Middle_Layer_Super_Output_Areas__December_2011__Boundaries.geojson");
    var geodata = geojson.json();


    if ("geolocation" in navigator) {
        var that =this;

        this.watchID = navigator.geolocation.watchPosition(function(position) {
            var lon = position.coords.longitude;
            var lat = position.coords.latitude;
            var point1 = turf.point([lon,lat], { });//x,y



            var features = geodata.features;

            for (var i = 0, len = features.length; i < len; i++) {
                var isInside = turf.inside(point1,features[i]);
                if(isInside) {
                    alert("Found enclosing!:"+features[i].properties.msoa11nm);
                    var positionInfo = "Found enclosing!:"+JSON.stringify(features[i].properties);
                    sessionStorage.setItem("location", positionInfo);
                    window.location.assign("local.html");
                }
            }
        },function(err) { alert(err); });
    } else {
        alert("no geolocation");
    }
}