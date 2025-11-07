import asyncio
from collections import defaultdict
from typing import AsyncGenerator
from app.domain.message.schema import MessageOut
import json


subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)


async def broadcast(chat_id: str, message: MessageOut):
    for queue in subscribers[chat_id]:
        await queue.put(message.model_dump())


async def subscribe(chat_id: str) -> AsyncGenerator[str, None]:
    queue: asyncio.Queue[dict] = asyncio.Queue()
    subscribers[chat_id].append(queue)

    try:
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=15)
                yield f"data: {json.dumps(msg)}\n\n"
            except asyncio.TimeoutError:
                # Keep-alive ping (to prevent proxy/client disconnect)
                yield ": keep-alive\n\n"
    finally:
        subscribers[chat_id].remove(queue)
