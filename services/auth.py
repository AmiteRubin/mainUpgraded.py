from typing import Self

from beanie import PydanticObjectId
from bson import DBRef
from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette.requests import Request

from webapp5353.models.core import RbacRole, User, UserInvitation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAuth:
    @classmethod
    async def create_user(
            cls, *,
            first_name: str,
            last_name: str,
            email: str,
            raw_password: str,
            role: RbacRole = RbacRole.TEAM_LEADER,
            team_id: PydanticObjectId | None = None
    ) -> Self:
        if role in (RbacRole.TEAM_LEADER, RbacRole.TEAM_MEMBER) and team_id is None:
            raise HTTPException(status_code=400, detail="Team leader and team member must be assigned to a team")
        try:
            obj = User(hashed_password=cls.get_password_hash(raw_password), role=role,
                       first_name=first_name, last_name=last_name, email=email, id=PydanticObjectId(),
                       team=DBRef('Team', team_id) if team_id else None)
            await obj.save()
            return obj
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.json())

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        return pwd_context.hash(password)

    @classmethod
    async def get_user(cls, user_id: str, client_id, fetch_client: bool = True):
        q = User.find(User.id == PydanticObjectId(user_id))
        if fetch_client:
            q = q.find(fetch_links=True)
        return await q.first_or_none()

    @classmethod
    async def authenticate_user(cls, *, email: str, password: str):
        user = await User.find(User.email == email).first_or_none()
        if not user:
            return False
        if not cls.verify_password(password, user.hashed_password):
            return False
        return user


async def user_maybe_pending_registration(email) -> bool:
    return await UserInvitation.find(UserInvitation.invitee_email == email, UserInvitation.completed == False).exists()


async def get_current_user(request: Request) -> 'User':
    email = request.session.get('email')
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    raw_password = request.session.get('password')
    user = await User.authenticate_user(email=email, password=raw_password)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_current_hamal_user(request: Request):
    user = await get_current_user(request)
    if user.role in (RbacRole.HAMAL, RbacRole.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


async def get_current_team_lead(request: Request):
    user = await get_current_user(request)
    if user.role != RbacRole.TEAM_LEADER:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


async def get_current_team_member(request: Request):
    user = await get_current_user(request)
    if user.role not in (RbacRole.TEAM_MEMBER, RbacRole.TEAM_LEADER):
        raise HTTPException(status_code=403, detail="Forbidden")
    return user
