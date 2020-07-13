
import json
import csv
import os
import datetime

CASE_WINDOW_DAYS = 14

print("Reading case data - England")

cases_data_by_date = {}

dates = set()
for file in os.listdir():
    if file.startswith("coronavirus-cases") and file.endswith(".json"):
        json_content = json.loads(open(file).read())
        for ltla in json_content["ltlas"]:
            dt = datetime.datetime.strptime(ltla["specimenDate"],"%Y-%m-%d")
            dates.add(dt)

recent_dates = sorted(list(dates),reverse=True)[:30]

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
                    (cases,days) = cases_data_by_date[rdt].get(ac,(0,0))
                    cases_data_by_date[rdt][ac] = (daily+cases,days+1)

print("reading msoa->district mapping")

mapping_msoa_to_district = {}
mapping_district_to_msoas = {}
mapping_district_name_to_code = {}
f = open("Domestic_electric_consumption_by_Middle_Layer_Super_Output_Area__MSOA___2010_to_2018.csv")
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
        district_name = line[mapping_columns["LAName"]]
        district_code = line[mapping_columns["LACode"]]
        mapping_district_name_to_code[district_name] = district_code
        mapping_msoa_to_district[msoa_code] = district_code
        if district_code not in mapping_district_to_msoas:
            mapping_district_to_msoas[district_code] = []
        mapping_district_to_msoas[district_code].append(msoa_code)


print("Reading case data - Wales")

for rdt in recent_dates:
    f = open("wales_cases.csv")
    reader = csv.reader(f)
    mapping_columns = {}
    for line in reader:
        if not mapping_columns:
            for idx in range(len(line)):
                mapping_columns[line[idx]] = idx
        else:
            district_name = line[mapping_columns["Local Authority"]]
            if district_name == "Outside Wales" or district_name == "Unknown":
                continue
            district_code = mapping_district_name_to_code[district_name]
            daily = int(line[mapping_columns["Cases (new)"]])
            dt = datetime.datetime.strptime(line[mapping_columns["Specimen date"]],"%d/%m/%Y")
            # cases_data_by_date[rdt][ac] = daily + cases
            day_in_window = (rdt - dt).days
            if day_in_window >= 0 and day_in_window < CASE_WINDOW_DAYS:
                (cases,days) = cases_data_by_date[rdt].get(district_code, (0,0))
                cases_data_by_date[rdt][district_code] = (daily+cases,days+1)
    f.close()

print("reading MSOA long names")
msoa_longnames = {}
f = open("MSOA-Names-v1.1.0.csv")
f.read(1)
reader = csv.reader(f)
mapping_columns = {}
for line in reader:
    if not mapping_columns:
        print(str(line))
        for idx in range(len(line)):
            mapping_columns[line[idx]] = idx
    else:
        msoa_code = line[mapping_columns["msoa11cd"]]
        msoa_longname = line[mapping_columns["msoa11hclnm"]]
        msoa_longnames[msoa_code] = msoa_longname
f.close()

print("reading MSOA population data")
msoa_population = {}
f = open("msoa_population.csv")
reader = csv.reader(f)
mapping_columns = {}
for line in reader:
    if not mapping_columns:
        for idx in range(len(line)):
            mapping_columns[line[idx]] = idx
    else:
        msoa_code = line[mapping_columns["Area Codes"]]
        msoa = line[mapping_columns["MSOA"]]
        pop = line[mapping_columns["All Ages"]]
        if msoa:
            pop = int(pop.replace(",",""))
            msoa_population[msoa_code] = pop
f.close()

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
f.close()

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

msoas = json.loads(open("826dc85fb600440889480f4d9dbb1a24_2.geojson").read())

scores = []

count = 0
errors = 1
max_score = None
latest_dt = recent_dates[0]
missing_msoas = []
missing_long_names = 0

for feature in msoas["features"]:
    properties = feature["properties"]
    msoa_code = properties["msoa11cd"]
    if msoa_code in msoa_longnames:
        properties["long_name"] = msoa_longnames[msoa_code]
    else:
        missing_long_names += 1

    count += 1
    properties["score"] = -1
    properties["history_date_desc"] = []
    for dt in recent_dates:
        dt_str = dt.strftime("%Y-%m-%d")
        if dt == latest_dt:
            properties["LatestDate"] = dt_str
        if msoa_code in mapping_msoa_to_district:
            district = mapping_msoa_to_district[msoa_code]
            if district not in cases_data_by_date[dt]:
                if dt == latest_dt:
                    properties["score"] = -1
                    errors += 1
                    missing_msoas.append(msoa_code+":"+district)
                else:
                    properties["history_date_desc"].append(-1)
            else:
                pop = msoa_population[msoa_code]
                (cases,days) = cases_data_by_date[dt][district]
                score = (msoa_weighting[msoa_code]*cases)*(100000/float(pop))*(1/days)
                if dt == latest_dt:
                    properties["score"] = score
                else:
                    properties["history_date_desc"].append(score)
                if max_score is None or score > max_score:
                    max_score = score
        else:
            if dt == latest_dt:
                errors += 1
                properties["score"] = -1
            else:
                properties["history_date_desc"].append(-1)


print("msoas written=%d"%count,"errors=%d"%errors,"max msoa score=%f"%max_score)
print(str(missing_msoas))
print(missing_long_names)
open("new.geojson","w").write(json.dumps(msoas))


