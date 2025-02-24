# Analyzing and finding ways to increase user satisfaction.
In this section, we would focus on how the potential relationships between user reviews and the items themselves. The scope of this would be limited to Amazon fashion.

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
|images|list (dict(str:str))|
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
|features|list(str)|
|description|list(str)|
|price|float|
|images|list(dict(str:str))|
|videos|list(dict(str:str))|
|bought_together|list|
|store|str|
|categories|list(str)|
|details|dict(str:str)|
|parent_asin|str|