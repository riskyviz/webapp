
import csv
import os.path
import json

# split up postcodes csv obtained from:
# https://www.freemaptools.com/download-uk-postcode-lat-lng.htm
# save as one JSON file per first 2 letters of the postcode

class CodeReader(object):

    def __init__(self,path):
        self.path = path
        self.postcode_groups = {}

    def load(self):
        f = open(self.path)
        r = csv.reader(f)
        lookup = {}
        for line in r:
            if not lookup:
                for i in range(len(line)):
                    lookup[line[i]] = i
            else:
                postcode = line[lookup["postcode"]]
                lat = line[lookup["latitude"]]
                lon = line[lookup["longitude"]]
                pg = postcode[:2]
                if pg not in self.postcode_groups:
                    self.postcode_groups[pg] = {}
                self.postcode_groups[pg][postcode] = {"lat":lat,"lon":lon}

    def dump(self,folder):
        for pg in self.postcode_groups:
            opath = os.path.join(folder,pg)+".json"
            open(opath,"w").write(json.dumps(self.postcode_groups[pg]))

if __name__ == '__main__':
    cr = CodeReader("ukpostcodes.csv")
    cr.load()
    cr.dump("postcode_lookup")