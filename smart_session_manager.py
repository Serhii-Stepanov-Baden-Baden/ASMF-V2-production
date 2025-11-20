"""
ASMF v2.0 - Умный Менеджер Сессий и Проектов
Управляет долгосрочными проектами с автоматическими архивами и переносом контекста
"""

import asyncio
import json
import lz4.frame
import sqlite3
import os
import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import pickle


class ArchiveType(Enum):
    """Типы архивов для классификации данных"""
    NOISE = "noise"                    # Шум - корзина
    CREATIVE_ARCHIVE = "creative"      # Архив творчества 
    SESSION_CARRY = "carry"            # Перенос в новую сессию


class ProjectStatus(Enum):
    """Статусы проектов"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ABANDONED = "abandoned"


@dataclass
class SessionContext:
    """Контекст сессии для переноса"""
    session_id: str
    project_id: str
    user_preferences: Dict[str, Any]
    emotional_state: Dict[str, float]
    active_concepts: List[str]
    knowledge_base: Dict[str, Any]
    work_progress: Dict[str, Any]
    creative_elements: List[str]
    timestamps: Dict[str, str]


@dataclass
class ProjectPhase:
    """Фаза проекта"""
    phase_id: str
    phase_name: str
    description: str
    start_session: str
    end_session: Optional[str]
    status: ProjectStatus
    deliverables: List[str]
    creative_breakthroughs: List[str]
    completion_percentage: float


@dataclass
class CreativeAchievement:
    """Творческое достижение для сохранения в архив"""
    achievement_id: str
    description: str
    code_fragments: List[str]
    concepts_involved: List[str]
    emotional_impact: float
    timestamp: str
    phase_id: str
    innovation_score: float


class SmartSessionManager:
    """Умный менеджер сессий и проектов"""
    
    def __init__(self, base_path: str = "/workspace/ASMF-v2-production/sessions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # База данных проектов и сессий
        self.db_path = self.base_path / "projects.db"
        self.init_database()
        
        # Конфигурация
        self.archive_threshold = 0.90  # 90% для автоархива
        self.max_session_duration = 1800  # 30 минут в секундах
        self.emotional_check_interval = 300  # 5 минут
        
        # Активные сессии и проекты
        self.active_session: Optional[SessionContext] = None
        self.active_project: Optional[str] = None
        self.session_start_time: Optional[datetime.datetime] = None
        
        # Эмоциональный мониторинг
        self.emotional_history = []
        self.creative_moments = []
        
    def init_database(self):
        """Инициализация базы данных проектов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                current_phase TEXT,
                total_phases INTEGER,
                completion_percentage REAL DEFAULT 0
            )
        ''')
        
        # Таблица фаз проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_phases (
                phase_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_name TEXT NOT NULL,
                description TEXT,
                start_session TEXT,
                end_session TEXT,
                status TEXT NOT NULL,
                completion_percentage REAL DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # Таблица сессий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_id TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                context_data TEXT,
                creative_achievements TEXT,
                emotional_summary TEXT,
                work_quality_score REAL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # Таблица творческих достижений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS creative_achievements (
                achievement_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                phase_id TEXT,
                description TEXT NOT NULL,
                code_fragments TEXT,
                concepts_involved TEXT,
                emotional_impact REAL,
                innovation_score REAL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Архивная система
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archives (
                archive_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                archive_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                compression_ratio REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_session(self, project_id: str, user_context: Dict[str, Any] = None) -> SessionContext:
        """Запуск новой сессии"""
        session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start_time = datetime.datetime.now()
        self.active_project = project_id
        
        # Загрузка контекста из предыдущих сессий
        previous_context = await self.load_session_context(project_id)
        
        # Создание контекста сессии
        self.active_session = SessionContext(
            session_id=session_id,
            project_id=project_id,
            user_preferences=previous_context.user_preferences if previous_context else user_context or {},
            emotional_state=previous_context.emotional_state if previous_context else {"energy": 0.8, "focus": 0.9},
            active_concepts=previous_context.active_concepts if previous_context else [],
            knowledge_base=previous_context.knowledge_base if previous_context else {},
            work_progress=previous_context.work_progress if previous_context else {},
            creative_elements=previous_context.creative_elements if previous_context else [],
            timestamps={"session_start": datetime.datetime.now().isoformat()}
        )
        
        # Запись в базу данных
        await self.record_session_start(session_id, project_id)
        
        return self.active_session
    
    async def load_session_context(self, project_id: str) -> Optional[SessionContext]:
        """Загрузка контекста из предыдущих сессий проекта"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем последнюю завершенную сессию
        cursor.execute('''
            SELECT session_id, context_data 
            FROM sessions 
            WHERE project_id = ? AND end_time IS NOT NULL
            ORDER BY start_time DESC 
            LIMIT 1
        ''', (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
            
        session_id, context_data = result
        try:
            context = json.loads(context_data)
            return SessionContext(**context)
        except:
            return None
    
    async def analyze_work_progress(self, current_work: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ прогресса работы для определения потребности в архиве"""
        if not self.active_session:
            return {"needs_archive": False, "reason": "Нет активной сессии"}
        
        # Анализ длительности сессии
        session_duration = (datetime.datetime.now() - self.session_start_time).total_seconds()
        time_factor = min(session_duration / self.max_session_duration, 1.0)
        
        # Анализ объёма работы
        work_volume = len(current_work.get('tasks_completed', []))
        volume_factor = min(work_volume / 10, 1.0)
        
        # Анализ творческих достижений
        creative_score = sum(self.active_session.creative_elements) if self.active_session.creative_elements else 0
        creative_factor = min(creative_score / 5, 1.0)
        
        # Общий прогресс
        total_progress = (time_factor + volume_factor + creative_factor) / 3
        
        needs_archive = total_progress >= self.archive_threshold
        
        return {
            "needs_archive": needs_archive,
            "progress_percentage": total_progress * 100,
            "time_factor": time_factor,
            "volume_factor": volume_factor,
            "creative_factor": creative_factor,
            "reason": "Архив нужен" if needs_archive else "Продолжаем работу"
        }
    
    async def classify_and_archive(self, work_data: Dict[str, Any]) -> Dict[str, str]:
        """Классификация данных и создание архивов"""
        if not self.active_session:
            return {"error": "Нет активной сессии"}
        
        archive_results = {}
        
        for category, data in work_data.items():
            if category == "noise_data":
                archive_type = ArchiveType.NOISE
                archive_path = await self.create_archive(
                    data, ArchiveType.NOISE, f"noise_{self.active_session.session_id}"
                )
                
            elif category in ["breakthrough", "innovation", "creative_solution"]:
                archive_type = ArchiveType.CREATIVE_ARCHIVE
                archive_path = await self.create_archive(
                    data, ArchiveType.CREATIVE_ARCHIVE, f"creative_{self.active_session.session_id}"
                )
                
                # Сохранение творческого достижения
                achievement = CreativeAchievement(
                    achievement_id=f"ach_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=data.get('description', ''),
                    code_fragments=data.get('code', []),
                    concepts_involved=data.get('concepts', []),
                    emotional_impact=data.get('emotional_impact', 0.8),
                    timestamp=datetime.datetime.now().isoformat(),
                    phase_id=self.get_current_phase_id(),
                    innovation_score=data.get('innovation_score', 0.7)
                )
                await self.save_creative_achievement(achievement)
                
            else:
                # Рабочие данные для переноса
                archive_type = ArchiveType.SESSION_CARRY
                archive_path = await self.create_archive(
                    data, ArchiveType.SESSION_CARRY, f"carry_{self.active_session.session_id}"
                )
            
            archive_results[category] = {
                "archive_path": str(archive_path),
                "archive_type": archive_type.value,
                "compressed": True
            }
        
        return archive_results
    
    async def create_archive(self, data: Any, archive_type: ArchiveType, filename: str) -> Path:
        """Создание сжатого архива данных"""
        archive_dir = self.base_path / "archives" / archive_type.value
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Сериализация данных
        serialized_data = pickle.dumps(data)
        
        # Сжатие
        compressed_data = lz4.frame.compress(serialized_data)
        
        # Сохранение
        archive_path = archive_dir / f"{filename}.lz4"
        with open(archive_path, 'wb') as f:
            f.write(compressed_data)
        
        # Запись в базу данных
        await self.record_archive(filename, archive_type, archive_path, len(compressed_data) / len(serialized_data))
        
        return archive_path
    
    async def prepare_session_transfer(self, project_id: str) -> Dict[str, Any]:
        """Подготовка данных для переноса в новую сессию"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем все завершенные фазы проекта
        cursor.execute('''
            SELECT phase_id, phase_name, status, completion_percentage
            FROM project_phases 
            WHERE project_id = ? AND status = ?
            ORDER BY phase_id
        ''', (project_id, ProjectStatus.COMPLETED.value))
        
        completed_phases = cursor.fetchall()
        
        # Получаем творческие достижения
        cursor.execute('''
            SELECT description, code_fragments, innovation_score, emotional_impact
            FROM creative_achievements 
            WHERE project_id = ? AND innovation_score > 0.7
            ORDER BY timestamp DESC
        ''', (project_id,))
        
        achievements = cursor.fetchall()
        
        # Получаем контекст последней сессии
        cursor.execute('''
            SELECT context_data 
            FROM sessions 
            WHERE project_id = ? AND end_time IS NOT NULL
            ORDER BY start_time DESC 
            LIMIT 1
        ''', (project_id,))
        
        last_context = cursor.fetchone()
        last_session_data = json.loads(last_context[0]) if last_context else {}
        
        conn.close()
        
        return {
            "completed_phases": completed_phases,
            "creative_achievements": achievements,
            "last_session_context": last_session_data,
            "transfer_timestamp": datetime.datetime.now().isoformat()
        }
    
    async def emotional_monitoring(self) -> Dict[str, Any]:
        """Мониторинг эмоционального состояния для поддержки"""
        if not self.active_session:
            return {"status": "no_session"}
        
        # Анализ эмоциональной истории
        recent_emotions = self.emotional_history[-5:] if self.emotional_history else []
        
        if not recent_emotions:
            return {"status": "insufficient_data"}
        
        # Вычисление трендов
        energy_trend = sum(e.get('energy', 0) for e in recent_emotions) / len(recent_emotions)
        focus_trend = sum(e.get('focus', 0) for e in recent_emotions) / len(recent_emotions)
        
        recommendations = []
        
        if energy_trend < 0.4:
            recommendations.append({
                "type": "energy_boost",
                "action": "break",
                "message": "Похоже, вы устали. Предлагаю сделать перерыв и рассказать анекдот!"
            })
        
        if focus_trend < 0.5:
            recommendations.append({
                "type": "focus_improvement", 
                "action": "change_activity",
                "message": "Концентрация снижается. Предлагаю переключиться на другую задачу."
            })
        
        if len(recent_emotions) >= 3 and all(e.get('frustration', 0) > 0.7 for e in recent_emotions):
            recommendations.append({
                "type": "frustration_help",
                "action": "encouragement",
                "message": "Замечаю фрустрацию. Помните - каждая проблема это возможность для роста!"
            })
        
        return {
            "energy_level": energy_trend,
            "focus_level": focus_trend,
            "recommendations": recommendations,
            "support_actions": recommendations
        }
    
    async def get_project_memory(self, project_id: str) -> Dict[str, Any]:
        """Получение полной памяти проекта"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Все фазы проекта
        cursor.execute('''
            SELECT * FROM project_phases WHERE project_id = ?
            ORDER BY phase_id
        ''', (project_id,))
        
        phases = cursor.fetchall()
        
        # Все творческие достижения
        cursor.execute('''
            SELECT * FROM creative_achievements WHERE project_id = ?
            ORDER BY timestamp DESC
        ''', (project_id,))
        
        achievements = cursor.fetchall()
        
        # Все сессии
        cursor.execute('''
            SELECT * FROM sessions WHERE project_id = ?
            ORDER BY start_time
        ''', (project_id,))
        
        sessions = cursor.fetchall()
        
        conn.close()
        
        return {
            "project_phases": phases,
            "creative_achievements": achievements,
            "session_history": sessions,
            "total_memory_size": len(str(phases)) + len(str(achievements)) + len(str(sessions))
        }
    
    async def close_session(self, final_work: Dict[str, Any] = None) -> Dict[str, Any]:
        """Завершение сессии с автоматическим архивированием"""
        if not self.active_session:
            return {"error": "Нет активной сессии"}
        
        self.active_session.timestamps["session_end"] = datetime.datetime.now().isoformat()
        
        # Финальный анализ и архивирование
        if final_work:
            archive_results = await self.classify_and_archive(final_work)
        else:
            archive_results = await self.classify_and_archive({"final_work": self.active_session.work_progress})
        
        # Запись завершения сессии
        await self.record_session_end(self.active_session.session_id, archive_results)
        
        # Подготовка данных для следующей сессии
        transfer_data = await self.prepare_session_transfer(self.active_session.project_id)
        
        session_summary = {
            "session_id": self.active_session.session_id,
            "duration": (datetime.datetime.now() - self.session_start_time).total_seconds(),
            "archives_created": len(archive_results),
            "creative_achievements": len([k for k in archive_results.keys() if 'creative' in k]),
            "transfer_data": transfer_data,
            "ready_for_next_session": True
        }
        
        # Очистка активной сессии
        self.active_session = None
        self.active_project = None
        self.session_start_time = None
        
        return session_summary
    
    # Вспомогательные методы для работы с базой данных
    async def record_session_start(self, session_id: str, project_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, project_id, start_time)
            VALUES (?, ?, ?)
        ''', (session_id, project_id, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    async def record_session_end(self, session_id: str, archive_data: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, context_data = ?, creative_achievements = ?
            WHERE session_id = ?
        ''', (
            datetime.datetime.now().isoformat(),
            json.dumps(asdict(self.active_session)) if self.active_session else "{}",
            json.dumps(archive_data),
            session_id
        ))
        conn.commit()
        conn.close()
    
    async def record_archive(self, filename: str, archive_type: ArchiveType, file_path: Path, ratio: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO archives (archive_id, session_id, archive_type, file_path, compression_ratio, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            self.active_session.session_id if self.active_session else "unknown",
            archive_type.value,
            str(file_path),
            ratio,
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    async def save_creative_achievement(self, achievement: CreativeAchievement):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO creative_achievements 
            (achievement_id, session_id, project_id, phase_id, description, 
             code_fragments, concepts_involved, emotional_impact, innovation_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            achievement.achievement_id,
            self.active_session.session_id,
            self.active_session.project_id,
            achievement.phase_id,
            achievement.description,
            json.dumps(achievement.code_fragments),
            json.dumps(achievement.concepts_involved),
            achievement.emotional_impact,
            achievement.innovation_score,
            achievement.timestamp
        ))
        conn.commit()
        conn.close()
    
    def get_current_phase_id(self) -> str:
        """Получение ID текущей фазы проекта"""
        return f"phase_{datetime.datetime.now().strftime('%Y%m%d')}"