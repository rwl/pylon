import pylon

import csv
#import kmldom
import zipfile
import xml.etree.ElementTree as ET
import geolocator.gislib
from bin.examples.national_grid import heysham, keadby

file = zipfile.ZipFile("spt.kmz", "r")

#for name in file.namelist():
#    data = file.read(name)
#    print name, len(data), repr(data[:40])

#element = kmldom.ParseKml(file.read("doc.kml"))
#kml = kmldom.AsKml(element)
#doc = kmldom.AsDocument(kml.get_feature())

#tree = ET.parse(file.open("doc.kml"))
tree = ET.parse("doc.kml")
root = tree.getroot()

#for pl in root.findall(".//{http://www.opengis.net/kml/2.2}Placemark"):
#    point = pl.find("./{http://www.opengis.net/kml/2.2}Point")
#    coord = point.findtext(".//{http://www.opengis.net/kml/2.2}coordinates")
#    name = pl.findtext("./{http://www.opengis.net/kml/2.2}name")
#    print '    "%s": (%s),' % (name, coord[:-3])

reader = csv.reader(open('generators.csv'), delimiter=',', quotechar='"')
for row in reader:
#    print ", ".join(row)

    p_max = float(row[3])
    g = pylon.Generator(None, name=row[1], p=p_max, p_max=p_max)
    g._company = row[0]
    g._fuel = row[2]
    g._year = int(row[4])
    g._location = row[5]

    if p_max >= 100.0:
        lc_name = row[1].lower().replace(' ', '_').replace("'", "")
        print '%s = pylon.Generator(None, name="%s", p_max=%.2f)' % (lc_name, row[1], p_max)
#        print '%s._company = "%s"' % (lc_name, row[0])
#        print '%s._fuel = "%s"' % (lc_name, row[2])
#        print '%s._year = %d' % (lc_name, int(row[4]))
#        print '%s._location = "%s"' %(lc_name, row[5])

# SPT 400kV
hunterston = pylon.Bus("HUER Hunterston", v_base=400.0, position=(-4.890804,55.7218))
inverkip = pylon.Bus("INKI Inverkip", v_base=400.0, position=(-4.885826,55.89851))
devol_moor = pylon.Bus("DEVM Devol Moor", v_base=400.0, position=(-4.708608,55.91584))
kilmarnock_south = pylon.Bus("KILS Kilmarnock South", v_base=400.0, position=(-4.463855094935374,55.5758378468798))
strathaven = pylon.Bus("STHA Strathaven", v_base=400.0, position=(-4.081388297064154,55.7534299786771))
coalburn = pylon.Bus("COAL Coalburn", v_base=400.0, position=(-3.888577,55.5893780000000))
elvanfoot = pylon.Bus("ELVA Elvanfoot", v_base=400.0, position=(-3.659598516077846,55.434032701650))
gretna = pylon.Bus("GRNA Gretna", v_base=400.0, position=(-3.067545,54.99248))
straiton = pylon.Bus("SMEA (Straiton)", v_base=400.0, position=(-3.165556231263057,55.8912564096860))
crystal_rig = pylon.Bus("CRYR Crystal Rig", v_base=400.0, position=(-2.733333,55.83333))
torness = pylon.Bus("TORN Torness", v_base=400.0, position=(-2.407694,55.96777))
cockenzie = pylon.Bus("COCK Cockenzie", v_base=400.0, position=(-2.971458,55.96755))
eccles = pylon.Bus("ECCL Eccles", v_base=400.0, position=(-2.329860668011021,55.6694176929855))

# NGET
harker = pylon.Bus("Harker", v_base=400.0)
stella_west = pylon.Bus("Stella West", v_base=400.0)
hutton_1 = pylon.Bus("Hutton 1", v_base=400.0)
hutton_2 = pylon.Bus("Hutton 2", v_base=400.0)
heysham = pylon.Bus("Heysham", v_base=400.0)
penwortham = pylon.Bus("Penwortham", v_base=400.0)
padham = pylon.Bus("Padham", v_base=400.0)
kearsley = pylon.Bus("Kearsley", v_base=400.0)
dains = pylon.Bus("Daines", v_base=400.0)
macclesfield = pylon.Bus("Macclesfield", v_base=400.0)
deeside = pylon.Bus("Deeside", v_base=400.0)
frodsham = pylon.Bus("Frodsham", v_base=400.0)
dinorwig = pylon.Bus("Dinorwig", v_base=400.0)
pentir = pylon.Bus("Pentir", v_base=400.0)
wylfa = pylon.Bus("Wylfa", v_base=400.0)
trawsfynydd = pylon.Bus("Trawsfynydd", v_base=400.0)
legacy = pylon.Bus("Legacy", v_base=400.0)
cellarhead = pylon.Bus("Cellarhead", v_base=400.0)
drakelow = pylon.Bus("Drakelow", v_base=400.0)
willington_east = pylon.Bus("Willington East", v_base=400.0)
ironbridge = pylon.Bus("Ironbridge", v_base=400.0)
rugeley = pylon.Bus("Rugeley", v_base=400.0)
hams_hall = pylon.Bus("Hams Hall", v_base=400.0)
feckenham = pylon.Bus("Feckenham", v_base=400.0)
walham = pylon.Bus("Walham", v_base=400.0)
rassau = pylon.Bus("Rassau", v_base=400.0)
pembroke = pylon.Bus("Pembroke", v_base=400.0)
swansea_north = pylon.Bus("Swansea North", v_base=400.0)
cilfynydd = pylon.Bus("Cilfynydd", v_base=400.0)
imperial_park = pylon.Bus("Imperial Park", v_base=400.0)
seabank = pylon.Bus("Seabank", v_base=400.0)
melksham = pylon.Bus("Melksham", v_base=400.0)
minety = pylon.Bus("Minety", v_base=400.0)
cowley = pylon.Bus("Cowley", v_base=400.0)
didcot = pylon.Bus("Didcot", v_base=400.0)
bramley = pylon.Bus("Bramley", v_base=400.0)
fleet = pylon.Bus("Fleet", v_base=400.0)
lovedean = pylon.Bus("Lovedean", v_base=400.0)
botley_wood = pylon.Bus("Botley Wood", v_base=400.0)
fawley = pylon.Bus("Fawley", v_base=400.0)
marchwood = pylon.Bus("Marchwood", v_base=400.0)
nursling = pylon.Bus("Nursling", v_base=400.0)
mannington = pylon.Bus("Mannington", v_base=400.0)
chickerell_1 = pylon.Bus("Chickerell 1", v_base=400.0)
chickerell_2 = pylon.Bus("Chickerell 2", v_base=400.0)
axminster = pylon.Bus("Axminster", v_base=400.0)
exeter = pylon.Bus("Exeter", v_base=400.0)
langage = pylon.Bus("Langage", v_base=400.0)
landulph_1 = pylon.Bus("Landulph 1", v_base=400.0)
landulph_2 = pylon.Bus("Landulph 2", v_base=400.0)
indian_queens = pylon.Bus("Indian Queens", v_base=400.0)
taunton = pylon.Bus("Taunton", v_base=400.0)
hinkley_point = pylon.Bus("Hinkley Point", v_base=400.0)
bolney = pylon.Bus("Bolney", v_base=400.0)
ninfield = pylon.Bus("Ninfield", v_base=400.0)
dugeness = pylon.Bus("Dugeness", v_base=400.0)
sellindge = pylon.Bus("Sellindge", v_base=400.0)
canterbury_north = pylon.Bus("Canterbury North", v_base=400.0)
kemsley = pylon.Bus("Kemsley", v_base=400.0)
rowdown = pylon.Bus("Rowdown", v_base=400.0)
beddington = pylon.Bus("Beddington", v_base=400.0)
littlebrook = pylon.Bus("Littlebrook", v_base=400.0)
grain_1 = pylon.Bus("Grain 1", v_base=400.0)
grain_2 = pylon.Bus("Grain 2", v_base=400.0)
kingsnorth = pylon.Bus("Kingsnorth", v_base=400.0)
northfleet_east = pylon.Bus("Northfleet East", v_base=400.0)
barking = pylon.Bus("Barking", v_base=400.0)
west_ham = pylon.Bus("Westham", v_base=400.0)
city_road = pylon.Bus("City Road", v_base=400.0)
unknown = pylon.Bus("Unknown", v_base=400.0)
coryton = pylon.Bus("Coryton", v_base=400.0)
rayleigh_main = pylon.Bus("Rayleigh Main", v_base=400.0)
bramford = pylon.Bus("Bramford", v_base=400.0)
sizewell = pylon.Bus("Sizewell", v_base=400.0)
norwich_main = pylon.Bus("Norwich Main", v_base=400.0)
pelham = pylon.Bus("Pelham", v_base=400.0)
rye_house = pylon.Bus("Rye House", v_base=400.0)
wymondley_main = pylon.Bus("Wymondley Main", v_base=400.0)
sundon_1 = pylon.Bus("Sundon 1", v_base=400.0)
sundon_2 = pylon.Bus("Sundon 2", v_base=400.0)
east_claydon = pylon.Bus("East Claydon", v_base=400.0)
enderby = pylon.Bus("Enderby", v_base=400.0)
ratcliffe_on_soar = pylon.Bus("Ratcliffe on Soar", v_base=400.0)
grendon = pylon.Bus("Grendon", v_base=400.0)
staythorpe = pylon.Bus("Staythorpe", v_base=400.0)
cottam = pylon.Bus("Cottam", v_base=400.0)
high_marnham = pylon.Bus("High Marnham", v_base=400.0)
eaton_socon = pylon.Bus("Eaton Socon", v_base=400.0)
burwell_main = pylon.Bus("Burwell Main", v_base=400.0)
walpole = pylon.Bus("Walpole", v_base=400.0)
spalding_north = pylon.Bus("Spalding North", v_base=400.0)
west_burton = pylon.Bus("West Burton", v_base=400.0)
keadby = pylon.Bus("Keadby", v_base=400.0)
grimsby_west = pylon.Bus("Grimsby West", v_base=400.0)
south_humber_bank = pylon.Bus("South Humber Bank", v_base=400.0)
killingholme = pylon.Bus("Killingholme", v_base=400.0)
humber_refinery = pylon.Bus("Humber Refinery", v_base=400.0)
creyke_beck = pylon.Bus("Creyke Beck", v_base=400.0)
thornton = pylon.Bus("Thornton", v_base=400.0)
drax = pylon.Bus("Drax", v_base=400.0)
eggsborough = pylon.Bus("Eggsborough", v_base=400.0)
thorpe_marsh = pylon.Bus("Thorpe Marsh", v_base=400.0)
brinsworth = pylon.Bus("Brinsworth", v_base=400.0)
stocksbridge = pylon.Bus("Stocksbridge", v_base=400.0)
monk_fryston = pylon.Bus("Monk Fryston", v_base=400.0)
osbaldwick = pylon.Bus("Osbaldwick", v_base=400.0)
norton = pylon.Bus("Norton", v_base=400.0)
lackenby = pylon.Bus("Lackenby", v_base=400.0)

spt_400 =[
    pylon.Branch(hunterston, inverkip),
    pylon.Branch(inverkip, devol_moor),
    pylon.Branch(hunterston, kilmarnock_south),
    pylon.Branch(kilmarnock_south, strathaven),
    pylon.Branch(strathaven, coalburn),
    pylon.Branch(coalburn, elvanfoot),
    pylon.Branch(elvanfoot, gretna),
    pylon.Branch(strathaven, straiton),
    pylon.Branch(straiton, torness),
    pylon.Branch(cockenzie, eccles)
]

ngt_400 = [
#    pylon.Branch(gretna, harker, 1),
    pylon.Branch(harker, hutton_1, 1),
    pylon.Branch(harker, hutton_2, 1),
    pylon.Branch(hutton_1, heysham, 1),
    pylon.Branch(hutton_2, heysham, 1),
    pylon.Branch(hutton_1, penwortham, 1),
    pylon.Branch(hutton_2, penwortham, 1),
    pylon.Branch(heysham, penwortham, 2),
    pylon.Branch(penwortham, padham, 1),
    pylon.Branch(penwortham, dains, 1),
    pylon.Branch(padham, kearsley, 1),
    pylon.Branch(kearsley, dains, 1),
    pylon.Branch(dains, deeside, 2),
    pylon.Branch(deeside, frodsham, 2),
    pylon.Branch(deeside, pentir, 2),
    pylon.Branch(pentir, dinorwig, 1),
    pylon.Branch(pentir, wylfa, 2),
    pylon.Branch(deeside, trawsfynydd, 1),
    pylon.Branch(deeside, legacy, 2),
    pylon.Branch(legacy, ironbridge, 2),
    pylon.Branch(ironbridge, rugeley, 1),
    pylon.Branch(rugeley, drakelow, 1),
    pylon.Branch(drakelow, cellarhead, 2),
    pylon.Branch(cellarhead, dains, 1),
    pylon.Branch(cellarhead, macclesfield, 1),
    pylon.Branch(dains, macclesfield, 1),
    pylon.Branch(drakelow, hams_hall, 1),
    pylon.Branch(hams_hall, willington_east, 1),
    pylon.Branch(hams_hall, feckenham, 1),
    pylon.Branch(feckenham, walham, 1),
    pylon.Branch(walham, pembroke, 1),
    pylon.Branch(walham, rassau, 1),
    pylon.Branch(rassau, cilfynydd, 1),
    pylon.Branch(cilfynydd, swansea_north, 1),
    pylon.Branch(cilfynydd, pembroke, 1),
    pylon.Branch(cilfynydd, pembroke, 1),
    pylon.Branch(swansea_north, pembroke, 1),
    pylon.Branch(cilfynydd, imperial_park, 1),
    pylon.Branch(cilfynydd, seabank, 1),
    pylon.Branch(imperial_park, melksham, 1),
    pylon.Branch(seabank, melksham, 1),
    pylon.Branch(melksham, minety, 2),
    pylon.Branch(minety, cowley, 1),
    pylon.Branch(minety, feckenham, 1),
    pylon.Branch(cowley, walham, 1),
    pylon.Branch(cowley, didcot, 2),
    pylon.Branch(didcot, bramley, 2),
    pylon.Branch(bramley, fleet, 2),
    pylon.Branch(fleet, lovedean, 2),
    pylon.Branch(lovedean, botley_wood, 1),
    pylon.Branch(lovedean, fawley, 1),
    pylon.Branch(botley_wood, fawley, 1),
    pylon.Branch(fawley, marchwood, 1),
    pylon.Branch(marchwood, nursling, 1),
    pylon.Branch(nursling, lovedean, 1),
    pylon.Branch(fawley, mannington, 1),
    pylon.Branch(lovedean, mannington, 1),
    pylon.Branch(mannington, chickerell_1, 1),
    pylon.Branch(mannington, chickerell_2, 1),
    pylon.Branch(chickerell_1, exeter, 1),
    pylon.Branch(chickerell_2, axminster, 1),
    pylon.Branch(exeter, langage, 2),
    pylon.Branch(langage, landulph_1, 1),
    pylon.Branch(langage, landulph_2, 1),
    pylon.Branch(landulph_1, indian_queens, 1),
    pylon.Branch(landulph_2, indian_queens, 1),
    pylon.Branch(indian_queens, taunton, 2, online=False),
    pylon.Branch(exeter, hinkley_point, 2),
    pylon.Branch(hinkley_point, melksham, 2),
    pylon.Branch(melksham, bramley, 2),
    pylon.Branch(lovedean, bolney, 2),
    pylon.Branch(bolney, ninfield, 2),
    pylon.Branch(ninfield, dugeness, 2),
    pylon.Branch(dugeness, sellindge, 2),
    pylon.Branch(sellindge, canterbury_north, 2),
    pylon.Branch(canterbury_north, kemsley, 2),
    pylon.Branch(kemsley, rowdown, 1),
    pylon.Branch(littlebrook, kemsley, 1),
    pylon.Branch(rowdown, littlebrook, 1),
    pylon.Branch(rowdown, beddington, 1),
    pylon.Branch(kemsley, grain_1, 1),
    pylon.Branch(kemsley, grain_2, 1),
    pylon.Branch(grain_1, grain_2, 1, b=0.9),
    pylon.Branch(grain_1, coryton, 1),
    pylon.Branch(grain_2, kingsnorth, 1),
    pylon.Branch(kingsnorth, northfleet_east, 2),
    pylon.Branch(northfleet_east, barking, 2),
    pylon.Branch(barking, west_ham, 2),
    pylon.Branch(west_ham, city_road, 2),
    pylon.Branch(city_road, unknown, 2),
    pylon.Branch(unknown, sundon_1, 1),
    pylon.Branch(kingsnorth, rayleigh_main, 1),
    pylon.Branch(rayleigh_main, coryton, 1),
    pylon.Branch(rayleigh_main, bramford),
    pylon.Branch(bramford, sizewell, 1),
    pylon.Branch(bramford, sizewell, 1),
    pylon.Branch(sizewell, norwich_main, 1),
    pylon.Branch(sizewell, pelham, 1),
    pylon.Branch(bramford, norwich_main, 1),
    pylon.Branch(norwich_main, walpole, 2),
    pylon.Branch(rayleigh_main, pelham, 1),
    pylon.Branch(pelham, rye_house, 1),
    pylon.Branch(pelham, wymondley_main, 1),
    pylon.Branch(wymondley_main, eaton_socon, 1),
    pylon.Branch(eaton_socon, cottam, 1),
    pylon.Branch(wymondley_main, cottam, 1),
    pylon.Branch(wymondley_main, sundon_2, 1),
    pylon.Branch(pelham, sundon_2, 1),
    pylon.Branch(sundon_1, east_claydon, 1),
    pylon.Branch(sundon_1, cowley, 1),
    pylon.Branch(east_claydon, cowley, 1),
    pylon.Branch(east_claydon, enderby, 2),
    pylon.Branch(enderby, ratcliffe_on_soar, 2),
    pylon.Branch(sundon_1, grendon, 1),
    pylon.Branch(sundon_2, grendon, 1),
    pylon.Branch(grendon, staythorpe, 1),
    pylon.Branch(grendon, west_burton, 1),
    pylon.Branch(staythorpe, cottam, 1),
    pylon.Branch(staythorpe, cottam, 1),
    pylon.Branch(staythorpe, ratcliffe_on_soar, 1),
    pylon.Branch(ratcliffe_on_soar, high_marnham, 1),
    pylon.Branch(high_marnham, west_burton, 1),
    pylon.Branch(west_burton, walpole, 1),
    pylon.Branch(walpole, burwell_main, 2),
    pylon.Branch(walpole, spalding_north, 1),
    pylon.Branch(spalding_north, keadby, 1),
    pylon.Branch(keadby, cottam, 2),
    pylon.Branch(keadby, west_burton, 1),
    pylon.Branch(keadby, grimsby_west, 1),
    pylon.Branch(grimsby_west, south_humber_bank, 1),
    pylon.Branch(south_humber_bank, killingholme, 1),
    pylon.Branch(killingholme, humber_refinery, 1),
    pylon.Branch(killingholme, creyke_beck, 1),
    pylon.Branch(humber_refinery, creyke_beck, 1),
    pylon.Branch(keadby, creyke_beck, 1),
    pylon.Branch(keadby, drax, 2),
    pylon.Branch(keadby, brinsworth, 1),
    pylon.Branch(brinsworth, thorpe_marsh, 1),
    pylon.Branch(thorpe_marsh, drax, 1),
    pylon.Branch(thorpe_marsh, eggsborough, 1),
    pylon.Branch(thorpe_marsh, stocksbridge, 1),
    pylon.Branch(stocksbridge, macclesfield, 1),
    pylon.Branch(eggsborough, monk_fryston, 1),
    pylon.Branch(monk_fryston, padham, 1),
    pylon.Branch(eggsborough, drax, 2),
    pylon.Branch(drax, thornton, 2),
    pylon.Branch(thornton, creyke_beck, 2),
    pylon.Branch(thornton, osbaldwick, 2),
    pylon.Branch(osbaldwick, norton, 2),
    pylon.Branch(thornton, lackenby, 2),
    pylon.Branch(norton, lackenby, 1),
#    pylon.Branch(stella_west, eccles, 2)
]

ngt400_positions = {
    "Heysham": (-2.889817603523912,54.0325236986067),
    "Harker": (-2.964096026479853,54.941846049675),
    "Stella West": (-1.742668520653984,54.978276476945),
    "Hutton 1": (-2.878398,54.63229),
    "Hutton 2": (-2.878398,54.63229),
    "Penwortham": (-2.756124320870268,53.7431662182153),
    "Padham": (-2.32743339134566,53.7946834966753),
    "Kearsley": (-2.357770946840267,53.5377766590708),
    "Daines": (-2.379557204711549,53.4260405728584),
    "Macclesfield": (-2.12819,53.26084),
    "Deeside": (-3.077540243994436,53.2305482761804),
    "Frodsham": (-2.71658663783474,53.3093371100614),
    "Dinorwig": (-4.114295,53.13252),
    "Pentir": (-4.158379606801104,53.1873950383748),
    "Wylfa": (-4.482851,53.41551),
    "Trawsfynydd": (-3.920197,52.9041759999999),
    "Legacy": (-3.053872186273413,53.0286738665159),
    "Cellarhead": (-2.082495385368309,53.0406605212692),
    "Drakelow": (-1.652883295804878,52.7735809534174),
    "Willington East": (-1.54682558029362,52.8550177962872),
    "Ironbridge": (-2.512461354749406,52.63042022629),
    "Rugeley": (-1.915175206703827,52.7565966969897),
    "Hams Hall": (-1.705175,52.52460),
    "Feckenham": (-1.972769170536403,52.250893686137),
    "Walham": (-2.254009436290156,51.8787882330553),
    "Rassau": (-3.226400903855693,51.8097757307408),
    "Pembroke": (-4.990532875435625,51.6818581510822),
    "Swansea North": (-3.946629,51.62044),
    "Cilfynydd": (-3.300734811688061,51.63565875699),
    "Imperial Park": (-3.03103738672417,51.5477246010170),
    "Seabank": (-2.670597,51.53923),
    "Melksham": (-2.150838076072542,51.3935690570800),
    "Minety": (-2.001723670712312,51.607467880478),
    "Cowley": (-2.05375,51.83071),
    "Didcot": (-1.260540031340124,51.6228122042465),
    "Bramley": (-1.077823390677238,51.3359022827527),
    "Fleet": (-0.8424104618638506,51.2760494702930),
    "Lovedean": (-1.039536,50.91746),
    "Botley Wood": (-1.232179486820255,50.8844629252112),
    "Fawley": (-1.328109620825974,50.8179476146304),
    "Marchwood": (-1.453906825286801,50.8894825276846),
    "Nursling": (-1.466244682528629,50.9449060784875),
    "Mannington": (-1.895043818044795,50.8467433695566),
    "Chickerell 1": (-2.486609385822157,50.6245668505529),
    "Chickerell 2": (-2.486609385822157,50.6245668505529),
    "Axminster": (-3.000022577344986,50.7815653966007),
    "Exeter": (-3.533617,50.721),
    "Langage": (-4.01056,50.3885669999999),
    "Indian Queens": (-4.931884,50.3924820000000),
    "Landulph 1": (-4.239615,50.4385),
    "Landulph 2": (-4.239615,50.4385),
    "Taunton": (-3.103446,51.01465),
    "Hinkley Point": (-3.132477,51.20817),
    "Bolney": (-0.202842,50.99530),
    "Dugeness": (0.9628562932696613,50.913030697050),
    "Ninfield": (0.4480812218590008,50.8813635730430),
    "Sellindge": (0.975537741715635,51.1064631014820),
    "Canterbury North": (1.080517,51.27726),
    "Kemsley": (0.7414941631712446,51.3681916704523),
    "Rowdown": (-0.003386563770761878,51.3518003628730),
    "Beddington": (-0.1283540801114123,51.3733056462245),
    "Littlebrook": (0.263184,51.33664),
    "Grain 1": (0.715028,51.4451809999999),
    "Grain 2": (0.715028,51.4451809999999),
    "Kingsnorth": (0.602274,51.4180510000000),
    "Northfleet East": (0.3119321650873028,51.4322322177975),
    "Barking": (0.08147799999999999,51.5362789999999),
    "Westham": (0.008677708408581874,51.5348504682561),
    "City Road": (-0.094483,51.52895),
    "Coryton": (0.5020520000000001,51.5131889999999),
    "Rayleigh Main": (0.605291,51.58599),
    "Bramford": (1.062241581797233,52.0713632981939),
    "Sizewell": (1.619797,52.21394),
    "Norwich Main": (1.299331958266214,52.6280405377592),
    "Pelham": (0.1182422422810963,51.9348864665105),
    "Rye House": (0.009131,51.762),
    "Wymondley Main": (-0.2502147770611752,51.9272221773639),
    "Sundon 1": (-0.5029223827557178,51.9362228169973),
    "Sundon 2": (-0.5029223827557178,51.9362228169973),
    "East Claydon": (-0.9072092603580684,51.9264101973322),
    "Enderby": (-1.215557231312531,52.5978401151180),
    "Ratcliffe on Soar": (-1.06799,52.72516),
    "Grendon": (-1.592186,52.59089),
    "Staythorpe": (-0.8688527981499279,53.0769776244108),
    "Cottam": (-0.7814806033729527,53.3036457390875),
    "High Marnham": (-0.7926447342129663,53.2292778505215),
    "Eaton Socon": (-0.3024698538888043,52.2148676366807),
    "Burwell Main": (0.3134943085383525,52.2806737919393),
    "Walpole": (0.1983293309076296,52.7266414133630),
    "Spalding North": (-0.13214,52.8076),
    "West Burton": (-1.88019,54.262),
    "Keadby": (-0.7568794563348045,53.5979583972366),
    "Grimsby West": (-0.07549271835070896,53.5649618767681),
    "South Humber Bank": (-0.1446758205689241,53.6013154086385),
    "Killingholme": (-0.255287,53.65656),
    "Humber Refinery": (-0.257908,53.64031),
    "Creyke Beck": (-0.4154484881061148,53.8005040149857),
    "Thornton": (-0.8479640000000001,53.8987390000000),
    "Drax": (-0.9968258156419276,53.7366118702590),
    "Eggsborough": (-1.127134887878601,53.7120631007537),
    "Thorpe Marsh": (-1.087041587989168,53.578547484096),
    "Brinsworth": (-1.351971793113087,53.4013477809212),
    "Stocksbridge": (-1.585843,53.48021),
    "Monk Fryston": (-1.266460874903959,53.7561415622095),
    "Osbaldwick": (-1.023464695761978,53.9566381755846),
    "Norton": (-1.364392917288791,54.5925123172160),
    "Lackenby": (-1.131592177533348,54.5667677394419),

    "Unknown": (0.0,0.0)
}

for l in spt_400:
    km = geolocator.gislib.getDistance(l.from_bus.position, l.to_bus.position)
    l._length = km

for l in ngt_400:
    from_pos = ngt400_positions[l.from_bus.name]
    to_pos = ngt400_positions[l.to_bus.name]
    km = geolocator.gislib.getDistance(from_pos, to_pos)
#    print "km", km
    l._length = km

# Power stations in the United Kingdom (>100MW).
gbus = {
#    "Kilroot": (ireland, 275.0),
#    "Baglan Bay": (balgan_bay, 275.0),
    "Barking": (barking, 400.0),
    "Dungeness B": (dugeness, 400.0),
#    "Hartlepool" (hartlepool, 275.0),
    "Heysham1": (heysham, 400.0),
    "Heysham2": (heysham, 400.0),
    "Hinkley Point B": (hinkley_point, 400.0),
    "Sizewell B": (sizewell, 400.0),
    "Hunterston B": (hunterston, 400.0),
    "Torness": (torness, 400.0),
    "Eggborough": (eggsborough, 400.0),
#    "Barry": (cardiff_east,tremorfa,, 275.0),
    "Glanford Brigg": (keadby, 400.0),
    "Killingholme": (killingholme, 400.0),
    "Kings Lynn": (walpole, 400.0),
#    "Peterborough": (None, 132.0),
#    "Roosecote": (None, 132.0),
    "South Humber Bank": (south_humber_bank, 400.0),
#    "Coolkeeragh": (derry, 275.0),
    "Corby": (grendon, 400.0),
    "Coryton": (coryton, 400.0),
#    "Derwent": (derby, 132.0),
    "Drax": (drax, 400.0),
    "Sutton Bridge": (walpole, 400.0),
    "Cottam": (cottam, 400.0),
    "West Burton": (west_burton, 400.0),
    "Kingsnorth": (kingsnorth, 400.0),
    "Ironbridge": (ironbridge, 400.0),
    "Ratcliffe": (ratcliffe_on_soar, 400.0),
    "Grain": (grain_1, 400.0),
#    "Taylor's Lane GT": (willesden, 275.0),
    "Connahs Quay": (deeside, 400.0),
    "Cottam Development Centre": (cottam, 400.0),
#    "Enfield": (waltham_cross, 400.0),
    "Killingholme": (killingholme, 400.0),
    "Shotton": ()
}

#sutton_bridge = pylon.Generator(None, name="Sutton Bridge", p_max=803.00)
#cottam = pylon.Generator(None, name="Cottam", p_max=2008.00)
#west_burton = pylon.Generator(None, name="West Burton", p_max=2012.00)
#kingsnorth = pylon.Generator(None, name="Kingsnorth", p_max=1940.00)
#ironbridge = pylon.Generator(None, name="Ironbridge", p_max=970.00)
#ratcliffe = pylon.Generator(None, name="Ratcliffe", p_max=2000.00)
#grain_ = pylon.Generator(None, name="Grain ", p_max=1300.00)
#taylors_lane_gt = pylon.Generator(None, name="Taylor's Lane GT", p_max=132.00)
#connahs_quay = pylon.Generator(None, name="Connahs Quay", p_max=1380.00)
#cottam_development_centre = pylon.Generator(None, name="Cottam Development Centre", p_max=400.00)
#enfield = pylon.Generator(None, name="Enfield", p_max=392.00)
#killingholme = pylon.Generator(None, name="Killingholme", p_max=900.00)
#shotton = pylon.Generator(None, name="Shotton", p_max=180.00)
#teesside_power_station = pylon.Generator(None, name="Teesside Power Station", p_max=1875.00)
#immingham_chp = pylon.Generator(None, name="Immingham CHP", p_max=1240.00)
#indian_queens = pylon.Generator(None, name="Indian Queens", p_max=140.00)
#dinorwig = pylon.Generator(None, name="Dinorwig", p_max=1728.00)
#ffestiniog = pylon.Generator(None, name="Ffestiniog", p_max=360.00)
#rugeley_ = pylon.Generator(None, name="Rugeley ", p_max=1006.00)
#deeside_ = pylon.Generator(None, name="Deeside ", p_max=500.00)
#saltend_ = pylon.Generator(None, name="Saltend ", p_max=1200.00)
#oldbury = pylon.Generator(None, name="Oldbury", p_max=434.00)
#wylfa = pylon.Generator(None, name="Wylfa", p_max=980.00)
#fellside_chp = pylon.Generator(None, name="Fellside CHP", p_max=180.00)
#ballylumford_b = pylon.Generator(None, name="Ballylumford B", p_max=540.00)
#ballylumford_c = pylon.Generator(None, name="Ballylumford C", p_max=616.00)
#rocksavage = pylon.Generator(None, name="Rocksavage", p_max=748.00)
#aberthaw_b = pylon.Generator(None, name="Aberthaw B", p_max=1586.00)
#tilbury_b_ = pylon.Generator(None, name="Tilbury B ", p_max=1063.00)
#didcot_a = pylon.Generator(None, name="Didcot A", p_max=1958.00)
#cowes_ = pylon.Generator(None, name="Cowes ", p_max=140.00)
#didcot_gt = pylon.Generator(None, name="Didcot GT", p_max=100.00)
#littlebrook_gt = pylon.Generator(None, name="Littlebrook GT", p_max=105.00)
#fawley_ = pylon.Generator(None, name="Fawley ", p_max=968.00)
#littlebrook_d_ = pylon.Generator(None, name="Littlebrook D ", p_max=1370.00)
#didcot_b = pylon.Generator(None, name="Didcot B", p_max=1390.00)
#great_yarmouth = pylon.Generator(None, name="Great Yarmouth", p_max=420.00)
#little_barford = pylon.Generator(None, name="Little Barford", p_max=665.00)
#foyers = pylon.Generator(None, name="Foyers", p_max=300.00)
#glendoe = pylon.Generator(None, name="Glendoe", p_max=100.00)
#sloy = pylon.Generator(None, name="Sloy", p_max=152.50)
#hadyard_hill = pylon.Generator(None, name="Hadyard Hill", p_max=120.00)
#peterhead = pylon.Generator(None, name="Peterhead", p_max=1540.00)
#fife_power_station = pylon.Generator(None, name="Fife Power Station", p_max=123.00)
#keadby = pylon.Generator(None, name="Keadby", p_max=749.00)
#medway = pylon.Generator(None, name="Medway", p_max=688.00)
#ferrybridge_c = pylon.Generator(None, name="Ferrybridge C", p_max=1960.00)
#fiddlers_ferry = pylon.Generator(None, name="Fiddler's Ferry", p_max=1980.00)
#cruachan = pylon.Generator(None, name="Cruachan", p_max=440.00)
#cockenzie = pylon.Generator(None, name="Cockenzie", p_max=1152.00)
#longannet = pylon.Generator(None, name="Longannet", p_max=2304.00)
#damhead_creek = pylon.Generator(None, name="Damhead Creek", p_max=800.00)
#rye_house = pylon.Generator(None, name="Rye House", p_max=715.00)
#shoreham = pylon.Generator(None, name="Shoreham", p_max=400.00)
#black_law = pylon.Generator(None, name="Black Law", p_max=124.00)
#seabank_1 = pylon.Generator(None, name="Seabank 1", p_max=812.00)
#seabank_2 = pylon.Generator(None, name="Seabank 2", p_max=410.00)
#spalding = pylon.Generator(None, name="Spalding", p_max=860.00)
#uskmouth = pylon.Generator(None, name="Uskmouth", p_max=363.00)