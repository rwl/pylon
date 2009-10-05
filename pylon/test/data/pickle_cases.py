#!/usr/bin/python

import sys
import os.path
import logging

from pylon.readwrite import MATPOWERReader, PickleWriter

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
    format="%(levelname)s: %(message)s")

CASE_FILE_NAMES = ['case30pwl.m', 'case6pwl.m', 'case6ww.m']

def pickle_cases():
    """ Parses the MATPOWER case files used for testing and pickles the
        resulting Case objects.
    """
    data_path = os.path.dirname(__file__)

    for case_file_name in CASE_FILE_NAMES:
        # Read the MATPOWER case file.
        case_file_path = os.path.join(data_path, case_file_name)
        case = MATPOWERReader().read(case_file_path)

        # Pickle the resulting Pylon Case object.
        root, extension = os.path.splitext(case_file_name)
        pickled_case_path = os.path.join(data_path, root + '.pkl')
        PickleWriter().write(case, pickled_case_path)

if __name__ == '__main__':
    pickle_cases()
