# DSA3101
AI-driven merchandise customization platform for E-commerce

```
pip install -r requirements.txt
```
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
