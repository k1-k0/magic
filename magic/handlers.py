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
from faker import Faker

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


logger = logging.getLogger(__name__)


def get_random_name():
    fake = Faker()
    return fake.name()


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

    # TODO: ensure ascii here
    await ws_current.send_json(data=ConnectEvent(value=name).model_dump())

    for ws in request.app["websockets"].values():
        # TODO: ensure ascii here
        await ws.send_json(data=JoinEvent(value=name).model_dump())

    # TODO: ensure ascii here
    await ws_current.send_json(
        data=TeamEvent(
            value=[name for name in request.app["websockets"].keys()]
        ).model_dump(),
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
        # TODO: ensure ascii here
        await ws.send_json(data=DisconnectEvent(value=name).model_dump())

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

    answers = game.answers()
    for i, ws in enumerate(app["websockets"].values()):
        json_data = json.dumps(
            AnswersEvent(value=answers[i]).model_dump(), ensure_ascii=False
        )
        await ws.send_str(data=json_data)

    active_questions = game.active_questions()
    for i, ws in enumerate(app["websockets"].values()):
        question = active_questions[i]
        game.set_owner(question=question.text, websocket=ws)
        data = json.dumps(
            QuestionEvent(value=question.text).model_dump(),
            ensure_ascii=False,
        )
        await ws.send_str(data=data)


async def answer(app: Application, ws: WebSocketResponse, event: AnswerEvent) -> None:
    game: Game = app["game"]

    # TODO: add check that game exists

    old_question, new_question, hit = game.check_answer(answer=event.value)

    if not new_question and hit:
        # TODO: make function for notify all websockets
        for websocket in app["websockets"].values():
            data = json.dumps(HitEvent(value=hit).model_dump(), ensure_ascii=False)
            await websocket.send_str(data=data)

            data = json.dumps(
                HealthEvent(value=game.health()).model_dump(), ensure_ascii=False
            )
            await websocket.send_str(data=data)

        return

    if new_question and old_question and not hit:
        # TODO: нужно рефакторить процесс поиска владельца вопроса 
        question_owner_websocket = game.get_owner(question=old_question.text)
        game.set_owner(question=new_question.text, websocket=question_owner_websocket)

        data = json.dumps(
            QuestionEvent(value=new_question.text).model_dump(), ensure_ascii=False
        )
        await question_owner_websocket.send_str(data=data)
