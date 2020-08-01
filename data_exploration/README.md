# CovidRiskFinder - Data Exploration

As part of the project, the team explored a number of data sources before selecting the data used to caclulate the risk estimates.

## Bedford and the surrounding area

Bedford is a small town with a population esimated at 106,940 in the 2011 census [wikipedia page](https://en.wikipedia.org/wiki/Bedford)

Bedford is surrounded by farmland and villages of varying sizes.

## Population Density

As part of the project we hoped to provide a "hyper local" assessment of risk based partly on population
denisty estimates.  A suitable 1km resolution dataset was available from the NERC Centre for Ecology & Hydrology:

Reis, S.; Liska, T.; Steinle, S.; Carnell, E.; Leaver, D.; Roberts, E.; Vieno, M.; Beck, R.; Dragosits, U. (2017). <b>UK gridded population 2011 based on Census 2011 and Land Cover Map 2015</b> NERC Environmental Information Data Centre. https://doi.org/10.5285/0995e94d-6d42-40c1-8ed4-5090d82471e1
          
The data was downloaded from https://catalogue.ceh.ac.uk/documents/0995e94d-6d42-40c1-8ed4-5090d82471e1

The data was then converted from raster to .geojson files (polygonized) using qgis and displayed on interactive maps for the Bedford area using [visigoth](https://visigoth.org)

![Plot of Population Density in the Bedford area](https://github.com/riskyviz/webapp/raw/master//data_exploration/bedford_residential_population_density.png)

[source code](https://github.com/riskyviz/webapp/blob/master/data_exploration/bedford_residential_population_density.py)

[Right click to download interactive HTML](https://github.com/riskyviz/webapp/raw/master/data_exploration/bedford_residential_population_density.html)

After some consideration we decided not to incorporate this data into the estimates of covid risk.  Our reasoning was that 
the statistical population density does not reflect the actual population density as experienced by people - or to put it 
another way - people tend to concentrate in small areas.

## Covid Deaths - Distribution By MSOA

For each Local Authority area, we plotted the distribution of population and Covid-19 deaths over the MSOAs, using data 
provided by the ONS.

From these plots we can see that deaths are not distributed in line with population.  However, we note that the numbers 
of deaths in many areas are low, and some of the variation can be explained by chance.  In the available time it was not 
possible to better model these effects but we decided to use a laplace correction (basically, add 4 deaths to each MSOA) 
when deciding how to distribute the risk of contracting Covid-19 in each area based on these statistics.

![Variation of population and COVID-19 deaths in Bedfordshire](https://github.com/riskyviz/webapp/raw/master/data_exploration/covid_deaths.png)

[source code](https://github.com/riskyviz/webapp/blob/master/data_exploration/covid_deaths.py)

[Right click to download interactive HTML](https://github.com/riskyviz/webapp/raw/master/data_exploration/covid_deaths.html)


## Plotting risk on a national map for England and Wales

To debug our methods, it was helpful to regularly plot the `new.geojson` file output from our [data ingest process](../data_ingest/README.md)
onto a zoomable chloropleth map covering England and Wales.

![Plot of Covid Risk in England and Wales](https://github.com/riskyviz/webapp/raw/master/data_exploration/england_wales_risk.png)

[source code](https://github.com/riskyviz/webapp/blob/master/data_exploration/england_wales_risk.py)

[Right click to download interactive HTML (Caution, 45Mb HTML file)](https://github.com/riskyviz/webapp/raw/master/data_exploration/england_wales_risk.html)

At a national or regional level, chloropleth maps are not a good representation as small areas are almost invisible and large areas dominate.

We can instead use the [population weighted centroids of each MSOA](http://geoportal.statistics.gov.uk/datasets/b0a6d8a3dc5d4718b3fd62c548d60f81_0):

```
wget https://opendata.arcgis.com/datasets/b0a6d8a3dc5d4718b3fd62c548d60f81_0.geojson
```
We generated plots of the risk scores using alternative methods to uncover the national distribution of Covid-19 risk:

![More Plots of Covid Risk in England and Wales](https://github.com/riskyviz/webapp/raw/master/data_exploration/england_wales_risk_plots.png)

[source code](https://github.com/riskyviz/webapp/blob/master/data_exploration/england_wales_risk_plots.py)

[Right click to download interactive HTML](https://github.com/riskyviz/webapp/raw/master/data_exploration/england_wales_risk_plots.html)

For the above plot you will need to collect a geoJSON file with the England and Wales outline from:

```
wget https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/eurostat/ew/nuts1.json
```

Although we think these alternatives, in particular heatmaps, do provide a better intuitive distribution of risk at the national level,
a choloropleth map probably makes more sense at the local level, because it is easier to understand and simple to draw.

## Covid Risk - local plot for Bedford

We plotted the estimate of covid risk produced by our method for Bedford and the surrounding area

![Plot of Covid Risk in the Bedford Area](https://github.com/riskyviz/webapp/raw/master/data_exploration/bedford_risk.png)

[source code](https://github.com/riskyviz/webapp/blob/master/data_exploration/bedford_risk.py)

[Right click to download interactive HTML](https://github.com/riskyviz/webapp/raw/master/data_exploration/bedford_risk.html)

