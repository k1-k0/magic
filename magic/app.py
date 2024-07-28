from typing import NoReturn
from aiohttp.web import (
    Application,
    get,
    run_app,
)

from magic.handlers import hello, websocket_handler


async def clear_websockets(app: Application) -> None:
    for websocket in app["websockets"].values():
        await websocket.close()

    app["websockets"].clear()


def main() -> NoReturn:
    app = Application()

    app.on_shutdown.append(clear_websockets)

    app.add_routes(
        routes=[
            get("/", hello),
            get("/ws", websocket_handler),
        ]
    )

    app["websockets"] = {}
    app["game"] = None

    run_app(app=app)

    raise SystemExit


if __name__ == "__main__":
    main()
