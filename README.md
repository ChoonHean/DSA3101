## Project 5: AI-Driven Merchandise Customization Platform for E-commerce

---

### Overview
In the rapidly evolving world of e-commerce, merchants face increasing competition to provide personalized shopping experiences for customers. 
However, traditional methods of inventory management and product customization have significant limitations. 
E-commerce platforms typically rely on pre-made product images and static inventory, which restricts customers' ability to customize items according to their preferences. 
This leads to challenges in customer satisfaction, missed sales opportunities, and inefficient use of resources.
---

### Repository Structure

```plaintext
need to put the directory tree here
```

---

### Setup Instructions

1. **Install required libraries**
   ```bash
   pip install -r requirements.txt
   ```

2. **Data Sources**
   - Download the `raw_data` folder from [Google Drive - raw_data](https://drive.google.com/drive/folders/1on_qvHQRGojjqKvjmyLU28PDIuUAnTlc?usp=share_link)
   - Place it inside the `dataset/` folder:
     ```plaintext
     dataset/
     └── raw_data/
     ```

---

## Subgroup A - AI Image Synthesis and User Experience
## Q1: How can we develop an AI model to generate realistic product images based on user customization choices?


---
## Q2: What factors influence user satisfaction during the product customization process?

---

## Subgroup B – Inventory Management and Pricing Optimization

## Q1: 

---
## Q3: How can we implement a dynamic pricing model for customized products?

_Note on the Data Usage:_   
- _Due to the lack of pricing information of customized and base products (e.g price of floral dress vs plain dress) in the original Amazon dataset, we decide to bring in a new dataset ‘amazon_fashion_sales.csv’ for Part I solution._
- _Part II of our solution will still be based on original Amazon dataset as we want to tap on the trained random forest regressor in Q1 for demand forecasting_

### Workflow

1. **Run `customization_price_optimizer.py`**  
   Calculates the optimal price to charge for a product customization (e.g., color, engraving, size adjustment), based on historical customer behavior. It uses a fitted probability curve to model the likelihood of purchase at various customization prices and finds the value of `x` that maximizes expected profit.

2. **Run `demand_price_adjustment.py`**  
   Forecasts product demand for the next quarter using a trained Random Forest model and recommends an adjustment to the base selling price based on predicted demand relative to historical averages.

### Solution Explained

### Part I: `customization_price_optimizer.py`

The first step focuses on determining how much to charge customers for a product customization in order to maximize expected profit. 

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

After optimizing the customization charges, the next step is to adjust the selling price to reflect predicted market demand for the upcoming quarter. 
We will use the trained random forest regressor in Q1. 

After optimizing the customization charges, the next step is to adjust the selling price to reflect predicted market demand for the upcoming quarter. We will use the trained Random Forest regressor from Q1.

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

By combining both components that reflect the customization and demand changes, this solution creates a **data-driven dynamic pricing system**.

---


=======
## Data Fields
### For User Reviews
| Field | Type | Description |
| :--- | --- |--- |
| rating | float | Rating of the product (from 1.0 to 5.0). |
| title | str |Title of the user review. |
| text | str |Text body of the user review. |
| images | list |Images of the users post after they have received the product.Each image has different sizes(small,medium,large), represented by the small_image_url,medium_image_url,large_image_url respectively. |
| asin | str |ID of the product. |
| parent_asin | str |Parent ID of the product. Note: Products with different colors, styles, sizes usually belong to the same parent ID. **Please use parent ID to find product meta.** |
| user_id | str |ID of the reviewer. |
| timestamp | int |Time of the review (unix time). |
| verified_purchase | bool |User purchase verification. |
| helpful_vote | int |Helpful votes of the review. |

### For Item Metadata
| Field | Type | Description |
| :--- | --- |--- |
| main_category | str | Main category (i.e.,domain) of the product. |
| title | str |Name of the product. |
| average_rating | float |Rating of the product shown on the product page. |
| rating_number | int |Number of ratings in the product. |
| features | list |Bullet-point format features of the product. |
| description | list |Description of the product. |
| price | float |Price in US dollars (at time of crawling). |
| images | list |Images of the product. Each image has different sizes (thumb, large, hi_res). The “variant” field shows the position of image. |
| videos | list |Videos of the product including title and url. |
| store | str |Store name of the product. |
| categories | list |Hierarchical categories of the product. |
| details | dict |Product details, including materials, brand, sizes, etc. |
| parent_asin | str |Parent ID of the product. |
| bought_together | list |Recommended bundles from the websites. |

### **Table Relationships**
- **`reviews.parent_asin`** → **FK → `items.parent_asin`**  
  (Each review is associated with an item.)



