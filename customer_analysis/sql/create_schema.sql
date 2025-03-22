CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS items (
    parent_asin VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    main_category VARCHAR NOT NULL,
    store VARCHAR,
    average_rating FLOAT,
    rating_number INTEGER,
    price FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    parent_asin VARCHAR NOT NULL,
    rating FLOAT,
    timestamp TIMESTAMP NOT NULL,
    helpful_vote INTEGER NOT NULL,
	verified_purchase BOOLEAN NOT NULL,
    title VARCHAR,
    text VARCHAR
);

