import logging
from typing import Any, Dict, List
from core.event_bus.publisher import EventPublisher, EventHandler
from core.exceptions import EventDispatchException

logger = logging.getLogger(__name__)

class InMemoryEventPublisher(EventPublisher):
    def __init__(self):
        self._subscribers: Dict[type, List[EventHandler]] = {}

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug({"event": "event_subscribed", "event_type": event_type.__name__, "handler": handler.__name__})

    async def publish(self, event: Any) -> None:
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        logger.info({"event": "event_published", "event_type": event_type.__name__, "handler_count": len(handlers)})
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error({"event": "event_dispatch_failed", "event_type": event_type.__name__, "error": str(e)})
                raise EventDispatchException(message=f"Handler {handler.__name__} failed: {str(e)}")
