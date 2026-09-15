from abc import ABC, abstractmethod


class BaseFormatHandler(ABC):

    @abstractmethod
    def add_unique_entropy(self, content: str | bytes, token: str) -> str | bytes:
        """Injects format-valid token entropy into content."""
        pass

    @abstractmethod
    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str | bytes, str]:
        """Applies format-specific structural corruptions."""
        pass