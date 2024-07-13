import logging
from typing import NoReturn
from aiohttp.web import Application, Request, Response, get, run_app, WebSocketResponse
from aiohttp import WSMsgType
from faker import Faker


log = logging.getLogger(__name__)


def get_random_name():
    fake = Faker()
    return fake.name()


async def hello(request: Request) -> Response:
    return Response(text="Hello, world!")


async def websocket_handler(request: Request):
    ws_current = WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return Response(text="not ready yet")

    await ws_current.prepare(request)

    name = request.query.get("name")
    log.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})

    # NOTE: name - websocket
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == WSMsgType.text:
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json({'action': 'sent', 'name': name, 'text': msg.data})
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current


async def clear_websockets(app: Application) -> None:
    for websocket in app['websockets'].values():
        await websocket.close()

    app['websockets'].clear()


def main() -> NoReturn:
    app = Application()

    app.on_shutdown.append(clear_websockets)

    app.add_routes(routes=[
        get("/", hello),
        get("/ws", websocket_handler),
    ])

    app['websockets'] = {}

    run_app(app=app)

    raise SystemExit


if __name__ == "__main__":
    main()
