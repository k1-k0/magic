import logging
from typing import NoReturn
from aiohttp.web import (
    Application,
    get,
    run_app,
    static,
)

from magic.handlers import index, websocket_handler


logging.basicConfig(level=logging.DEBUG)


async def clear_websockets(app: Application) -> None:
    for websocket in app["websockets"].values():
        await websocket.close()

    app["websockets"].clear()


def main() -> NoReturn:
    app = Application()

    app.on_shutdown.append(clear_websockets)

    app.add_routes(
        routes=[
            get("/", index),
            get("/ws", websocket_handler),
            static("/", path="static")
        ]
    )

    app["websockets"] = {}
    app["game"] = None

    run_app(app=app)

    raise SystemExit


if __name__ == "__main__":
    main()
