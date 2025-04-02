### Q5: How can we integrate reinforcement learning into our pricing and inventory optimization models?

For pricing, a Q-learning model can be used, with the state as the current price of the item, and the action would be to
increase the price, remain at the same price, or decrease the price. Then as the model runs with a fixed period for it
to update the values, such as a week or month. For pricing, the state for the Q-learning model will be the current
price, and the available actions are to increase the price, remain at the same price, or decrease the price. The reward
it then receives can be the profit from the past period. That way, when the model aims to maximize rewards, it is
actually maximizing profits.

The file `price_q_learning.py` contains a model that implements this idea, but the reward function has to be set
properly for a concrete use case. For this demonstration, a simple reward of 5 - price is given, just to show that the
model will prefer to set the price to be lower to maximize rewards after enough training.

The current model inherits Greedy Q-learning, such that the action with the highest expected rewards is chosen with
probability ε, and a random action is taken with probability 1 - ε. This balances the exploration-exploitation dilemma.
There are a few ways to give the model a better head start, by using past data. The Q-table can be manually updated with
sales history, or even with current data. This allows the model to explore possible states and know their values without
having the model make the decisions which might potentially lead to bad actions taken during the exploration stage. This
can allow the reinforcement learning model, which usually has slow starts due to the lack of data available, to train
before even being deployed. As such, ε can be adjusted based on the stage the model is at, allowing it to take the more
favourable actions after it has collected enough data.