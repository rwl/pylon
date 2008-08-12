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
Samples are not memorised : each time a new experience is available, the
neural network is asked to train. The sample is then forgotten.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import Dict, Int, Instance

# Local imports:
from reward_memoriser_nn import RewardMemorizerNN

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RewardMemorizerNNSinglePass" class:
#------------------------------------------------------------------------------

class RewardMemorizerNNSinglePass(RewardMemorizerNN):
    """
    Samples are not memorised : each time a new experience is available, the
    neural network is asked to train. The sample is then forgotten.

    """

    def __init__(self, dvc=None, **traits):
        if dvc is None:
            dvc = NullValueChooser()
        self.value_chooser = dvc
        self.rescale = True
        
        super(RewardMemorizerNNSinglePass, self).__init__(value_chooser=dvc,
            rescale=True, **traits)


    def put(self, s, a, sp, qsa):
        prosize = a.nn_coding_size()
        if memory is None:
            archi = [int() for __idx0 in range(3)]
            archi[0] = s.nn_coding_size() + prosize
            archi[1] = 1 + archi[0] / 5
            archi[2] = 1
            memory = NeuralNetwork(archi)
            memory.set_epoch(1)
            memory.init_network()
        inputs = [float() for __idx0 in range(s.nn_coding_size() + prosize)]
        outputs = [float() for __idx0 in range(1)]
        if rescale:
            outputs[0] = inverse_logistic(qsa)
        else:
            outputs[0] = qsa
        System.arraycopy(s.nnCoding(), 0, inputs, 0, s.nnCodingSize())
        System.arraycopy(a.nnCoding(), 0, inputs, s.nnCodingSize(), prosize)
        try:
            memory.learn_from_one_example(Sample(inputs, outputs))
        except (Exception, ), e:
            print "RewardMemorizerNNSinglePass" + e
        return

# EOF -------------------------------------------------------------------------
