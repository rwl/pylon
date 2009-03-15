'''
Created on 13 Mar 2009

@author: rwl
'''
import unittest

from CIM13.Core import Terminal, RegularTimePoint

from CIM13.LoadModel \
    import Load, ConformLoadGroup, ConformLoadSchedule, SubLoadArea, LoadArea

from CIM13.Generation.Production \
    import GeneratingUnit, GenUnitOpCostCurve, GenUnitOpSchedule


class Test(unittest.TestCase):


    def test_load_model(self):
        """ Test instantiation of load model classes.
        """
#        load_area = LoadArea()
#
#        sub_load_area = SubLoadArea(load_area=load_area)
#        load_area.SubLoadAreas.append(sub_load_area)

        conform_load_group = ConformLoadGroup()#sub_load_area)

        schedule = ConformLoadSchedule(conform_load_group)

        # Add a time point to the load schedule.
        tp1 = RegularTimePoint(interval_schedule=schedule)
        schedule.TimePoints.append(tp1)

        # Add the schedule to the load group's list of load schedules.
        conform_load_group.ConformLoadSchedules.append(schedule)

        load = Load(name="Load 1", LoadGroup=conform_load_group)

        # Add the load to the load group's list of energy consumers.
        conform_load_group.EnergyConsumers.append(load)

#        load.configure_traits()


    def test_generation(self):
        """ Test creation of generation.
        """
        curve = GenUnitOpCostCurve()
        schedule = GenUnitOpSchedule()
        unit = GeneratingUnit(GenUnitOpCostCurves=[curve],
                              GenUnitOpSchedule=schedule)
        unit.configure_traits()

        print unit.name


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_model']
    unittest.main()