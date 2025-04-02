1. **Run `customization_price_optimizer.py`**  
   Calculates the optimal price to charge for a product customization (e.g., color, engraving, size adjustment), based
   on historical customer behavior. It uses a fitted probability curve to model the likelihood of purchase at various
   customization prices and finds the value of `x` that maximizes expected profit.

2. **Run `demand_price_adjustment.py`**  
   Forecasts product demand for the next quarter using a trained Random Forest model and recommends an adjustment to the
   base selling price based on predicted demand relative to historical averages.