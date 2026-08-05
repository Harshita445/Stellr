from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_dashboard_service
from app.schemas.dashboard.responses import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    result = await dashboard_service.get_dashboard(current_user["user_id"])
    return DashboardResponse(**result)
