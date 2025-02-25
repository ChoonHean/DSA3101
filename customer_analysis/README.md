# Analyzing and finding ways to increase user satisfaction.
In this section, we would focus on how the potential relationships between user reviews and the items themselves. The scope of this would be limited to Amazon fashion.

## How to run
```pip install -r requirements.txt```
Run ```set_hf_env.bat``` file to suppress warnings when downloading datasets.
Set your configurations in ```config/cofig.yaml``` based on the dataset(s) you would like to download.
```python -m main.py``` 
Do note that due to the large dataset sizes, the ```main.py``` script might take a long time to run.


## Structure of raw data
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

## 
For each category, we would structure them into databases with the following schema. 
