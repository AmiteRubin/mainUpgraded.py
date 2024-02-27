from datetime import datetime

from beanie import Link
from pydantic import Field

from webapp5353.models.core import MissionReport, Team


class MissionReportRequest(MissionReport):
    team: Link[Team] = Field(..., exclude=True)
    date_reported: datetime = Field(..., exclude=True)
