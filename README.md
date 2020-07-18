# riskCovid - team VISIGOTH

This repo explores a way to present information to the public on the risk of contracting cvoid-19 as part of the 
4th NERC COVID-19 Digital Sprint Hackathon "Visualising risk"

https://digitalenvironment.org/home/covid-19-digital-sprint-hackathons/

https://digitalenvironment.org/home/covid-19-digital-sprint-hackathons/covid-19-hackathon-4-visualising-risk/

## Aims and Methodology

We decided to provide a map based approach, deilvering localised risk information via a web application that is 
designed to work well on a smartphone or a device with a larger screen. 

[Click here for a summary of the app](COVIDRiskFinder.pdf)

[Click here to launch the App](https://riskyviz.github.io/webapp/riskCOVID/)

We decided to define risk as simply the risk of an individual contracting the virus.  

We did not consider the risks of severe illness or mortality which are known to vary by demographic factors 
(for example age).  Although useful, this personalised definition of risk does not consider the 
risk of spreading the virus through the community.

The main design decisions for the user experience were:

* Provide a simple explaination of risk in terms of low/medium/high and traffic light colours
* Provide simple and clear advice dependent upon the estimated risk
* Link to official information on COVID-19
* Provide a way to drill down to information on the current trends in each local area
* Cover England and Wales 
* Provide risk estimates at as local a level as possible 

The implementation requirements were:

* Use a simple explainable method for calculating risk estimates
* Use information that is currently available to the public through official and verifiable sources
* Make the updating of risk information easy and practical to perform on a daily basis (within 10 minutes)

## Methodology

We define risk of contracting covid as either HIGH, MEDIUM or LOW, according to an estmate of the current daily positive test rate per 100K poplation.

According to [this article](https://www.americanprogress.org/issues/healthcare/news/2020/05/04/484373/evidence-based-thresholds-states-must-meet-control-coronavirus-spread-safely-reopen-economies/) the US Center for Disease Control (CDC) identifies:

* low-medium threshold as 10 positive cases per 100K people per 14 days (0.71 daily positive rate)
* medium-high threshold as 50 positive cases per 100K people per 14 days (3.51 daily positive rate)

Our estimates of daily positive test rates are based on the data released daily by [the UK government](https://coronavirus.data.gov.uk/archive) and [the Welsh government](https://public.tableau.com/profile/public.health.wales.health.protection#!/vizhome/RapidCOVID-19virology-Public/Headlinesummary)
This data provides the number of daily positive (lab confirmed) cases in each Lower Tier Local Authority (LTLA).   

We perform the following post processing steps on the data:

(1) Distribute the positive test cases from an LTLA unevenly amongst the middle super output areas (MSOAs) that make up each LTLA.  A MSOA is an ideal unit of geography for providing local advice.  Each MSOA comprises [on average 7200 people](https://en.wikipedia.org/wiki/Middle_Layer_Super_Output_Area).

It is unlikely that the virus spreads evenly through each MSOA within an LTLA.  The algorithm for distributing test cases considers the distribution of deaths recorded by the ONS in each MSOA from COVID-19 in the 3 month period (March 2020 to May 2020)
as being a useful model for how recent cases will be distributed across an LTLA.  This approach has obvious weaknesses due to the fact that the mortality rate is known to vary widely within local areas, and of course, the way in which the virus spreads will change over time.  It would have been ideal to have available information on COVID-19 infections at the MSOA level, but the UK and Welsh governments do not yet release this data.

(2) Compute a linear weighted average of the estimated daily positive count for each MSOA over the previous 14 days

Whilst providing higher weights to recent case statistics (for example if a spike is developing quickly), this approach smooths out fluctuations due to weekend reporting.

Basing risk on the number of positive cases (lab confirmed tests) introduces an unfortunate bias towards indicating higher risks simply because more tests are being performed within a LTLA.   If data was made available for the number of tests carried out per day as well as the number of positive tests, we could attempt to correct for this bias.

## Repo Structure

The repo is divided into three sections

data_ingest folder - see the [README](data_ingest/README.md) - combine data to be used by the web app (Python)
riskCOVID - see the [README](riskCOVID/README.md) - source code for the web app (HTML/JavaScript/CSS)
population_density - see the [README](population_density/README.md) - exploring population density in the bedford area

## WebApp Visualisations

We introduce a number of visualisations:

* Zoomable "slippy" map overlaying semi-transparent areas coloured by risk (green,amber,red) on openstreetmap
* Traffic light graphic and icons for 
* Risk stripes - borrowing heavily from [Climate/Warming Stripes](https://showyourstripes.info/).
  These subdivide the traffic light colours into hues to show how the risk has altered over the previous 30 days.
* Plot of estimated case rate over previous 30 days.

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
