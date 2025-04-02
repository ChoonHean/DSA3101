### Q5: How can we integrate reinforcement learning into our pricing and inventory optimization models?

For inventory management, Q-learning can be used, which learns to maximize the rewards for taking an action. In this
case, the state will be the number of products left in stock, and the action can be included in 2 ways: either it is a
binary choice to restock or not, or it can also include how much to restock. The reward will then be the cost of making
the action: in the case of restocking, we will incur costs due to having to store the products in a warehouse. If we
choose not to restock, and stock falls below 0 and there are orders that are unable to be fulfilled, it also results in
costs in lost sales and unsatisfied customers who will be unlikely to purchase again. When the model maximizes rewards,
it is actually minimizing costs, which achieves the same goal.

The file `inventory_q_learning.py` contains a model which implements the binary choice, with the state key as products
left, and whether to restock or not. The restocking quantity is fixed at a set amount. Each iteration, the number of
purchases is drawn from a normal distribution, and the reward is given as lost sales if there is no restock but stock
falls below 0, and if restock is chosen, a storage cost per item is given. After the training, it can be seen that the
model tends to prefer restocking when the state is lower, and the higher the stock left, restocking is less desirable.
This model can then be used to find the optimal threshold value that the merchant should restock, when the Q-value of
the state-action pair for restocking is higher than the Q-value of the state-action pair for not restocking.

Before relying on the model to manage inventory, we can train it with past data. We can manually update the Q-table
based on costs incurred when a decision to restock or not was taken, allowing the model to learn from the actions of
others. This way, the exploration stage of the model is conducted before it is deployed, allowing it to have a better
knowledge of state-action pairs by the time it is deployed, and can minimize costs incurred by the merchant effectively.

Further improvements to this model can be made, by also adding more possible actions, which also tells the merchant how
much to restock, instead of only whether to restock or not. However, this requires a lot more data, as there are now
more state-action pairs, meaning that more iterations are needed for the model to explore the possibilities before it
can work to its full potential.