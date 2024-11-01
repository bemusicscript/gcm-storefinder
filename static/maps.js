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
const map = L.map('map', {preferCanvas: true}).setView([36, 138], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
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
                <font size="3" style="line-break:anywhere;">${store.address}</font>
                <br><br>
                <ul>
                    <li>
                        <font size="3"><a target="_blank" href="https://maps.google.com/maps?q=${store.name}@${store.location.join(",")}&zoom=16&hl=en">Google Maps</a></font>
                    </li>
                    <li>
                        <font size="3"><a target="_blank" href="https://map.yahoo.co.jp/search?q=${store.name}&lat=${store.location[0]}&lng=${store.location[1]}&zoom=16&hl=en">Yahoo Maps (JP)</a></font>
                    </li>
                </ul>
            </div>
        `;
        marker.bindPopup(markerContent).openPopup();
        markers.addLayer(marker);
    });
    map.addLayer(markers);
};

document.addEventListener('DOMContentLoaded', () => chooseGame("duplicate"));