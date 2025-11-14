from .base_agent import BaseAgent

class StaysAgent(BaseAgent):
    def __init__(self):
        super().__init__("StaysAgent")

    def handle_request(self, input_data):
        # Abhi simple static stay suggestions return kar rahe hain
        return {"stays": ["Hotel Sunshine", "Cozy Inn", "Budget Stay"]}
