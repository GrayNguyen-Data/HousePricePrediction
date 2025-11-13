CREATE TABLE IF NOT EXISTS bronze.raw_data(
    id SERIAL PRIMARY KEY,
    title TEXT,
    address TEXT,
    area TEXT,
    floors TEXT,
    furniture TEXT,
    bedrooms TEXT,
    bathrooms TEXT,
    price TEXT,
    price_m2 TEXT,
    posted_date TEXT,
    link TEXT UNIQUE
)