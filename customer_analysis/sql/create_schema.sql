CREATE TABLE IF NOT EXISTS items (
    item_id SERIAL PRIMARY KEY,
    parent_asin VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    main_category VARCHAR NOT NULL,
    store VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS item_metrics (
    item_id INT NOT NULL,
    average_rating FLOAT,
    rating_number INTEGER,
    price FLOAT NOT NULL,
    CONSTRAINT fk_item_metrics FOREIGN KEY (item_id)
        REFERENCES items(item_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT unique_item_metrics UNIQUE (item_id)
);


CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR PRIMARY KEY,
    asin NOT NULL VARCHAR,
    rating FLOAT,
    timestamp NOT NULL INTEGER,
    helpful_vote NOT NULL INTEGER,
	verified_purchase NOT NULL BOOLEAN
    title VARCHAR,
    text VARCHAR,
    CONSTRAINT fk_reviews FOREIGN KEY (asin) 
        REFERENCES items(item_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
