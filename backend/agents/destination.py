from .base_agent import BaseAgent

class DestinationAgent(BaseAgent):
    def __init__(self):
        super().__init__("DestinationAgent")

    def handle_request(self, input_data):
        # Return an array of destinations as expected by the frontend
        return {
            "plan": [
                f"Suggested destination based on: {str(input_data)}",
                "Sample attraction 1",
                "Sample attraction 2"
            ]
        }
