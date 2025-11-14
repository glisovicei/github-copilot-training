"""
Unit tests for src.data package.

Tests for Database and Preprocessor classes.
"""
import unittest
from src.data.database import Database
from src.data.preprocessor import Preprocessor


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.connect()

    def test_fetch_data(self):
        query = "SELECT * FROM predictions;"
        result = self.db.fetch_data(query)
        self.assertIsInstance(result, list)


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = Preprocessor()

    def test_preprocess_data(self):
        raw_data = [{"feature1": 1.0, "feature2": 2.0}, {"feature1": 2.0, "feature2": 3.0}]
        processed_data = self.preprocessor.preprocess_data(raw_data)
        self.assertEqual(len(processed_data), 2)


if __name__ == '__main__':
    unittest.main()
