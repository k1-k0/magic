from enum import StrEnum
import logging
from aiohttp.web import (
    Request,
    Response,
    WebSocketResponse,
    StreamResponse,
)
from aiohttp import WSMsgType
from faker import Faker


logger = logging.getLogger(__name__)


def get_random_name():
    fake = Faker()
    return fake.name()


async def hello(request: Request) -> Response:
    return Response(text="Hello, world!")


async def websocket_handler(request: Request) -> StreamResponse:
    ws_current = WebSocketResponse()

    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        logger.error(f"{ws_ready} websocket isn't ready yet")
        return Response(text="not ready yet")

    await ws_current.prepare(request)

    name = request.query.get("name", get_random_name())
    logger.info("%s joined.", name)

    await ws_current.send_json({"action": "connect", "name": name})

    for ws in request.app["websockets"].values():
        await ws.send_json({"action": "join", "name": name})

    # NOTE: name - websocket
    request.app["websockets"][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == WSMsgType.text:
            # TODO: в msg.data сообщения в заданном протоколе
            for ws in request.app["websockets"].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {
                            "action": "sent",
                            "name": name,
                            "text": msg.data,
                        },
                    )
        else:
            break

    del request.app["websockets"][name]
    logger.info("%s disconnected.", name)
    for ws in request.app["websockets"].values():
        await ws.send_json({"action": "disconnect", "name": name})

    return ws_current
