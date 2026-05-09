import base64
import logging
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from .services import (
    get_completed_vs_missed,
    get_completion_by_day,
    get_user_habit_stats,
)

logger = logging.getLogger(__name__)


def _fig_to_base64(fig) -> str:
    buffer = BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _build_empty_chart(title: str, message: str) -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_title(title)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    ax.axis("off")
    return _fig_to_base64(fig)


def _handle_chart_error(chart_name: str) -> str:
    logger.error("Failed to build %s chart", chart_name, exc_info=True)
    return _build_empty_chart("График недоступен", "Попробуйте снова позже.")


def build_bar_chart(user) -> str:
    try:
        stats = get_user_habit_stats(user)
        habits = stats["habits"]
        if not habits:
            return _build_empty_chart(
                "Выполнения по привычкам",
                "Пока нет доступных привычек.",
            )

        titles = [habit["title"] for habit in habits]
        counts = [habit["completion_count"] for habit in habits]

        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.bar(titles, counts, color="#198754")
        ax.set_title("Выполнения по привычкам")
        ax.set_xlabel("Привычка")
        ax.set_ylabel("Количество выполнений")
        ax.tick_params(axis="x", rotation=30)
        return _fig_to_base64(fig)
    except Exception:
        return _handle_chart_error("bar")


def build_pie_chart(user) -> str:
    try:
        completion_stats = get_completed_vs_missed(user)
        values = [
            completion_stats["completed"],
            completion_stats["missed"],
        ]
        if sum(values) == 0:
            return _build_empty_chart(
                "Выполнено и пропущено",
                "Пока нет выполнений.",
            )

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(
            values,
            labels=["Выполнено", "Пропущено"],
            autopct="%1.1f%%",
            colors=["#198754", "#dc3545"],
            startangle=90,
        )
        ax.set_title("Выполнено и пропущено")
        return _fig_to_base64(fig)
    except Exception:
        return _handle_chart_error("pie")


def build_line_chart(user) -> str:
    try:
        completion_data = get_completion_by_day(user)
        if not completion_data:
            return _build_empty_chart(
                "Выполнения по дням",
                "История выполнений пока пуста.",
            )

        dates = [item["date"] for item in completion_data]
        counts = [item["count"] for item in completion_data]

        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(dates, counts, marker="o", linewidth=2, color="#0d6efd")
        ax.set_title("Выполнения по дням")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Количество выполнений")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(alpha=0.3)
        return _fig_to_base64(fig)
    except Exception:
        return _handle_chart_error("line")


def build_histogram(user) -> str:
    try:
        stats = get_user_habit_stats(user)
        completion_counts = [habit["completion_count"] for habit in stats["habits"]]
        if not completion_counts:
            return _build_empty_chart(
                "Распределение выполнений",
                "Пока нет доступных привычек.",
            )

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(completion_counts, bins=min(10, max(len(completion_counts), 1)), color="#fd7e14", edgecolor="white")
        ax.set_title("Распределение выполнений по привычкам")
        ax.set_xlabel("Количество выполнений")
        ax.set_ylabel("Количество привычек")
        return _fig_to_base64(fig)
    except Exception:
        return _handle_chart_error("histogram")


def build_scatter_chart(user) -> str:
    try:
        stats = get_user_habit_stats(user)
        habits = stats["habits"]
        if not habits:
            return _build_empty_chart(
                "Цель и факт выполнения",
                "Пока нет доступных привычек.",
            )

        targets = [habit["target_count"] for habit in habits]
        completions = [habit["completion_count"] for habit in habits]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.scatter(targets, completions, color="#6f42c1", alpha=0.8, s=80)
        ax.set_title("Цель и факт выполнения")
        ax.set_xlabel("Целевое количество")
        ax.set_ylabel("Количество выполнений")
        ax.grid(alpha=0.3)
        return _fig_to_base64(fig)
    except Exception:
        return _handle_chart_error("scatter")
