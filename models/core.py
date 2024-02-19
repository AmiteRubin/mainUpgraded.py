from datetime import datetime, date
from enum import Enum
from typing import Self

import pymongo
from fastapi import HTTPException
from passlib.context import CryptContext
from beanie import Document, PydanticObjectId, Link, BackLink
from pydantic import ValidationError, Field, BaseModel
from pymongo import IndexModel
from starlette.requests import Request


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
    team: Link[Team] | None

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


class MissionReport(Document):
    team: Link[Team]

    takeoff_time: datetime
    landing_time: datetime | None
    location: str
    mission_purpose: str = ''
    central_wing: str
    left_dihedral: str
    right_dihedral: str
    boom_tail: str
    boom_engine: str
    height_Rudder: str
    battery: str
    gps_transmitter: str
    payload: str
    pod: str
    operator_1: str
    operator_2: str
    operator_3: str
    operator_4: str

    date_reported: datetime = Field(default_factory=datetime.today)


