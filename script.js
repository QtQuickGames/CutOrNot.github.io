
async function collectPinData(fileName)
{
let data = await fetch(fileName);
data = await data.text();
data = JSON.parse(data);
let output = [];
data.features.forEach(element => {
  output.push(element);
});
return output;
}

async function collectAreaData(fileName)
{
let data = await fetch(fileName);
data = await data.text();
data = JSON.parse(data);
let output = [];
output[0] = [];
data.features.forEach(element => {
element.geometry.coordinates[0].forEach(coord=>{
    output[0].push(coord.reverse());
})
  })
return output;
}

async function main()
{

//customowa pinezka
var treeIcon = L.icon({
    iconUrl: 'images/drzewko.png',
    iconSize:[40, 40]
});


var map = L.map('map').setView([52.245, 21.285], 15);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


/*
//pobieranie koordynatów z GeoJson
let data = await collectPinData('geojson/pins.geojson');
console.log(data);
data.forEach(element=>{
var marker = L.marker(element,{icon:treeIcon}).addTo(map);
marker.bindTooltip(`element coordinates: ${element[0].toFixed(2)} , ${element[1].toFixed(2)}`);
});


data = await collectAreaData('geojson/polygon.geojson');
data.forEach(element=>{
var eastPoland = L.polygon(element, {color: 'green'}).addTo(map);
});


data = await collectAreaData('geojson/drzewa4p.geojson');
data.forEach(element=>{
var lodz = L.polygon(element, {color: 'green'}).addTo(map);
});
*/

//cluster na mapę

var markers = new L.MarkerClusterGroup({});
data = await collectPinData('geojson/drzewa4p.geojson');
let iterator = 1;
data.forEach(element=>{
  let dat = L.marker([element.geometry.coordinates[1],element.geometry.coordinates[0]], {icon:treeIcon});
dat.bindTooltip(`<b>id</b>: ${iterator} <br> <b>koordynaty</b>: ${element.geometry.coordinates[1].toFixed(2)}, ${element.geometry.coordinates[0].toFixed(2)}`);
iterator++;
  markers.addLayer(dat);
});
map.addLayer(markers);

}

main();