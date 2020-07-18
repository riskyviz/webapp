# Data Ingest

Mash up COVID-19, ONS, GIS datasets to produce `new.geojson` that scores each MSOA with an estimate of the daily rate of new Covid19 cases per 100K population

Several steps involve converting Excel tables within spreadsheets to CSV files - LibreOffice can be used if excel is not available.

# One time setup

These steps need to be performed once, they do not need to be re-run on a daily basis.

(0) Install visigoth 

The visigoth library is used to reduce the size of the output geojson file

`pip install visigoth`

Download the following data files into the `data_ingest` folder

(1) Get MSOA names

```
wget https://visual.parliament.uk/msoanames/static/MSOA-Names-v1.1.0.csv
```

(2) Get a useful file with up to date mapping from MSOA to LTLA

```
wget https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/868793/Domestic_electric_consumption_by_Middle_Layer_Super_Output_Area__MSOA___2010_to_2018.csv/preview
```

(3) Get population estimates per MSOA

download data `https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/middlesuperoutputareamidyearpopulationestimates`
convert to CSV file "msoa_population.csv"

(4) Get covid deaths per MSOA (up to May)

download data `https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/deathsinvolvingcovid19bylocalareaanddeprivation`
convert to CSV file "covid_deaths_msoa.csv"

(5) Get GeoJSON file with MSOA boundaries

```
wget https://opendata.arcgis.com/datasets/826dc85fb600440889480f4d9dbb1a24_2.geojson
```

## Daily Step

There are separate steps to download the latest cases data for England and Wales

(1) England

Download latest JSON cases fle from https://coronavirus.data.gov.uk/archive and rename to coronavirus-cases.json

(2) Wales

https://public.tableau.com/profile/public.health.wales.health.protection#!/vizhome/RapidCOVID-19virology-Public/Headlinesummary
Click on download data
Extract table "Tests by specimen date" to wales_cases.csv

(3) Run `python3 ingest.py`

This should produce the `new.geojson` file with the following properties for each MSOA:

* msoa11cd: MSOA code
* long_name: A human readable name for the MSOA
* score: An estimate for the latest case rate per 100K population per day in this MSOA
* LatestDate: the date for which the score is made
* history_date_desc: A list of case rate estimates for previous days, sorted in reverse chronological order

Sample output looks like:

```
Reading case data - England
reading msoa->district mapping
Reading case data - Wales
reading MSOA long names
reading MSOA population data
reading deaths data
calculating msoa weightings
creating intermediate output geojson
msoas written=7201 errors=5 max msoa score=32.107793 missing longnames=0
failed to compute scores for:
	E02000001
	E02006781
optimisng geojson file to reduce file size
writing out summary CSV with latest scores per MSOA, descending order
Summary
	;-) Low Risk 5999 (83.31 percent)
	;-| Moderate Risk 1144 (15.89 percent)
	;-( High Risk 58 (0.81 percent)
```