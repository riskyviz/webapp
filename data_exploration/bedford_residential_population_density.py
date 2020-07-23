# -*- coding: utf-8 -*-

import os

from visigoth import Diagram
from visigoth.common import Legend, Text, MapLayerManager
from visigoth.map_layers import Chloropleth, WMS
from visigoth.utils.mapping.projections import Projections
from visigoth.utils.colour import ContinuousPalette
from visigoth.containers import Map, Sequence

folder=os.path.split(__file__)[0]

d = Diagram()

bedford_lat = 52.135
bedford_lon = -0.47
box = 0.5

hs = Sequence(orientation="horizontal") # main component
vs = Sequence(orientation="vertical")   # position to the right

m = Map(zoom_to=4,width=768,projection=Projections.EPSG_4326,boundaries=((bedford_lon-box/2,bedford_lat-box/2),(bedford_lon+box/2,bedford_lat+box/2)),font_height=18)
hs.add(m)

wms = WMS(type="osm")
m.add(wms)

palette=ContinuousPalette(colourMap=["white","red"],min_val=0)
palette.setDefaultColour("red")
residential = Chloropleth("pd_residential_bedford.geojson",valueNameOrFn=lambda p:p["DN"],labelNameOrFn=lambda x:"DN",palette=palette, stroke_width=0)
residential.setOpacity(0.75)
residential.setInfo("population density per sq km","","Contains data supplied by Natural Environment Research Council. ©NERC (Centre for Ecology & Hydrology). Contains National Statistics data © Crown copyright and database right 2011.","https://catalogue.ceh.ac.uk/documents/0995e94d-6d42-40c1-8ed4-5090d82471e1")
m.add(residential)

mlm = MapLayerManager([{"layer":wms,"label":"OpenStreetMap"},{"layer":residential,"label":"Residential Population Density"}],
                      title="Controls",height=150)

vs.add(Text("Bedford Area Population Density (per sq km)"))
vs.add(Legend(palette))
vs.add(mlm)

hs.add(vs)
d.add(hs)

d.connect(mlm,"manage_layers",m,"manage_layers")

html = d.draw(format="html")
f = open("bedford_residential_population_density.html", "w")
f.write(html)
f.close()

