from pyqlearning.qlearning.greedy_q_learning import GreedyQLearning
from numpy.random import normal
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


class InventoryReinforcementLearning(GreedyQLearning):
    def __init__(self):
        super().__init__()
        self.set_alpha_value(1.0)

    def learn(self, state_key, limit=1000):
        """
        Learning and searching the optimal solution.

        Args:
            state_key:      Initial state.
            limit:          The maximum number of iterative updates based on value iteration algorithms.
        """
        self.t = 1
        while self.t <= limit:
            next_action_list = self.extract_possible_actions(state_key)
            if len(next_action_list):
                action_key = self.select_action(
                    state_key=state_key,
                    next_action_list=next_action_list
                )
                reward_value, next_state_key = self.observe_reward_value(state_key, action_key)

            if len(next_action_list):
                # Max-Q-Value in next action time.

                next_next_action_list = self.extract_possible_actions(next_state_key)
                next_action_key = self.predict_next_action(next_state_key, next_next_action_list)
                next_max_q = self.extract_q_df(next_state_key, next_action_key)

                # Update Q-Value.
                self.update_q(
                    state_key=state_key,
                    action_key=action_key,
                    reward_value=reward_value,
                    next_max_q=next_max_q
                )
                # Update State.
                state_key = next_state_key

            # Normalize.
            self.normalize_q_value()
            self.normalize_r_value()

            # Vis.
            self.visualize_learning_result(state_key)
            # Check.
            if self.check_the_end_flag(state_key) is True:
                break

            # Epsode.
            self.t += 1

        print(self.q_df[self.q_df.state_key <= 30].sort_values(["state_key", "action_key"]))

    def extract_possible_actions(self, state_key):
        """
        Returns the possible actions that are possible. Both actions are always possible at every state.
        0 means do not restock, 1 means restock.
        :param state_key: the current amount of stock left
        :return: list of 0 and 1
        """
        return [0, 1]

    def observe_reward_value(self, state_key, action_key):
        """
        Returns the reward for restocking/ not restocking at the current inventory level.
        At each time step, if the agent restocks, a cost is assigned per unit left as storing items in the warehouse
        incurs costs. If the agent does not restock, a penalty is assigned if there is not enough stock left to fulfil
        incoming orders.
        The number of customer purchases at each time step is drawn from a normal distribution with mean 5 and
        standard deviation 1, rounded down to the nearest integer.
        :param state_key:
        :param action_key:
        :return:
        """
        if action_key == 1:  # Restock
            state_key += 10
        purchased = int(normal(5, 1))  # Number of customers purchasing at the current time
        state_key -= purchased
        reward = 0
        if action_key == 1:  # Penalty per stock if restocked
            if state_key > 0:
                reward = state_key * -0.1
        else:
            if state_key < 0:  # Penalty for not having enough stock to fulfil orders
                reward = -5
        return reward, state_key if state_key > 0 else 10
