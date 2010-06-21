#------------------------------------------------------------------------------
# Copyright (C) 2006 Charles Gieseler
# Copyright (C) 2010 Richard Lincoln
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

""" Defines classes that implement the Roth-Erev reinforcement learning method.
The original Roth-Erev reinforcement learning algorithm was presented by
A. Roth and I. Erev in:

  - A. E. Roth, I. Erev, D. Fudenberg, J. Kagel, J. Emilie and R. X. Xing,
    "Learning in Extensive-Form Games: Experimental Data and Simple Dynamic
    Models in the Intermediate Term", Games and Economic Behavior, 8-1,
    pp 164-212, 1995

  - Erev, Ido and Roth, Alvin E., "Predicting How People Play Games:
    Reinforcement Learning in Experimental Games with Unique, Mixed Strategy
    Equilibria", The American Economic Review, 88-4, pp 848--881, 1998

Implementation adapted from the RothErevLearner in JRELM by Charles Gieseler
which was itself adapted, in part, from the RothErevLearner in the Java
JLCRAgent Simulator API (JASA) by Steve Phelps, Department of Computer Science,
University of Liverpool.  For further details see:

  - Charles Gieseler, "A Java Reinforcement Learning Module for the Repast
    Toolkit: Facilitating Study and Implementation with Reinforcement Learning
    in Social Science Multi-Agent Simulations", MSc Thesis, Department of
    Computer Science, Iowa State University, 2005

@license: GNU GPLv2
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import random
import scipy

from pybrain.rl.learners.valuebased.valuebased import ValueBasedLearner
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.explorers.discrete.discrete import DiscreteExplorer
from pybrain.utilities import drawIndex

#------------------------------------------------------------------------------
#  "RothErev" class:
#------------------------------------------------------------------------------

class RothErev(ValueBasedLearner):
    """ Defines the Roth-Erev reinforcement learning method presented in:

      - A. E. Roth, I. Erev, "Predicting How People Play Games with Unique
        Mixed-Strategy Equilibria," American Economics Review, Volume 88, 1998,
        848-881.
    """

    #: Does the algorithm work on-policy or off-policy?
    offPolicy = False

    #: Does the algorithm run in batch mode or online?
    batchMode = True


    def __init__(self, experimentation=0.5, recency=0.5):

        #----------------------------------------------------------------------
        #  ValuebasedLearner interface:
        #----------------------------------------------------------------------

        #: Default exploration according to a discrete probability distribution
        #: function.
        self.explorer = ProportionalExplorer()

        #----------------------------------------------------------------------
        #  RothErev interface:
        #----------------------------------------------------------------------

        #: The tendency for experimentation among action choices. The algorithm
        #: will sometimes choose non-optimal actions in favour of exploring the
        #: domain.
        #: Note: Be careful not to choose value e where (1-e) == e / (N - 1),
        #: where N is the size of the action domain (i.e. e == 0.75 and N == 4)
        #: This will result in all    action propensities receiving the same
        #: experience update value, regardless of the last action chosen.
        #: Action choice probabilities will then remain uniform and no learning
        #: will occur.
        assert 0.0 <= experimentation <= 1.0
        self.experimentation = experimentation

        #: The initial propensity value assigned to all actions. Used instead of
        #: a scaling parameter.
#        assert initialPropensity >= 0.0
#        self.initialPropensity = initialPropensity

        #: The degree to which actions are 'forgotten'. Used to degrade the
        #: propensity for choosing actions. Meant to make recent experience
        #: more prominent than past experience in the action choice process.
        assert 0.0 <= recency <= 1.0
        self.recency = recency

        #: Last action chosen from the policy.
        self._lastSelectedAction = -1

    #--------------------------------------------------------------------------
    #  Learner interface:
    #--------------------------------------------------------------------------

    def learn(self):
        """ Learn on the current dataset, either for many timesteps and even
        episodes (batchMode = True) or for a single timestep
        (batchMode = False). Batch mode is possible, because Q-Learning is an
        off-policy method.

        In batchMode, the algorithm goes through all the samples in the history
        and performs an update on each of them. if batchMode is False, only the
        last data sample is considered. The user himself has to make sure to
        keep the dataset consistent with the agent's history.
        """
        if self.batchMode:
            samples = self.dataset
        else:
            samples = [[self.dataset.getSample()]]

        for seq in samples:
            for _, self._lastSelectedAction, reward in seq:
                self._updatePropensities(reward)


#    def reset(self):
#        """ Clear all learned knowledge. The Action propensities are set to the
#        current initial value and the probability values in the policy.
#        """
#        super(RothErev, self).reset()
#        self.dataset.clear()
#        self.module.initialise(self.initialPropensity)

    #--------------------------------------------------------------------------
    #  RothErev interface:
    #--------------------------------------------------------------------------

    def _updatePropensities(self, reward):
        """ Update the propensities for all actions. The propensity for last
        action chosen will be updated using the feedback value that resulted
        from performing the action.

        If j is the index of the last action chosen, r_j is the reward received
        for performing j, i is the current action being updated, q_i is the
        propensity for i, and phi is the recency parameter, then this update
        function can be expressed as::

                q_i = (1-phi) * q_i + E(i, r_j)
        """
        phi = self.recency

        for i in range(self.module.numActions):
            carryOver = (1 - phi) * self.module.getValue(0, i)
            experience = self._experience(i, reward)
            self.module.updateValue(0, i, carryOver + experience)


    def _experience(self, actionIndex, reward):
        """ This is the standard experience function for the Roth-Erev
        algorithm. Here propensities for all actions are updated and similarity
        does not come into play. That is, all action choices are assumed to be
        equally similar. If the actionIndex points to the action the reward is
        associated with (usually the last action taken) then simply adjust the
        weight by the experimentation. Otherwise, adjust the weight by a
        smaller portion of the reward.

        If j is the index of the last action chosen, r_j is the reward received
        for performing j, i is the current action being updated, n is the size
        of the action domain and e is the experimentation parameter, then this
        experience function  can be expressed as::
                         _
                        |  r_j * (1-e)         if i = j
            E(i, r_j) = |
                        |_ r_j * (e /(n-1))    if i != j
        """
        e = self.experimentation

        rewardedIndex = self._lastSelectedAction

        if actionIndex == rewardedIndex:
            experience = reward * (1 - e)
        else:
            experience = reward * (e / (self.module.numActions - 1))

        return experience

#------------------------------------------------------------------------------
#  "VariantRothErev" class:
#------------------------------------------------------------------------------

class VariantRothErev(RothErev):
    """ Variant Roth-Erev Learner

    This ReinforcementLearner implements a variation of the Roth-Erev
    algorithm as presented in:

      - James Nicolaisen, Valentin Petrov, and Leigh Tesfatsion, "Market Power
        and Efficiency in a Computational Electricity Market with
        Discriminatory Double-Auction Pricing," IEEE Transactions on
        Evolutionary Computation, Volume 5, Number 5, 2001, 504-523.

    @see L{RothErev} for details on the original Roth-Erev algorithm.
    """

    def experience(self, actionIndex, reward):
        """ This is an altered version of the experience function for used in
        the standard Roth-Erev algorithm.  Like in RELearner, propensities for
        all actions are updated and similarity does not come into play. If the
        actionIndex points to the action the reward is associated with (usually
        the last action taken) then simply adjust the weight by the
        experimentation. Otherwise increase the weight of the action by a small
        portion of its current propensity.

        If j is the index of the last action chosen, r_j is the reward received
        for performing j, i is the current action being updated, q_i is the
        propensity for i, n is the size of the action domain and e is the
        experimentation parameter, then this experience function can be
        expressed as::

                        |  r_j * (1-e)         if i = j
            E(i, r_j) = |
                        |_ q_i * (e /(n-1))    if i != j
        """
        e = self.parameters.experimentation
        rewardedIndex = self.actionIDList.index(self.lastSelectedAction)

        if actionIndex == rewardedIndex:
            experience = reward * (1 - e)
        else:
            propensity = self.module.getValue(0, actionIndex)
            experience = propensity * (e / (self.module.numActions - 1))

        return experience

#------------------------------------------------------------------------------
#  "PropensityTable" class:
#------------------------------------------------------------------------------

class PropensityTable(ActionValueTable):
    """ Interface for building a stateless reinforcement learning policy. This
    type of policy simply maintains a distribution guiding action choice
    irrespective of the current state of the world. That is, it simply
    maintains the propensity for selection of each action for all world states.
    """

    def __init__(self, numActions, name=None):
        ActionValueTable.__init__(self, 1, numActions, name)

#------------------------------------------------------------------------------
#  "ProportionalExplorer" class:
#------------------------------------------------------------------------------

class ProportionalExplorer(DiscreteExplorer):
    """ A discrete explorer that executes the actions with a probability that
    is proportional to the action propensities.
    """

    def _forwardImplementation(self, inbuf, outbuf):
        """ Proportional probability method.
        """
        assert self.module

        propensities = self.module.propensities
        summedProps = sum(propensities)
        probabilities = propensities / summedProps

#        action = eventGenerator(probabilities)
        action = drawIndex(probabilities)

        outbuf[:] = scipy.array([action])

#------------------------------------------------------------------------------
#  "eventGenerator" function:
#------------------------------------------------------------------------------

def eventGenerator(distrib):
    eventIndex = 0
    randValue = random.random()

    while (randValue > 0.0) and (eventIndex < len(distrib)):
        randValue -= distrib[eventIndex]
        eventIndex += 1

    return eventIndex - 1

# EOF -------------------------------------------------------------------------
