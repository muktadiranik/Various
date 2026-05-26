# app/events/handlers.py
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventHandler:
    """Handle domain events and trigger appropriate actions"""

    def __init__(self):
        self._handlers: Dict[str, list] = {}
        self._running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

    def register(self, event_type: str, handler_func):
        """Register a handler for an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler_func)
        logger.info(f"Registered handler for event: {event_type}")

    async def dispatch(self, event_type: str, data: Dict[str, Any]):
        """Dispatch an event to all registered handlers"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler(event_type, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

    async def queue_event(self, event_type: str, data: Dict[str, Any]):
        """Queue an event for async processing"""
        await self._event_queue.put({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _process_events(self):
        """Background worker to process queued events"""
        while self._running:
            try:
                event = await self._event_queue.get()
                await self.dispatch(event["type"], event["data"])
                self._event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event queue: {e}")

    async def start(self):
        """Start the event processing worker"""
        if not self._worker_task or self._worker_task.done():
            self._running = True
            self._worker_task = asyncio.create_task(self._process_events())
            logger.info("Event handler worker started")

    async def stop(self):
        """Stop the event processing worker"""
        self._running = False
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Event handler worker stopped")


# Global event handler instance
event_handler = EventHandler()


# Example event handlers
async def on_message_created(event_type: str, data: Dict[str, Any]):
    """Handle message created event"""
    logger.debug(f"Message created: {data.get('message_id')}")


async def on_user_online(event_type: str, data: Dict[str, Any]):
    """Handle user online event"""
    logger.debug(f"User online: {data.get('user_id')}")


async def on_user_offline(event_type: str, data: Dict[str, Any]):
    """Handle user offline event"""
    logger.debug(f"User offline: {data.get('user_id')}")


# Register default handlers
event_handler.register("message_created", on_message_created)
event_handler.register("user_online", on_user_online)
event_handler.register("user_offline", on_user_offline)