from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def handle_request(self, input_data):
        """
        Process input data and return agent-specific response.
        Must be implemented by subclasses.
        """
        pass
