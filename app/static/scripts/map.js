
function createLeafletMap(){
    let map;

    // Create map with custom settings
    map = L.map('map', {
        zoom: 13,
        zoomControl: false
    });

    // OpenStreetMap tiles: no access token needed
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    getCityLatLng(state, city)
        .then(data => {
            if(data[0] && data[0].lat && data[0].lon) {
                let latLng = [data[0].lat, data[0].lon];
                map.panTo(latLng);
                let popup = L.popup({
                    closeOnClick: false,
                    autoClose: false,
                    closeButton: false,
                    keepInView: true
                }).setContent(city + ', ' + state);
                L.marker(latLng).bindPopup(popup).addTo(map).openPopup();
            } else {
                $('#map').hide()
            }
        });
}

function getCityLatLng(state, city){
    let country = 'United States';
    let apiUrl = 'https://nominatim.openstreetmap.org/search?format=json&country='+country+'&state='+state+'&city='+city;
    return $.getJSON(apiUrl);
}

function findDistance(){
    // source https://stackoverflow.com/questions/8658730/what-is-the-conversion-of-latitude-longitude-to-a-1-mile
    let myLatLng, otherLatLng;
    let p1 = getCityLatLng(myState, myCity)
        .then(data => {
            myLatLng = new google.maps.LatLng(data[0].lat, data[0].lon);
        });
    let p2 = getCityLatLng(otherState, otherCity)
        .then(data => {
            otherLatLng = new google.maps.LatLng(data[0].lat, data[0].lon);
        });
    Promise.all([p1, p2])
        .then(() => {
            let distance = google.maps.geometry.spherical.computeDistanceBetween(myLatLng,otherLatLng);
            let miles = parseInt(distance * 0.000621371);
            if(miles) {
                let text = miles + ' miles away';
                $('#miles-away').text(text)
            }
        });
}