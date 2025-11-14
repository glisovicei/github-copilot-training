"""
Unit tests for src.agents package.

Tests for DiscountAgent and RouteAnalyzer.
"""
import unittest
from src.agents.discount_agent import DiscountAgent
from src.agents.route_analyzer import RouteAnalyzer


class TestDiscountAgent(unittest.TestCase):
    def setUp(self):
        self.agent = DiscountAgent()

    def test_calculate_discount(self):
        route = "NYC-LAX"
        passenger_history = {"flights": 10, "last_flight": "2023-01-01"}
        discount = self.agent.calculate_discount(route, passenger_history)
        self.assertIsInstance(discount, float)


class TestRouteAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = RouteAnalyzer()

    def test_analyze_route(self):
        route = "NYC-LAX"
        insights = self.analyzer.analyze_route(route)
        self.assertIsInstance(insights, dict)


if __name__ == '__main__':
    unittest.main()
