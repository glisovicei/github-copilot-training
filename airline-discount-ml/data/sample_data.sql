-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_data TEXT NOT NULL,
    predicted_value REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data into all tables
INSERT OR IGNORE INTO passengers (name, travel_history) VALUES
    ('John Smith', '{"flights": 10, "miles": 5000}'),
    ('Jane Doe', '{"flights": 25, "miles": 15000}'),
    ('Bob Johnson', '{"flights": 5, "miles": 2500}');

INSERT OR IGNORE INTO routes (origin, destination, distance) VALUES
    ('New York', 'London', 3459.0),
    ('Los Angeles', 'Tokyo', 5478.0),
    ('San Francisco', 'Paris', 5558.0);

INSERT OR IGNORE INTO discounts (passenger_id, route_id, discount_value) VALUES
    (1, 1, 15.0),
    (2, 2, 25.0),
    (3, 3, 10.0);

INSERT OR IGNORE INTO predictions (input_data, predicted_value) VALUES
    ('{"feature1": 1.0, "feature2": 2.0}', 3.5),
    ('{"feature1": 2.0, "feature2": 3.0}', 4.5),
    ('{"feature1": 3.0, "feature2": 4.0}', 5.5);