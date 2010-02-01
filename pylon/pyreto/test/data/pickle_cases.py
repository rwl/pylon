#!/usr/bin/python

import sys
import logging

from pylon.util import pickle_matpower_cases

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
    format="%(levelname)s: %(message)s")

if __name__ == '__main__':
    pickle_matpower_cases('t_auction_case.m', case_format=1)
