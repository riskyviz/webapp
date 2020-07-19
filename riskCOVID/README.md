# CovidRiskFinder Prototype Web App

This prototype web app presents estimates of local risk of contracting Covid-19.

## Open hosted version

The web app is hosted by github [click here to open](https://riskyviz.github.io/webapp/riskCOVID/)

## Running Locally

To serve the app locally, clone this repo and then:

```
cd webapp/riskCOVID
python3 -m http.server
```

Open the app in a we browser by navigating to localhost:8000

## Using the app

On first opening the app you will be presented with a start screen allowing you to 
* either use your device's location (press the `Set Location` button) or 
* to search for a UK location or postcode - enter this in the search box

Note - after clicking on `Set Location` your device may check that you consent to sharing
your location data.  Be assured that your location data will not be passed to the 
server.  No data is stored or tracked on the server.

After providing your device location or a search location, the main screen should 
open.  This displays a map at the top of the screen, centered on this location.  After a few seconds, 
the map will colour areas as green, amber or red, depending upon the risk estimate in each area.

## Visualisations

We introduce a number of visualisations:

* Zoomable "slippy" map overlaying semi-transparent areas coloured by risk (green,amber,red) on openstreetmap
* Traffic light graphic and icons for 
* Risk stripes - borrowing heavily from [Climate/Warming Stripes](https://showyourstripes.info/).
  These subdivide the traffic light colours into hues to show how the risk has altered over the previous 30 days.
* Plot of estimated case rate over previous 30 days.

## Limitations and future work

As discussed in [the main README](../README.md) the estimates could be improved by having 
more detailed data made available, in particular:

* daily test statistics at the MSOA level
* inclusion of the positive test rate into the statistics 
 
This app is a prototype and could be improved in many ways:

* user experience improvements (after feedback from real users)
* minimisation of data load size (a single geojson file that is approximately 5Mb compressed is loaded for England and Wales)

## Acknowledgements

Our prototype relies upon a number of open source libraries and open data services:

[LeafetJS](https://leafletjs.com/)
[Turfjs](https://turfjs.org/)
[JQuery](https://jquery.com/)
[Bootstrap](https://getbootstrap.com/)
[Font-Awesome](https://github.com/FortAwesome/Font-Awesome)
[Mapbox](https://www.mapbox.com/)
[Popper](https://popper.js.org/)
[OpenStreetMap](https://www.openstreetmap.org/)
[ChartJS](https://www.chartjs.org/)