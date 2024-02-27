from fastapi import Query

QueryStartDate = Query(..., description="Start date in ISO-8601 format", alias='startDate', example='2024-02-15')
QueryEndDate = Query(..., description="End date in ISO-8601 format", alias='endDate', example='2024-02-20')
