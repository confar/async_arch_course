from datetime import date

from fastapi import Depends, APIRouter, Query, HTTPException

from app.api.analytics.serializers import AnalyticsDashboardSerializer, MostExpensiveTaskSerializer
from app.api.base_deps import get_analytics_service, get_current_account
from starlette import status

from app.core.analytics.services import NotSufficientPrivileges

router = APIRouter()


@router.get("/dashboard/", response_model=AnalyticsDashboardSerializer)
async def get_analytics_dashboard(account=Depends(get_current_account),
                                  analytics_service=Depends(get_analytics_service)):
    try:
        total_sum_earned, negative_balance_popugs_count = await analytics_service.get_analytics_data_for_today(
            account=account)
    except NotSufficientPrivileges:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights")
    else:
        return AnalyticsDashboardSerializer(total_sum_earned=total_sum_earned, 
                                        negative_balance_popugs_count=negative_balance_popugs_count)


@router.get("/most-expensive-task/", response_model=MostExpensiveTaskSerializer)
async def get_most_expensive_task_for_period(
        date_from: date = Query(None),
        date_till: date = Query(None),
        account=Depends(get_current_account),
        analytics_service=Depends(get_analytics_service)):
    try:
        cost = await analytics_service.get_most_expensive_task_cost_for_period(account=account, 
                                                                           date_from=date_from, date_till=date_till)
    except NotSufficientPrivileges:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights")
    else:
        return MostExpensiveTaskSerializer(costs=cost,
                                           date_from=date_from,
                                           date_till=date_till)
