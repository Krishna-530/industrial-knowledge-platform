from core.event_bus.publisher import EventPublisher, EventHandler

__all__ = ["EventPublisher", "EventHandler"]
from core.event_bus.in_memory_publisher import InMemoryEventPublisher

# Global singleton for the application event bus
event_publisher = InMemoryEventPublisher()

def get_event_publisher() -> EventPublisher:
    return event_publisher
