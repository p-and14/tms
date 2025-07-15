import asyncio
import logging

import config

from src.messaging.consumers import send_message

log = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        asyncio.run(send_message())
    except (asyncio.CancelledError, KeyboardInterrupt) as e:
        pass
