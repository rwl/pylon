#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines classes for learning to optimise power flow.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import array

from pybrain.rl.environments import Environment, EpisodicTask

from pylon import NewtonPF, FastDecoupledPF

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "CaseEnvironment" class:
#------------------------------------------------------------------------------

class CaseEnvironment(Environment):
    """ Defines a case optimisation environment.
    """
    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, profile=None):
        """ Constructor for CaseEnvironment.
        """
        #----------------------------------------------------------------------
        #  "CaseEnvironment" interface:
        #----------------------------------------------------------------------

        # Case to be optimised.
        self.case = case

        # Load profile expressed as an array of values between 0.0 and 1.0.
        self.profile = [1.0] if profile is None else profile

        # Count of profile steps.
        self._step = 0

        # Initial generator set-points.
        self._Pg0 = array([g.p for g in self.case.online_generators])

        # Initial active power demand vector.
        self._Pd0 = array([b.p_demand for b in self.case.buses])

        #----------------------------------------------------------------------
        #  "Environment" interface:
        #----------------------------------------------------------------------

        # Set the number of action values that the environment accepts.
        self.indim = len(self.case.online_generators)

        # Set the number of sensor values that the environment produces.
        self.outdim = len(self.case.buses)

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        Pd = array([b.p_demand for b in self.case.buses])
        return Pd


    def performAction(self, action):
        """ Perform an action on the world that changes it's internal state.
        """
        assert len(action) == len(self.case.online_generators)

        for i, g in enumerate(self.case.online_generators):
            g.p = action[i]

        NewtonPF(self.case).solve()
        #FastDecoupledPF(self.case).solve()

        # Apply load profile.
        for i, b in enumerate(self.case.buses):
            b.p_demand = self._Pd0[i] * self.profile[self._step]

        self._step += 1


    def reset(self):
        """ Reinitialises the environment.
        """
        self._step = 0

        for i, g in enumerate(self.case.online_generators):
            g.p = self._Pg0[i]

        for i, b in enumerate(self.case.buses):
            b.p_demand = self._Pd0[i]

        self.case.reset()

#------------------------------------------------------------------------------
#  "MinimiseCostTask" class:
#------------------------------------------------------------------------------

class MinimiseCostTask(EpisodicTask):
    """ Defines the task of minimising costs.
    """

    def __init__(self, environment):
        """ Constructor for cost minimisation task.
        """
        super(MinimiseCostTask, self).__init__(environment)

        #----------------------------------------------------------------------
        #  "Task" interface:
        #----------------------------------------------------------------------

        # Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        # Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getReward(self):
        """ Returns the reward corresponding to the last action performed.
        """
        cost = sum([g.total_cost() for g in self.env.case.online_generators])

        return -cost


    def isFinished(self):
        """ Is the current episode over?
        """
        return self.env._step > len(self.env.profile)

    #--------------------------------------------------------------------------
    #  "MinimiseCostTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        limits = []
        for i in range(len(self.env.case.buses)):
            limits.append((0.0, self.env._Pd0[i]))

        return limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        limits = []
        for g in self.env.case.generators:
            limits.append((g.p_min, g.p_max))

        return limits

# EOF -------------------------------------------------------------------------
