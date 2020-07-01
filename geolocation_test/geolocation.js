async function boot() {
    var geojson = await fetch("826dc85fb600440889480f4d9dbb1a24_2.geojson");
    var geodata = await geojson.json();


    if ("geolocation" in navigator) {
            var that =this;
            this.watchID = navigator.geolocation.watchPosition(function(position) {
                var lon = position.coords.longitude;
                var lat = position.coords.latitude;
                var point1 = turf.point([lon,lat], { });//x,y
                alert("lon="+lon+",lat="+lat);

                var features = geodata.features;

                for (var i = 0, len = features.length; i < len; i++) {
                    var isInside = turf.inside(point1,features[i]);
                    if(isInside) {
                        alert("Found enclosing!:"+JSON.stringify(features[i].properties));
                    }
                }
            },function(err) { alert(err); });
    } else {
        alert("no geolocation");
    }
}