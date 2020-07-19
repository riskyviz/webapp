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

The data was converted to .geojson files (polygonized) using qgis and displayed on interactive maps for the Bedford area using visigoth.

![Plot of Population Density in the Bedford area](https://riskyviz.github.io/webapp/data_exploration/bedford_residential_population_density.png)

[source code](bedford_residential_population_density.py)

[Interactive version](https://riskyviz.github.io/webapp/data_exploration/edford_residential_population_density.html)

After some consideration we decided not to incorporate this data into the estimates of covid risk.  Our reasoning was that 
the statistical population density does not reflect the actual population density as experienced by people - or to put it 
another way - people tend to concentrate in small areas.

## Covid Risk

We plotted the estimate of covid risk produced by our method for Bedford and the surrounding area

![Plot of Covid Risk in the Bedford Area](https://riskyviz.github.io/webapp/data_exploration/bedford_risk.png)

[source code](risk_bedford.py)

[Interactive version](https://riskyviz.github.io/webapp/data_exploration/bedford_risk.html)

# Covid Risk Estimates at the National Level

To debug our methods, it was helpful to regularly plot the `new.geojson` file output from our [data ingest process](../data_ingest/README.md)
onto a zoomable map covering England and Wales.

![Plot of Covid Risk in England and Wales](https://riskyviz.github.io/webapp/data_exploration/england_wales_risk.png)

[source code](risk_bedford.py)

[Interactive version (Caution, 45Mb HTML file)](https://riskyviz.github.io/webapp/data_exploration/england_wales_risk.html)
