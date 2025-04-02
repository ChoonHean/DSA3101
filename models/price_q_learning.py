from pyqlearning.qlearning.greedy_q_learning import GreedyQLearning
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


class PriceReinforcementLearning(GreedyQLearning):
    """
    A Reinforcement Learning model that builds on the abstract base class GreedyQLearning
    with concrete implementations for extract_possible_actions and observe_reward_value.
    It outputs an action to take, and receives a reward for taking that action. In this case,
    it would be the profits from selling the items. It will then update its Q-table and output the
    next action to take, either to maximize profits from known state-action pairs or explore alternative
    actions that might lead to more rewards.
    """
    def __init__(self):
        super().__init__()
        self.set_alpha_value(0.8)
        self.set_epsilon_greedy_rate(0.8)

    def extract_possible_actions(self, state_key):
        """
        Returns the possible actions that can be made at the current state.
        In this case, the actions possible will be to decrease price by 1 unit,
        stay at the same price, or increase price by 1 unit.
        This method should be replaced with the actual price points that the item could be set to.
        :param state_key: the current state
        :return: list of possible next states
        """
        return list(filter(lambda x: 1 <= x <= 5, (state_key - 1, state_key, state_key + 1)))

    def observe_reward_value(self, state_key, action_key):
        """
        Returns the reward value for taking this action.
        In this case, the state_key is irrelevant, as the action key determines the next state and reward.
        The current reward value is simulated as we have not yet sold anything, but the return value
        should be replaced with the profit for the actual use case.
        :param state_key: the current state
        :param action_key: the next state
        :return: a reward for taking this action
        """
        return 5 - action_key

    def learn(self, a, limit=1000):
        super().learn(a, limit)
        print(self.q_df.sort_values("q_value", ascending=False))

if __name__ == "__main__":
    rl = PriceReinforcementLearning()
    rl.learn()
    # Since the reward is 5 - action_key, the reward should be higher when the action_key is lower.
    # The printed Q-table should show that lower action_keys have higher Q-values, with higher Q-values
    # indiciating higher expected rewards for taking that action.