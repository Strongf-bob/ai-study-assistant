"""
Планировщик задач
"""
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
import json
import os


@dataclass
class Task:
    """Задача"""
    id: str
    title: str
    subject: str
    deadline: str
    estimated_minutes: int
    priority: str
    completed: bool = False

    def is_overdue(self) -> bool:
        deadline_dt = datetime.fromisoformat(self.deadline)
        return datetime.now() > deadline_dt and not self.completed

    def time_left(self) -> str:
        deadline_dt = datetime.fromisoformat(self.deadline)
        delta = deadline_dt - datetime.now()

        if delta.days > 0:
            return f"{delta.days} дней"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600} часов"
        else:
            return f"{delta.seconds // 60} минут"


class SimpleScheduler:
    """Планировщик"""

    def __init__(self, storage_path: str = "./data/tasks.json"):
        self.storage_path = storage_path
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task(**task) for task in data]
        except FileNotFoundError:
            self.tasks = []

    def save_tasks(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            data = [
                {
                    'id': t.id, 'title': t.title, 'subject': t.subject,
                    'deadline': t.deadline, 'estimated_minutes': t.estimated_minutes,
                    'priority': t.priority, 'completed': t.completed
                }
                for t in self.tasks
            ]
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_task(self, title: str, subject: str, deadline_days: int = 7,
                 estimated_minutes: int = 60, priority: str = "medium") -> Task:
        task_id = f"task_{len(self.tasks) + 1}"
        deadline = (datetime.now() + timedelta(days=deadline_days)).isoformat()

        task = Task(task_id, title, subject, deadline, estimated_minutes, priority)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def complete_task(self, task_id: str) -> bool:
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.completed = True
            self.save_tasks()
            return True
        return False

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.completed]

    def get_today_tasks(self) -> List[Task]:
        today = datetime.now().date()
        return [t for t in self.tasks 
                if datetime.fromisoformat(t.deadline).date() == today and not t.completed]

    def get_overdue_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.is_overdue()]

    def get_high_priority(self) -> List[Task]:
        return [t for t in self.tasks if t.priority == "high" and not t.completed]

    def get_stats(self) -> dict:
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.completed])
        return {
            "total": total,
            "completed": completed,
            "pending": len(self.get_pending_tasks()),
            "overdue": len(self.get_overdue_tasks()),
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0
        }

    def format_task_list(self) -> str:
        result = "📋 **Твои задачи:**\n\n"

        overdue = self.get_overdue_tasks()
        high = self.get_high_priority()
        today = self.get_today_tasks()

        if overdue:
            result += "⚠️ **Просроченные:**\n"
            for task in overdue[:3]:
                result += f"- {task.title} ({task.subject})\n"
            result += "\n"

        if high:
            result += "🔥 **Высокий приоритет:**\n"
            for task in high[:3]:
                result += f"- {task.title} (до {task.time_left()})\n"
            result += "\n"

        if today:
            result += "📅 **На сегодня:**\n"
            for task in today:
                result += f"- {task.title} ({task.estimated_minutes} мин)\n"
        else:
            result += "✅ На сегодня задач нет!\n"

        stats = self.get_stats()
        result += f"\n📊 **Статистика:** {stats['completed']}/{stats['total']} выполнено"
        return result
