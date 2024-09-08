from aiohttp.web import WebSocketResponse
import json
from faker import Faker

from magic.models import Event


async def send_json(ws: WebSocketResponse, event: Event) -> None:
    data = json.dumps(obj=event.model_dump(), ensure_ascii=False)
    await ws.send_str(data=data)


def get_random_name():
    fake = Faker()
    return fake.name()
