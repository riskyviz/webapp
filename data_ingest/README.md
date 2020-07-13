# setup

Get MSOA names
wget https://visual.parliament.uk/msoanames/static/MSOA-Names-v1.1.0.csv

Get a useful file with up to date mapping from MSOA to LTLA
wget https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/868793/Domestic_electric_consumption_by_Middle_Layer_Super_Output_Area__MSOA___2010_to_2018.csv/preview

Get population estimates per MSOA
download data https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/middlesuperoutputareamidyearpopulationestimates
convert to CSV file "msoa_population.csv"

Get covid deaths per MSOA (up to May)
download data https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/deathsinvolvingcovid19bylocalareaanddeprivation
convert to CSV file "covid_deaths_msoa.csv"

Get GeoJSON file with MSOA boundaries
wget https://opendata.arcgis.com/datasets/826dc85fb600440889480f4d9dbb1a24_2.geojson

# data ingest

There are separate steps to download the latest cases data for England and Wales

England:
Download latest JSON cases from https://coronavirus.data.gov.uk/archive to coronavirus-cases-XXXX.json

Wales:
https://public.tableau.com/profile/public.health.wales.health.protection#!/vizhome/RapidCOVID-19virology-Public/Headlinesummary
Click on download data
Extract table "Tests by specimen date" to wales_cases.csv