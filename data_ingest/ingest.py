
# mash up daily data on new lab confirmed coronavirus cases in england and wales and compile a geojson
# which scores each MSOA with an estimate of the lab test case rate

import json
import csv
import datetime

# pip install visigoth
from visigoth.utils.geojson.geojson_transform import GeoJsonTransformer

HISTORY_DAYS = 30
CASE_WINDOW_DAYS = 14

# use thresholds defined by CDC
# https://www.americanprogress.org/issues/healthcare/news/2020/05/04/484373/evidence-based-thresholds-states-must-meet-control-coronavirus-spread-safely-reopen-economies/
LOW_THRESHOLD = 0.71
HIGH_THRESHOLD = 3.57

print("Reading case data - England")

# mapping dt => LA area => case count
cases_data_by_date = {}

# work out which dates are available in the English data
dates = set()
# and which areas in england and wales have covid case data
case_reporting_areas = set()

json_content = json.loads(open("coronavirus-cases.json").read())
for ltla in json_content["ltlas"]:
    dt = datetime.datetime.strptime(ltla["specimenDate"],"%Y-%m-%d")
    ac = ltla["areaCode"]
    dates.add(dt)
    case_reporting_areas.add(ac)

# collect the most recent days in descending order
recent_dates = sorted(list(dates),reverse=True)[:HISTORY_DAYS]
current_date = recent_dates[0]

# sanity check - should be no missing days
for index in range(0,len(recent_dates)-1):
    dt1 = recent_dates[index]
    dt2 = recent_dates[index+1]
    if (dt1 - dt2).days != 1 or (dt1 - dt2).seconds != 0:
        raise Exception("missing days in covid test data?")

# go back through the recent dates and for each recent date and each area compute a weighted (cases,count) for the
# previous CASE_WINDOW_DAYS days
for rdt in recent_dates:
    cases_data_by_date[rdt] = {}
    json_content = json.loads(open("coronavirus-cases.json").read())
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
            # apply a linear weighting over the case window to give more recent cases more weight
            weight = (CASE_WINDOW_DAYS - day_in_window) / CASE_WINDOW_DAYS
            (cases,days) = cases_data_by_date[rdt].get(ac,(0,0))
            cases_data_by_date[rdt][ac] = (weight*daily+cases,days+weight)

# this file is the only one I could find with the up to date mapping from LA area to MSOA
# collect the mapping from MSOA to LA and record various statistics

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
        year = line[mapping_columns["YEAR"]]
        if year != "2018":
            continue
        # only construct a mapping for districts for which we have covid case stats
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
            case_reporting_areas.add(district_code)
            daily = int(line[mapping_columns["Cases (new)"]])
            dt = datetime.datetime.strptime(line[mapping_columns["Specimen date"]],"%d/%m/%Y")
            # cases_data_by_date[rdt][ac] = daily + cases
            day_in_window = (rdt - dt).days
            if day_in_window >= 0 and day_in_window < CASE_WINDOW_DAYS:
                # apply a linear weighting to give more recent cases more weight
                weight = (CASE_WINDOW_DAYS - day_in_window) / CASE_WINDOW_DAYS
                (cases, days) = cases_data_by_date[rdt].get(district_code, (0, 0))
                cases_data_by_date[rdt][district_code] = (weight * daily + cases, days + weight)
    f.close()

print("reading MSOA long names")
msoa_longnames = {}
f = open("MSOA-Names-v1.1.0.csv")
f.read(1) # skip Unicode BOM
reader = csv.reader(f)
mapping_columns = {}
for line in reader:
    if not mapping_columns:
        for idx in range(len(line)):
            mapping_columns[line[idx]] = idx
    else:
        msoa_code = line[mapping_columns["msoa11cd"]]
        msoa_longname = line[mapping_columns["msoa11hclnm"]]
        msoa_longnames[msoa_code] = msoa_longname
f.close()

# Read in data providing a recent population estimate for each MSOA
# These estimates will be used to map from daily positive test case count to rate per 100K population
print("reading MSOA population data")

# msoa => population estimate
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

# read in historical deaths recorded by the ONS at MSOA level
# this will be used to decide how to distribute LA case counts amongst enclosed MSOAs
# and estimate case data at the MSOA level.  Obviously it would have been ideal to have
# the actual number of cases per day per MSOA.
print("reading deaths data")
deaths_by_msoa = {}     # record deaths per MSOA
deaths_by_district = {} # and deaths per LA district
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

# compute a normalised weighting for each MSOA within an LA district based on deaths per MSOA
print("calculating msoa weightings")
msoa_weighting = {}
for msoa_code in deaths_by_msoa:
    district = mapping_msoa_to_district.get(msoa_code, None)
    msoa_deaths = deaths_by_msoa[msoa_code]
    if district:
        district_deaths = deaths_by_district[district]
        # laplace correction - add 4 extra deaths in each MSOA
        # to avoid an MSOA given zero weighting and smooth some of the effects
        # due to random noise
        msoas_in_district = len(mapping_district_to_msoas[district])
        weighting = (4+msoa_deaths) / (4*msoas_in_district+district_deaths)
        msoa_weighting[msoa_code] = weighting

print("creating intermediate output geojson")

msoas = json.loads(open("826dc85fb600440889480f4d9dbb1a24_2.geojson").read())

latest_scores = [] # track the latest scores as a list of (msoa_code,score) pairs
no_scores = [] # list of MSOA for which we cannot compute scores

count = 0
errors = 1
max_score = None
latest_dt = recent_dates[0]

missing_long_names = 0

for feature in msoas["features"]:
    properties = feature["properties"]
    msoa_code = properties["msoa11cd"]
    if msoa_code in msoa_longnames:
        properties["long_name"] = msoa_longnames[msoa_code]
    else:
        missing_long_names += 1

    count += 1
    properties["score"] = None
    properties["history_date_desc"] = []
    properties["pop"] = msoa_population[msoa_code]
    for dt in recent_dates:
        dt_str = dt.strftime("%Y-%m-%d")
        if dt == latest_dt:
            properties["LatestDate"] = dt_str

        district = mapping_msoa_to_district[msoa_code]
        if district not in case_reporting_areas:
            # here we have no idea how to score the MSOA
            # this occurs with special cases - City of Londan and Scilly Isles
            # because we do not have case information at the district level
            if dt == latest_dt:
                errors += 1
                properties["score"] = None
                no_scores.append(msoa_code)
            else:
                properties["history_date_desc"].append(None)

        if district not in cases_data_by_date[dt]:
            # this can happen if there are no reports of Coronavius cases
            # over the previous CASE_WINDOW_DAYS
            # we don't know if this is because there are no cases
            # or if the data is not reported
            # assume 0 cases for now
            if dt == latest_dt:
                properties["score"] = 0.0
                latest_scores.append((msoa_code,0.0))
                errors += 1
            else:
                properties["history_date_desc"].append(0.0)
        else:
            pop = msoa_population[msoa_code]
            (cases,days) = cases_data_by_date[dt][district]
            score = (msoa_weighting[msoa_code]*cases)*(100000/float(pop))*(1/days)
            if dt == latest_dt:
                properties["score"] = score
                latest_scores.append((msoa_code,score))
            else:
                properties["history_date_desc"].append(score)
            if max_score is None or score > max_score:
                max_score = score

# write out a quick report
print("msoas written=%d"%count,"errors=%d"%errors,"max msoa score=%f"%max_score,"missing longnames=%d"%missing_long_names)
print("failed to compute scores for:")
for msoa in no_scores:
    print("\t"+msoa)

open("intermediate.geojson","w").write(json.dumps(msoas))

# try to shrink the file size a bit by reducing accuracy to 4 dp (equivalent to ~10m) and remove unused properties
print("optimisng geojson file to reduce file size")
gjt = GeoJsonTransformer(decimal_places=4,include_properties=["msoa11cd", "long_name", "score", "history_date_desc", "LatestDate"])
gjt.transform_file("intermediate.geojson","new.geojson")

print("writing out summary CSV with latest scores per MSOA, descending order")
# write out a sorted list of MSOAs in order of decreasing score
latest_scores_desc = sorted(latest_scores,key=lambda x:x[1],reverse=True)
f = open("latest_scores.csv","w")
w = csv.writer(f)
w.writerow(["MSOA","Score"])
low_count = 0
moderate_count = 0
high_count = 0
for (msoa,score) in latest_scores_desc:
    if score < LOW_THRESHOLD:
        low_count += 1
    elif score < HIGH_THRESHOLD:
        moderate_count += 1
    else:
        high_count += 1
    w.writerow([msoa,score])
f.close()

print("Summary")
total_count = low_count+moderate_count+high_count
print("\t;-) Low Risk %d (%0.2f percent)"%(low_count,100.0*low_count/total_count))
print("\t;-| Moderate Risk %d (%0.2f percent)"%(moderate_count,100.0*moderate_count/total_count))
print("\t;-( High Risk %d (%0.2f percent)"%(high_count,100.0*high_count/total_count))


