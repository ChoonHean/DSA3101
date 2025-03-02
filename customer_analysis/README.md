# Analyzing and finding ways to increase user satisfaction.
In this section, we would focus on how the potential relationships between user reviews and the items themselves. The scope of this would be limited to Amazon fashion.

## How to run
```
pip install -r requirements.txt
set_hf_env.bat
python -m main.py
```
Set your configurations in ```config/cofig.yaml``` based on the dataset(s) you would like to download.

Do note that due to the large dataset sizes, the ```main.py``` script might take a long time to run.


## Schema of raw data
For each item, there would be a corresponding review, as well as a corresponding metadata attached to it. The structure of the data obtained would be as follows.

### Reviews
|Field|Type|
|--|--|
|sort_timestamp|int|
|rating|float|
|helpful_votes|int|
|title|str|
|text|str|
|images|list|
|asin|str|
|verified_purchase|bool|
|parent_asin|str|
|user_id|str|

### Metadata
|Field|Type|
|--|--|
|main_category|str|
|title|str|
|average_rating|float|
|rating_number|int|
|features|list|
|description|list|
|price|float|
|images|list|
|videos|list|
|bought_together|list|
|store|str|
|categories|list|
|details|dict|
|parent_asin|str|

## Scehma of processed data

# 📄 Database Schema

## 🗄️ Table: `items`
| Column        | Data Type  | Constraints                |
|--------------|-----------|----------------------------|
| `item_id`    | `SERIAL`  | `PRIMARY KEY`              |
| `parent_asin`| `VARCHAR` | `NOT NULL UNIQUE`          |
| `title`      | `VARCHAR` | `NOT NULL`                 |
| `main_category` | `VARCHAR` | `NOT NULL`             |
| `store`      | `VARCHAR` | `NOT NULL`                 |

---

## 🗄️ Table: `item_metrics`
| Column        | Data Type  | Constraints                        |
|--------------|-----------|------------------------------------|
| `item_id`    | `INT`     | `FOREIGN KEY REFERENCES items(item_id) ON DELETE CASCADE` |
| `average_rating` | `FLOAT`  |                                  |
| `rating_number`  | `INTEGER` |                                |
| `price`      | `FLOAT`   | `NOT NULL`                        |
| **Constraint** | **`UNIQUE (item_id)`** | Ensures one row per item |

---

## 🗄️ Table: `reviews`
| Column        | Data Type  | Constraints                        |
|--------------|-----------|------------------------------------|
| `review_id`  | `INT`     | `PRIMARY KEY`                     |
| `asin`       | `VARCHAR` | `NOT NULL`                        |
| `rating`     | `FLOAT`   |                                    |
| `timestamp`  | `INTEGER` | `NOT NULL`                        |
| `helpful_vote` | `INTEGER` | `NOT NULL`                     |
| `verified_purchase` | `BOOLEAN` | `NOT NULL`                 |
| `title`      | `VARCHAR` |                                    |
| `text`       | `VARCHAR` |                                    |
| **Constraint** | **`FOREIGN KEY (review_id) REFERENCES items(item_id) ON DELETE CASCADE`** | Ensures referential integrity |

---

## 🔄 Relationships
- **One-to-One:** `item_metrics.item_id` → `items.item_id`
- **One-to-Many:** `reviews.review_id` → `items.item_id`
- **Foreign Key:** `reviews.review_id` references `items.item_id` (`ON DELETE CASCADE`)

---
