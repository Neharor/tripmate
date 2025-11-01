from base_agent import BaseAgent
from destination import DestinationAgent
from stays import StaysAgent
# import other agents similarly

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("OrchestratorAgent")
        self.destination_agent = DestinationAgent()
        self.stays_agent = StaysAgent()
        # initialize other agents similarly

    def handle_request(self, input_data):
        # Example: delegate to destination and stays agents
        destination_result = self.destination_agent.handle_request(input_data)
        stays_result = self.stays_agent.handle_request(input_data)
        # Combine responses into a single result dictionary
        combined_result = {
            "destinations": destination_result,
            "stays": stays_result
            # include other agent results when added
        }
        return combined_result
