'''
Created on 13 Mar 2009

@author: rwl
'''
import unittest

from iec61970.core import Terminal

from iec61970.loadmodel \
    import Load, ConformLoadGroup, ConformLoadSchedule, SubLoadArea, LoadArea


class Test(unittest.TestCase):


    def test_load_model(self):
        """ Test instantiation of load model classes.
        """
        load_area = LoadArea(sub_load_areas)

        sub_load_area = SubLoadArea(load_area, load_groups)

        load_schedule = ConformLoadSchedule(conform_load_group)

        load_group = ConformLoadGroup(conform_load_schedules, sub_load_area)


        load = Load(name="Load 1")
        t1 = Terminal(conducting_equipment=load)
        load.Terminals = [t1]

        load.configure_traits()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_model']
    unittest.main()