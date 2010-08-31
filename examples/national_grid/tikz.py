__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import os.path
import math
import zipfile
import xml.etree.ElementTree as ET

NS_KML = "http://www.opengis.net/kml/2.2"

MERC_SCALE = 1e5

NGT_PATH = "national_grid.kmz"
NGT_PATH_PATH = "ngt_path.kml"
CITIES_PATH = "uk_cities.kmz"
OUT_PATH = "/home/rwl/latex/tikz/tikz/"

# Mercator projection algorithms by Paulo Silva
def deg_rad(ang):
    return ang*(math.pi/180.0)

def merc_x(lon):
    r_major=6378137.000
    return r_major*deg_rad(lon)

def merc_y(lat):
    if lat>89.5:lat=89.5
    if lat<-89.5:lat=-89.5
    r_major=6378137.000
    r_minor=6356752.3142
    temp=r_minor/r_major
    es=1-(temp*temp)
    eccent=math.sqrt(es)
    phi=(lat*math.pi)/180
    sinphi=math.sin(phi)
    con=eccent*sinphi
    com=.5*eccent
    con=math.pow(((1.0-con)/(1.0+con)),com)
    ts=math.tan(.5*((math.pi*0.5)-phi))/con
    y=0-r_major*math.log(ts)
    return y

def write_coords(tikz_fd, coords):
    frags = coords.split(" ")
    for i, c in enumerate(frags):
        if len(c):
            if i != 0:
                tikz_fd.write(" -- ")
#            print tuple([float(a) for a in c.split(",")])
            x, y, _ = [float(a) for a in c.split(",")]
            tikz_fd.write('(%.16f, %.16f)' % (merc_x(x) / MERC_SCALE, merc_y(y) / MERC_SCALE))
    tikz_fd.write(";\n")

def write_linear_rings(kmz_path, tikz_fd, style="-"):
    file = zipfile.ZipFile(kmz_path, "r")
    tree = ET.parse(file.open("doc.kml")) # Python 2.6

    #tree = ET.parse("data/doc.kml")

    root = tree.getroot()

    for lr in root.findall(".//{%s}LinearRing" % NS_KML):
        coords = lr.findtext(".//{%s}coordinates" % NS_KML)
        tikz_fd.write("\draw[%s] " % style)
        write_coords(tikz_fd, coords)

def write_line_strings(kml_path, tikz_fd, defaultStyle="-"):
    tree = ET.parse(kml_path)
    root = tree.getroot()

    for pm in root.findall(".//{%s}Placemark" % NS_KML):
        style = pm.findtext("./{%s}styleUrl" % NS_KML)
        if style is None:
            style = defaultStyle
        ls = pm.find("./{%s}LineString" % NS_KML)
        coords = ls.findtext(".//{%s}coordinates" % NS_KML)
        tikz_fd.write("\draw[%s] " % style)
        write_coords(tikz_fd, coords)

def write_generators(kmz_path, tikz_fd, gen_dir="gen"):
    file = zipfile.ZipFile(kmz_path, "r")
    tree = ET.parse(file.open("doc.kml")) # Python 2.6

    #tree = ET.parse("data/doc.kml")

    root = tree.getroot()

    for folder in root.findall(".//{%s}Folder" % NS_KML):
        if folder.findtext("./{%s}name" % NS_KML) == gen_dir:
            for placemark in folder.findall("./{%s}Placemark" % NS_KML):
                desc = placemark.findtext("./{%s}description" % NS_KML)
                Pg = float(desc.split(",")[1])

                point = placemark.find("./{%s}Point" % NS_KML)
                coords = point.findtext("./{%s}coordinates" % NS_KML)
                x, y, _ = [float(a) for a in coords.split(",")]
                mx, my = merc_x(x) / MERC_SCALE, merc_y(y) / MERC_SCALE
#                r = Pg / 120.0
                r = math.sqrt(Pg / 6.0)
                tikz_fd.write('\\fill[fill=black!50,semitransparent] (%.16f, %.16f) circle (%.2fpt);\n' %
                    (mx, my, r))
#                tikz_fd.write('\\fill[fill=black] (%.16f, %.16f) circle (1pt);\n' %
#                    (mx, my))
                tikz_fd.write('\\node [cross out,draw=black!60,minimum width=2pt,minimum height=2pt,inner sep=0pt] at (%.16f, %.16f) {};\n' % (mx, my))

def write_boundary_tex():
    simple = False
    boundaries_path = os.path.join(OUT_PATH, "boundaries.tex")

    if simple:
        uk_path = "data/UK-simplified.kmz"
        ireland_path = "data/Ireland-simplified.kmz"
    else:
        uk_path = "data/UK.kmz"
        ireland_path = "data/Ireland.kmz"

    boundaries_fd = open(boundaries_path, "w+b")
    boundaries_fd.write("% UK\n")
    boundaries_fd.write("\\tikzstyle{uk} = [-];\n")
    boundaries_fd.write("\\tikzstyle{ire} = [-];\n")
    write_linear_rings(uk_path, boundaries_fd, style="uk")
    boundaries_fd.write("\n% Ireland\n")
    write_linear_rings(ireland_path, boundaries_fd, style="ire")
    boundaries_fd.close()

def write_branch_tex():
    branches_path = os.path.join(OUT_PATH, "branches.tex")

    branches_fd = open(branches_path, "w+b")
    branches_fd.write("% Lines\n")
    write_line_strings(NGT_PATH_PATH, branches_fd, "other")
    branches_fd.close()

def write_generator_tex():
    generators_path = os.path.join(OUT_PATH, "generators.tex")

    generators_fd = open(generators_path, "w+b")
    generators_fd.write("% Generators\n")
    write_generators(NGT_PATH, generators_fd)
    generators_fd.close()

def write_city_tex():
    cities_path = os.path.join(OUT_PATH, "cities.tex")

    file = zipfile.ZipFile(CITIES_PATH, "r")
    tree = ET.parse(file.open("doc.kml")) # Python 2.6
    root = tree.getroot()

    cities_fd = open(cities_path, "w+b")
    cities_fd.write("% Cities\n")

    for placemark in root.findall(".//{%s}Placemark" % NS_KML):
        name = placemark.findtext("./{%s}name" % NS_KML)

        point = placemark.find("./{%s}Point" % NS_KML)
        coords = point.findtext("./{%s}coordinates" % NS_KML)
        x, y, _ = [float(a) for a in coords.split(",")]
        mx, my = merc_x(x) / MERC_SCALE, merc_y(y) / MERC_SCALE

        cities_fd.write('\\node [city] at (%.16f, %.16f) {%s};\n' %
                        (mx, my, name))

    cities_fd.close()


def main():
#    write_boundary_tex()
    write_branch_tex()
#    write_generator_tex()
#    write_city_tex()

if __name__ == "__main__":
    main()
