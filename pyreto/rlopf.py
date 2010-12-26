#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
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
from pybrain.rl.experiments import EpisodicExperiment

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

        #: Case to be optimised.
        self.case = case

        #: Load profile expressed as an array of values between 0.0 and 1.0.
        self.profile = [1.0] if profile is None else profile

        #: Count of profile steps.
        self._step = 0

        #: Initial generator set-points.
        gens = [g for g in case.online_generators if g.bus.type != REFERENCE]
        self._Pg0 = array([g.p for g in gens])

        #: Initial active power demand vector.
        self._Pd0 = array([b.p_demand for b in case.buses if b.type == PQ])

        #: Store generator set-point actions.
        self._Pg = zeros((len(self.case.online_generators), len(self.profile)))

        #----------------------------------------------------------------------
        #  "Environment" interface:
        #----------------------------------------------------------------------

        #: Set the number of action values that the environment accepts.
        self.indim = len(gens)

        #: Set the number of sensor values that the environment produces.
        self.outdim = len([b for b in case.buses if b.type == PQ])

    #--------------------------------------------------------------------------
    #  "CaseEnvironment" interface:
    #--------------------------------------------------------------------------

#    def _setProfile(self, value):
#        g = [g for g in self.case.online_generators if g.bus.type != REFERENCE]
#        self._Pg = zeros((len(g), len(value)))
#        self._profile = value
#
#    def _getProfile(self):
#        return self._profile
#
#    profile = property(_getProfile, _setProfile)

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

        # Compute power flows and slack generator set-point.
        NewtonPF(self.case, verbose=False).solve()
        #FastDecoupledPF(self.case, verbose=False).solve()

        # Store all generator set-points (only used for plotting).
        self._Pg[:, self._step] = [g.p for g in self.case.online_generators]

        # Apply the next load profile value to the original demand at each bus.
        if self._step != len(self.profile) - 1:
            pq_buses = [b for b in self.case.buses if b.type == PQ]
            for i, b in enumerate(pq_buses):
                b.p_demand = self._Pd0[i] * self.profile[self._step + 1]

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

        # Apply load profile to the original demand at each bus.
        for i, b in enumerate([b for b in self.case.buses if b.type == PQ]):
            b.p_demand = self._Pd0[i] * self.profile[self._step]

        # Initialise the record of generator set-points.
        self._Pg = zeros((len(self.case.online_generators), len(self.profile)))

        # Apply the first load profile value.
#        self.step()

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

        #: Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        #: Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getReward(self):
        """ Returns the reward corresponding to the last action performed.
        """
        on = self.env.case.online_generators
        generators = [g for g in on if g.bus.type != REFERENCE]

        cost = sum([g.total_cost() for g in generators])


        ref_penalty = 1000.0
        refs = [g for g in on if g.bus.type == REFERENCE]
        for g in refs:
            # Do not receive payment for negative Pg at slack bus.
            if g.p > 0.0:
                cost += g.total_cost()
            # Add a penalty if the output of the slack generator is infeasible.
            if not (g.p_min <= g.p <= g.p_max):
                cost += ref_penalty
#                logger.info("Infeasible slack generator output: %.3f" % g.p)

#        logger.info("Cost: %.3f" % cost)

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

#------------------------------------------------------------------------------
#  "OPFExperiment" class:
#------------------------------------------------------------------------------

class OPFExperiment(EpisodicExperiment):
    """ Defines a simple experiment subclass that saves generator set-points.
    """

    def __init__(self, agent, task):
        super(OPFExperiment, self).__init__(agent, task)

        self.Pg = None

    #--------------------------------------------------------------------------
    #  "EpisodicExperiment" interface:
    #--------------------------------------------------------------------------

    def _oneInteraction(self):
        """ Does one interaction between the task and the agent.
        """
        if self.doOptimization:
            raise Exception('When using a black-box learning algorithm, only full episodes can be done.')
        else:
            self.stepid += 1
            self.agent.integrateObservation(self.task.getObservation())
            self.task.performAction(self.agent.getAction())

            # Save the cumulative sum of set-points for each period.
            for i, g in enumerate(self.task.env.case.online_generators):
                self.Pg[i, self.stepid - 1] = self.Pg[i, self.stepid - 1] + g.p

            reward = self.task.getReward()
            self.agent.giveReward(reward)
            return reward


    def doEpisodes(self, number=1):
        """ Does the the given number of episodes.
        """
        env = self.task.env
        self.Pg = zeros((len(env.case.online_generators), len(env.profile)))

        rewards = super(OPFExperiment, self).doEpisodes(number)

        # Average the set-points for each period.
        self.Pg = self.Pg / number

        return rewards

# EOF -------------------------------------------------------------------------
