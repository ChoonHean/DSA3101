## Project 5: AI-Driven Merchandise Customization Platform for E-commerce



### Overview

In the rapidly evolving world of e-commerce, merchants face increasing competition to provide personalized shopping
experiences for customers.
However, traditional methods of inventory management and product customization have significant limitations.
E-commerce platforms typically rely on pre-made product images and static inventory, which restricts customers' ability
to customize items according to their preferences.
This leads to challenges in customer satisfaction, missed sales opportunities, and inefficient use of resources.


### Repository Structure

| Folder/File                     | Description                                          |
|---------------------------------|------------------------------------------------------|
| `group_a`                       | Group A code                                         |
| `group_b`                       | Group B code                                         |
| `group_b/data`                  | Clean and transformed data for use in Group B's code |
| `group_b/data_cleaning_scripts` | Scripts used to clean and transform the raw data     |
| `group_b/demand`                | Contains scripts for predicting demand               |
| `group_b/inventory`             | Contains scripts for inventory management            |
| `group_b/pricing`               | Contains scripts for pricing optimization            |
| `raw_data`                      | The raw jsonl files that contains the data used      |
| `README.md`                     | Project documentation                                |
| `requirements.txt`              | Dependencies list                                    |

---

### Setup Instructions

1. **Install required libraries**
   ```bash
   pip install -r requirements.txt
   ```

2. **Data Sources**
    - Download the `raw_data` folder
      from [Google Drive - raw_data](https://drive.google.com/drive/folders/1on_qvHQRGojjqKvjmyLU28PDIuUAnTlc?usp=share_link)
    - Place it inside the `raw_data/` folder.
3. For specific instructions on how to run each part of the project,
   refer to the READMEs in the respective directories.

---

## Data Fields

| Field             | Type  | Description                                                                                                                                                                                         |
|:------------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| rating            | float | Rating of the product (from 1.0 to 5.0).                                                                                                                                                            |
| title             | str   | Title of the user review.                                                                                                                                                                           |
| text              | str   | Text body of the user review.                                                                                                                                                                       |
| images            | list  | Images of the users post after they have received the product.Each image has different sizes(small,medium,large), represented by the small_image_url,medium_image_url,large_image_url respectively. |
| asin              | str   | ID of the product.                                                                                                                                                                                  |
| parent_asin       | str   | Parent ID of the product. Note: Products with different colors, styles, sizes usually belong to the same parent ID. **Please use parent ID to find product meta.**                                  |
| user_id           | str   | ID of the reviewer.                                                                                                                                                                                 |
| timestamp         | int   | Time of the review (unix time).                                                                                                                                                                     |
| verified_purchase | bool  | User purchase verification.                                                                                                                                                                         |
| helpful_vote      | int   | Helpful votes of the review.                                                                                                                                                                        |

### For Item Metadata

| Field           | Type  | Description                                                                                                                    |
|:----------------|-------|--------------------------------------------------------------------------------------------------------------------------------|
| main_category   | str   | Main category (i.e., domain) of the product.                                                                                   
| title           | str   | Name of the product.                                                                                                           |
| average_rating  | float | Rating of the product shown on the product page.                                                                               |
| rating_number   | int   | Number of ratings in the product.                                                                                              |
| features        | list  | Bullet-point format features of the product.                                                                                   |
| description     | list  | Description of the product.                                                                                                    |
| price           | float | Price in US dollars (at time of crawling).                                                                                     |
| images          | list  | Images of the product. Each image has different sizes (thumb, large, hi_res). The “variant” field shows the position of image. |
| videos          | list  | Videos of the product including title and url.                                                                                 |
| store           | str   | Store name of the product.                                                                                                     |
| categories      | list  | Hierarchical categories of the product.                                                                                        |
 details         | dict  | Product details, including materials, brand, sizes, etc.                                                                       |
| parent_asin     | str   | Parent ID of the product.                                                                                                      |
| bought_together | list  | Recommended bundles from the websites.                                                                                         |

### **Table Relationships**
- **`reviews.parent_asin`** → **FK → `items.parent_asin`**  
  (Each review is associated with an item.)
