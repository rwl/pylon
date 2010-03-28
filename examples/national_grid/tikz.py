__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import zipfile
import xml.etree.ElementTree as ET

#file = zipfile.ZipFile("data/UK.kmz", "r")
#tree = ET.parse(file.open("doc.kml")) # Python 2.6

tree = ET.parse("data/doc.kml")

root = tree.getroot()

fd = open("/home/rwl/latex/workspace/tikz/boundaries.tex", "w+b")

for lr in root.findall(".//{http://www.opengis.net/kml/2.2}LinearRing"):
#    point = pl.find("./{http://www.opengis.net/kml/2.2}Point")
    coords = lr.findtext(".//{http://www.opengis.net/kml/2.2}coordinates")
#    name = lr.findtext("./{http://www.opengis.net/kml/2.2}name")
    fd.write("\draw[-] ")
    frags = coords.split(" ")
    for i, c in enumerate(frags):
        # (-4.1336116790771502, 52.914445877075202, 0.0)
        if len(c):
#            print tuple([float(a) for a in c.split(",")])
            x, y, z = [float(a) for a in c.split(",")]
            fd.write('(%.16f, %.16f)' % (x, y - 50.0))

#            print i, len(frags) - 2
            if not i == len(frags) - 2:
                fd.write(" -- ")
    fd.write(";\n")

fd.close()