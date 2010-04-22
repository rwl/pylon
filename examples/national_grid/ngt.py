__author__ = 'Richard Lincoln, r.w.lincoln@gmail.com'

import os
import sys
import math
import csv
import logging
import pylon

logger = logging.getLogger()

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

DATA_DIR = "./data/"

BUS_DATA = [os.path.join(DATA_DIR, "spt_substations.csv"),
            os.path.join(DATA_DIR, "shetl_substations.csv"),
            os.path.join(DATA_DIR, "nget_substations.csv")
            ]

LOAD_DATA = [os.path.join(DATA_DIR, "demand_generation_pf-2009_10wp.csv"),
             os.path.join(DATA_DIR, "demand_generation_pf-2009_10sop.csv")]

SHUNT_DATA = [os.path.join(DATA_DIR, "spt_shunt_data.csv"),
              os.path.join(DATA_DIR, "shetl_shunt_data.csv"),
              os.path.join(DATA_DIR, "nget_shunt_data.csv")
              ]

BRANCH_DATA = [
               os.path.join(DATA_DIR, "spt_circuit_param.csv"),
               os.path.join(DATA_DIR, "shetl_circuit_param.csv"),
               os.path.join(DATA_DIR, "nget_circuit_param.csv")
               ]

TRANSFORMER_DATA = [os.path.join(DATA_DIR, "spt_transformer_details.csv"),
                    os.path.join(DATA_DIR, "shetl_transformer_details.csv"),
                    os.path.join(DATA_DIR, "nget_transformer_details.csv")
                    ]

GENERATOR_DATA = [os.path.join(DATA_DIR, "generator_unit_data.csv")]

def get_bus_map(path, bus_map=None, voltage=400):
    bus_map = {} if bus_map is None else bus_map

    bus_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = bus_reader.next() # skip first row
    for row in bus_reader:
        assert int(row[2]) in [400, 275, 132, 66, 33, 11]

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


def add_loads(path, bus_map, voltage=400, others=None):
    others = [] if others is None else others

    load_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = load_reader.next() # skip first row

    for row in load_reader:
        pf = float(row[2])
        Sd = float(row[3])
#        dg = float(row[5])
        node_id = row[6]

        if len(node_id):
            if node_id[4] == str(voltage)[0]:
                if bus_map.has_key(node_id[:4]):
                    node = bus_map[node_id[:4]]
                else:
                    print "Load bus not found.", node_id[:4], node_id, voltage
                    found = [oth[node_id[:4]].v_base for oth in others if oth.has_key(node_id[:4])]
                    if found:
                        print "Load bus %s found at: %s" % (node_id[:4], found)
                    continue

                Pd = Sd * pf
                Qd = math.sqrt(Sd**2 - Pd**2)
                node.p_demand += Pd
                node.q_demand += Qd

    return bus_map


def add_shunts(path, bus_map, voltage=400):
    shunt_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = shunt_reader.next() # skip first row

    for row in shunt_reader:
        if row[6] == "Tertiary Connected":
            continue

#        print row[0], row[1][4], row[6][0]
        if len(row[6]):
            if row[1][4] != row[6][0]:
                print "Shunt-bus voltage mismatch:", row[1][4], row[6]
#        else:
#            print "No voltage entry for shunt.", row[0], row[1][4]

        if row[1][4] == str(voltage)[0]:
            try:
                node = bus_map[row[1][:4]]
            except KeyError:
                if len(row[6]):
                    if row[1][4] != row[6][0]:
                        print "Shunt bus not found: %s %s" % (row[1][:4], row[6])
                continue

#            print "Shunt:", node.name, row[6], row[3], row[4]

            if len(row[3]):
                node.b_shunt += float(row[3])
            elif len(row[4]):
                node.b_shunt -= float(row[4])
            else:
                raise

    return bus_map


def get_branches(path, bus_map, voltage=400, others=None, season="winter"):
    others = [] if others is None else others

    branch_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = branch_reader.next() # skip first row
    branches = []
    for row in branch_reader:
    #    print ", ".join(row)
        n1_id = row[0]
        n2_id = row[1]

        # Ignore branches of other voltages (according to 5th digit).
        if row[0][4] != str(voltage)[0]:
#            print "skipping:", row[0][4], str(voltage)[0] + ", ".join(row)
            continue
#        else:
#            print "branching: " + ", ".join(row)

        try:
            node1 = bus_map[n1_id[:4]]
        except KeyError:
            print "Bus 1 not found: %s (%s--%s) %d" % (row[0][:4], row[0], row[1], voltage)
            found = [oth[n1_id[:4]].v_base for oth in others if oth.has_key(n1_id[:4])]
            if found:
                print "Bus %s found at: %s" % (n1_id[:4], found)
            continue

        try:
            node2 = bus_map[n2_id[:4]]
        except KeyError:
            print "Bus 2 not found: %s (%s--%s) %d" % (n2_id[:4], row[0], row[1], voltage)
            found = [oth[n2_id[:4]].v_base for oth in others if oth.has_key(n2_id[:4])]
            if found:
                print "Bus %s found at: %s" % (n2_id[:4], found)
            continue

        r = float(row[5]) / 100.0
        x = float(row[6]) / 100.0
        b = float(row[7]) / 100.0

        if season == "winter":
            rate_a = float(row[8])
        elif season == "autumn":
            rate_a = float(row[9])
        elif season == "summer":
            rate_a = float(row[10])
        elif season == "spring":
            rate_a = float(row[11])
        else:
            raise

        l = pylon.Branch(node1, node2, r=r, x=x, b=b, rate_a=rate_a)
        branches.append(l)

    return branches


def get_transformers(path, voltage_map, others=None):
    others = [] if others is None else others

    branch_reader = csv.reader(open(path), delimiter=',', quotechar='"')

    _ = branch_reader.next() # skip first row
    branches = []
    for row in branch_reader:
#        print ", ".join(row)
        node1_id = row[0]
        node2_id = row[1]

        if voltage_map.has_key(node1_id[4]):
            bus_map1 = voltage_map[node1_id[4]]
        else:
#            print "Skipping TRX at:", node1_id[4]
            continue

        if voltage_map.has_key(node2_id[4]):
            bus_map2 = voltage_map[node2_id[4]]
        else:
#            print "Skipping TRX at:", node2_id[4]
            continue

        if bus_map1.has_key(node1_id[:4]):
            node1 = bus_map1[node1_id[:4]]
        else:
            print "Trx bus 1 not found: %s (%s--%s)" % (node1_id[:5], node1_id, node2_id)
            found = [oth[node1_id[:4]].v_base for oth in others if oth.has_key(node1_id[:4])]
            if found:
                print "Trx bus %s found at: %s" % (node1_id[:4], found)
            continue

        if bus_map2.has_key(node2_id[:4]):
            node2 = bus_map2[node2_id[:4]]
        else:
            print "Trx bus 2 not found: %s (%s--%s)" % (node2_id[:5], node1_id, node2_id)
            found = [oth[node2_id[:4]].v_base for oth in others if oth.has_key(node2_id[:4])]
            if found:
                print "Trx bus %s found at: %s" % (node2_id[:4], found)
            continue

        print "Transformer:", node1.name, node1.v_base, node2.v_base

        r = float(row[2]) / 100.0
        x = float(row[3]) / 100.0
        b = float(row[4]) / 100.0
        rate_a = float(row[5])

        l = pylon.Branch(node1, node2, name=node1.name, r=r, x=x, b=b, ratio=1.0, rate_a=rate_a)
        branches.append(l)

    return branches


def get_generators(path, bus_map, voltage=400, licensee="SPT", aggregate=False, others=None):
    others = [] if others is None else others

    generator_reader = csv.reader(open(path),
                                  delimiter=',', quotechar='"')

    _ = generator_reader.next() # skip first row
    generators = []
    gen_map = {}
    for row in generator_reader:

        if not len(row[9]) >= 4:
#            print "No Bus: " + ", ".join(row)
            continue

        if row[9][4] == str(voltage)[0] and row[11] == licensee:
            node_id = row[9]

            try:
                node = bus_map[node_id[:4]]
            except KeyError:
                print "Generator bus not found: %s %s %d" % (node_id[:5], row[4], voltage)
                found = [oth[node_id[:4]].v_base for oth in others if oth.has_key(node_id[:4])]
                if found:
                    print "Gen bus %s found at: %s" % (node_id[:4], found)
                continue

            name = row[0] if not len(row[1]) else "%s-%s" % (row[0], row[1])

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

            if gen_map.has_key(row[9][:5]):
                g = gen_map[node_id[:5]]
                g.p_min += p_min
                g.p_max += p_max
                g.q_min += q_min
                g.q_max += q_max
            else:
                node.type = pylon.PV

                g = pylon.Generator(node, name,
                                    p_min=p_min, p_max=p_max,
                                    q_min=q_min, q_max=q_max)

                print "Generator:", name, node.name, p_max

                if aggregate:
                    gen_map[node_id[:5]] = g

            g._company = row[2]
            g._fuel = row[3]

            generators.append(g)

    if aggregate:
        return gen_map.values()
    else:
        return generators

def main():
    bus_map400 = {}
    for path in BUS_DATA:
        bus_map400 = get_bus_map(path, bus_map400, 400)

    bus_map275 = {}
    for path in BUS_DATA:
        bus_map275 = get_bus_map(path, bus_map275, 275)

    bus_map132 = {}
    for path in BUS_DATA:
        bus_map132 = get_bus_map(path, bus_map132, 132)

    bus_map66 = {}
    for path in BUS_DATA:
        bus_map66 = get_bus_map(path, bus_map66, 66)

    bus_map33 = {}
    for path in BUS_DATA:
        bus_map33 = get_bus_map(path, bus_map33, 33)

    bus_map11 = {}
    for path in BUS_DATA:
        bus_map11 = get_bus_map(path, bus_map11, 11)

    # Shunts.
    for path in SHUNT_DATA:
        add_shunts(path, bus_map400, voltage=400)

    for path in SHUNT_DATA:
        add_shunts(path, bus_map275, voltage=275)

    for path in SHUNT_DATA:
        add_shunts(path, bus_map132, voltage=132)

    for path in SHUNT_DATA:
        add_shunts(path, bus_map66, voltage=66)

    for path in SHUNT_DATA:
        add_shunts(path, bus_map33, voltage=33)

    for path in SHUNT_DATA:
        add_shunts(path, bus_map11, voltage=11)

    maps = [bus_map400, bus_map275, bus_map132, bus_map66, bus_map33, bus_map11]
    # Lines and cables.
    branches400 = []
    for path in BRANCH_DATA:
        branches400.extend(get_branches(path, bus_map400, 400, maps))

#    branches275 = []
#    for path in BRANCH_DATA:
#        branches275.extend(get_branches(path, bus_map275, 275, maps))
#
#    branches132 = []
#    for path in BRANCH_DATA:
#        branches132.extend(get_branches(path, bus_map132, 132, maps))

    # Transformers.
    transformers = []
    for path in TRANSFORMER_DATA:
        transformers.extend(
            get_transformers(path, {"4": bus_map400,
                                    "2": bus_map275,
#                                    "1": bus_map132
                                    }, maps))

    # Generators.
    aggregate = False
    generators = []
    for path in GENERATOR_DATA:
        generators.extend(get_generators(path, bus_map400, voltage=400, licensee="SPT", aggregate=aggregate, others=maps))
        generators.extend(get_generators(path, bus_map400, voltage=400, licensee="SHETL", aggregate=aggregate, others=maps))
        generators.extend(get_generators(path, bus_map400, voltage=400, licensee="NGET", aggregate=aggregate, others=maps))

#        generators.extend(get_generators(path, bus_map275, voltage=275, licensee="SPT", others=maps))
#        generators.extend(get_generators(path, bus_map275, voltage=275, licensee="SHETL", others=maps))
#        generators.extend(get_generators(path, bus_map275, voltage=275, licensee="NGET", others=maps))
#
#        generators.extend(get_generators(path, bus_map132, voltage=132, licensee="SPT", others=maps))
#        generators.extend(get_generators(path, bus_map132, voltage=132, licensee="SHETL", others=maps))
#        generators.extend(get_generators(path, bus_map132, voltage=132, licensee="NGET", others=maps))
#
#        generators.extend(get_generators(path, bus_map66, voltage=66, licensee="SPT", others=maps))
#        generators.extend(get_generators(path, bus_map66, voltage=66, licensee="SHETL", others=maps))
#        generators.extend(get_generators(path, bus_map66, voltage=66, licensee="NGET", others=maps))
#
#        generators.extend(get_generators(path, bus_map33, voltage=33, licensee="SPT", others=maps))
#        generators.extend(get_generators(path, bus_map33, voltage=33, licensee="SHETL", others=maps))
#        generators.extend(get_generators(path, bus_map33, voltage=33, licensee="NGET", others=maps))
#
#        # Assume "5" used in substation code to indicate 11kV.
#        generators.extend(get_generators(path, bus_map11, voltage=511, licensee="SPT", others=maps))
#        generators.extend(get_generators(path, bus_map11, voltage=511, licensee="SHETL", others=maps))
#        generators.extend(get_generators(path, bus_map11, voltage=511, licensee="NGET", others=maps))

    buses = bus_map400.values() + \
            bus_map275.values() + \
            bus_map132.values() + \
            bus_map66.values() + \
            bus_map33.values() + \
            bus_map11.values()

    branches = transformers + \
               branches400# + \
#               branches275 + \
#               branches132 + \

    print len(buses), len(branches), len(generators)

    for path in LOAD_DATA:
        add_loads(path, bus_map400, 400, maps)
#        add_loads(path, bus_map275, 275, maps)
#        add_loads(path, bus_map132, 132, maps)
#        add_loads(path, bus_map66, 66, maps)
#        add_loads(path, bus_map33, 33, maps)
#        add_loads(path, bus_map11, 11, maps)

        case = pylon.Case(buses=buses, branches=branches, generators=generators)
        case.index_buses(start=1)

        root, _ = os.path.splitext(os.path.basename(path))
        ident = root.split("-")[-1]
        case.name = "NGET-%s" % ident

#        case.save_matpower("/tmp/ngt-%s.m" % ident)
        case.save_psse("/tmp/ngt-%s.raw" % ident)


if __name__ == '__main__':
    main()
