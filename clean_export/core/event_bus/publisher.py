from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

EventHandler = Callable[[Any], Awaitable[None]]

class EventPublisher(ABC):
    @abstractmethod
    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        pass

    @abstractmethod
    async def publish(self, event: Any) -> None:
        pass
