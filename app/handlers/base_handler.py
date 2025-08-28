# app/handlers/base_handler.py
from abc import ABC, abstractmethod

class BaseHandler(ABC):
    """
    Abstract base class for all command handlers.
    Ensures that each handler has a consistent interface.
    """
    
    @abstractmethod
    def handle(self, *args, **kwargs):
        """
        The main method to execute the handler's logic.
        This method must be implemented by all concrete handlers.
        """
        pass
