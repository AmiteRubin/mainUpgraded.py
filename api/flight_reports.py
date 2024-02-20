from datetime import datetime
from typing import Annotated

from beanie.odm.operators.find.comparison import GTE
from fastapi import Depends, APIRouter, HTTPException

from webapp5353.common.consts import QueryStartDate
from webapp5353.models.core import User, MissionReport
from webapp5353.services.auth import get_current_team_member

AuthTeamMemeber = Annotated[User, Depends(get_current_team_member)]

router = APIRouter(prefix='/api/v1/flights', tags=['Flight Reports'])


@router.post('/team/flight/start')
async def report_takeoff(user: AuthTeamMemeber): ...

@router.post('/team/flight/close')
async def report_landing(user: AuthTeamMemeber) -> MissionReport:
    current_mission = await MissionReport.find(
        MissionReport.team.id == user.team_id,
        MissionReport.landing_time == None  # noqa
    ).first_or_none()

    if current_mission is None:
        raise HTTPException(status_code=400, detail="No active mission found")

    current_mission.landing_time = datetime.now()
    await current_mission.save()
    return current_mission


@router.post('/team/flight')
async def report_flight(user: AuthTeamMemeber):
    print('hi')


@router.get('/team')
async def team_report(
        user: AuthTeamMemeber,
        start_date: Annotated[datetime | None, QueryStartDate] = None
) -> list[MissionReport]:
    missions = MissionReport.find(MissionReport.team.id == user.team_id)
    if start_date:
        missions = missions.find(GTE(MissionReport.created_at, start_date))
    # return await missions.to_list()
    # TOOD: add rendering of the templates
