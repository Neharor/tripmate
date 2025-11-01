from base_agent import BaseAgent

class DestinationAgent(BaseAgent):
    def __init__(self):
        super().__init__("DestinationAgent")

    def handle_request(self, input_data):
        # For now, return a static sample or simple logic
        return {"plan": "Sample destination plan based on " + str(input_data)}
