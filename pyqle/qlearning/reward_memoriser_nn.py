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
Memorizing Q(s,a) in a neural network.

Each experience is transformed into a Sample. At some moment, the Samples
are gathered into a Dataset and fed into a neural network, which is asked
to learn Q(s,a) from this dataset.
When asked to return a Q(s,a) value, this class uses the neural network to
compute it.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging

# Enthought library imports
from enthought.traits.api import Long, Int, Instance, Bool

# Local imports:
from action_state_pair import ActionStatePair

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "RewardMemorizerNN" class:
#------------------------------------------------------------------------------

class RewardMemorizerNN(RewardStore):
    """
    Memorizing Q(s,a) in a neural network.
    
    Each experience is transformed into a Sample. At some moment, the Samples
    are gathered into a Dataset and fed into a neural network, which is asked
    to learn Q(s,a) from this dataset.
    When asked to return a Q(s,a) value, this class uses the neural network to
    compute it.

    """
    
    serial_version_uid = Long
    
    # The neural network plays the role of memory
    memory = Instance(NeuralNetwork, ())
    
    # The current samples
    dataset = Instance(Dataset, ())
    
    # The maximum number of Samples contained into the dataset
    max_size = Int(5000)
    
    # Control the number of newcoming samples
    new_ones = Int(0)
    
    # Each time incoming samples reach limit, the neural network is asked to
    # learn.
    limit = Int(50)
    
    generator = Instance(Random)
    
    value_chooser = Instance(DefaultValueChooser)

    # To rescale the values between 0 and 1
    rescale = Bool(False)


    def __init__(self, dvc=None, **traits):
        if dvc is None:
            dvc = NullValueChooser()
        self.value_chooser = dvc
        self.rescale = True
        
        super(RewardMemorizerNN, self).__init__(value_chooser=dvc,
            rescale=True, **traits)


    def inverse_logistic(self, x):
        """
        Maps R to [0,1]
        
        """
        
        u = Math.exp(x)
        return u / 1 + u


    def logistic(self, x):
        """
        Maps [0,1] to R
        
        """
        
        return Math.log(x / 1 - x)


    def get_weight(self, i, j, k):
        return self.memory.get_weight(i, j, k)


    def get_size_of_layer(self, i):
        return self.memory.get_size_of_layer(i)


    def set_epoch(self, i):
        self.memory.set_epoch(i)


    def set_rescale(self):
        """
        Enable rescaling
        
        """
        
        self.rescale = True


    def unset_rescale(self):
        """
        Disable rescaling
        
        """
        
        self.rescale = False


    def get(self, s, a):
        prosize = a.nn_coding_size()
        inputs = [float() for idx in range(s.nn_coding_size() + prosize)]
        resu = [float() for idx in range(1)]
        System.arraycopy(s.nnCoding(), 0, inputs, 0, s.nnCodingSize())
        System.arraycopy(a.nnCoding(), 0, inputs, s.nnCodingSize(), prosize)
        if self.memory is not None:
            try:
                resu = self.memory.classify(inputs)
            except (Exception, ), e:
                print "xxx:" + e
            if not self.rescale:
                return resu[0]
            else:
                return self.logistic(resu[0])
        else:
            return self.value_chooser.get_value()


    def set_nn(self, desc_layers):
        self.memory = NeuralNetwork(desc_layers)
        self.memory.set_epoch(100)
        self.memory.init_network()


    def put(self, s, a, sp, qsa):
        prosize = a.nn_coding_size()
        if self.memory is None:
            # Build it
            archi = [int() for __idx0 in range(3)]
            archi[0] = s.nn_coding_size() + prosize
            archi[1] = 7
            archi[2] = 1
            self.memory = NeuralNetwork(archi)
            # TODO experiments for chess endgames: low down for other examples
            self.memory.set_epoch(100)
            self.memory.init_network()
        inputs = [float() for __idx0 in range(s.nn_coding_size() + prosize)]
        outputs = [float() for __idx0 in range(1)]
        if self.rescale:
            outputs[0] = self.inverse_logistic(qsa)
        else:
            outputs[0] = qsa
        System.arraycopy(s.nn_coding(), 0, inputs, 0, s.nn_coding_size())
        System.arraycopy(a.nnCoding(), 0, inputs, s.nnCodingSize(), prosize)
        self.dataset.add(Sample(inputs, outputs))
        self.new_ones += 1
        if (self.new_ones % self.limit == 1):
            try:
                self.memory.learn_from_dataset_non_stochastic(self.dataset)
            except (Exception, ), e:
                System.err.println("YYY" + e)
                System.exit(-1)
        if self.dataset.n_instances() > self.max_size:
            u = self.generator.next_int(self.max_size)
            self.my_dataset.remove(u)
        return


    def toString(self):
        """
        Supposed to print Q(s,a) value. More difficult than when Q(s,a) are
        really stored : we can only sample the values...
        
        """
        
        return "No interesting view on the Neural Network"


    def extractDataset(self):
        """
        No dataset extraction at this time
        
        """
        
        return

# EOF -------------------------------------------------------------------------
