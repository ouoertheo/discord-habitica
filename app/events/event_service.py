import asyncio
from asyncio.coroutines import iscoroutine
from loguru import logger
from enum import Enum

# TODO: Separate out the rest of the events into their own module

################
## App Events ##
################

class ReceiveHabiticaWebhookEvent:
    'Provides raw payload for a webhook'
    type = "receive_habitca_webhook_event"
    def __init__(self, payload) -> None:
        self.payload = payload
    

##################
### Event Logic ##
##################

subscribers = {}

def subscribe(event_type: str, fcn):
    if not event_type in subscribers:
        subscribers[event_type] = []
    if fcn not in subscribers[event_type]:
        subscribers[event_type].append(fcn)
        logger.info(f"Registered `{event_type}` to function `{fcn.__name__}`")

async def post_event(event):
    if not event.type in subscribers:
        logger.warning(f"Posted event type {event.type} but no subscribers")
        return
    logger.info(f"Posted event type `{event.type}`, calling functions: `{[fcn.__name__ for fcn in subscribers[event.type]]}`")
    # Can't gather non-coroutines, so call sync functions first, then gather async functions.
    coroutines = []
    for fcn in subscribers[event.type]:
        return_val = fcn(event)
        if iscoroutine(return_val):
            coroutines.append(return_val)
    await asyncio.gather(*coroutines)