"""
Простое хранилище учебных материалов (замена RAG)
"""
import json
import os
from typing import List, Dict, Optional
from config import settings


class SimpleStorage:
    """Простое хранилище вместо ChromaDB"""

    def __init__(self):
        self.materials_path = settings.MATERIALS_PATH
        self.materials: List[Dict] = []
        self.load_materials()
        print("✅ Простое хранилище инициализировано")

    def load_materials(self):
        """Загрузка из JSON"""
        try:
            if os.path.exists(self.materials_path):
                with open(self.materials_path, 'r', encoding='utf-8') as f:
                    self.materials = json.load(f)
        except:
            self.materials = []

    def save_materials(self):
        """Сохранение в JSON"""
        os.makedirs(os.path.dirname(self.materials_path), exist_ok=True)
        with open(self.materials_path, 'w', encoding='utf-8') as f:
            json.dump(self.materials, f, ensure_ascii=False, indent=2)

    def add_document(self, text: str, metadata: Optional[Dict] = None) -> bool:
        """Добавление документа"""
        try:
            doc = {
                "id": len(self.materials) + 1,
                "text": text,
                "metadata": metadata or {}
            }
            self.materials.append(doc)
            self.save_materials()
            print(f"✅ Добавлен документ #{doc['id']}")
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """Простой поиск по ключевым словам"""
        query_lower = query.lower()
        results = []

        for doc in self.materials:
            text_lower = doc['text'].lower()
            # Простое совпадение по словам
            score = sum(1 for word in query_lower.split() if word in text_lower)
            if score > 0:
                results.append({
                    'text': doc['text'],
                    'metadata': doc.get('metadata', {}),
                    'score': score
                })

        # Сортируем по релевантности
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n_results]

    def generate_answer_with_context(self, question: str, llm_client, n_results: int = 3) -> str:
        """Ответ с контекстом из материалов"""
        docs = self.search(question, n_results)

        if not docs:
            return "Не нашёл информации в базе знаний. Попробую ответить из общих знаний.\n\n" +                    llm_client.generate(question, temperature=0.7)

        # Формируем контекст
        context = "\n\n".join([doc['text'] for doc in docs])

        prompt = f"""Используя контекст ниже, ответь на вопрос.

Контекст:
{context}

Вопрос: {question}

Дай точный ответ на основе контекста."""

        return llm_client.generate(prompt, "Ты AI-ассистент для обучения.", 0.3)

    def get_stats(self) -> Dict:
        """Статистика"""
        return {
            "total_documents": len(self.materials),
            "path": self.materials_path
        }

    def clear(self) -> bool:
        """Очистка"""
        self.materials = []
        self.save_materials()
        print("✅ База очищена")
        return True
