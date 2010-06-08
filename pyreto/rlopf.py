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

from numpy import array, zeros

from pybrain.rl.environments import Environment, EpisodicTask

from pylon import PQ, REFERENCE, NewtonPF#, FastDecoupledPF

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
        gens = [g for g in case.online_generators if g.bus.type != REFERENCE]
        self._Pg0 = array([g.p for g in gens])

        # Initial active power demand vector.
        self._Pd0 = array([b.p_demand for b in case.buses if b.type == PQ])

        # Store generator set-point actions.
        self._Pg = zeros((len(gens), len(self.profile)))

        #----------------------------------------------------------------------
        #  "Environment" interface:
        #----------------------------------------------------------------------

        # Set the number of action values that the environment accepts.
        self.indim = len(gens)

        # Set the number of sensor values that the environment produces.
        self.outdim = len([b for b in case.buses if b.type == PQ])

    #--------------------------------------------------------------------------
    #  "CaseEnvironment" interface:
    #--------------------------------------------------------------------------

    def _setProfile(self, value):
        g = [g for g in self.case.online_generators if g.bus.type != REFERENCE]
        self._Pg = zeros((len(g), len(value)))
        self._profile = value

    def _getProfile(self):
        return self._profile

    profile = property(_getProfile, _setProfile)

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        Pd = array([b.p_demand for b in self.case.buses if b.type == PQ])
        logger.info("State: %s" % list(Pd))
        return Pd


    def performAction(self, action):
        """ Perform an action on the world that changes it's internal state.
        """
        gs = [g for g in self.case.online_generators if g.bus.type !=REFERENCE]

        assert len(action) == len(gs)

        logger.info("Action: %s" % list(action))

        # Set the output of each (non-reference) generator.
        for i, g in enumerate(gs):
            g.p = action[i]

            self._Pg[i, self._step] = action[i]

        # Solve the power flow problem for the new case.
        NewtonPF(self.case, verbose=False).solve()
        #FastDecoupledPF(self.case, verbose=False).solve()

        s = [g for g in self.case.online_generators if g.bus.type == REFERENCE]
        logger.info("Slack: %.3f" % s[0].p)

        # Apply load profile to the demand at each bus.
        for i, b in enumerate([b for b in self.case.buses if b.type == PQ]):
            b.p_demand = self._Pd0[i] * self.profile[self._step]

        self._step += 1

        logger.info("Entering step %d." % self._step)


    def reset(self):
        """ Re-initialises the environment.
        """
        logger.info("Reseting environment.")

        self._step = 0

        # Reset the set-point of each generator to its original value.
        gs = [g for g in self.case.online_generators if g.bus.type !=REFERENCE]
        for i, g in enumerate(gs):
            g.p = self._Pg0[i]

        # Reset the demand at each bus to its original value.
        for i, b in enumerate([b for b in self.case.buses if b.type == PQ]):
            b.p_demand = self._Pd0[i]

        # Initialise the record of generator set-points.
        self._Pg = zeros((len(gs), len(self.profile)))

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
        generators = [g for g in self.env.case.online_generators
                      if g.bus.type != REFERENCE]

        cost = sum([g.total_cost() for g in generators])
        logger.info("Cost: %.3f" % cost)

        return -cost


    def isFinished(self):
        """ Is the current episode over?
        """
        finished = (self.env._step == len(self.env.profile))
        if finished:
            logger.info("Finished episode.")
        return finished

    #--------------------------------------------------------------------------
    #  "MinimiseCostTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        limits = []
        for i in range(len([b for b in self.env.case.buses if b.type == PQ])):
            limits.append((0.0, self.env._Pd0[i]))

        logger.info("Sensor limits: %s" % limits)

        return limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        generators = [g for g in self.env.case.online_generators
                      if g.bus.type != REFERENCE]
        limits = []
        for g in generators:
            limits.append((g.p_min, g.p_max))

        logger.info("Actor limits: %s" % limits)

        return limits

# EOF -------------------------------------------------------------------------
