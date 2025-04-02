# Analyzing and finding ways to increase user satisfaction.

In this section, we would focus on how the potential relationships between user reviews and the items themselves. The
scope of this would be limited to Amazon fashion.

---

## How to run

Download postgresql and create a database [here](https://www.postgresql.org/)

```
python customer_anlysis.py
```

Set your configurations in ```config/cofig.yaml``` based on the dataset(s) you would like to download.

Do note that due to the large dataset sizes, ```customer_analysis.py``` script might take a long time to run.

Our insights are present in ```report.md```.
---

## Raw data schema

For each item, there would be a corresponding review, as well as a corresponding metadata attached to it. The structure
of the data obtained would be as follows. [structure](https://amazon-reviews-2023.github.io/)

## Database Schema

### 📌 Items Table

| Column Name      | Data Type | Constraints   | Description                    |
|------------------|-----------|---------------|--------------------------------|
| `parent_asin`    | `VARCHAR` | `PRIMARY KEY` | Unique identifier for the item |
| `title`          | `VARCHAR` | `NOT NULL`    | Title of the item              |
| `main_category`  | `VARCHAR` | `NOT NULL`    | Main category of the item      |
| `store`          | `VARCHAR` | -             | Store selling the item         |
| `average_rating` | `FLOAT`   | -             | Average rating of the item     |
| `rating_number`  | `INTEGER` | -             | Number of ratings received     |
| `price`          | `FLOAT`   | `NOT NULL`    | Price of the item              |

---

### 📌 Reviews Table

| Column Name         | Data Type   | Constraints   | Description                                   |
|---------------------|-------------|---------------|-----------------------------------------------|
| `review_id`         | `SERIAL`    | `PRIMARY KEY` | Unique identifier for the review              |
| `parent_asin`       | `VARCHAR`   | `NOT NULL`    | Foreign key referring to `items(parent_asin)` |
| `rating`            | `FLOAT`     | -             | Rating given in the review                    |
| `timestamp`         | `TIMESTAMP` | `NOT NULL`    | Timestamp of when the review was posted       |
| `helpful_vote`      | `INTEGER`   | `NOT NULL`    | Number of helpful votes received              |
| `verified_purchase` | `BOOLEAN`   | `NOT NULL`    | Whether the reviewer purchased the item       |
| `title`             | `VARCHAR`   | -             | Title of the review                           |
| `text`              | `VARCHAR`   | -             | Full text content of the review               |

---

### 🔗 **Table Relationships**

- **`reviews.parent_asin`** → **FK → `items.parent_asin`**  
  (Each review is associated with an item.)

