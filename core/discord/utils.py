import json
import textwrap

from loguru import logger
import requests

from core.discord import config as discord_config

_CHAR_LIMIT = 2000


def send(message: str, image_url: str | None = None) -> None:
    config = discord_config.load_config()
    embeds = []

    if not config.webhook:
        logger.warning("discord dev_webhook is not set. Skip sending message to dev.")
        return

    if image_url:
        embeds = [{"image": {"url": image_url}}]

    try:
        response = requests.post(
            url=config.webhook,
            data=json.dumps(
                {
                    "content": textwrap.dedent(message),
                    "embeds": embeds,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to send message to dev: {e}") from e


def send_messages(message: str | list[str], character_limit: int = _CHAR_LIMIT) -> None:
    if isinstance(message, str):
        message = [message]

    message_chunk = ""

    for i, msg in enumerate(message):
        if len(message_chunk) + len(msg) > character_limit:
            send(message_chunk)
            message_chunk = msg

        else:
            message_chunk = "\n".join([message_chunk, msg])
