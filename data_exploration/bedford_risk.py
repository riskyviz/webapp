# -*- coding: utf-8 -*-

import os

from visigoth import Diagram
from visigoth.common import Legend, Text
from visigoth.map_layers import Chloropleth, WMS
from visigoth.utils.mapping.projections import Projections
from visigoth.utils.colour import DiscretePalette
from visigoth.containers import Map, Sequence

folder=os.path.split(__file__)[0]

d = Diagram()

bedford_lat = 52.135
bedford_lon = -0.47
box = 0.5

hs = Sequence(orientation="horizontal") # main component
vs = Sequence(orientation="vertical")   # position to the right

m = Map(zoom_to=4,width=768,projection=Projections.EPSG_4326,boundaries=((bedford_lon-box/2,bedford_lat-box/2),(bedford_lon+box/2,bedford_lat+box/2)),font_height=18)

wms = WMS(type="osm")
m.add(wms)

palette=DiscretePalette()
palette.setDefaultColour("grey")

palette.addColour("high","red")
palette.addColour("moderate","orange")
palette.addColour("low","green")

def scoreThreshold(score):
    if score is None:
        return "unknown"
    elif score < 0.71:
        return "low"
    elif score < 3.57:
        return "moderate"
    else:
        return "high"

risk = Chloropleth("../riskCOVID/new.geojson",valueNameOrFn=lambda p:scoreThreshold(p["score"]),labelNameOrFn=lambda x:"Riskk Score",palette=palette, stroke_width=0)
risk.setOpacity(0.5)
risk.setInfo("estimate of covid risk","","Contains data supplied by UK office of national statistics, the UK government, and the Welsh government")
m.add(risk)

vs.add(Text("Bedford Area Covid Risk Estimates - Sample 18th July 2020"))
hs.add(m)
vs.add(Legend(palette))
hs.add(vs)
d.add(hs)

html = d.draw(format="html")
f = open("bedford_risk.html", "w")
f.write(html)
f.close()

