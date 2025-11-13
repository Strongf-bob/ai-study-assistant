"""
Клиент для работы с Ollama
"""
import requests
from typing import List, Dict
from config import settings


class OllamaClient:
    """Клиент для Ollama (локальный LLM)"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    def check_connection(self) -> bool:
        """Проверка подключения"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate(
        self,
        prompt: str,
        system: str = "Ты AI помощник для оптимизации учебы студентов.",
        temperature: float = 0.7
    ) -> str:
        """Генерация ответа"""
        try:
            url = f"{self.base_url}/api/generate"

            payload = {
                "model": self.model,
                "prompt": f"System: {system}\n\nUser: {prompt}",
                "stream": False,
                "options": {"temperature": temperature}
            }

            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Ошибка: {response.status_code}"

        except Exception as e:
            return f"Ошибка: {str(e)}"

    def create_study_plan(self, subject: str, level: str, goal: str, hours: int) -> str:
        """План обучения"""
        prompt = f"""Создай детальный план обучения:
- Предмет: {subject}
- Уровень: {level}
- Цель: {goal}
- Время: {hours} часов в неделю

Структура:
1. Этапы (недели/темы)
2. Темы для изучения
3. Ресурсы
4. Задания
5. Контрольные точки"""

        return self.generate(prompt, "Ты опытный педагог-методист.", 0.5)

    def explain_concept(self, concept: str, style: str = "visual", level: str = "intermediate") -> str:
        """Объяснение концепции"""
        styles = {
            "visual": "с визуальными метафорами",
            "auditory": "через звуковые аналогии",
            "kinesthetic": "через практические примеры",
            "reading": "через текстовое описание"
        }

        prompt = f"""Объясни "{concept}" для уровня {level}, {styles.get(style, "понятно")}.

Включи:
1. Определение
2. 2-3 примера
3. Ключевые моменты
4. Частые ошибки"""

        return self.generate(prompt, temperature=0.6)

    def generate_quiz(self, topic: str, num: int = 5, level: str = "intermediate") -> str:
        """Генерация теста"""
        prompt = f"""Создай {num} вопросов по "{topic}" уровня {level}.

Для каждого:
1. Вопрос
2. 4 варианта (A, B, C, D)
3. Правильный ответ
4. Объяснение"""

        return self.generate(prompt, temperature=0.5)
