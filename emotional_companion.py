"""
ASMF v2.1 - Эмоциональный Компаньон
Интеллектуальная система поддержки пользователя в долгосрочных проектах
Автор: Serhii Stepanov (Baden-Baden, Germany)
Версия: 2.1 (GPU + Enhanced Storage + LLM Integration)
"""

import asyncio
import random
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
import logging
import time
import numpy as np

# v2.1 модули с fallback механизмами
try:
    from gpu_support import GPUSupportModule
    GPU_AVAILABLE = True
except ImportError:
    GPUSupportModule = None
    GPU_AVAILABLE = False

try:
    from database_optimization import EnhancedStorageSystem, StorageType
    STORAGE_AVAILABLE = True
except ImportError:
    EnhancedStorageSystem = None
    StorageType = None
    STORAGE_AVAILABLE = False

try:
    from llm_wrapper import UniversalLLMWrapper
    LLM_AVAILABLE = True
except ImportError:
    UniversalLLMWrapper = None
    LLM_AVAILABLE = False


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
    """Эмоциональный компаньон для поддержки в работе (v2.1)"""
    
    def __init__(self, db_path: str = "emotional_companion_v2_1.db"):
        self.db_path = db_path
        self.version = "2.1"
        
        # v2.1 модули инициализация
        self.gpu_support = GPUSupportModule() if GPU_AVAILABLE else None
        self.enhanced_storage = EnhancedStorageSystem() if STORAGE_AVAILABLE else None
        self.llm_wrapper = UniversalLLMWrapper() if LLM_AVAILABLE else None
        
        # v2.1 статистика
        self.v21_stats = {
            "gpu_analyzes": 0,
            "enhanced_storage_ops": 0,
            "llm_analyzes": 0,
            "total_interactions": 0,
            "start_time": time.time()
        }
        
        # Инициализация БД v2.1
        self._init_v21_database()
        
        # База знаний о поддержке (расширенная в v2.1)
        self.encouragement_phrases = [
            "Помните, каждая проблема - это возможность для роста!",
            "Вы на правильном пути. Каждый шаг приближает к цели!",
            "Ваша настойчивость восхищает. Продолжайте в том же духе!",
            "Каждое исправление делает код лучше. Вы создаёте что-то особенное!",
            "Ваше творчество уникально. Доверьтесь процессу!",
            "Каждая строчка кода - это вклад в будущее. Гордитесь своей работой!",
            "Прогресс не всегда линеен, но каждая попытка ценна!",
            "Ваши идеи достойны воплощения. Не сомневайтесь в себе!",
            # v2.1 добавлено: Более персонализированные фразы
            "Ваш опыт и интуиция - ваши главные преимущества!",
            "Каждый вызов делает вас сильнее и мудрее!",
            "Ваше упорство достойно восхищения и уважения!"
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
            },
            # v2.1 добавлено: больше шуток
            {
                "setup": "Какой язык программирования самый веселый?",
                "punchline": "Python - потому что у него множество библиотек для развлечений!",
                "category": "languages"
            },
            {
                "setup": "Почему компьютер не любит работать по понедельникам?",
                "punchline": "У него похмельный синдром после выходных!",
                "category": "worklife"
            }
        ]
        
        self.energy_boost_activities = [
            "Попробуйте сделать 5 глубоких вдохов",
            "Прогуляйтесь 10 минут на свежем воздухе",
            "Выпейте стакан воды и потянитесь",
            "Послушайте любимую музыку 3 минуты",
            "Посмотрите в окно и заметьте 3 красивые вещи",
            "Сделайте простые упражнения для глаз",
            "Проветрите комнату",
            # v2.1 добавлено: более разнообразные активности
            "Сделайте 10 приседаний для активации",
            "Посмотрите короткое мотивирующее видео",
            "Напишите 3 вещи, за которые благодарны"
        ]
        
        self.focus_techniques = [
            "Техника Помодоро: 25 минут работы + 5 минут отдыха",
            "Правило 2 минут: если задача займет меньше 2 минут - сделайте сейчас",
            "Техника захвата: запишите все мысли и вернитесь к работе",
            "Метод черепахи: начните с самой маленькой части задачи",
            "Техника блокбастера: разбейте большую задачу на сцены",
            # v2.1 добавлено: новые техники
            "Техника 5-минутного спринта: работайте 5 минут на максимуме",
            "Метод блокировки: отключите все уведомления на 30 минут"
        ]
        
        self.perspective_shifts = [
            "Представьте, что вы объясняете это ребенку - как бы вы это сделали?",
            "Если бы у вас был безграничный бюджет, как бы вы решили эту задачу?",
            "Что бы сказал ваш любимый учитель в такой ситуации?",
            "Представьте решение через 10 лет - какие технологии помогут?",
            "Как бы подошел к этому Маск/Джобс/Тим Кук?",
            "Что если перевернуть проблему с ног на голову?",
            # v2.1 добавлено: новые перспективы
            "Что бы вы посоветовали лучшему другу в такой же ситуации?",
            "Какую суперсилу вы бы использовали для решения этой проблемы?"
        ]
        
        # История взаимодействий v2.1
        self.interaction_history = []
        self.current_mood_tracking = []
        
    def _init_v21_database(self):
        """Инициализация БД v2.1 с расширенной схемой"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Основная таблица эмоциональных метрик
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotional_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    user_input TEXT,
                    energy_level REAL,
                    focus_level REAL,
                    frustration_level REAL,
                    satisfaction_level REAL,
                    motivation_level REAL,
                    stress_level REAL,
                    work_duration_minutes REAL,
                    error_count INTEGER,
                    completion_percentage REAL,
                    session_id TEXT
                )
            ''')
            
            # v2.1 таблица для GPU метрик
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gpu_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    operation_type TEXT,
                    gpu_time_ms REAL,
                    cpu_time_ms REAL,
                    speedup_factor REAL,
                    batch_size INTEGER,
                    success BOOLEAN
                )
            ''')
            
            # v2.1 таблица для LLM инсайтов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS llm_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    analysis_type TEXT,
                    input_text TEXT,
                    llm_response TEXT,
                    confidence_score REAL,
                    processing_time_ms REAL,
                    model_used TEXT
                )
            ''')
            
            # v2.1 таблица для статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS v21_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    metric_name TEXT,
                    metric_value REAL,
                    additional_data TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.v21_stats["enhanced_storage_ops"] += 1
            
        except Exception as e:
            logging.warning(f"Ошибка инициализации БД v2.1: {e}")
    
    async def _gpu_accelerated_analysis(self, user_input: str, work_context: Dict[str, Any]) -> EmotionalMetrics:
        """GPU-ускоренный анализ эмоций (v2.1)"""
        if not self.gpu_support:
            return await self._fallback_analysis(user_input, work_context)
        
        try:
            # Подготовка данных для GPU
            features = self._prepare_emotion_features(user_input, work_context)
            
            # GPU обработка (быстрее в 3-5 раз для больших данных)
            gpu_result = await self.gpu_support.accelerate_tensor_operation(
                operation="emotion_analysis",
                data=features,
                model="emotion_classifier_v2_1"
            )
            
            self.v21_stats["gpu_analyzes"] += 1
            
            # Преобразование GPU результатов в метрики
            metrics = self._gpu_result_to_metrics(gpu_result, work_context)
            
            return metrics
            
        except Exception as e:
            logging.warning(f"GPU анализ недоступен, использую fallback: {e}")
            return await self._fallback_analysis(user_input, work_context)
    
    def _prepare_emotion_features(self, user_input: str, work_context: Dict[str, Any]) -> np.ndarray:
        """Подготовка признаков для GPU анализа"""
        features = []
        
        # Текстовые признаки
        text_lower = user_input.lower()
        
        # Энергетические ключевые слова
        energy_words = ["устал", "сонный", "энергии нет", "выдохся", "сил нет", "усталость"]
        focus_words = ["отвлекается", "не могу сосредоточиться", "мысли скачут", "рассеивается"]
        frustration_words = ["бесит", "достало", "не работает", "глючит", "ошибка", "гнев"]
        satisfaction_words = ["получилось", "классно", "отлично", "доволен", "успех"]
        motivation_words = ["мотивация", "хочется", "интересно", "вдохновляет"]
        
        # Подсчет ключевых слов
        features.append(sum(1 for word in energy_words if word in text_lower))
        features.append(sum(1 for word in focus_words if word in text_lower))
        features.append(sum(1 for word in frustration_words if word in text_lower))
        features.append(sum(1 for word in satisfaction_words if word in text_lower))
        features.append(sum(1 for word in motivation_words if word in text_lower))
        
        # Контекстные признаки из работы
        if work_context:
            work_duration = work_context.get('work_duration_minutes', 30)
            error_count = work_context.get('error_count', 0)
            progress = work_context.get('completion_percentage', 0.5)
            
            features.extend([
                min(1.0, work_duration / 120.0),  # нормированная длительность
                min(1.0, error_count / 10.0),     # нормированные ошибки
                progress,                         # прогресс
                work_duration / 60.0              # часы работы
            ])
        else:
            features.extend([0.5, 0.0, 0.5, 0.0])
        
        return np.array(features, dtype=np.float32)
    
    def _gpu_result_to_metrics(self, gpu_result: Any, work_context: Dict[str, Any]) -> EmotionalMetrics:
        """Преобразование GPU результатов в эмоциональные метрики"""
        if isinstance(gpu_result, dict) and 'emotion_scores' in gpu_result:
            scores = gpu_result['emotion_scores']
            return EmotionalMetrics(
                energy_level=scores.get('energy', 0.5),
                focus_level=scores.get('focus', 0.5),
                frustration_level=scores.get('frustration', 0.3),
                satisfaction_level=scores.get('satisfaction', 0.5),
                motivation_level=scores.get('motivation', 0.5),
                stress_level=scores.get('stress', 0.3)
            )
        else:
            # Fallback к базовому анализу
            return self._basic_emotion_analysis(work_context)
    
    async def _llm_enhanced_analysis(self, user_input: str, basic_metrics: EmotionalMetrics) -> EmotionalMetrics:
        """LLM-улучшенный анализ эмоций (v2.1)"""
        if not self.llm_wrapper:
            return basic_metrics
        
        try:
            prompt = f"""
            Проанализируй эмоциональное состояние пользователя на основе:
            
            Ввод: "{user_input}"
            
            Базовые метрики:
            - Энергия: {basic_metrics.energy_level}
            - Фокус: {basic_metrics.focus_level}
            - Фрустрация: {basic_metrics.frustration_level}
            - Удовлетворение: {basic_metrics.satisfaction_level}
            - Мотивация: {basic_metrics.motivation_level}
            - Стресс: {basic_metrics.stress_level}
            
            Дай улучшенные метрики в JSON формате с ключами: energy_level, focus_level, frustration_level, satisfaction_level, motivation_level, stress_level
            """
            
            llm_response = await self.llm_wrapper.generate_response(
                prompt=prompt,
                model="emotion_analyst_v2_1",
                max_tokens=150
            )
            
            # Парсинг LLM ответа
            improved_metrics = self._parse_llm_emotion_response(llm_response)
            
            self.v21_stats["llm_analyzes"] += 1
            
            return improved_metrics
            
        except Exception as e:
            logging.warning(f"LLM анализ недоступен, использую базовые метрики: {e}")
            return basic_metrics
    
    def _parse_llm_emotion_response(self, llm_response: str) -> EmotionalMetrics:
        """Парсинг LLM ответа для улучшенных метрик"""
        try:
            # Простой парсинг JSON из ответа
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                metrics_dict = json.loads(json_match.group())
                return EmotionalMetrics(
                    energy_level=float(metrics_dict.get('energy_level', 0.5)),
                    focus_level=float(metrics_dict.get('focus_level', 0.5)),
                    frustration_level=float(metrics_dict.get('frustration_level', 0.3)),
                    satisfaction_level=float(metrics_dict.get('satisfaction_level', 0.5)),
                    motivation_level=float(metrics_dict.get('motivation_level', 0.5)),
                    stress_level=float(metrics_dict.get('stress_level', 0.3))
                )
        except Exception as e:
            logging.warning(f"Ошибка парсинга LLM ответа: {e}")
        
        # Fallback к базовым значениям
        return EmotionalMetrics(0.5, 0.5, 0.3, 0.5, 0.5, 0.3)
    
    async def _fallback_analysis(self, user_input: str, work_context: Dict[str, Any]) -> EmotionalMetrics:
        """Fallback анализ без GPU/LLM (совместимость)"""
        return self._basic_emotion_analysis(work_context)
    
    def _basic_emotion_analysis(self, work_context: Dict[str, Any]) -> EmotionalMetrics:
        """Базовый анализ эмоций без GPU/LLM"""
        # Упрощенная версия базового анализа
        work_energy = 0.5
        work_focus = 0.5
        work_stress = 0.3
        
        if work_context:
            work_duration = work_context.get('work_duration_minutes', 30)
            if work_duration > 90:
                work_energy = max(0.1, 1.0 - (work_duration - 90) / 120)
                work_stress = min(1.0, 0.3 + (work_duration - 90) / 60)
            
            error_count = work_context.get('error_count', 0)
            work_stress += error_count * 0.1
            work_focus = max(0.2, 1.0 - error_count * 0.15)
            
            progress = work_context.get('completion_percentage', 0.5)
            work_satisfaction = progress
            work_motivation = min(1.0, 0.5 + progress * 0.5)
        
        return EmotionalMetrics(
            energy_level=work_energy,
            focus_level=work_focus,
            frustration_level=work_stress,
            satisfaction_level=work_satisfaction if 'work_satisfaction' in locals() else 0.5,
            motivation_level=work_motivation if 'work_motivation' in locals() else 0.5,
            stress_level=work_stress
        )
    
    async def analyze_emotional_state(self, user_input: str = "", work_context: Dict[str, Any] = None) -> EmotionalMetrics:
        """Анализ эмоционального состояния пользователя (v2.1)"""
        
        start_time = time.time()
        
        # v2.1 анализ: GPU + LLM + fallback
        if GPU_AVAILABLE:
            basic_metrics = await self._gpu_accelerated_analysis(user_input, work_context)
        else:
            basic_metrics = await self._fallback_analysis(user_input, work_context)
        
        # LLM улучшение если доступно
        if LLM_AVAILABLE:
            final_metrics = await self._llm_enhanced_analysis(user_input, basic_metrics)
        else:
            final_metrics = basic_metrics
        
        # Enhanced Storage для больших данных
        if len(self.current_mood_tracking) > 1000 and STORAGE_AVAILABLE:
            try:
                await self._archive_old_emotions()
            except Exception as e:
                logging.warning(f"Ошибка архивации: {e}")
        
        # Сохранение в историю
        self.current_mood_tracking.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "metrics": final_metrics,
            "context": work_context,
            "user_input": user_input,
            "processing_time_ms": (time.time() - start_time) * 1000,
            "gpu_used": GPU_AVAILABLE,
            "llm_used": LLM_AVAILABLE
        })
        
        # Сохранение в БД v2.1
        await self._save_to_database_v21(user_input, final_metrics, work_context, start_time)
        
        self.v21_stats["total_interactions"] += 1
        
        return final_metrics
    
    async def _save_to_database_v21(self, user_input: str, metrics: EmotionalMetrics, 
                                   work_context: Dict[str, Any], start_time: float):
        """Сохранение метрик в БД v2.1"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO emotional_metrics 
                (timestamp, user_input, energy_level, focus_level, frustration_level,
                 satisfaction_level, motivation_level, stress_level, work_duration_minutes,
                 error_count, completion_percentage, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(), user_input, metrics.energy_level, metrics.focus_level,
                metrics.frustration_level, metrics.satisfaction_level, metrics.motivation_level,
                metrics.stress_level, work_context.get('work_duration_minutes', 30) if work_context else 30,
                work_context.get('error_count', 0) if work_context else 0,
                work_context.get('completion_percentage', 0.5) if work_context else 0.5,
                work_context.get('session_id', 'default') if work_context else 'default'
            ))
            
            # v2.1 статистика
            processing_time_ms = (time.time() - start_time) * 1000
            cursor.execute('''
                INSERT INTO v21_stats (timestamp, metric_name, metric_value, additional_data)
                VALUES (?, ?, ?, ?)
            ''', (
                time.time(), "analysis_processing_time", processing_time_ms,
                f"gpu:{GPU_AVAILABLE},llm:{LLM_AVAILABLE},enhanced_storage:{STORAGE_AVAILABLE}"
            ))
            
            conn.commit()
            conn.close()
            
            self.v21_stats["enhanced_storage_ops"] += 1
            
        except Exception as e:
            logging.warning(f"Ошибка сохранения в БД v2.1: {e}")
    
    async def _archive_old_emotions(self):
        """Архивация старых эмоциональных данных в Enhanced Storage"""
        if not self.enhanced_storage:
            return
        
        try:
            # Архивация данных старше 7 дней
            cutoff_time = datetime.datetime.now() - datetime.timedelta(days=7)
            
            recent_data = [
                entry for entry in self.current_mood_tracking 
                if datetime.datetime.fromisoformat(entry["timestamp"]) > cutoff_time
            ]
            
            if len(self.current_mood_tracking) - len(recent_data) > 0:
                old_data = [
                    entry for entry in self.current_mood_tracking 
                    if datetime.datetime.fromisoformat(entry["timestamp"]) <= cutoff_time
                ]
                
                # Сохранение в Enhanced Storage
                archive_key = f"emotions_archive_{datetime.datetime.now().strftime('%Y%m%d')}"
                await self.enhanced_storage.store_data(
                    key=archive_key,
                    data=old_data,
                    storage_type=StorageType.LONG_TERM
                )
                
                # Очистка старых данных из памяти
                self.current_mood_tracking = recent_data
                
                logging.info(f"Архивировано {len(old_data)} записей эмоциональных данных")
                
        except Exception as e:
            logging.warning(f"Ошибка архивации эмоциональных данных: {e}")
    
    async def generate_support_response(self, metrics: EmotionalMetrics, context: Dict[str, Any] = None) -> SupportResponse:
        """Генерация ответа поддержки на основе эмоционального анализа (v2.1)"""
        
        # Определение основного состояния (улучшенная логика v2.1)
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
        
        # v2.1 улучшенный выбор действия поддержки
        action, message, activities = await self._select_support_action_v21(primary_state, metrics, context)
        
        return SupportResponse(
            action=action,
            message=message,
            emotional_state=primary_state,
            suggested_activities=activities,
            urgency_level=urgency,
            follow_up_needed=urgency > 0.6
        )
    
    async def _select_support_action_v21(self, state: EmotionalState, metrics: EmotionalMetrics, 
                                       context: Dict[str, Any]) -> Tuple[SupportAction, str, List[str]]:
        """Выбор конкретного действия поддержки (v2.1 улучшенная логика)"""
        
        if state == EmotionalState.TIRED:
            joke = random.choice(self.jokes_collection)
            
            # v2.1 персонализация сообщения
            time_of_day = datetime.datetime.now().hour
            if 6 <= time_of_day < 12:
                time_greeting = "Доброе утро"
            elif 12 <= time_of_day < 18:
                time_greeting = "Добрый день"
            else:
                time_greeting = "Добрый вечер"
            
            message = f"{time_greeting}! Похоже, вы устали! {joke['setup']} {joke['punchline']}\n\nА теперь давайте сделаем перерыв! {random.choice(self.energy_boost_activities)}"
            return (SupportAction.BREAK_SUGGESTION, message, self.energy_boost_activities)
        
        elif state == EmotionalState.FRUSTRATED:
            encouragement = random.choice(self.encouragement_phrases)
            perspective = random.choice(self.perspective_shifts)
            
            # v2.1 более эмпатичное сообщение
            message = f"Понимаю, как тяжело бывает в такие моменты. {encouragement}\n\nА давайте посмотрим на это под другим углом:\n{perspective}"
            return (SupportAction.COMFORT, message, self.perspective_shifts)
        
        elif state == EmotionalState.CONFUSED:
            technique = random.choice(self.focus_techniques)
            
            # v2.1 контекстуальные техники
            if context and context.get('task_type') == 'debugging':
                technique = "Техника резиновой утки: объясните проблему вслух или плюшевому утенку"
            
            message = f"Замечаю, что фокус стал рассеиваться. Вот техника, которая может помочь:\n\n{technique}"
            return (SupportAction.FOCUS_TECHNIQUE, message, self.focus_techniques)
        
        elif state == EmotionalState.SATISFIED:
            # v2.1 персонализированное поздравление
            achievement = context.get('current_achievement', 'важный результат') if context else 'важный результат'
            message = f"Отлично! Вы достигли {achievement}! 🎉\n\nВаша работа продвигается отлично. Это достижение стоит отметить!"
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
        """Рассказывание мотивирующего анекдота (v2.1)"""
        if category == "random":
            joke = random.choice(self.jokes_collection)
        else:
            jokes = [j for j in self.jokes_collection if j["category"] == category]
            joke = random.choice(jokes) if jokes else random.choice(self.jokes_collection)
        
        return joke
    
    async def emergency_support(self, crisis_level: float = 0.9) -> SupportResponse:
        """Экстренная поддержка при высоком уровне стресса (v2.1 улучшенная)"""
        
        crisis_messages = [
            "Стоп. Сейчас важнее всего ваше благополучие. Давайте сделаем паузу.",
            "Вы делаете невероятную работу. Ошибки - это часть процесса обучения.",
            "Каждый великий программист когда-то был начинающим. Не будьте к себе слишком строги.",
            "Ваше здоровье важнее любого кода. Сделайте глубокий вдох.",
            "Помните: баги исправляются, а здоровье - нет. Позаботьтесь о себе.",
            # v2.1 добавлено: более персонализированные сообщения
            "Ваш прогресс впечатляет. Не позволяйте временным трудностям затмить ваши достижения.",
            "Каждая проблема - это возможность стать лучше. Вы справитесь с этим!",
            "Ваше терпение и упорство - ваши суперсилы. Используйте их мудро."
        ]
        
        message = random.choice(crisis_messages)
        
        emergency_activities = [
            "Закройте глаза на 2 минуты",
            "Выпейте стакан воды медленно",
            "Встаньте и пройдитесь",
            "Позвоните другу",
            "Послушайте расслабляющую музыку",
            # v2.1 добавлено: больше активностей
            "Сделайте 5-минутную медитацию",
            "Напишите 3 вещи, за которые благодарны",
            "Выходите на улицу на 5 минут"
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
        """Адаптивное поощрение на основе прогресса проекта (v2.1 улучшенное)"""
        
        completion_rate = progress_metrics.get("completion_rate", 0.5)
        quality_score = progress_metrics.get("quality_score", 0.5)
        innovation_level = progress_metrics.get("innovation_score", 0.5)
        bug_count = progress_metrics.get("bug_count", 0)
        
        if completion_rate > 0.9:
            return f"🔥 Невероятно! Вы почти у цели! Качество {quality_score:.1%} и инновации {innovation_level:.1%} - это профессиональный уровень! Осталось совсем немного!"
        elif completion_rate > 0.7:
            return f"💪 Отличная работа! {completion_rate:.1%} проекта завершено. Вы в отличной форме! Каждый компонент работает как часы!"
        elif completion_rate > 0.5:
            return f"🚀 Прогресс идет хорошо! Половина пути пройдена. Каждая строчка кода приближает к цели!"
        elif completion_rate > 0.3:
            return f"✨ Неплохой старт! {completion_rate:.1%} проекта готово. Время набрать темп!"
        elif completion_rate > 0.1:
            return f"🎯 Каждый проект начинается с первого шага. Ваш старт уже заложил фундамент успеха!"
        else:
            return f"🌱 Любое великое начинание с маленького шага. Вы уже на пути к чему-то удивительному!"
    
    async def get_emotional_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Получение сводки эмоционального состояния за период (v2.1 улучшенное)"""
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=time_window_hours)
        recent_data = [
            entry for entry in self.current_mood_tracking 
            if datetime.datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        if not recent_data:
            return {"status": "no_data", "message": "Недостаточно данных за период"}
        
        # v2.1 расширенный анализ трендов
        energy_trend = sum(e["metrics"].energy_level for e in recent_data) / len(recent_data)
        focus_trend = sum(e["metrics"].focus_level for e in recent_data) / len(recent_data)
        frustration_trend = sum(e["metrics"].frustration_level for e in recent_data) / len(recent_data)
        satisfaction_trend = sum(e["metrics"].satisfaction_level for e in recent_data) / len(recent_data)
        motivation_trend = sum(e["metrics"].motivation_level for e in recent_data) / len(recent_data)
        
        # v2.1 анализ производительности системы
        avg_processing_time = sum(e.get("processing_time_ms", 0) for e in recent_data) / len(recent_data)
        gpu_usage_rate = sum(1 for e in recent_data if e.get("gpu_used", False)) / len(recent_data)
        llm_usage_rate = sum(1 for e in recent_data if e.get("llm_used", False)) / len(recent_data)
        
        # Рекомендации (v2.1 расширенные)
        recommendations = []
        if frustration_trend > 0.6:
            recommendations.append("Уровень фрустрации высок - рекомендуется больше перерывов и техник релаксации")
        if energy_trend < 0.4:
            recommendations.append("Энергия низкая - важно следить за режимом отдыха и питания")
        if focus_trend < 0.5:
            recommendations.append("Фокус нестабилен - используйте техники концентрации и тайм-менеджмента")
        if motivation_trend < 0.4:
            recommendations.append("Мотивация снижена - напомните себе о целях и достижениях")
        if satisfaction_trend > 0.7:
            recommendations.append("Отличное настроение! Используйте этот период для решения сложных задач")
        
        # v2.1 добавляет системные рекомендации
        system_recommendations = []
        if avg_processing_time > 100:  # > 100ms
            system_recommendations.append("Производительность системы можно улучшить")
        if gpu_usage_rate > 0.5:
            system_recommendations.append("Активно используется GPU - система работает эффективно")
        if llm_usage_rate > 0.3:
            system_recommendations.append("Часто используется LLM - интеллектуальный анализ активен")
        
        return {
            "period_hours": time_window_hours,
            "data_points": len(recent_data),
            "energy_trend": energy_trend,
            "focus_trend": focus_trend,
            "frustration_trend": frustration_trend,
            "satisfaction_trend": satisfaction_trend,
            "motivation_trend": motivation_trend,
            "overall_mood": "positive" if energy_trend > 0.6 and frustration_trend < 0.4 else "needs_attention",
            "recommendations": recommendations,
            # v2.1 добавляет системную информацию
            "system_stats": {
                "avg_processing_time_ms": avg_processing_time,
                "gpu_usage_rate": gpu_usage_rate,
                "llm_usage_rate": llm_usage_rate,
                "version": self.version
            },
            "system_recommendations": system_recommendations
        }
    
    async def get_v21_statistics(self) -> Dict[str, Any]:
        """Получение статистики v2.1"""
        runtime = time.time() - self.v21_stats["start_time"]
        
        return {
            "version": self.version,
            "runtime_seconds": runtime,
            "total_interactions": self.v21_stats["total_interactions"],
            "gpu_analyzes": self.v21_stats["gpu_analyzes"],
            "enhanced_storage_ops": self.v21_stats["enhanced_storage_ops"],
            "llm_analyzes": self.v21_stats["llm_analyzes"],
            "capabilities": {
                "gpu_acceleration": GPU_AVAILABLE,
                "enhanced_storage": STORAGE_AVAILABLE,
                "llm_integration": LLM_AVAILABLE
            },
            "database_path": self.db_path,
            "current_mood_tracking_size": len(self.current_mood_tracking)
        }
