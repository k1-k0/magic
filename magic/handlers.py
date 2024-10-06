import asyncio
import json
import logging
from aiohttp.web import (
    Application,
    Request,
    Response,
    WebSocketResponse,
    StreamResponse,
    FileResponse,
)
from aiohttp import WSMsgType

from magic.models import (
    AnswersEvent,
    ConnectEvent,
    DisconnectEvent,
    HealthEvent,
    HitEvent,
    JoinEvent,
    QuestionEvent,
    AnswerEvent,
    TeamEvent,
)
from magic.types import Action
from magic.game import Game
from magic.utils import get_random_name, send_json


logger = logging.getLogger(__name__)


async def index(request: Request) -> StreamResponse:
    return FileResponse(path="static/index.html")


async def websocket_handler(request: Request) -> StreamResponse:
    ws_current = WebSocketResponse()

    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        logger.error(f"{ws_ready} websocket isn't ready yet")
        return Response(text="not ready yet")

    await ws_current.prepare(request)

    name = request.query.get("name", get_random_name())
    logger.info("%s joined.", name)

    await send_json(
        ws=ws_current,
        event=ConnectEvent(value=name),
    )

    for ws in request.app["websockets"].values():
        await send_json(ws=ws, event=JoinEvent(value=name))

    await send_json(
        ws=ws_current,
        event=TeamEvent(value=[name for name in request.app["websockets"].keys()]),
    )

    request.app["websockets"][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == WSMsgType.text:
            # TODO: add msg.data validation and graceful handle

            await handle_event(
                event_data=json.loads(msg.data),
                app=request.app,
                ws_current=ws_current,
            )
        else:
            break

    del request.app["websockets"][name]
    logger.info("%s disconnected.", name)
    for ws in request.app["websockets"].values():
        await send_json(ws=ws, event=DisconnectEvent(value=name))

    return ws_current


async def handle_event(
    event_data: dict[str, str], app: Application, ws_current: WebSocketResponse
) -> None:
    event_action = event_data["action"]

    if event_action == Action.START:
        await start(app=app)
    elif event_action == Action.ANSWER:
        event = AnswerEvent.model_validate(obj=event_data)
        await answer(app=app, ws=ws_current, event=event)
    else:
        logger.error(f"Unsupported event action '{event_action}'")


async def start(app: Application) -> None:
    websockets = app["websockets"]
    game = Game(players=len(websockets))
    app["game"] = game

    answers = game.answers
    for i, ws in enumerate(app["websockets"].values()):
        await send_json(ws=ws, event=AnswersEvent(value=answers[i]))

    active_questions = game.active_questions
    for i, ws in enumerate(app["websockets"].values()):
        question = active_questions[i]
        game.set_owner(question=question.text, websocket=ws)

        question.set_sent_time()
        await send_json(ws=ws, event=QuestionEvent(value=question.text))


async def answer(app: Application, ws: WebSocketResponse, event: AnswerEvent) -> None:
    game: Game = app["game"]
    # TODO: add check that game exists

    old_question, new_question, hit = game.check_answer(answer=event.value)

    if hit:
        # TODO: вынести в отдельную функцию общего оповещения
        for websocket in app["websockets"].values():
            await asyncio.gather(
                send_json(ws=websocket, event=HitEvent(value=hit)),
                send_json(ws=websocket, event=HealthEvent(value=game.health)),
            )

    if new_question:
        # TODO: нужно рефакторить процесс поиска владельца вопроса
        question_owner_websocket = game.get_owner(question=old_question.text)
        game.set_owner(question=new_question.text, websocket=question_owner_websocket)

        new_question.set_sent_time()
        await send_json(
            ws=question_owner_websocket, event=QuestionEvent(value=new_question.text)
        )
