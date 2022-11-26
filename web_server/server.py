from quart import Quart, request
import json
import logging
from discord_habitica import bot
from habitica.habitica_service import habitica

logger = logging.getLogger(__name__)
app = Quart(__name__)

@app.route("/habitica", methods=['POST'])
async def habitica_listener():
    """
    Listen for Habitica Webhooks. 
    """
    request = json.loads(await request.data)
    user_id = request["data"]["user"]["id"]
    if user_id in habitica.users:


    if "webhookType" in request:
        if request["webhookType"] == "groupChatReceived": # TODO: Generalize this better
            logger.debug(request)
            await bot.handle_webhook(request)
    else:
        logger.error("Malformed webhook invocation")
    return ""

