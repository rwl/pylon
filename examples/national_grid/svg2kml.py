__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

from math import pi, atan, exp
import xml.etree.ElementTree as ET
from pathdata import svg

SVG_NS = "http://www.w3.org/2000/svg"
KML_NS = "http://www.opengis.net/kml/2.2"

SVG_PATH = "SYSFigureA13Ungrouped.svg"
KML_PATH = "/tmp/UKGrid.kml"

#COLOR_400 = "rgb(0%,0%,100%)"
COLOR_400 = "#0000ff"
ID_400 = "line400"

def main():
    svg_tree = ET.parse(SVG_PATH)
    svg_root = svg_tree.getroot()

    svg_group = svg_root.find("{%s}g" % SVG_NS)

    kml_root = ET.Element("{%s}kml" % KML_NS)
    kml_doc = ET.SubElement(kml_root, "{%s}Document" % KML_NS)

    style_kml(kml_doc)

    pt = 0.000352777778 # metres
    m = 2834.64567 # points

    def add_line(coords_text, name, style_id):
        mark = ET.SubElement(kml_doc, "{%s}Placemark" % KML_NS)
        ET.SubElement(mark, "{%s}styleUrl" % KML_NS).text = style_id
        ET.SubElement(mark, "{%s}name" % KML_NS).text = name
        linestring = ET.SubElement(mark, "{%s}LineString" % KML_NS)
        coords = ET.SubElement(linestring, "{%s}coordinates" % KML_NS)
        coords.text = coords_text

    for path in svg_root.findall("./{%s}path" % SVG_NS):
        style = path.get("style")
        if ("stroke:%s" % COLOR_400) in style.split(";"):
            d = path.get("d")

            steps = svg.parseString(d)

            for command, points in steps:
                if command == "m":
                    # scale
                    points = [metres2latlon((p[1] * -1000.0),
                                            (p[0] * 1000.0)) for p in points]
#                    points = [(p[0] + 1.0, p[1]) for p in points]
                    x, y = x0, y0 = points[0]
                    coords_text = "%.5f,%.5f,0" % (x, y)
                    for xr, yr in points[1:]:
                        x += xr
                        y += yr
                        coords_text += " %.5f,%.5f,0" % (x, y)
                elif command in ["Z", "z"]:
                    coords_text += " %.5f,%.5f,0" % (x0, y0)
#                else:
#                    print command, points

                add_line(coords_text, path.get("id"), ID_400)


#            i = 0
#            while i < len(d):
#                # m 256.32031,478.80078 -0.12109,0 0,-0.48047
#                if d[i] == "m": # relative move to
#                    print "m:", d[i:]
#                    i += 1
#                    points = [float(p) for p in d[i].split(",")] # 256.32031,478.80078
#                    origin = points
#                    print "O:", origin
#                    coords_text = "%.5f,%.5f,0" % (points[0], points[1])
#                    i += 1
#                    n = 1 # num points
#                    while i < len(d) and d[i] not in ["M", "m"]:
#                        print "Di", d[i]
#                        if d[i] == "z": # close path
#                            coords_text += " %.5f,%.5f,0" % (origin[0], origin[1])
#                            n += 1
#                            i += 1
#                        else:
#                            rel_points = [float(p) for p in d[i].split(",")]
#                            points[0] += rel_points[0]
#                            points[1] += rel_points[1]
#                            print "R:", points, rel_points
#                            coords_text += " %.5f,%.5f,0" % (points[0], points[1])
#                            n += 1
#                            i += 1
#
#                    if n > 1:
#                        mark = ET.SubElement(kml_doc, "{%s}Placemark" % KML_NS)
#                        ET.SubElement(mark, "{%s}styleUrl" % KML_NS).text = ID_400
#                        ET.SubElement(mark, "{%s}name" % KML_NS).text = path.get("id")
#                        linestring = ET.SubElement(mark, "{%s}LineString" % KML_NS)
#                        coords = ET.SubElement(linestring, "{%s}coordinates" % KML_NS)
#                        coords.text = coords_text
#                    else:
#                        print "skipping"
##                    i += 1
#
#                if i < len(d) and d[i] == "M":
#                    print "M:", d[i:]
#                    i += 1


#            for move_to in d.split("M"):
#                if len(move_to) == 0:
#                    continue
#                for close_path in move_to.split("Z"):
#                    if len(close_path) == 0:
#                        continue
#
#                    mark = ET.SubElement(kml_doc, "{%s}Placemark" % KML_NS)
#                    ET.SubElement(mark, "{%s}styleUrl" % KML_NS).text = ID_400
#
#                    ET.SubElement(mark, "{%s}name" % KML_NS).text = path.get("id")
#
#                    linestring = ET.SubElement(mark, "{%s}LineString" % KML_NS)
#
#                    coords_text = ""
#                    for line_to in close_path.split("L"):
#                        if len(line_to.split()) == 0:
#                            continue
#                        points = [float(pnt) for pnt in line_to.split()]
#                        #FIXME: Convert points to lon/lat.
#                        coords_text += " %s,%s,0" % (points[0], points[1])
#                    coords = ET.SubElement(linestring, "{%s}coordinates" % KML_NS)
#                    coords.text = coords_text

    indent(kml_root)
    kml_tree = ET.ElementTree(kml_root)
    kml_tree.write(KML_PATH)

def style_kml(kml_doc):
    style400 = ET.SubElement(kml_doc, "{%s}Style" % KML_NS, id=ID_400)
    linestyle400 = ET.SubElement(style400, "{%s}LineStyle" % KML_NS)
    # KML color: aabbggrr
    ET.SubElement(linestyle400, "{%s}color" % KML_NS).text = "7f00ffff"
    ET.SubElement(linestyle400, "{%s}width" % KML_NS).text = "5"

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

def metres2latlon(mx, my, origin_shift= 2 * pi * 6378137 / 2.0):
    """Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in
    WGS84 Datum"""
    lon = (mx / origin_shift) * 180.0
    lat = (my / origin_shift) * 180.0

    lat = 180 / pi * (2 * atan( exp( lat * pi / 180.0)) - pi / 2.0)
    return lat, lon

if __name__ == "__main__":
    main()
