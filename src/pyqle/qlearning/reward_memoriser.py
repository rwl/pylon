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
Memorising  Q(s,a) in Dict. The key is the pair (state, value).

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

from random import Random

# Enthought library imports
from enthought.traits.api import \
    Dict, Int, Instance, List, Property

# Pyqle imports:
from pyqle.dataset.dataset import Dataset

from pyqle.dataset.sample import Sample

# Local imports:
from abstract_reward_store import AbstractRewardStore

from abstract_value_chooser import AbstractValueChooser

from null_value_chooser import NullValueChooser

from action_state_pair import ActionStatePair

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RewardMemoriser" class:
#------------------------------------------------------------------------------

class RewardMemoriser(AbstractRewardStore):
    """
    Memorising  Q(s,a) in Dict. The key is the pair (state, value).

    """
    
    map = Dict
    
    generator = Instance(Random, Random())
    
    # Number of items stored
    n_items = Property(Int, depends_on=["map", "map_items"])
    
    histogram = List([int() for idx in range(1000)])
    
    numer = Int(0)
    
    order = Int(0)
    
    value_chooser = Instance(AbstractValueChooser, NullValueChooser())


    def __init__(self, value_chooser=None, **traits):
        if value_chooser is not None:
            self.value_chooser = value_chooser
            self.order = self.numer
            
            super(RewardMemoriser, self).__init__(value_chooser=value_chooser,
                order=self.numer, **traits)
            
            self.numer += 1
        else:
            super(RewardMemoriser, self).__init__(**traits)


    def _get_n_items(self):
        """
        Property getter
        
        """
        
        return len(self.map)


    def get(self, state, action):
        """
        Read Q(s,a)
        
        """
        
        if action is None or state is None:
            return 0
        
        us = ActionStatePair(action, state)
        
        if self.map.has_key(us):
            db = self.map[us]
        else:
            db = None
        
        if db is None:
            u = self.value_chooser.get_value()
            self.map[ActionStatePair(action, state)] = float(u)
            return u
        
        return float(db)


    def put(self, state, action, qsa, new_state=None):
        """
        Store Q(s,a) : change its value if already there.
        
        We sometimes need the new state (sp)...
        
        """
        
        if new_state is not None:
            # FIXME: Comparison with newly instantiated object!
            if not self.map.has_key(ActionStatePair(action, state)):
                self.map[ActionStatePair(action, state)] = float(qsa)
        else:
            self.map[ActionStatePair(action, state)] = float(qsa)


#    def make_histogram(self):
#        """
#        To monitor the evolution of Q(s,a) values.
#        
#        """
#        
#        keys = map.keySet()
#        enu = keys.iterator()
#        min = 10000.0
#        max = -10000.0
#        sum = 0.0
#        number = 0
#        while enu.hasNext():
#            courante = enu.next()
#            db = Double(self[courante.getState(), courante.getAction()])
#            d = db.doubleValue()
#            if d > max:
#                max = d
#            if d < min:
#                min = d
#            sum += d
#            number += 1
#        mean = sum / number
#        ecartType = 0.0
#        enu = keys.iterator()
#        while enu.hasNext():
#            courante = enu.next()
#            db = Double(self[courante.getState(), courante.getAction()])
#            d = db.doubleValue()
#            ecartType += d - mean * d - mean
#            self.histogram[Math.floor(999 * d - min / max - min)] += 1
#
#
#    def display_histogram(self):
#        ## for-while
#        i = 0
#        while i < 1000:
#            print i + " " + self.histogram[i]
#            i += 1


    def to_string(self):
        # State/Action pairs
        keys = self.map.keys()
        prov = {}
        s = len(keys) + " state/action pairs \nListing of ALL  Q(s,a)\n"
        for key in keys:
            best_act = prov[key.get_state()]
            if best_act is None:
                prov[key.get_state()] = key.get_action()
            else:
                if self.get(key.get_state(), key.get_action()) > \
                self.get(key.get_state(), best_act):
                    prov[key.get_state()] = key.get_action()
        bk = prov.keys()
        s += "Best values Q(s,a) for given s and a\n"
        for key in bk:
            best = prov[key]
            s += count + " : " + key + "---->" + best + " : " + self[key, best] + "\n"
        return s


    def extract_dataset(self):
        """
        Extracts dataset for use with local NN
        
        """
        
        for_nn = Dataset()
        keys = self.map.keys()
        for key in keys:
            state = key.get_state()
            action = key.get_action()
            prosize = action.nn_coding_size()
            u = [float() for idx in range(state.nn_coding_size() + prosize)]
            # FIXME: Copy array in Python
#            System.arraycopy(state.nn_coding(), 0, u, 0, state.nn_coding_size())
#            System.arraycopy(action.nn_coding(), 0, u, state.nn_coding_size(), prosize)
            v = [float() for idx in range(1)]
            v[0] = 1.0 + self.get(etat, act) / 2.0
            for_nn.add(Sample(u, v))
        return for_nn

# EOF -------------------------------------------------------------------------
