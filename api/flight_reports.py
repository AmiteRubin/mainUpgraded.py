import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated, Union

from beanie import Link
from beanie.odm.operators.find.comparison import GTE
from fastapi import Depends, APIRouter, HTTPException, Form
from pydantic import BaseModel, Field, BeforeValidator
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from webapp5353.common.consts import QueryStartDate
from webapp5353.models.core import User, MissionReport, Team, RbacRole, ComponentIdType, MissionReportForm
from webapp5353.services.auth import get_current_team_member

AuthTeamMemeber = Annotated[User, Depends(get_current_team_member)]

router = APIRouter(prefix='/api/v1/flights', tags=['Flight Reports'])
BASE_PATH = Path(__file__)
templates_dir = BASE_PATH.parent.parent / 'templates'
templates = Jinja2Templates(directory=str(templates_dir))


class NameOnlyProjection(BaseModel):
    first_name: str
    last_name: str


class TeamName(BaseModel):
    name: str


@router.get('/team/flight/start', response_class=HTMLResponse)
async def get_report_takeoff(request: Request):
    user_names, team_names = await asyncio.gather(
        User.find(User.role == RbacRole.TEAM_MEMBER).project(NameOnlyProjection).to_list(),
        Team.find_all().project(TeamName).to_list()
    )
    return templates.TemplateResponse(
        request=request,
        name="report_takeoff.html",
        context={'operators_list': [f'{u.first_name} {u.last_name}' for u in user_names],
                 'teams_list': [u.name for u in team_names]}
    )


@router.post('team/flight/start', response_class=HTMLResponse)
async def report_takeoff(request: Request, form: MissionReportForm = Form(...)):
    team = await Team.find_one(Team.name == form.team_name)
    existing_mission_bool = MissionReport.find(
        MissionReport.team.id == team.id,
        MissionReport.landing_time == None  # it means that the team's UAV is still on air
    ).exists()
    if existing_mission_bool:
        raise HTTPException(status_code=400, detail="Active mission found")
        #i can give the user the flight that is now on going!
    """
    team = await Team.find_one(Team.name == form.team_name)
    existing_mission = MissionReport.find(
        MissionReport.team.id == team.id,
        MissionReport.landing_time == None  # it means that the team's UAV is still on air
    )
    if existing_mission_bool:
        raise HTTPException(status_code=400, detail="Active mission found")
        return templates.TemplateResponse(request=request, name="index.html")
    """
    # now i'd like to take in all the parameters given by the front end, as fields in the form
    else:
        mission_report = MissionReport.from_form(form=form, team=team)
        await mission_report.save()
        logging.info(f'new mission created for team; {team.name}')

    return templates.TemplateResponse(request=request, name="index.html")


# in report landing, we will have an automation that reports malfunctioned parts to Amlach
@router.post('/team/flight/close')
async def report_landing(user: AuthTeamMemeber) -> MissionReport:
    current_mission = await MissionReport.find(
        MissionReport.team.id == user.team_id,
        MissionReport.landing_time == None  # noqa
    ).first_or_none()

    if current_mission is None:
        raise HTTPException(status_code=400, detail="No active mission found")

    current_mission.landing_time = datetime.now()  # it should be given as a parameter by the operator, not necessarily "now"
    await current_mission.save()
    return current_mission


@router.post('/team/flight/report')
async def report_flight(user: AuthTeamMemeber, request_form: MissionReport):
    # we will need to do validation to the data input-ed by the operators
    await request_form.save()
    return request_form


# is router.post(...) here alright? or there is a need to do both get and post for it, as it can show the teams equipment
# and the users can modify it accordingly.
# maybe it will be better to have one template for viewing, and one template for modifying...
@router.post('/team/uav_equipment')
async def manage_uav_equipment(user: AuthTeamMemeber): ...


# here the team will have access to view its equipment, nd if necessary it'll change stuff like Central Wing etc.


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
