'''
Created on 13 Mar 2009

@author: rwl
'''
import unittest

from iec61970.Core import Terminal, RegularTimePoint

from iec61970.LoadModel \
    import Load, ConformLoadGroup, ConformLoadSchedule, SubLoadArea, LoadArea


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
        tp1 = RegularTimePoint(interval_schedule=schedule)
        schedule.TimePoints.append(tp1)

        conform_load_group.ConformLoadSchedules.append(schedule)


        load = Load(name="Load 1", LoadGroup=conform_load_group)

        load.configure_traits()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_model']
    unittest.main()