import asyncio
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from webapp5353.api.flight_control import router as dashboard_router
from webapp5353.api.flight_reports import router as reports_router
from webapp5353.common.db import init_db
from webapp5353.models.core import Team, UavComponent, UserInvitation, User, MissionReport


@asynccontextmanager
async def lifespan(app):
    await init_db([Team, UavComponent, UserInvitation, User, MissionReport])
    yield
    print('tamut')


BASE_PATH = Path(__file__)
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_PATH.parent / 'templates')), name="static")
app.add_middleware(SessionMiddleware, secret_key='beastmistake')
app.include_router(dashboard_router)
app.include_router(reports_router)


@app.get('/ping')
def ping():
    return {
        'msg': 'pong'
    }


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
