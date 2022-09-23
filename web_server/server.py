
from quart import Quart, request
import json
import logging
from discord_habitica import bot

logger = logging.getLogger(__name__)
app = Quart(__name__)

def 

@app.route("/habitica", methods=['POST'])
async def habitica_listener():
    webhook_json = json.loads(await request.data)
    if "webhookType" in webhook_json:
        if webhook_json["webhookType"] == "groupChatReceived": # TODO: Generalize this better
            logger.debug(webhook_json)
            await bot.handle_webhook(webhook_json)
    else:
        logger.error("Malformed webhook invocation")
    return ""
