from datetime import datetime
from typing import Annotated

from beanie import Link
from beanie.odm.operators.find.comparison import GTE
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from webapp5353.common.consts import QueryStartDate
from webapp5353.models.core import User, MissionReport, Team
from webapp5353.services.auth import get_current_team_member, get_current_hamal_user

AuthHamal = Annotated[User, Depends(get_current_hamal_user)]

router = APIRouter(prefix='/api/v1/flights', tags=['Flight Reports'])


@router.get('/hamal/dashboard/{varone}')
async def dashboard(user: AuthHamal) -> list[MissionReport]:
    # we will need to do validation to the data input-ed by the operators
    current_missions = await MissionReport.find(
        MissionReport.landing_time == None  # noqa
    ).to_list()
    return current_missions


@router.post('/hamal/manage_users')
async def dashboard(user: AuthHamal): ...
