__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

from relearner import RELearner, REParameters

class AREParameters(REParameters):
    """ Parameters required for the Advanced version of the Roth-Erev
        reinforcement learning algorithm. These parameters include setting for
        features extended from the standard Roth-Erev algorithm. This includes:

            Alternative methods to generate Action probabilities.
            Alternative methods of reward spillover among similar actions
            Ability to specify similar measures for Action comparison
    """

    def __init__(self):
        # Which method of reward spillover to use.
        selectedSpillover = None

        # List of available spillover methods.
        spilloverList = []


    def init(self):
        if self.spilloverList is None:
            self.spilloverList = []

        self.buildSpilloverSelector()


    def buildSpilloverSelector(self):
        # Add no-spillover option if not already present.
        if NoSpillover not in self.spilloverList:
            noSpill = NoSpillover()
            self.spilloverList.append(noSpill)

        # Add standard spillover if not already present
        if StandardSpillover not in self.spilloverList:
            standard = StandardSpillover(self.getExperimentation(),
                                         self.getNumberOfActions())
            self.spilloverList.append(standard)


class ARELearner(RELearner):
    """ An extension of the VRELearner. This engine implements the same
        modified version of the Roth-Erev reinforcement learning algorithm with
        added features.
    """

    def __init__(self):
        # Flag to use relative propensities to generate action probabilities
        # from action propensities. This is used by default. The probability
        # for each action is the propensity for that action over the total
        # propesities over all actions.
        #
        # P(i) = q(i) / Sum_all_j(q(j))
        #
        # Where P(i) is the probability of choosing action i, q(i) is the
        # propensity for action i and j runs from 1 to n (the total number of
        # actions).
        USE_RELATIVE_PROPENSITY_PROBABILITY = 10101

        # Flag to use the Boltzman distribution to generate action probabilities
        # from action propensities.
        #
        #    P(i) = e ^(q(i)/T) / Sum_all_j(e ^(q(j)/T))
        #
        # Where P(i) is the probability of choosing action i, q(i) is the
        # propensity for action i and j runs from 1 to n (the total number of
        # actions). T is the temperature parameter...
        # TODO: Look up info about Gibbs/Boltzmann temperature
        USE_BOLTZMAN_PROBABILITY = 11212

        # Flag indicating which method of response weighting to use in updating
        # the propensities of actions from a given reward. This determines how
        # much of the reward value is "spilled over" to actions that are
        # similar to the action that the reward is associated with (usually the
        # last one chosen). Similarity between actions is defined by the given
        # similarity measure.
        spilloverType = -1

        spillover = SpilloverWeightGenerator()

        EXPONENTIAL_SPILLOVER = 20101

        LOGARITHMIC_SPILLOVER = 21212

        LINEAR_SPILLOVER = 22323

        STANDARD_SPILLOVER = 23434

        NO_SPILLOVER = 29999


    def init(self):
        super(ARELearner, self).init()
        self.spillover = None


    def experience(self, actionIndex, reward):
        if self.spillover is None:
            return super(ARELearner, self).experience(actionIndex, reward)

        responseValue = 0
        domain = self.policy.getActionDomain()

        action = domain.getAction(actionIDList.get(actionIndex))

        responseValue = reward * self.spillover.generateWeight(action)

        return responseValue


class AdvancedRothErevLearner(RELearner):
    """ An extension of the MRELearner. This engine implements the same
        modified version of the Roth-Erev reinforcement learning algorithm with
        added features.
    """

    def experience(self, actionIndex, reward):
        if self.spillover is None:
            return super(ARELearner, self).experience(actionIndex, reward)

        responseValue = 0.0
        weight = 0.0
        similarity = 0.0

        domain = self.policy.getActionDomain()

        action = domain.getAction(actionIDList.get(actionIndex))

        responseValue = reward * self.spillover.generateWeight(action)

        return responseValue


    def updateProbabilities(self):
        """ pdates the probability for each action to be chosen in the policy.
        """
        method = self.parameters.getProbabilityMethod()

        if method == self.USE_RELATIVE_PROPENSITY_PROBABILITY:
            self.generateProportionalProbs()
        elif method == self.USE_BOLTZMAN_PROBABILITY:
            self.generateBoltzmanProbs()
        else:
            self.generateBoltzmanProbs()


    def generateProportionalProbs(self):
        """ Generate action probabilities using a proportional distribution.
            Warning: In situations where the MRELearner may receive negative
            reward values, this probability method may yield negative
            probabilities. This can be avoided by setting the intial propensity
            to a sufficiently value. However, it is recommended that MRELearner
            only be used in the simulations with positive reward values.
        """
        summedProps = 0.0
        newProb = 0.0

        for actID in self.actionIDList:
            summedProps += self.policy.getPropensity(actID)

        # For each Action, divide its propensity by the sum of all
        # propensities. Then set its probability value to the result.
        for actID in self.actionIDList:
            newProb = self.policy.getPropensity(actID) / summedProps
            self.policy.setProbability(actID, newProb)
