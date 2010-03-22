import pylon

import csv

BUS_DATA = ["data/spt_substations.csv",
#            "data/shetl_substations.csv",
#            "data/nget_substations.csv"
            ]

BRANCH_DATA = [
               "data/spt_circuit_param.csv",
#               "data/shetl_circuit_param.csv",
#               "data/nget_circuit_param.csv"
               ]

TRANSFORMER_DATA = ["data/spt_transformer_details.csv",
#                    "data/shetl_transformer_details.csv",
#                    "data/nget_transformer_details.csv"
                    ]

SHUNT_DATA = ["data/spt_shunt_data.csv",
#              "data/shetl_shunt_data.csv",
#              "data/nget_shunt_data.csv"
              ]

def get_bus_map(path, bus_map=None, voltage=400):
    bus_map = {} if bus_map is None else bus_map

    bus_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = bus_reader.next() # skip first row
    for row in bus_reader:
        assert int(row[2]) in [400, 275, 132, 33]

        if row[2] == str(voltage):
            name = row[1]
            assert len(name) == 4

            b = pylon.Bus(name, v_base=float(row[2]), b_shunt=float(row[5]))
            b._long_name = row[0]

            if not bus_map.has_key(name):
                bus_map[name] = b
            else:
                if int(bus_map[name].v_base) != int(voltage):
                    print "Duplicate bus:", name, bus_map[name].v_base, voltage
#                else:
#                    print "Duplicate bus (equal voltage):", name

    return bus_map


bus_map400 = {}
for path in BUS_DATA:
    bus_map400 = get_bus_map(path, bus_map400, 400)

bus_map275 = {}
for path in BUS_DATA:
    bus_map275 = get_bus_map(path, bus_map275, 275)

bus_map132 = {}
for path in BUS_DATA:
    bus_map132 = get_bus_map(path, bus_map132, 132)

bus_map33 = {}
for path in BUS_DATA:
    bus_map33 = get_bus_map(path, bus_map33, 033)


def add_shunts(path, bus_map, voltage=400):
    shunt_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = shunt_reader.next() # skip first row

    for row in shunt_reader:
        if row[6] == str(voltage):
            try:
                node = bus_map[row[1][:4]]
            except KeyError:
                print "Shunt bus not found: %s %s" % (row[1][:4], row[6])
                continue

            name = row[1] if not len(row[2]) else "%s-%s" % (row[1], row[2])

            print "Shunt:", name, node.name, row[3], row[4]

            if len(row[3]):
                node.b_shunt = float(row[3])
            elif len(row[4]):
                node.b_shunt = -1 * float(row[4])
            else:
                raise

    return bus_map

for path in SHUNT_DATA:
    add_shunts(path, bus_map400, voltage=400)

#for path in SHUNT_DATA:
#    add_shunts(path, bus_map275, voltage=275)
#
#for path in SHUNT_DATA:
#    add_shunts(path, bus_map132, voltage=132)
#
#for path in SHUNT_DATA:
#    add_shunts(path, bus_map33, voltage=33)


def get_branches(path, bus_map, voltage=400):

    branch_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = branch_reader.next() # skip first row
    branches = []
    for row in branch_reader:
    #    print ", ".join(row)

        # Ignore branches of other voltages (according to 5th digit).
        if row[0][4] != str(voltage)[0]:
#            print "skipping:", row[0][4], str(voltage)[0] + ", ".join(row)
            continue
#        else:
#            print "branching: " + ", ".join(row)

        try:
            node1 = bus_map[row[0][:4]]
        except KeyError:
            print "Bus not found: %s" % row[0][:4]
            continue

        try:
            node2 = bus_map[row[1][:4]]
        except KeyError:
            print "Bus not found: %s" % row[1][:4]
            continue

        l = pylon.Branch(node1, node2,
                         r=float(row[5]), x=float(row[6]), b=float(row[7]),
                         rate_a=float(row[8]), rate_b=float(row[9]),
                         rate_c=float(row[10]))
        branches.append(l)

    return branches


branches400 = []
for path in BRANCH_DATA:
    branches400.extend(get_branches(path, bus_map400, 400))

branches275 = []
for path in BRANCH_DATA:
    branches275.extend(get_branches(path, bus_map275, 275))

branches132 = []
for path in BRANCH_DATA:
    branches132.extend(get_branches(path, bus_map132, 132))



def get_transformers(path, bus_map1, bus_map2, voltages=(400,275)):

    branch_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = branch_reader.next() # skip first row
    branches = []
    for row in branch_reader:

        s = [str(voltage)[0] for voltage in voltages]

        if row[0][4] not in s or row[1][4] not in s:
#            print "Skipping: " + ", ".join(row)
            continue
#        else:
#            print "transforming: " + ", ".join(row)

        if row[0][4] == str(voltages[0])[0]:
            bus_map = bus_map1
        elif row[0][4] == str(voltages[1])[0]:
            bus_map = bus_map2
        else:
            raise

        try:
            node1 = bus_map[row[0][:4]]
        except KeyError:
            print "Bus not found: %s" % row[0][:4]
            continue

        if row[1][4] == str(voltages[0])[0]:
            bus_map = bus_map1
        elif row[1][4] == str(voltages[1])[0]:
            bus_map = bus_map2
        else:
            raise

        try:
            node2 = bus_map[row[1][:4]]
        except KeyError:
            print "Bus not found: %s" % row[1][:4]
            continue

        print "Transformer:", node1.name, node1.v_base, node2.v_base

        l = pylon.Branch(node1, node2, name=node1.name,
                         r=float(row[2]), x=float(row[3]), b=float(row[3]),
                         rate_a=float(row[5]))
        branches.append(l)

    return branches

transformers400 = []
for path in TRANSFORMER_DATA:
    transformers400.extend(
        get_transformers(path, bus_map400, bus_map275, (400, 275)))

#transformers275 = []
#for path in BRANCH_DATA:
#    transformers275.extend(get_transformers(path, bus_map275, 275))
#
#transformers132 = []
#for path in BRANCH_DATA:
#    transformers132.extend(get_transformers(path, bus_map132, 132))


def get_generators(path, bus_map, voltage=400, licensee="SPT"):
    generator_reader = csv.reader(open(path),
                                  delimiter=',', quotechar='"')

    _ = generator_reader.next() # skip first row
    generators = []
    for row in generator_reader:

        if not len(row[9]) >= 4:
#            print "No Bus: " + ", ".join(row)
            continue

        if row[9][4] == str(voltage)[0] and row[11] == licensee:

            try:
                node = bus_map[row[9][:4]]
            except KeyError:
                print "Generator bus not found: %s %s" % (row[9][:4], row[4])
                continue

            name = row[0] if not len(row[1]) else "%s-%s" % (row[0], row[1])

            print "Generator:", name, node.name

            if not len(row[4]):
                continue
            p_max = float(row[4])
            p_min = p_max * 0.25

            if not len(row[6]):
                q_min = -0.4 * p_max
            else:
                q_min = float(row[6])
            if not len(row[7]):
                q_max = 0.4 * p_max
            else:
                q_max = float(row[7])

            g = pylon.Generator(node, name, p_min=p_min, p_max=p_max, q_min=q_min, q_max=q_max)
            g._company = row[2]
            g._fuel = row[3]

            generators.append(g)

    return generators

generators = get_generators("data/generator_unit_data.csv",
                            bus_map400, voltage=400, licensee="SPT")

#print len(bus_map400), len(bus_map275), len(bus_map132), len(bus_map33)
#print len(branches400)#, len(branches275), len(branches132), len(branches33)
#len(branches)
print len(generators)
