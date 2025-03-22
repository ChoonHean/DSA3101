from pyqlearning.qlearning.greedy_q_learning import GreedyQLearning
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


class PriceReinforcementLearning(GreedyQLearning):
    def __init__(self):
        super().__init__()
        self.set_alpha_value(1.0)
        self.set_epsilon_greedy_rate(0.8)

    def extract_possible_actions(self, state_key):
        """
        Returns the possible actions that can be made at the current state.
        In this case, the action will be transitioning to the next state
        :param state_key: the current state
        :return: list of possible next states
        """
        return list(filter(lambda x: 1 <= x <= 5, (state_key - 1, state_key, state_key + 1)))

    def observe_reward_value(self, state_key, action_key):
        """
        Returns the reward value for taking this action.
        In this case, the state_key is irrelevant, as the action key determines the next state and reward.
        :param state_key: the current state
        :param action_key: the next state
        :return: a reward for taking this action
        """
        return 5 - action_key

    def learn(self, a, limit=1000):
        super().learn(a, limit)
        print(self.q_df.sort_values("q_value", ascending=False))
