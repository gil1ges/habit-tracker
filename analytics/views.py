import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .charts import (
    build_bar_chart,
    build_histogram,
    build_line_chart,
    build_pie_chart,
    build_scatter_chart,
)
from .external_api import get_motivational_quote
from .services import get_user_habit_stats

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    logger.info("Analytics dashboard opened: user_id=%s", request.user.id)
    context = {
        "stats": get_user_habit_stats(request.user),
        "quote": get_motivational_quote(),
        "bar_chart": build_bar_chart(request.user),
        "pie_chart": build_pie_chart(request.user),
        "line_chart": build_line_chart(request.user),
        "histogram_chart": build_histogram(request.user),
        "scatter_chart": build_scatter_chart(request.user),
    }
    return render(request, "analytics/dashboard.html", context)


@login_required
def api_stats(request):
    try:
        return JsonResponse(get_user_habit_stats(request.user))
    except Exception:
        logger.warning(
            "Analytics stats API failed: user_id=%s",
            request.user.id,
            exc_info=True,
        )
        return JsonResponse({"detail": "Unable to load analytics stats."}, status=500)

