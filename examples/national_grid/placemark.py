__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import os
import csv
import zipfile
import xml.etree.ElementTree as ET

ns = "http://www.opengis.net/kml/2.2"

file = zipfile.ZipFile("national_grid.kmz", "r")

tree = ET.parse(file.open("doc.kml")) # Python 2.6 and later.
#tree = ET.parse("doc.kml")
root = tree.getroot()

path_root = ET.Element("{%s}kml" % ns)
doc = ET.SubElement(path_root, "{%s}Document" % ns)

style400 = ET.SubElement(doc, "{%s}Style" % ns, id="line400")
linestyle400 = ET.SubElement(style400, "{%s}LineStyle" % ns)
ET.SubElement(linestyle400, "{%s}color" % ns).text = "7f00ffff" # aabbggrr
ET.SubElement(linestyle400, "{%s}width" % ns).text = "5"

style275 = ET.SubElement(doc, "{%s}Style" % ns, id="line275")
linestyle275 = ET.SubElement(style275, "{%s}LineStyle" % ns)
ET.SubElement(linestyle275, "{%s}color" % ns).text = "7f3030ff" # aabbggrr FF3030
ET.SubElement(linestyle275, "{%s}width" % ns).text = "4"

style275 = ET.SubElement(doc, "{%s}Style" % ns, id="line132")
linestyle275 = ET.SubElement(style275, "{%s}LineStyle" % ns)
ET.SubElement(linestyle275, "{%s}color" % ns).text = "7fffbf00" # aabbggrr 00BFFF
ET.SubElement(linestyle275, "{%s}width" % ns).text = "3"

DATA_DIR = "./data/"

BRANCH_DATA = [
               os.path.join(DATA_DIR, "spt_circuit_param.csv"),
               os.path.join(DATA_DIR, "shetl_circuit_param.csv"),
               os.path.join(DATA_DIR, "nget_circuit_param.csv")
               ]

for path in BRANCH_DATA:
    reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = reader.next() # skip first row
    for row in reader:
        node1_id = row[0][:4]
        node2_id = row[1][:4]

#        pl1 = root.find(".//{%s}Placemark[@description='%s']" % (ns, node1_id))
#        pl2 = root.find(".//{%s}Placemark[@description='%s']" % (ns, node1_id))

        pl1 = None
        pl2 = None
        for pl in root.findall(".//{%s}Placemark" % ns):
            desc = pl.findtext("./{%s}description" % ns)

#            print desc

            if desc is not None:
                if pl1 is None and node1_id == desc[:4]:
                    pl1 = pl
                if pl2 is None and node2_id == desc[:4]:
                    pl2 = pl
                if pl1 is not None and pl2 is not None:
#                    print "found:", pl1.findtext("./{%s}description" % ns), pl2.findtext("./{%s}description" % ns)
                    break
        else:
            print "Placemark not found", node1_id, node2_id

        if pl1 is not None and pl2 is not None:
            pnt1 = pl1.find("./{%s}Point" % ns)
            coord1 = pnt1.findtext(".//{%s}coordinates" % ns)
            pnt2 = pl2.find("./{%s}Point" % ns)
            coord2 = pnt2.findtext(".//{%s}coordinates" % ns)

            pl_pth = ET.SubElement(doc, "{%s}Placemark" % ns)

            name = "%s %s" % (node1_id, node2_id)
            ET.SubElement(pl_pth, "{%s}name" % ns).text = name

            if len(row[0]) > 4:
                if row[0][4] == "4":
                    ET.SubElement(pl_pth, "{%s}styleUrl" % ns).text = "line400"
                elif row[0][4] == "2":
                    ET.SubElement(pl_pth, "{%s}styleUrl" % ns).text = "line275"
                elif row[0][4] == "1":
                    ET.SubElement(pl_pth, "{%s}styleUrl" % ns).text = "line132"

            ls = ET.SubElement(pl_pth, "{%s}LineString" % ns)

            c = ET.SubElement(ls, "{%s}coordinates" % ns)
            c.text = "%s %s" % (coord1, coord2)

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

indent(path_root)
et = ET.ElementTree(path_root)

et.write("/tmp/ngt_path.kml")
