import asyncio

class CancellationToken:
    """
    A token used to signal cancellation across asynchronous boundaries.
    Allows API requests (e.g. client disconnect) to cleanly cancel deep workflows.
    """
    def __init__(self):
        self._event = asyncio.Event()

    def cancel(self):
        """Signal that cancellation is requested."""
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._event.is_set()

    async def wait(self):
        """Wait until cancellation is requested."""
        await self._event.wait()
