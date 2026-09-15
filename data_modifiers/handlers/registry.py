from data_modifiers.handlers.base import BaseFormatHandler
from data_modifiers.handlers.binary_handler import BinaryHandler
from data_modifiers.handlers.csv_handler import CSVHandler
from data_modifiers.handlers.fallback_handler import FallbackHandler
from data_modifiers.handlers.json_handler import JSONHandler
from data_modifiers.handlers.xml_handler import XMLHandler


class HandlerRegistry:

    def __init__(self):
        self._handlers: dict[str, BaseFormatHandler] = {
            ".json": JSONHandler(),
            ".csv": CSVHandler(),
            ".xml": XMLHandler(),
            ".html": XMLHandler(),
            ".jpg": BinaryHandler(),
            ".png": BinaryHandler(),
        }
        self._fallback = FallbackHandler()

    def get_handler(
        self, extension: str, is_binary: bool = False
    ) -> BaseFormatHandler:
        if is_binary:
            return self._handlers.get(extension.lower(), BinaryHandler())
        return self._handlers.get(extension.lower(), self._fallback) 