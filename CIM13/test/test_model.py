'''
Created on 13 Mar 2009

@author: rwl
'''
import unittest

from CIM13 import Model

from CIM13.Core import Terminal, RegularTimePoint

from CIM13.LoadModel \
    import Load, ConformLoadGroup, ConformLoadSchedule, SubLoadArea, LoadArea

from CIM13.Generation.Production \
    import GeneratingUnit, GenUnitOpCostCurve, GenUnitOpSchedule

from CIM13.Topology \
    import ConnectivityNode

from CIM13.Wires \
    import SynchronousMachine, ReactiveCapabilityCurve


class ModelTest(unittest.TestCase):
    """ Defines a test case for the Common Information Model.
    """

    def test_create_elements(self):
        """ Test creation of model elements.
        """
        model = Model()

        terminal   = Terminal()
        time_point = RegularTimePoint()

        node = ConnectivityNode()

        load          = Load()
        load_group    = ConformLoadGroup()
        load_schedule = ConformLoadSchedule()
        load_area     = LoadArea()
        sub_load_area = SubLoadArea()

        gen_unit     = GeneratingUnit()
        cost_curve   = GenUnitOpCostCurve()
        gen_schedule = GenUnitOpSchedule()

        machine = SynchronousMachine()
        curve = ReactiveCapabilityCurve()


    def test_one_to_one(self):
        """ Test handling of one-to-one associations.
        """
        schedule = GenUnitOpSchedule()
        unit = GeneratingUnit(GenUnitOpSchedule=schedule)

        self.assertEqual(schedule.GeneratingUnit, unit)


    def test_one_to_many(self):
        """ Test handling on one-to-many associations.
        """
        load_group = ConformLoadGroup()
        load = Load(LoadGroup=load_group)

        self.assertTrue(load in load_group.EnergyConsumers)


    def test_many_to_one(self):
        """ Test handling of many-to-one associations.
        """
        model = Model()
        element = ConnectivityNode()
        model.Contains.append(element)

        self.assertEqual(element.ContainedBy, model)


#    def test_many_to_many(self):
#        """ Test handling of many-to-many associations.
#        """
#        curve = ReactiveCapabilityCurve()
#        machine = SynchronousMachine()#ReactiveCapabilityCurves=[curve])

#        self.assertTrue(machine in curve.SynchronousMachines)

#        machine2 = SynchronousMachine()
#        machine2.ReactiveCapabilityCurves.append(curve)

#        self.assertTrue(machine2 in curve.SynchronousMachines)


#    def test_load_model(self):
#        """ Test creation of a load.
#        """
##        load_area = LoadArea()
##
##        sub_load_area = SubLoadArea(load_area=load_area)
##        load_area.SubLoadAreas.append(sub_load_area)
#
#        conform_load_group = ConformLoadGroup()#sub_load_area)
#
#        schedule = ConformLoadSchedule(conform_load_group)
#
#        # Add a time point to the load schedule.
#        tp1 = RegularTimePoint(interval_schedule=schedule)
#        schedule.TimePoints.append(tp1)
#
#        # Add the schedule to the load group's list of load schedules.
#        conform_load_group.ConformLoadSchedules.append(schedule)
#
#        load = Load(name="Load 1", LoadGroup=conform_load_group)
#
#        # Add the load to the load group's list of energy consumers.
#        conform_load_group.EnergyConsumers.append(load)
#
##        load.configure_traits()


#    def test_generation(self):
#        """ Test creation of generation.
#        """
#        curve = GenUnitOpCostCurve()
#        schedule = GenUnitOpSchedule()
#        unit = GeneratingUnit(GenUnitOpCostCurves=[curve],
#                              GenUnitOpSchedule=schedule)
#        unit.configure_traits()
#
#        print unit.name


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_model']
    unittest.main()