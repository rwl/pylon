__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
KML_NS = "http://www.opengis.net/kml/2.2"

SVG_PATH = "SYSFigureA13.svg"
KML_PATH = "/tmp/UKGrid.kml"

COLOR_400 = "rgb(0%,0%,100%)"
ID_400 = "line400"

def main():
    svg_tree = ET.parse(SVG_PATH)
    svg_root = svg_tree.getroot()

    svg_group = svg_root.find("{%s}g" % SVG_NS)

    kml_root = ET.Element("{%s}kml" % KML_NS)
    kml_doc = ET.SubElement(kml_root, "{%s}Document" % KML_NS)

    style_kml(kml_doc)

    for path in svg_group.findall("./{%s}path" % SVG_NS):
        style = path.get("style")
        if ("stroke:%s" % COLOR_400) in style.split(";"):
            mark = ET.SubElement(kml_doc, "{%s}Placemark" % KML_NS)
            ET.SubElement(mark, "{%s}styleUrl" % KML_NS).text = ID_400

            ET.SubElement(mark, "{%s}name" % KML_NS).text = path.get("id")

            d = path.get("d")
            for move_to in d.split("M"):
                if len(move_to) == 0:
                    continue
                for close_path in move_to.split("Z"):
                    if len(close_path) == 0:
                        continue
                    linestring = ET.SubElement(mark, "{%s}LineString" % KML_NS)
                    coords_text = ""
                    for line_to in close_path.split("L"):
                        if len(line_to.split()) == 0:
                            continue
                        points = [float(pnt) for pnt in line_to.split()]
                        #FIXME: Convert points to lon/lat.
                        if points[0] > 6000.0:
                            coords_text += " %s,%s,0" % (points[0] - 6200.0,
                                                         points[1] - 2500.0)
                    coords = ET.SubElement(linestring, "{%s}coordinates" % KML_NS)
                    coords.text = coords_text

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

if __name__ == "__main__":
    main()
