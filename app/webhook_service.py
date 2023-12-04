# Standalone FastAPI server that submits events with webhook payloads.

from fastapi import FastAPI, Response, Request
from fastapi.background import BackgroundTasks
import json
from pathlib import Path
import uvicorn
from loguru import logger
from app.events.event_service import post_event, ReceiveHabiticaWebhookEvent, subscribe

webhook_fastapi_app = FastAPI()

# Create webhook endpoint
@webhook_fastapi_app.post('/webhook')
async def receive_webhook(data: Request, background_tasks: BackgroundTasks):
    data = await data.json()
    background_tasks.add_task(capture_webhook,data=data)
    return Response(status_code=202)

# Emit webhook event
async def capture_webhook(data):
    if "webhookType" in data:
        await post_event(ReceiveHabiticaWebhookEvent(data))
    else:
        logger.warning("Invalid webhook received")

# Save webhook events for dev purposes
async def handle_record_webhook(data: ReceiveHabiticaWebhookEvent):
    hook_type = data.payload['task']['type'] if 'task' in data.payload else 'other'
    path = Path(f"test\\sample_data\\{data.payload['webhookType']}-{hook_type}.json")
    logger.info(f"Recording webhook payload to {path}")
    with open(path, 'w') as fh:
        json.dump(data.payload, fh)

subscribe(ReceiveHabiticaWebhookEvent.type, handle_record_webhook)

if __name__ == "__main__":
    uvicorn.run(webhook_fastapi_app, host="0.0.0.0", port=12555)
