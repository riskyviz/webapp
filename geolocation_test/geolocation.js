async function boot() {
    var geojson = await fetch("826dc85fb600440889480f4d9dbb1a24_2.geojson");
    var geodata = await geojson.json();

    function locate(lon,lat) {
        var point1 = turf.point([lon,lat], { });//x,y
        var features = geodata.features;

        for (var i = 0, len = features.length; i < len; i++) {
            var isInside = turf.inside(point1,features[i]);
            if(isInside) {
                alert("Found enclosing!:"+JSON.stringify(features[i].properties));
            }
        }
    }

    async function location_by_postcode(postcode) {
        var pg = postcode.slice(0,2);
        var r = await fetch("postcode_lookup/"+pg+".json");
        var postcodes = await r.json();
        if (postcode in postcodes) {
            var lon = postcodes[postcode].lon;
            var lat = postcodes[postcode].lat;
            locate(lon, lat);
        }
    }

    var location_input = document.getElementById("location_input");
    var location_go = document.getElementById("location_go");

    location_go.onclick = function() {
        var postcode = location_input.value;
        location_by_postcode(postcode);
    }

    if ("geolocation" in navigator) {
            var that =this;
            this.watchID = navigator.geolocation.watchPosition(function(position) {
                var lon = position.coords.longitude;
                var lat = position.coords.latitude;
                alert(locate(lon,lat));
            },function(err) { alert(err); });
    } else {
        alert("no geolocation");
    }
}