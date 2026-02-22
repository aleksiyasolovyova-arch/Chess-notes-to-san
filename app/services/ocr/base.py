from abc import ABC, abstractmethod


class OCRProvider(ABC):

    @abstractmethod
    def recognize(self, image_bytes: bytes) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...