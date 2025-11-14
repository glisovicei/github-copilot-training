class DiscountAgent:
    def calculate_discount(self, route, passenger_history):
        # Implement logic to calculate customized discount based on route and passenger history
        discount = 0.0
        # Example logic (to be replaced with actual implementation)
        trips = passenger_history.get('flights', passenger_history.get('history_trips', passenger_history.get('trips', 0)))
        if trips > 5:
            discount += 10
        if isinstance(route, dict) and route.get('distance', 0) > 1000:
            discount += 5
        return discount