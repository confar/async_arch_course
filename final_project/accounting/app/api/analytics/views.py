from datetime import date

from fastapi import Depends, APIRouter, Query

from app.api.analytics.serializers import AnalyticsDashboardSerializer, MostExpensiveTaskSerializer
from app.api.base_deps import get_analytics_service, get_current_account

router = APIRouter()


@router.get("/dashboard/", response_model=AnalyticsDashboardSerializer)
async def get_analytics_dashboard(account=Depends(get_current_account),
                                  analytics_service=Depends(get_analytics_service)):
    total_sum_earned, negative_balance_popugs_count = analytics_service.get_analytics_data_for_today(account=account)
    return AnalyticsDashboardSerializer(total_sum_earned=total_sum_earned, 
                                        negative_balance_popugs_count=negative_balance_popugs_count)


@router.put("/most-expensive-task/", response_model=MostExpensiveTaskSerializer)
async def get_most_expensive_task_for_period(
        date_from: date = Query(None),
        date_till: date = Query(None),
        account=Depends(get_current_account),
        analytics_service=Depends(get_analytics_service)):
    cost = analytics_service.get_most_expensive_task_cost_for_period(account=account)
    return MostExpensiveTaskSerializer(costs=cost,
                                       date_from=date_from,
                                       date_till=date_till)
