# Configuration settings for the airline discount machine learning project

DATABASE_URL = "postgresql://user:password@localhost:5432/airline_discount_db"
MODEL_PATH = "models/discount_model.pkl"
LOG_LEVEL = "INFO"
DISCOUNT_THRESHOLD = 0.1
FEATURES = ["feature1", "feature2", "feature3"]