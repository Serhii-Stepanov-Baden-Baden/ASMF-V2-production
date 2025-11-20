"""
ASMF v2.0 - Эмоциональный Компаньон
Интеллектуальная система поддержки пользователя в долгосрочных проектах
"""

import asyncio
import random
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class EmotionalState(Enum):
    """Эмоциональные состояния"""
    ENERGETIC = "energetic"
    FOCUSED = "focused" 
    TIRED = "tired"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"
    SATISFIED = "satisfied"
    MOTIVATED = "motivated"


class SupportAction(Enum):
    """Действия поддержки"""
    ENCOURAGE = "encourage"
    BREAK_SUGGESTION = "break_suggestion"
    JOKE_TELLING = "joke_telling"
    PERSPECTIVE_SHIFT = "perspective_shift"
    TASK_SWITCH = "task_switch"
    CELEBRATION = "celebration"
    COMFORT = "comfort"
    FOCUS_TECHNIQUE = "focus_technique"


@dataclass
class EmotionalMetrics:
    """Метрики эмоционального состояния"""
    energy_level: float        # 0.0 - 1.0
    focus_level: float         # 0.0 - 1.0
    frustration_level: float   # 0.0 - 1.0
    satisfaction_level: float  # 0.0 - 1.0
    motivation_level: float    # 0.0 - 1.0
    stress_level: float        # 0.0 - 1.0


@dataclass
class SupportResponse:
    """Ответ системы поддержки"""
    action: SupportAction
    message: str
    emotional_state: EmotionalState
    suggested_activities: List[str]
    urgency_level: float       # 0.0 - 1.0
    follow_up_needed: bool


class EmotionalCompanion:
    """Эмоциональный компаньон для поддержки в работе"""
    
    def __init__(self):
        # База знаний о поддержке
        self.encouragement_phrases = [
            "Помните, каждая проблема - это возможность для роста!",
            "Вы на правильном пути. Каждый шаг приближает к цели!",
            "Ваша настойчивость восхищает. Продолжайте в том же духе!",
            "Каждое исправление делает код лучше. Вы создаёте что-то особенное!",
            "Ваше творчество уникально. Доверьтесь процессу!",
            "Каждая строчка кода - это вклад в будущее. Гордитесь своей работой!",
            "Прогресс не всегда линеен, но каждая попытка ценна!",
            "Ваши идеи достойны воплощения. Не сомневайтесь в себе!"
        ]
        
        self.jokes_collection = [
            {
                "setup": "Почему программисты предпочитают темную тему?",
                "punchline": "Потому что свет привлекает баги!",
                "category": "programming"
            },
            {
                "setup": "Как называется программист, который не пьет кофе?",
                "punchline": "Дебаггер!",
                "category": "coffee"
            },
            {
                "setup": "Что говорит один байт другому?",
                "punchline": "Ты выглядишь немного не в своем бите!",
                "category": "wordplay"
            },
            {
                "setup": "Почему функция всегда возвращалась грустной?",
                "punchline": "Потому что у неё было слишком много return-ов!",
                "category": "programming"
            },
            {
                "setup": "Как называется программист, который разводит рыбок?",
                "punchline": "Аква-программист!",
                "category": "wordplay"
            },
            {
                "setup": "Почему цикл while никогда не устает?",
                "punchline": "Потому что он всегда в condition!",
                "category": "programming"
            }
        ]
        
        self.energy_boost_activities = [
            "Попробуйте сделать 5 глубоких вдохов",
            "Прогуляйтесь 10 минут на свежем воздухе",
            "Выпейте стакан воды и потянитесь",
            "Послушайте любимую музыку 3 минуты",
            "Посмотрите в окно и заметьте 3 красивые вещи",
            "Сделайте простые упражнения для глаз",
            "Проветрите комнату"
        ]
        
        self.focus_techniques = [
            "Техника Помодоро: 25 минут работы + 5 минут отдыха",
            "Правило 2 минут: если задача займет меньше 2 минут - сделайте сейчас",
            "Техника захвата: запишите все мысли и вернитесь к работе",
            "Метод черепахи: начните с самой маленькой части задачи",
            "Техника блокбастера: разбейте большую задачу на сцены"
        ]
        
        self.perspective_shifts = [
            "Представьте, что вы объясняете это ребенку - как бы вы это сделали?",
            "Если бы у вас был безграничный бюджет, как бы вы решили эту задачу?",
            "Что бы сказал ваш любимый учитель в такой ситуации?",
            "Представьте решение через 10 лет - какие технологии помогут?",
            "Как бы подошел к этому Маск/Джобс/Тим Кук?",
            "Что если перевернуть проблему с ног на голову?"
        ]
        
        # История взаимодействий
        self.interaction_history = []
        self.current_mood_tracking = []
        
    async def analyze_emotional_state(self, user_input: str = "", work_context: Dict[str, Any] = None) -> EmotionalMetrics:
        """Анализ эмоционального состояния пользователя"""
        
        # Анализ текста (базовая версия)
        energy_keywords = ["устал", "сонный", "энергии нет", "выдохся", "сил нет"]
        focus_keywords = ["отвлекается", "не могу сосредоточиться", "мысли скачут", "рассеивается"]
        frustration_keywords = ["бесит", "достало", "не работает", "глючит", "ошибка", "гнев"]
        satisfaction_keywords = ["получилось", "классно", "отлично", "доволен", "успех"]
        motivation_keywords = ["мотивация", "хочется", "интересно", "вдохновляет"]
        
        text_lower = user_input.lower()
        
        # Подсчет ключевых слов
        energy_score = sum(1 for word in energy_keywords if word in text_lower) / len(energy_keywords)
        focus_score = sum(1 for word in focus_keywords if word in text_lower) / len(focus_keywords)
        frustration_score = sum(1 for word in frustration_keywords if word in text_lower) / len(frustration_keywords)
        satisfaction_score = sum(1 for word in satisfaction_keywords if word in text_lower) / len(satisfaction_keywords)
        motivation_score = sum(1 for word in motivation_keywords if word in text_lower) / len(motivation_keywords)
        
        # Анализ контекста работы
        work_energy = 0.5
        work_focus = 0.5
        work_stress = 0.3
        
        if work_context:
            # Время работы
            work_duration = work_context.get('work_duration_minutes', 30)
            if work_duration > 90:
                work_energy = max(0.1, 1.0 - (work_duration - 90) / 120)
                work_stress = min(1.0, 0.3 + (work_duration - 90) / 60)
            
            # Количество ошибок
            error_count = work_context.get('error_count', 0)
            work_stress += error_count * 0.1
            work_focus = max(0.2, 1.0 - error_count * 0.15)
            
            # Прогресс
            progress = work_context.get('completion_percentage', 0.5)
            work_satisfaction = progress
            work_motivation = min(1.0, 0.5 + progress * 0.5)
        
        # Финальные метрики
        metrics = EmotionalMetrics(
            energy_level=max(0.1, min(1.0, work_energy * 0.7 + (1.0 - energy_score) * 0.3)),
            focus_level=max(0.1, min(1.0, work_focus * 0.7 + (1.0 - focus_score) * 0.3)),
            frustration_level=max(0.1, min(1.0, work_stress * 0.7 + frustration_score * 0.3)),
            satisfaction_level=max(0.1, min(1.0, work_satisfaction * 0.7 + satisfaction_score * 0.3)),
            motivation_level=max(0.1, min(1.0, work_motivation * 0.7 + motivation_score * 0.3)),
            stress_level=max(0.1, min(1.0, work_stress))
        )
        
        # Сохранение в историю
        self.current_mood_tracking.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "metrics": metrics,
            "context": work_context
        })
        
        return metrics
    
    async def generate_support_response(self, metrics: EmotionalMetrics, context: Dict[str, Any] = None) -> SupportResponse:
        """Генерация ответа поддержки на основе эмоционального анализа"""
        
        # Определение основного состояния
        if metrics.energy_level < 0.3:
            primary_state = EmotionalState.TIRED
            urgency = 0.8
        elif metrics.frustration_level > 0.7:
            primary_state = EmotionalState.FRUSTRATED
            urgency = 0.9
        elif metrics.focus_level < 0.4:
            primary_state = EmotionalState.CONFUSED
            urgency = 0.6
        elif metrics.satisfaction_level > 0.7:
            primary_state = EmotionalState.SATISFIED
            urgency = 0.1
        elif metrics.motivation_level > 0.7:
            primary_state = EmotionalState.MOTIVATED
            urgency = 0.2
        elif metrics.focus_level > 0.7:
            primary_state = EmotionalState.FOCUSED
            urgency = 0.1
        else:
            primary_state = EmotionalState.ENERGETIC
            urgency = 0.3
        
        # Выбор действия поддержки
        action, message, activities = await self._select_support_action(primary_state, metrics, context)
        
        return SupportResponse(
            action=action,
            message=message,
            emotional_state=primary_state,
            suggested_activities=activities,
            urgency_level=urgency,
            follow_up_needed=urgency > 0.6
        )
    
    async def _select_support_action(self, state: EmotionalState, metrics: EmotionalMetrics, context: Dict[str, Any]) -> Tuple[SupportAction, str, List[str]]:
        """Выбор конкретного действия поддержки"""
        
        if state == EmotionalState.TIRED:
            joke = random.choice(self.jokes_collection)
            message = f"Похоже, вы устали! {joke['setup']} {joke['punchline']}\n\nА теперь давайте сделаем перерыв! {random.choice(self.energy_boost_activities)}"
            return (SupportAction.BREAK_SUGGESTION, message, self.energy_boost_activities)
        
        elif state == EmotionalState.FRUSTRATED:
            encouragement = random.choice(self.encouragement_phrases)
            perspective = random.choice(self.perspective_shifts)
            message = f"{encouragement}\n\nА давайте посмотрим на это под другим углом:\n{perspective}"
            return (SupportAction.COMFORT, message, self.perspective_shifts)
        
        elif state == EmotionalState.CONFUSED:
            technique = random.choice(self.focus_techniques)
            message = f"Замечаю, что фокус стал рассеиваться. Вот техника, которая может помочь:\n\n{technique}"
            return (SupportAction.FOCUS_TECHNIQUE, message, self.focus_techniques)
        
        elif state == EmotionalState.SATISFIED:
            message = f"Отлично! Вы достигли важного результата! 🎉\n\nВаша работа продвигается отлично. Это достижение стоит отметить!"
            return (SupportAction.CELEBRATION, message, ["Отметьте достижение", "Сделайте скриншот", "Поделитесь успехом"])
        
        elif state == EmotionalState.MOTIVATED:
            message = f"Ваша мотивация на высоте! 🌟\n\nИспользуйте этот момент для решения самых сложных задач. Вы в отличной форме!"
            return (SupportAction.ENCOURAGE, message, ["Решите сложную задачу", "Экспериментируйте с новым подходом", "Документируйте идеи"])
        
        elif state == EmotionalState.FOCUSED:
            message = f"Фокус идеален! 🎯\n\nЭто лучшее время для глубокой работы и решения сложных задач."
            return (SupportAction.ENCOURAGE, message, ["Погрузитесь в сложную задачу", "Оптимизируйте код", "Рефакторинг"])
        
        else:
            message = f"Ваше состояние стабильно. {random.choice(self.encouragement_phrases)}\n\nПродолжайте в том же духе!"
            return (SupportAction.ENCOURAGE, message, ["Продолжайте работу", "Проверьте прогресс", "Планируйте следующие шаги"])
    
    async def tell_joke(self, category: str = "random") -> Dict[str, str]:
        """Рассказывание мотивирующего анекдота"""
        if category == "random":
            joke = random.choice(self.jokes_collection)
        else:
            jokes = [j for j in self.jokes_collection if j["category"] == category]
            joke = random.choice(jokes) if jokes else random.choice(self.jokes_collection)
        
        return joke
    
    async def emergency_support(self, crisis_level: float = 0.9) -> SupportResponse:
        """Экстренная поддержка при высоком уровне стресса"""
        
        crisis_messages = [
            "Стоп. Сейчас важнее всего ваше благополучие. Давайте сделаем паузу.",
            "Вы делаете невероятную работу. Ошибки - это часть процесса обучения.",
            "Каждый великий программист когда-то был начинающим. Не будьте к себе слишком строги.",
            "Ваше здоровье важнее любого кода. Сделайте глубокий вдох.",
            "Помните: баги исправляются, а здоровье - нет. Позаботьтесь о себе."
        ]
        
        message = random.choice(crisis_messages)
        
        emergency_activities = [
            "Закройте глаза на 2 минуты",
            "Выпейте стакан воды медленно",
            "Встаньте и пройдитесь",
            "Позвоните другу",
            "Послушайте расслабляющую музыку"
        ]
        
        return SupportResponse(
            action=SupportAction.COMFORT,
            message=message,
            emotional_state=EmotionalState.FRUSTRATED,
            suggested_activities=emergency_activities,
            urgency_level=crisis_level,
            follow_up_needed=True
        )
    
    async def adaptive_encouragement(self, progress_metrics: Dict[str, float]) -> str:
        """Адаптивное поощрение на основе прогресса проекта"""
        
        completion_rate = progress_metrics.get("completion_rate", 0.5)
        quality_score = progress_metrics.get("quality_score", 0.5)
        innovation_level = progress_metrics.get("innovation_score", 0.5)
        
        if completion_rate > 0.9:
            return f"🔥 Невероятно! Вы почти у цели! Качество {quality_score:.1%} и инновации {innovation_level:.1%} - это профессиональный уровень!"
        elif completion_rate > 0.7:
            return f"💪 Отличная работа! {completion_rate:.1%} проекта завершено. Вы в отличной форме!"
        elif completion_rate > 0.5:
            return f"🚀 Прогресс идет хорошо! Половина пути пройдена. Каждая строчка кода приближает к цели!"
        elif completion_rate > 0.3:
            return f"✨ Неплохой старт! {completion_rate:.1%} проекта готово. Время набрать темп!"
        else:
            return f"🎯 Каждый проект начинается с первого шага. Ваш старт уже заложил фундамент успеха!"
    
    async def get_emotional_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Получение сводки эмоционального состояния за период"""
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=time_window_hours)
        recent_data = [
            entry for entry in self.current_mood_tracking 
            if datetime.datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        if not recent_data:
            return {"status": "no_data", "message": "Недостаточно данных за период"}
        
        # Анализ трендов
        energy_trend = sum(e["metrics"].energy_level for e in recent_data) / len(recent_data)
        focus_trend = sum(e["metrics"].focus_level for e in recent_data) / len(recent_data)
        frustration_trend = sum(e["metrics"].frustration_level for e in recent_data) / len(recent_data)
        
        # Рекомендации
        recommendations = []
        if frustration_trend > 0.6:
            recommendations.append("Уровень фрустрации высок - рекомендуется больше перерывов")
        if energy_trend < 0.4:
            recommendations.append("Энергия низкая - важно следить за режимом отдыха")
        if focus_trend < 0.5:
            recommendations.append("Фокус нестабилен - используйте техники концентрации")
        
        return {
            "period_hours": time_window_hours,
            "data_points": len(recent_data),
            "energy_trend": energy_trend,
            "focus_trend": focus_trend,
            "frustration_trend": frustration_trend,
            "overall_mood": "positive" if energy_trend > 0.6 and frustration_trend < 0.4 else "needs_attention",
            "recommendations": recommendations
        }