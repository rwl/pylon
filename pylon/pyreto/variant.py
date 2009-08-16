__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

from relearner import RELearner

class VRELearner(RELearner):
    """ Variant Roth-Erev Learner

        This ReinforcementLearner implements a variation of the Roth-Ere'ev
        algorithm as presented in:

            James Nicolaisen, Valentin Petrov, and Leigh Tesfatsion, "Market
            Power and Efficiency in a Computational Electricity Market with
            Discriminatory Double-Auction Pricing," IEEE Transactions on
            Evolutionary Computation, Volume 5, Number 5, 2001, 504-523.

        See RELearner for details on the original Roth-Erev algorithm
    """
    def updateProbabilities(self):
        """ Updates the probability for each action to be chosen in the policy.
        """
        self.generateBoltzmanProbs()

    def experience(self, actionIndex, reward):
        """ This is an altered version of the experience function for used in
            the standard Roth-Erev algorithm.  Like in RELearner, propensities
            for all actions are updated and similarity does not come into play.
            If the actionIndex points to the action the reward is associated
            with (usually the last action taken) then simply adjust the weight
            by the experimentation. Otherwise increase the weight of the action
            by a small portion of its current propensity.

            If j is the index of the last action chosen, r_j is the reward
            received for performing j, i is the current action being updated,
            q_i is the propensity for i, n is the size of the action domain and
            e is the experimentation parameter, then this experience function
            can be expressed as:

                          |  r_j * (1-e)         if i = j
              E(i, r_j) = |
                          |_ q_i * (e /(n-1))    if i != j
        """
        e = self.parameters.experimentation
        rewardedIndex = self.actionIDList.index(self.lastSelectedAction)

        if actionIndex == rewardedIndex:
            experience = reward * (1 - e)
        else:
            propensity = self.policy.getPropensity(actionIndex)
            experience = propensity * (e / (self.domainSize - 1))

        return experience
