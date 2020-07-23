
import csv
from visigoth.utils.geojson import GeojsonReader
from visigoth import Diagram
from visigoth.map_layers import KDE, Hexbin, Geoimport, Cartogram
from visigoth.utils.colour import ContinuousPalette
from visigoth.containers import Map, Sequence
from visigoth.utils.colour import DiscretePalette
from visigoth.utils.marker import MarkerManager
from visigoth.common import Text


gjr = GeojsonReader()

# population-weighted centroids
# wget https://opendata.arcgis.com/datasets/b0a6d8a3dc5d4718b3fd62c548d60f81_0.geojson

centroids = {} # msoa => (short-name,lon,lat)
(points,lines,polys) = gjr.extract("b0a6d8a3dc5d4718b3fd62c548d60f81_0.geojson")
for (properties,multipoints) in points:
    msoa = properties["msoa11cd"]
    sname = properties["msoa11nm"]
    lon = multipoints[0][0]
    lat = multipoints[0][1]
    centroids[msoa] = (sname,lon,lat)

dataset = []

f = open("../data_ingest/latest_scores.csv","r")
r = csv.reader(f)
row = 0
for line in r:
    row += 1
    if row > 1:
        msoa = line[0]
        score = float(line[1])
        (sname,lon,lat) = centroids[msoa]
        risk_band = "unknown"
        if score < 0.71:
            risk_band = "low"
        elif score < 3.71:
            risk_band = "moderate"
        else:
            risk_band = "high"

        dataset.append({"msoa":msoa,"lat":lat,"lon":lon,"score":score,"risk_band":risk_band,"name":sname})


gi = Geoimport("nuts1.json",polygon_style=lambda p:{"fill":"none"}) # https://github.com/martinjc/UK-GeoJSON/blob/master/json/eurostat/ew/nuts1.json


d = Diagram()
s = Sequence(orientation="horizontal")

# KDE Plot first
p1 = ContinuousPalette(colourMap=["#0000FF00","yellow","red"],withIntervals=False)
k = KDE(dataset,bandwidth=10000,nr_samples_across=80,lon="lon",lat="lat",colour="score",contour_bands=20,palette=p1)
m1 = Map(width=1024, boundaries=((-6,50),(2,56)))
m1.add(gi)
m1.add(k)
s.add(Sequence().add(Text("Heat Map")).add(m1))

# Hex bin
p2 = ContinuousPalette(colourMap=["#0000FF00","yellow","red"],withIntervals=False)
h = Hexbin(dataset,colour="score",nr_bins_across=80,lon="lon",lat="lat",palette=p2,stroke_width=0.5)
m2 = Map(width=1024, boundaries=((-6,50),(2,56)))
m2.add(gi)
m2.add(h)
s.add(Sequence().add(Text("Binned Plot")).add(m2))

# Cartogram

p3 = DiscretePalette()
p3.addColour("low","green").addColour("moderate","orange").addColour("high","red")
mm = MarkerManager()
mm.setDefaultRadius(5)
cg = Cartogram(dataset,marker_manager=mm,iterations=100,lon="lon",lat="lat",colour="risk_band",palette=p3,f2=1)
m3 = Map(width=1024,boundaries=((-6,50),(2,56)))
m3.add(gi)
m3.add(cg)
s.add(Sequence().add(Text("Cartogram")).add(m3))

d.add(Text("Covid-19 Estimated Rate - 18th July - National Maps"))
d.add(s)

html = d.draw(format="html")
f = open("england_wales_risk_plots.html", "w")
f.write(html)
f.close()