from abc import ABC, abstractmethod

class Task(ABC):
    @abstractmethod
    def execute(self, query: str) -> str:
        """Executes the task with the given query and returns a string result."""
        pass
