## Q3: How can we implement a dynamic pricing model for customized products?

_Note on the Data Usage:_

- _Due to the lack of pricing information of customized and base products (e.g price of floral dress vs plain dress) in
  the original Amazon dataset, we decide to bring in a new dataset ‘amazon_fashion_sales.csv’ for Part I solution. This
  is reasonable as merchants should have their past sales history as well as reviews about past products, which is
  something that online datasets did not have._
- _Part II of our solution will still be based on original Amazon dataset as we want to tap on the trained random forest
  regressor in Q1 for demand forecasting_
### Part I: `customization_price_optimizer.py`

The first step focuses on determining how much to charge customers for a product customization in order to maximize
expected profit.

Let:

- `x` = Customization price charged to customer
- `a` = Additional cost to manufacture the customized item
- `p(x)` = Probability that a customer will buy customized product at price `x`
- `s` = Selling price of the base item
- `c` = Cost of the base item

Profit from base item = `s - c`  
Profit from customized item = `s - c + x - a`

The expected profit at a given customization price x is:

```
Expected Profit = (1 - p(x))(s - c) + p(x)(s - c + x - a)
```

Using this model, the optimizer searches for the value of x that maximizes expected profit from customization.

### Part II: `demand_price_adjustment.py`

After optimizing the customization charges, the next step is to adjust the selling price to reflect predicted market
demand for the upcoming quarter.
We will use the trained random forest regressor in Q1.

After optimizing the customization charges, the next step is to adjust the selling price to reflect predicted market
demand for the upcoming quarter. We will use the trained Random Forest regressor from Q1.

#### Key idea:

1. Predict the next-quarter demand (i.e. forcasted demand) using the model.
2. Calculate baseline demand as the average demand over the past four quarters.
3. Compute demand difference:
   ```
   Demand difference = (forecasted demand - baseline demand) / baseline demand
   ```
4. Calculate price change percentage:
   ```
   Percentage Price Change = Demand difference / PED
   ```
   *Note: PED (Price Elasticity of Demand) is assumed to be -1.5*
5. Constrain the final price change within ±25%.

This ensures pricing remains responsive, yet stable enough for real-world deployment.

By combining both components that reflect the customization and demand changes, this solution creates a **data-driven
dynamic pricing system**.

