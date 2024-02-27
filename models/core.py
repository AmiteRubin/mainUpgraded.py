import asyncio
from datetime import datetime
from enum import Enum
from typing import Union, TypeVar

from beanie import Document, PydanticObjectId, Link
from pydantic import Field, BaseModel
from pymongo import IndexModel

from webapp5353.common.db import init_db

ComponentIdType = TypeVar('ComponentIdType', bound=str)
UserId = TypeVar('UserId', bound=PydanticObjectId)


class UavComponent(Document):
    type: str
    id_number: ComponentIdType
    flight_time: float
    last_maintenance: datetime
    number_of_excepetional_events: int


class Team(Document):
    leader: Link['User']
    company: str


class RbacRole(str, Enum):
    ADMIN = 'admin'
    TEAM_MEMBER = 'team_member'
    TEAM_LEADER = 'team_leader'
    HAMAL = 'hamal'
    AMLACH = 'amlach'


class RoleAssignment(BaseModel):
    role: RbacRole
    edit_man_power: bool = False
    edit_missions: bool = True
    reports_access: bool = True


class User(Document):
    first_name: str
    last_name: str
    email: str
    role: RbacRole
    hashed_password: str
    team: Link[Team] | None = None

    class Settings:
        indexes = [IndexModel([('email', 1)], unique=True)]

    @property
    def team_id(self) -> PydanticObjectId | None:
        if not self.team:
            return None
        if isinstance(self.team, Link):
            return self.team.ref.id
        return self.team.id


class UserInvitation(Document):
    invitee_email: str
    inviter: Link[User]
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class MissionReportFieldsMixin(BaseModel):
    takeoff_time: datetime
    landing_time: Union[datetime, None] = None
    location: str
    mission_purpose: str = ''
    central_wing: ComponentIdType
    left_dihedral: ComponentIdType
    right_dihedral: ComponentIdType
    boom_tail: ComponentIdType
    boom_engine: ComponentIdType
    height_Rudder: ComponentIdType
    battery: ComponentIdType
    gps_transmitter: ComponentIdType
    payload: ComponentIdType
    pod: ComponentIdType
    operator_1: str
    operator_2: str
    operator_3: str
    operator_4: str

    date_reported: datetime = Field(default_factory=datetime.today)


class MissionReportForm(BaseModel):
    team_name: str = Field(description='the team name to associate a mission to')


class MissionReport(Document, MissionReportFieldsMixin):
    team: Link[Team]

    @classmethod
    def from_form(cls, form: MissionReportForm, team: Team):
        as_dict = form.model_dump(exclude={'team_name'})
        return cls(**as_dict, team=team)
