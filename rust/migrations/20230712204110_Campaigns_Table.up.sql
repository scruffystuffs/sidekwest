CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
) STRICT;