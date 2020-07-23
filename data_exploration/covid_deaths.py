
import csv

from visigoth import Diagram
from visigoth.charts import Bar
from visigoth.common import Legend, Text, Space
from visigoth.utils.colour import DiscretePalette

mapping_msoa_to_district = {}
mapping_district_to_msoas = {}
mapping_district_name_to_code = {}

f = open("../data_ingest/Domestic_electric_consumption_by_Middle_Layer_Super_Output_Area__MSOA___2010_to_2018.csv")
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
        if msoa_code not in mapping_district_to_msoas:
            mapping_district_to_msoas[district_code].append(msoa_code)


msoa_population = {}
f = open("../data_ingest/msoa_population.csv")
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

deaths_by_msoa = {}     # record deaths per MSOA
deaths_by_district = {} # and deaths per LA district
f = open("../data_ingest/covid_deaths_msoa.csv")
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

d = Diagram()

for district_name in mapping_district_name_to_code:
    district_code = mapping_district_name_to_code[district_name]
    msoas = mapping_district_to_msoas[district_code]

    tpop = 0
    tdeaths = 0
    if district_code[0] != "E" and district_code[0] != "W":
        continue

    for msoa in msoas:
        tpop += msoa_population[msoa]
        tdeaths += deaths_by_msoa[msoa]

    tdeaths += len(msoas)
    plot_data = []
    for msoa in msoas:
        pop = msoa_population[msoa]
        deaths = deaths_by_msoa[msoa]
        plot_data.append( {"district":district_name,"msoa":msoa,"measure":"deaths","percentage":100*deaths/tdeaths})
        plot_data.append(
            {"district": district_name, "msoa": msoa, "measure": "population", "percentage": 100 * pop / tpop})
    p = DiscretePalette()
    p.addColour("deaths","red")
    p.addColour("population","blue")
    t1 = Text(district_name+" - Population and Covid 19 Deaths (March-May) over MSOAs",font_height=24)
    t2 = Text("Total deaths %d, Total population %d"%(tdeaths,tpop),font_height=16)
    b = Bar(data=plot_data,palette=p,width=1536,height=512,x="msoa",y="percentage",colour="measure",stacked=False)
    l = Legend(p)
    s = Space(100)
    d.add(t1).add(t2).add(b).add(l).add(s)


open("covid_deaths.html","w").write(d.draw())