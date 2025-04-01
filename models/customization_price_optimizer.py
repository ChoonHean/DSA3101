import numpy as np
import pandas as pd

from scipy.optimize import minimize, curve_fit
from sklearn.preprocessing import MinMaxScaler


class CustomizationPriceOptimizer:
    """
    A class that finds the optimal price to charge for customizations.
    It makes use of past sales data in the following way:
    The variable x, which is the price customers pay for customization,
    found by doing customized item price - non-customized (base) item price.
    p(x), the probability that a customer will buy the customized product if the cost is x.
    It is the ratio of customized items bought / total items bought.
    Define a few other variables,
    s, the selling price of the base item
    c, the materials cost to make the base item.
    Then the profit from selling a base item is s - c.
    a, the additional material and / or manpower cost to produce a customized item.
    x, the increased charge that customers pay for customization.
    Then the profit from selling a customized item is s - c + x - a.
    With that, the expected profit overall at a certain x is
    (1 - p(x))(s - c) + p(x)(s - c + x - a) = p(x)(x - a) + s - c
    If s and c are fixed, maximizing p(x)(x - a) will maximize the expected profit.
    This class maximizes p(x)(x - a) by minimizing -p(x)(x - a).
    It applies bayesian learning with p(x) by setting the price to certain values
    and observing the probabilities, it will receive more data to refine p_x to be more accurate.
    """

    def __init__(self):
        def p_x(x, a, b):
            return (1 / (x + a)) + b

        self.p_x = p_x
        self.a = 0
        self.b = 0

    def find_optimal_price(
            self,
            data: pd.DataFrame,
            item: str,
            customization: str,
            base_choices: list[str],
            customization_material_cost: float
    ) -> float:
        """
        Takes in a dataframe of sales history, and applies maximization to find the optimal price
         to set customization prices at to maximize the expected profit.
        :param data: Dataframe of sales history.
        :param item: The name of the item that the model is being used to find the price.
        :param customization: The column name of the customization being considered.
        :param base_choices: A list of options that are considered base products i.e. no extra customization cost
        :param customization_material_cost: The extra materials or manpower cost that a customized item costs for the manufacturer.
        :return: The optimal price to set the customization cost at to maximize expected profits.
        """
        data = data[data['parent'] == item]
        data = data[data['size'] == 'L']
        grouped_data = data.groupby("week")
        prices_and_proportions = map(
            lambda group: self.extract_cost_and_proportion(group, customization, base_choices),
            grouped_data
        )
        prices, proportions = map(lambda ls: np.array(ls), zip(*prices_and_proportions))
        xScaler = MinMaxScaler(feature_range=(0.01, 0.99))
        prices = prices.reshape(-1, 1)
        prices = xScaler.fit_transform(prices)
        prices = prices.reshape(len(prices))
        (self.a, self.b), cov = curve_fit(
            self.p_x,
            prices,
            proportions,
            bounds=((-3, -np.inf), (-1, np.inf))
        )
        customization_material_cost_normalised = xScaler.transform(
            np.array([[customization_material_cost]])
        )[0][0]
        optimized_price_normalised = minimize(
            fun=lambda x: (-self.p_x(x, self.a, self.b)) * (x - customization_material_cost_normalised),
            x0=0.5
        ).x
        return xScaler.inverse_transform(np.array([optimized_price_normalised]))[0][0]

    def extract_cost_and_proportion(
            self,
            grouped_data: pd.api.typing.DataFrameGroupBy,
            customization: str,
            base_choices: list[str]
    ) -> tuple[float, float]:
        """
        Takes in a dataframe of grouped items, and outputs the customization cost and
        proportion of customers who opted for customization, which is used to fit p_x.
        :param grouped_data: A dataframe grouped by the time period e.g. week, month.
        :param customization: The column name of the customization being considered.
        :param base_choices: A list of options that are considered base products i.e. no extra customization cost
        :return: The customization cost, x and proportion of customers who bought a customized product, p_x.
        """
        data = grouped_data[1]
        customized_price = data[~data[customization].isin(base_choices)]["price"].mean()
        base_price = data[data[customization].isin(base_choices)]["price"].mean()
        base_proportion = len(data[data[customization].isin(base_choices)]) / len(data)
        return customized_price - base_price, 1 - base_proportion


if __name__ == "__main__":
    df = pd.read_csv("../dataset/cleaned_data/amazon_fashion_sales.csv")
    print(CustomizationPriceOptimizer().find_optimal_price(
        df,
        'JN_KURTA',
        'color',
        ['White', 'Black'],
        50
    ))
