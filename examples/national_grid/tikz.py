__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import math
import zipfile
import xml.etree.ElementTree as ET

NS_KML = "http://www.opengis.net/kml/2.2"

MERC_SCALE = 1e5

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

def write_linear_rings(kmz_path, tikz_fd):
    file = zipfile.ZipFile(kmz_path, "r")
    tree = ET.parse(file.open("doc.kml")) # Python 2.6

    #tree = ET.parse("data/doc.kml")

    root = tree.getroot()

    for lr in root.findall(".//{%s}LinearRing" % NS_KML):
        coords = lr.findtext(".//{%s}coordinates" % NS_KML)
        tikz_fd.write("\draw[-] ")
        frags = coords.split(" ")
        for i, c in enumerate(frags):
            if len(c):
#                print tuple([float(a) for a in c.split(",")])
                x, y, _ = [float(a) for a in c.split(",")]
                tikz_fd.write('(%.16f, %.16f)' % (merc_x(x) / MERC_SCALE, merc_y(y) / MERC_SCALE))
                if not i == len(frags) - 2:
                    tikz_fd.write(" -- ")
        tikz_fd.write(";\n")

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


def main():
    tikz_path = "/home/rwl/latex/workspace/tikz/tikz/boundaries.tex"
#    uk_path = "data/UK.kmz"
#    ireland_path = "data/Ireland.kmz"
    uk_path = "data/UK-simplified.kmz"
    ireland_path = "data/Ireland-simplified.kmz"
    gen_path = "national_grid.kmz"

    tikz_fd = open(tikz_path, "w+b")
    tikz_fd.write("% UK\n")
    write_linear_rings(uk_path, tikz_fd)
    tikz_fd.close()

    tikz_fd = open(tikz_path, "a+b")
    tikz_fd.write("\n% Ireland\n")
    write_linear_rings(ireland_path, tikz_fd)
    tikz_fd.close()

    tikz_fd = open(tikz_path, "a+b")
    tikz_fd.write("\n% Generators\n")
    write_generators(gen_path, tikz_fd)
    tikz_fd.close()


if __name__ == "__main__":
    main()
