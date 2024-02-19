from typing import Annotated

from fastapi import Depends

from models.core import User, get_current_hamal_user, UserInvitation


async def add_users(
        user: Annotated[User, Depends(get_current_hamal_user)], emails: list[str]
):
    invites = [UserInvitation(invitee_email=email, inviter=user) for email in emails]
