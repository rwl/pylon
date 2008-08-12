#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

"""
For storing integer approwimations of  Q(s,a)

The paper defining the algorithm:

http://asl.epfl.ch/aslInternalWeb/ASL/publications/uploadedFiles/
compactQlearning_for%20print%20version.pdf

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import Dict, Int, Instance

# Local imports:
from action_state_pair import ActionStatePair

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RewardMemorizerInteger" class:
#------------------------------------------------------------------------------

class RewardMemorizerInteger(HasTraits):
    """
    For storing integer approwimations of  Q(s,a)
    
    The paper defining the algorithm:
    
    http://asl.epfl.ch/aslInternalWeb/ASL/publications/uploadedFiles/
    compactQlearning_for%20print%20version.pdf

    """
    
    serial_version_uid = Long
    
    generator = Instance(Random)
    
    histogram = [int() for idx in range(1000)]
    
    max_value = Int(0)
    
    number = Int(0)


    def get(self, s, a):
        """
        Get a value from the state and action
        
        """
        
        us = ActionStatePair(a, s)
        db = self[us]
        if db is None:
            u = self.generator.next_int(10)
            self.put(ActionStatePair(a, s), Integer(u))
            if u > self.max_value:
                self.max_value = u
            self.number += 1
            return u
        return db.int_value()


    def put(self, s, a, sp, qsa):
        """
        Store Q(s,a)
        
        """
        
        if sp is not None:
            if self.put(ActionStatePair(a, s), Integer(qsa)) is None:
                self.number += 1
        else:
            self.put(ActionStatePair(a, s), Integer(qsa))


    def to_string(self):
        s = self.number + " couples Etat/action\nAffichage de tous les Q(s,a)\n"
        prov = {}
        keys = self.keySet()
        enu = keys.iterator()
        while enu.hasNext():
            courante = enu.next()
            s += (courante.getState() + " " + courante.getAction() + " " +  
                (courante.getState(), courante.getAction()) + "\n")
            bestAct = prov[courante.getState()]
            if bestAct is None:
                prov.put(courante.getState(), courante.getAction())
            else:
                if self[courante.getState(), courante.getAction()] > self[courante.getState(), bestAct]:
                    prov.put(courante.getState(), courante.getAction())
        bk = prov.keySet()
        ebis = bk.iterator()
        s += "Affichage des meilleurs actions selon l'�tat\n"
        while ebis.hasNext():
            s1 = ebis.next()
            best = prov[s1]
            s += s1 + "---->" + best + " : " + self[s1, best] + "\n"
        return s


    def divide(self, factor):
        """
        qsa=qsa/factor
        
        """
        
        keys = self.keySet()
        enu = keys.iterator()
        while enu.hasNext():
            courante = enu.next()
            value = self[courante].intValue()
            self.put(courante, Integer(value / factor))


    def get_max_value(self):
        keys = self.keySet()
        enu = keys.iterator()
        value = 0
        while enu.hasNext():
            courante = enu.next()
            value = self[courante].intValue()
            if value > self.maxValue:
                self.maxValue = value
        return self.maxValue


    def normalize(self):
        self.getMaxValue()
        keys = self.keySet()
        enu = keys.iterator()
        while enu.hasNext():
            courante = enu.next()
            value = self[courante].intValue()
            rapport = value / self.maxValue + 0.0 * 1000
            super.put(courante, Integer(rapport))
        self.maxValue = 1000


    def make_histogram(self):
        self.histogramme = [int() for __idx0 in range(1000)]
        keys = self.keySet()
        enu = keys.iterator()
        self.maxValue = 0
        count = 0
        while enu.hasNext():
            value = self[enu.next()].intValue()
            if value > self.maxValue:
                self.maxValue = value
            print count + " xx " + value
            count += 1
        enu = keys.iterator()
        while enu.hasNext():
            value = self[enu.next()].intValue()
            self.histogramme[999 * value / self.maxValue] += 1


    def display_histogram(self):
        ## for-while
        i = 0
        while i < 1000:
            print i + " " + self.histogramme[i]
            i += 1

# EOF -------------------------------------------------------------------------
