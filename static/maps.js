const getLastMod = (dateString) => {
    const pad = num => String(num).padStart(2, '0');
    const date = new Date(Date.parse(dateString));
    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const hour = pad(date.getHours());
    const min = pad(date.getMinutes());
    const sec = pad(date.getSeconds());
    return `${year}/${month}/${day} ${hour}:${min}:${sec}`;
}

const revision = "1"
const map = L.map('map', {
//    preferCanvas: true,
	minZoom: 3,
    maxZoom: 19,
}).setView([36, 138], 6);

var gl = L.maplibreGL({
    style: "./static/styles.json", //https://tile.openstreetmap.jp/styles/openmaptiles/style.json",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors',
}).addTo(map);


const markers = L.markerClusterGroup();
const locationIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const chooseGame = async (gameName) => {
    markers.clearLayers();
    const response = await fetch(`./json/${gameName}.json?${revision}`);
    const lastModified = document.querySelector("#last-modified");
    lastModified.innerHTML = `Database: ${getLastMod(response.headers.get("Last-Modified"))}`;

    const stores = await response.json();
    stores.forEach(store => {
        const marker = L.marker(store.location, { icon: locationIcon });
        const markerContent = `
            <div class="notranslate store-info">
                <font size="4"><b>${store.name}</b></font>
                <br><br>
                <font size="2.5" style="line-break:anywhere;">${store.address}</font>
                <br><br>
                <ul>
                    <li><font size="3"><a target="_blank" href="https://www.google.com/maps/search/?api=1&query=${store.name}&zoom=16&hl=en">Google Maps</a></font></li>
                    ${store.country !== "JP" ? `<li><font size="3"><a target="_blank" href="https://google.com/search?q=${store.name}">Google Search</a></font></li>` : ''}
					${store.country === "JP" ? `<li><font size="3"><a target="_blank" href="https://map.yahoo.co.jp/search?q=${store.name}&lat=${store.location[0]}&lng=${store.location[1]}&zoom=16&hl=en">Yahoo Maps (日本語)</a></font></li>` : ''}
                </ul>
				${store.country !== "JP" ? '<br><font size="2.5" color="red">Stores outside Japan may be inaccurate.<br>Use this data at your own risk!<br></font>': ''}
            </div>
        `;
        marker.bindPopup(markerContent).openPopup();
        markers.addLayer(marker);
    });
    map.addLayer(markers);
};

document.addEventListener('DOMContentLoaded', () => chooseGame("duplicate"));
