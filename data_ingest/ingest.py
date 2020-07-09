
# wget "https://c19downloads.azureedge.net/downloads/json/dated/coronavirus-cases_202007031451.json"
# OLD wget wget https://opendata.arcgis.com/datasets/fe6c55f0924b4734adf1cf7104a0173e_0.csv
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/868793/Domestic_electric_consumption_by_Middle_Layer_Super_Output_Area__MSOA___2010_to_2018.csv/preview

# https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/deathsinvolvingcovid19bylocalareaanddeprivation

import json
import csv
import os
import datetime

CASE_WINDOW_DAYS = 14

print("Reading case data")

cases_data_by_date = {}

dates = set()
for file in os.listdir():
    if file.startswith("coronavirus-cases") and file.endswith(".json"):
        json_content = json.loads(open(file).read())
        for ltla in json_content["ltlas"]:
            dt = datetime.datetime.strptime(ltla["specimenDate"],"%Y-%m-%d")
            dates.add(dt)

recent_dates = sorted(list(dates),reverse=True)[:30]
print(recent_dates)

for rdt in recent_dates:
    cases_data_by_date[rdt] = {}
    for file in os.listdir():
        if file.startswith("coronavirus-cases") and file.endswith(".json"):
            json_content = json.loads(open(file).read())
            for ltla in json_content["ltlas"]:
                ac = ltla["areaCode"]
                an = ltla["areaName"]
                dt = datetime.datetime.strptime(ltla["specimenDate"],"%Y-%m-%d")
                day_in_window = (rdt-dt).days
                if day_in_window >= 0 and day_in_window < CASE_WINDOW_DAYS:
                    daily = ltla["dailyLabConfirmedCases"]
                    if not daily:
                        daily = 0
                    else:
                        daily = int(daily)
                    cases = cases_data_by_date[rdt].get(ac,0)
                    cases_data_by_date[rdt][ac] = daily+cases

print("reading msoa->district mapping")

mapping_msoa_to_district = {}
mapping_district_to_msoas = {}

f = open("Domestic_electric_consumption_by_Middle_Layer_Super_Output_Area__MSOA___2010_to_2018.csv")
# f = open("fe6c55f0924b4734adf1cf7104a0173e_0.csv")
reader = csv.reader(f)
mapping_columns = {}
for line in reader:
    if not mapping_columns:
        for idx in range(len(line)):
            mapping_columns[line[idx]] = idx
    else:
        # msoa_code = line[mapping_columns["MSOA11CD"]]
        msoa_code = line[mapping_columns["MSOACode"]]
        # district_code = line[mapping_columns["LAD17CD"]]
        district_code = line[mapping_columns["LACode"]]

        mapping_msoa_to_district[msoa_code] = district_code
        if district_code not in mapping_district_to_msoas:
            mapping_district_to_msoas[district_code] = []
        mapping_district_to_msoas[district_code].append(msoa_code)

print("reading deaths data")
deaths_by_msoa = {}
deaths_by_district = {}
f = open("covid_deaths_msoa.csv")
reader = csv.reader(f)
mapping_columns = {}
for line in reader:
    if not mapping_columns:
        for idx in range(len(line)):
            mapping_columns[line[idx]] = idx
    else:
        msoa_code = line[mapping_columns["MSOA code"]]
        deaths = int(line[mapping_columns["Covid Deaths 3 month - March to May"]])
        deaths_by_msoa[msoa_code] = deaths
        district = mapping_msoa_to_district.get(msoa_code,None)
        if district:
            district_deaths = deaths_by_district.get(district,0)
            district_deaths += deaths
            deaths_by_district[district] = district_deaths

print("calculating msoa weightings")

msoa_weighting = {}
for msoa_code in deaths_by_msoa:
    district = mapping_msoa_to_district.get(msoa_code, None)
    msoa_deaths = deaths_by_msoa[msoa_code]
    if district:
        district_deaths = deaths_by_district[district]
        weighting = (1+msoa_deaths) / (1+district_deaths)
        msoa_weighting[msoa_code] = weighting
        # print(msoa_deaths,district_deaths,weighting)

print("writing per-msoa scores to scores.json")
msoas = json.loads(open("/home/dev/github/webapp/riskCOVID/Middle_Layer_Super_Output_Areas__December_2011__Boundaries.geojson").read())

scores = []

count = 0
errors = 1
max_score = None
latest_dt = recent_dates[0]
missing_msoas = []

for feature in msoas["features"]:
    msoa_code = feature["properties"]["msoa11cd"]
    if msoa_code[:1] == "W":
        continue
    count += 1
    item = {"Area Codes":msoa_code}
    history = []
    # print("processing "+msoa_code)
    for dt in recent_dates:
        dt_str = dt.strftime("%Y-%m-%d")
        if dt == latest_dt:
            item["LatestDate"] = dt_str
        if msoa_code in mapping_msoa_to_district:
            district = mapping_msoa_to_district[msoa_code]
            if district not in cases_data_by_date[dt]:
                if dt == latest_dt:
                    item["Score"] = -1
                    errors += 1
                    missing_msoas.append(msoa_code+":"+district)
                else:
                    history.append(-1)
            else:
                score = msoa_weighting[msoa_code]*cases_data_by_date[dt][district]
                if dt == latest_dt:
                    item["Score"] = score
                else:
                    history.append(score)
                if max_score is None or score > max_score:
                    max_score = score
        else:
            if dt == latest_dt:
                errors += 1
                item["Score"] = -1
            else:
                history.append(-1)

    item["history_date_desc"] = history
    scores.append(item)

print("msoas written=%d"%count,"errors=%d"%errors,"max msoa score=%f"%max_score)
print(str(missing_msoas))
open("scores.json","w").write(json.dumps(scores))