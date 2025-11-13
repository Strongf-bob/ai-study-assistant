"""
Упрощённая конфигурация для Python 3.13 (без ChromaDB)
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Settings:
    """Настройки упрощённой версии"""

    # Ollama настройки
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    # Простое хранилище (JSON файлы)
    MATERIALS_PATH: str = "./data/materials.json"
    TASKS_PATH: str = "./data/tasks.json"

    # Настройки обучения
    DEFAULT_STUDY_SESSION: int = 25
    BREAK_DURATION: int = 5

    # Стили обучения
    LEARNING_STYLES: List[str] = None
    DIFFICULTY_LEVELS: List[str] = None

    def __post_init__(self):
        self.LEARNING_STYLES = ["visual", "auditory", "kinesthetic", "reading"]
        self.DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]


settings = Settings()
