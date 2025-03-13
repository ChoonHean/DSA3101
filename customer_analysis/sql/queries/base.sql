SELECT * FROM items
JOIN reviews ON items.parent_asin = reviews.parent_asin
WHERE verified_purchase = true