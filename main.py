"""
AI Помощник для учебы - Упрощённая версия для Python 3.13
"""
from ollama_client import OllamaClient
from simple_storage import SimpleStorage
from scheduler import SimpleScheduler
from config import settings


class StudyAssistantSimple:
    """Упрощённая версия для Python 3.13"""

    def __init__(self):
        print("🚀 Инициализация AI Помощника (упрощённая версия)...\n")

        print("📡 Подключение к Ollama...")
        self.llm = OllamaClient()

        print("💾 Инициализация хранилища...")
        self.storage = SimpleStorage()

        print("📅 Загрузка планировщика...")
        self.scheduler = SimpleScheduler()

        self.user_profile = {
            "name": "Студент",
            "learning_style": "visual",
            "level": "intermediate"
        }

        print("\n✅ Готов к работе!\n")

    def check_ollama(self) -> bool:
        if not self.llm.check_connection():
            print("❌ Ollama не запущен!")
            print("\nДля запуска:")
            print("1. Установи Ollama: https://ollama.com")
            print(f"2. Скачай модель: ollama pull {settings.OLLAMA_MODEL}")
            print("3. Запусти: ollama serve")
            return False
        return True

    def process_query(self, query: str) -> str:
        query_lower = query.lower()

        if any(w in query_lower for w in ["план", "распланируй"]):
            return self._handle_planning(query)

        elif any(w in query_lower for w in ["объясни", "что такое"]):
            return self._handle_explanation(query)

        elif any(w in query_lower for w in ["задачи", "дела"]):
            return self.scheduler.format_task_list()

        elif any(w in query_lower for w in ["тест", "quiz"]):
            return self._handle_quiz(query)

        else:
            return self.storage.generate_answer_with_context(query, self.llm)

    def _handle_planning(self, query: str) -> str:
        subject = "Общее"
        for subj in ["математика", "физика", "python", "программирование"]:
            if subj in query.lower():
                subject = subj.capitalize()
                break

        plan = self.llm.create_study_plan(
            subject, self.user_profile["level"], "Освоить материал", 10
        )
        return f"📚 **План обучения по {subject}**\n\n{plan}"

    def _handle_explanation(self, query: str) -> str:
        rag_answer = self.storage.generate_answer_with_context(query, self.llm, 2)

        if "не нашёл" in rag_answer.lower() or len(rag_answer) < 100:
            concept = query.replace("объясни", "").replace("что такое", "").strip()
            return self.llm.explain_concept(
                concept, self.user_profile["learning_style"], self.user_profile["level"]
            )

        return rag_answer

    def _handle_quiz(self, query: str) -> str:
        topic = query.replace("тест", "").replace("quiz", "").replace("по", "").strip()
        if not topic or len(topic) < 3:
            topic = "общие знания"

        quiz = self.llm.generate_quiz(topic, 5, self.user_profile["level"])
        return f"📝 **Тест: {topic}**\n\n{quiz}"

    def add_material(self, text: str, subject: str = "общее") -> bool:
        return self.storage.add_document(text, {"subject": subject})

    def add_task(self, title: str, subject: str, days: int = 7, priority: str = "medium"):
        self.scheduler.add_task(title, subject, days, priority=priority)
        return True

    def show_help(self):
        print("""
╔══════════════════════════════════════════════════════════╗
║     AI ПОМОЩНИК ДЛЯ УЧЕБЫ (Упрощённая версия)           ║
╚══════════════════════════════════════════════════════════╝

📖 КОМАНДЫ:

🎯 ПЛАНИРОВАНИЕ:
   • "Создай план обучения по математике"

📚 ОБУЧЕНИЕ:
   • "Объясни что такое рекурсия"

✅ ЗАДАЧИ:
   • "Покажи мои задачи"

📝 ТЕСТЫ:
   • "Тест по физике"

💾 УПРАВЛЕНИЕ:
   • help - справка
   • stats - статистика
   • exit - выход

───────────────────────────────────────────────────────────
✨ Упрощённая версия для Python 3.13:
   • LLM: Ollama + Llama 3.2
   • Хранилище: JSON файлы (без ChromaDB)
   • 100% бесплатно и локально!
───────────────────────────────────────────────────────────
""")

    def show_stats(self):
        print("\n📊 СТАТИСТИКА:")
        print("=" * 50)

        task_stats = self.scheduler.get_stats()
        print(f"\n✅ Задачи:")
        print(f"   Всего: {task_stats['total']}")
        print(f"   Выполнено: {task_stats['completed']}")
        print(f"   Прогресс: {task_stats['completion_rate']}%")

        storage_stats = self.storage.get_stats()
        print(f"\n📚 База знаний:")
        print(f"   Документов: {storage_stats['total_documents']}")

        print(f"\n🤖 AI:")
        print(f"   Модель: {settings.OLLAMA_MODEL}")
        print(f"   Статус: {'🟢 Подключена' if self.llm.check_connection() else '🔴 Не подключена'}")
        print("=" * 50)

    def run(self):
        if not self.check_ollama():
            return

        self.show_help()
        print("\n💬 Начни диалог!\n")

        while True:
            try:
                user_input = input("\n👤 Вы: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "выход", "quit"]:
                    print("\n👋 До встречи!")
                    break

                elif user_input.lower() == "help":
                    self.show_help()
                    continue

                elif user_input.lower() == "stats":
                    self.show_stats()
                    continue

                print("\n🤖 Ассистент: ", end="", flush=True)
                response = self.process_query(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 До встречи!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")


def main():
    assistant = StudyAssistantSimple()

    # Добавляем примеры
    print("📝 Добавляю примеры материалов...\n")

    assistant.add_material(
        "Python - высокоуровневый язык программирования. "
        "Простой синтаксис. Используется для веб-разработки, анализа данных, ML.",
        "programming"
    )

    assistant.add_material(
        "Рекурсия - функция вызывает сама себя. "
        "Нужен базовый случай. Пример: факториал.",
        "programming"
    )

    assistant.add_task("Решить задачи по алгебре", "Математика", 2, "high")
    assistant.add_task("Прочитать главу по физике", "Физика", 3)

    assistant.run()


if __name__ == "__main__":
    main()
