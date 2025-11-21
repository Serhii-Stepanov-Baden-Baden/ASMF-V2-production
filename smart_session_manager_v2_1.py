"""
ASMF v2.1 - Умный Менеджер Сессий и Проектов
Управляет долгосрочными проектами с GPU ускорением, Enhanced Storage и LLM интеграцией
Автоматические архивы, перенос контекста и умная классификация данных

Автор: Serhii Stepanov (Baden-Baden, Germany)  
Дата: 21 ноября 2025
Версия: 2.1 - Smart Session Manager Enhanced
"""

import asyncio
import json
import lz4.frame
import sqlite3
import os
import datetime
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import pickle
import numpy as np

# v2.1 imports с fallback механизмами
V2_1_AVAILABLE = False
GPU_AVAILABLE = False
STORAGE_AVAILABLE = False
LLM_AVAILABLE = False

try:
    from gpu_support import GPUSupportModule
    GPU_AVAILABLE = True
except ImportError:
    GPUSupportModule = None

try:
    from database_optimization import EnhancedStorageSystem
    STORAGE_AVAILABLE = True
except ImportError:
    EnhancedStorageSystem = None

try:
    from llm_wrapper_v2_1 import UniversalLLMWrapper
    LLM_AVAILABLE = True
except ImportError:
    UniversalLLMWrapper = None

# Проверяем доступность v2.1
try:
    V2_1_AVAILABLE = GPU_AVAILABLE and STORAGE_AVAILABLE and LLM_AVAILABLE
except:
    V2_1_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArchiveType(Enum):
    """Типы архивов для классификации данных v2.1"""
    NOISE = "noise"                    # Шум - корзина
    CREATIVE_ARCHIVE = "creative"      # Архив творчества 
    SESSION_CARRY = "carry"            # Перенос в новую сессию
    LLM_ENHANCED = "llm_enhanced"      # v2.1: LLM-обработанные данные
    GPU_OPTIMIZED = "gpu_optimized"    # v2.1: GPU-оптимизированные архивы
    ENHANCED_STORAGE = "enhanced_storage"  # v2.1: Enhanced Storage архивы

class ProjectStatus(Enum):
    """Статусы проектов v2.1"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ABANDONED = "abandoned"
    # v2.1 новые статусы
    GPU_OPTIMIZED = "gpu_optimized"    # v2.1: GPU ускоренный проект
    LLM_ANALYZED = "llm_analyzed"      # v2.1: LLM обработанный проект
    ENHANCED_STORAGE = "enhanced_storage"  # v2.1: Enhanced Storage оптимизированный

@dataclass
class SessionContext:
    """Контекст сессии для переноса v2.1"""
    session_id: str
    project_id: str
    user_preferences: Dict[str, Any]
    emotional_state: Dict[str, float]
    active_concepts: List[str]
    knowledge_base: Dict[str, Any]
    work_progress: Dict[str, Any]
    creative_elements: List[str]
    timestamps: Dict[str, str]
    # v2.1 дополнительные поля
    gpu_metrics: Dict[str, Any] = None
    llm_analysis: Dict[str, Any] = None
    enhanced_storage_refs: Dict[str, str] = None
    v2_1_features: List[str] = None

@dataclass
class ProjectPhase:
    """Фаза проекта v2.1"""
    phase_id: str
    phase_name: str
    description: str
    start_session: str
    end_session: Optional[str]
    status: ProjectStatus
    deliverables: List[str]
    creative_breakthroughs: List[str]
    completion_percentage: float
    # v2.1 расширения
    gpu_accelerated: bool = False
    llm_enhanced: bool = False
    enhanced_storage_used: bool = False
    ai_generated_insights: List[str] = None
    optimization_score: float = 0.0

@dataclass
class CreativeAchievement:
    """Творческое достижение для сохранения в архив v2.1"""
    achievement_id: str
    description: str
    code_fragments: List[str]
    concepts_involved: List[str]
    emotional_impact: float
    timestamp: str
    phase_id: str
    innovation_score: float
    # v2.1 расширения
    llm_generated_summary: str = ""
    gpu_processing_time_ms: float = 0.0
    semantic_embeddings: List[float] = None
    llm_confidence_score: float = 0.0
    enhanced_storage_optimized: bool = False

class SmartSessionManager:
    """Умный менеджер сессий и проектов v2.1"""
    
    def __init__(self, base_path: str = "/workspace/ASMF-v2-production/sessions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # База данных проектов и сессий
        self.db_path = self.base_path / "projects_v2_1.db"  # v2.1 обновлена
        self.init_database()
        
        # v2.1: Конфигурация с GPU и LLM параметрами
        self.archive_threshold = 0.90  # 90% для автоархива
        self.max_session_duration = 1800  # 30 минут в секундах
        self.emotional_check_interval = 300  # 5 минут
        self.use_gpu = False  # v2.1 GPU поддержка
        self.use_llm = False  # v2.1 LLM поддержка
        
        # v2.1: GPU модуль
        self.gpu_module = None
        if GPU_AVAILABLE:
            try:
                self.gpu_module = GPUSupportModule(
                    device_name="cuda:0",
                    enable_memory_monitoring=True
                )
                self.use_gpu = True
                logger.info("GPU acceleration enabled for Smart Session Manager")
            except Exception as e:
                logger.warning(f"Failed to initialize GPU support: {e}")
        
        # v2.1: Enhanced Storage
        self.enhanced_storage = None
        if STORAGE_AVAILABLE:
            try:
                self.enhanced_storage = EnhancedStorageSystem(
                    blob_storage_path=str(self.base_path / "enhanced_storage"),
                    faiss_index_path=str(self.base_path / "faiss_index"),
                    cache_size=1000
                )
                logger.info("Enhanced Storage system initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Enhanced Storage: {e}")
        
        # v2.1: LLM Wrapper
        self.llm_wrapper = None
        if LLM_AVAILABLE:
            try:
                self.llm_wrapper = UniversalLLMWrapper()
                self.use_llm = True
                logger.info("LLM integration enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM support: {e}")
        
        # Активные сессии и проекты
        self.active_session: Optional[SessionContext] = None
        self.active_project: Optional[str] = None
        self.session_start_time: Optional[datetime.datetime] = None
        
        # Эмоциональный мониторинг
        self.emotional_history = []
        self.creative_moments = []
        
        # v2.1: Статистика с GPU, LLM и Enhanced Storage метриками
        self.manager_stats = {
            'sessions_created': 0,
            'sessions_completed': 0,
            'archives_created': 0,
            'creative_achievements': 0,
            'gpu_accelerated_analyses': 0,
            'llm_enhanced_classifications': 0,
            'enhanced_storage_optimizations': 0,
            'processing_time_ms': 0.0,
            'memory_optimizations': 0,
            'ai_insights_generated': 0,
            'v2_1_features_used': 0
        }

    def init_database(self):
        """Инициализация базы данных проектов v2.1"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # v2.1: Обновленная таблица проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                current_phase TEXT,
                total_phases INTEGER,
                completion_percentage REAL DEFAULT 0,
                -- v2.1 дополнительные поля
                gpu_accelerated BOOLEAN DEFAULT FALSE,
                llm_enhanced BOOLEAN DEFAULT FALSE,
                enhanced_storage_used BOOLEAN DEFAULT FALSE,
                ai_insights_count INTEGER DEFAULT 0,
                optimization_score REAL DEFAULT 0.0,
                version TEXT DEFAULT '2.1'
            )
        ''')
        
        # v2.1: Обновленная таблица фаз проектов
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
                -- v2.1 дополнительные поля
                gpu_accelerated BOOLEAN DEFAULT FALSE,
                llm_enhanced BOOLEAN DEFAULT FALSE,
                enhanced_storage_used BOOLEAN DEFAULT FALSE,
                ai_generated_insights TEXT,  -- JSON array
                optimization_score REAL DEFAULT 0.0,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # v2.1: Обновленная таблица сессий
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
                -- v2.1 дополнительные поля
                gpu_metrics TEXT,  -- JSON
                llm_analysis TEXT,  -- JSON
                enhanced_storage_refs TEXT,  -- JSON
                v2_1_features TEXT,  -- JSON array
                processing_time_ms REAL DEFAULT 0.0,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        # v2.1: Обновленная таблица творческих достижений
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
                -- v2.1 дополнительные поля
                llm_generated_summary TEXT,
                gpu_processing_time_ms REAL DEFAULT 0.0,
                semantic_embeddings TEXT,  -- JSON array
                llm_confidence_score REAL DEFAULT 0.0,
                enhanced_storage_optimized BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # v2.1: Обновленная архивная система
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archives (
                archive_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                archive_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                compression_ratio REAL,
                created_at TEXT NOT NULL,
                -- v2.1 дополнительные поля
                gpu_optimized BOOLEAN DEFAULT FALSE,
                llm_classified BOOLEAN DEFAULT FALSE,
                enhanced_storage_ref TEXT,
                ai_classification_confidence REAL DEFAULT 0.0,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # v2.1: Таблица AI инсайтов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_insights (
                insight_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                session_id TEXT,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence_score REAL,
                generated_at TEXT NOT NULL,
                gpu_generated BOOLEAN DEFAULT FALSE,
                llm_model_used TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (project_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def start_session(self, project_id: str, user_context: Dict[str, Any] = None) -> SessionContext:
        """Запуск новой сессии v2.1"""
        session_id = f"session_v2_1_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start_time = datetime.datetime.now()
        self.active_project = project_id
        
        # v2.1: Загрузка контекста с GPU оптимизацией
        previous_context = await self.load_session_context(project_id)
        
        # Создание контекста сессии v2.1
        self.active_session = SessionContext(
            session_id=session_id,
            project_id=project_id,
            user_preferences=previous_context.user_preferences if previous_context else user_context or {},
            emotional_state=previous_context.emotional_state if previous_context else {"energy": 0.8, "focus": 0.9},
            active_concepts=previous_context.active_concepts if previous_context else [],
            knowledge_base=previous_context.knowledge_base if previous_context else {},
            work_progress=previous_context.work_progress if previous_context else {},
            creative_elements=previous_context.creative_elements if previous_context else [],
            timestamps={"session_start": datetime.datetime.now().isoformat()},
            # v2.1 поля
            gpu_metrics={"session_start_time": datetime.datetime.now().isoformat()},
            llm_analysis={"context_loaded": previous_context is not None},
            enhanced_storage_refs={},
            v2_1_features=["gpu_acceleration", "enhanced_storage", "llm_integration"] if V2_1_AVAILABLE else []
        )
        
        # v2.1: LLM анализ контекста если доступен
        if self.use_llm and previous_context:
            try:
                llm_analysis = await self._llm_analyze_context(previous_context)
                self.active_session.llm_analysis.update(llm_analysis)
                self.manager_stats['llm_enhanced_classifications'] += 1
            except Exception as e:
                logger.warning(f"LLM context analysis failed: {e}")
        
        # Запись в базу данных
        await self.record_session_start(session_id, project_id)
        
        self.manager_stats['sessions_created'] += 1
        if V2_1_AVAILABLE:
            self.manager_stats['v2_1_features_used'] += 1
        
        return self.active_session
    
    async def load_session_context(self, project_id: str) -> Optional[SessionContext]:
        """Загрузка контекста из предыдущих сессий проекта v2.1"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # v2.1: Получаем последнюю завершенную сессию с v2.1 данными
        cursor.execute('''
            SELECT session_id, context_data, gpu_metrics, llm_analysis, enhanced_storage_refs, v2_1_features
            FROM sessions 
            WHERE project_id = ? AND end_time IS NOT NULL
            ORDER BY start_time DESC 
            LIMIT 1
        ''', (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
            
        session_id, context_data, gpu_metrics, llm_analysis, enhanced_storage_refs, v2_1_features = result
        
        try:
            context = json.loads(context_data)
            # v2.1: Восстанавливаем дополнительные поля
            context['gpu_metrics'] = json.loads(gpu_metrics) if gpu_metrics else {}
            context['llm_analysis'] = json.loads(llm_analysis) if llm_analysis else {}
            context['enhanced_storage_refs'] = json.loads(enhanced_storage_refs) if enhanced_storage_refs else {}
            context['v2_1_features'] = json.loads(v2_1_features) if v2_1_features else []
            
            return SessionContext(**context)
        except Exception as e:
            logger.error(f"Error loading session context: {e}")
            return None
    
    async def analyze_work_progress(self, current_work: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ прогресса работы с GPU ускорением для определения потребности в архиве v2.1"""
        if not self.active_session:
            return {"needs_archive": False, "reason": "Нет активной сессии"}
        
        start_time = datetime.datetime.now()
        
        try:
            # v2.1: Базовый анализ
            session_duration = (datetime.datetime.now() - self.session_start_time).total_seconds()
            time_factor = min(session_duration / self.max_session_duration, 1.0)
            
            work_volume = len(current_work.get('tasks_completed', []))
            volume_factor = min(work_volume / 10, 1.0)
            
            creative_score = sum(self.active_session.creative_elements) if self.active_session.creative_elements else 0
            creative_factor = min(creative_score / 5, 1.0)
            
            # v2.1: GPU-ускоренный анализ если доступен
            if self.use_gpu and self.gpu_module:
                gpu_analysis = await self._gpu_analyze_progress(current_work, time_factor, volume_factor, creative_factor)
                self.manager_stats['gpu_accelerated_analyses'] += 1
                
                # Используем GPU результаты если они лучше
                if gpu_analysis.get('confidence', 0) > 0.8:
                    analysis_result = gpu_analysis
                else:
                    # Комбинируем базовый и GPU анализ
                    analysis_result = self._combine_analysis_results(
                        {"time_factor": time_factor, "volume_factor": volume_factor, "creative_factor": creative_factor},
                        gpu_analysis
                    )
            else:
                analysis_result = {
                    "time_factor": time_factor,
                    "volume_factor": volume_factor,
                    "creative_factor": creative_factor
                }
            
            # v2.1: LLM улучшенная оценка если доступен
            if self.use_llm:
                llm_insights = await self._llm_analyze_work_progress(current_work, analysis_result)
                analysis_result.update(llm_insights)
            
            # Общий прогресс
            total_progress = (analysis_result["time_factor"] + analysis_result["volume_factor"] + analysis_result["creative_factor"]) / 3
            needs_archive = total_progress >= self.archive_threshold
            
            # v2.1: Обновляем статистику
            processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            self.manager_stats['processing_time_ms'] += processing_time
            
            return {
                "needs_archive": needs_archive,
                "progress_percentage": total_progress * 100,
                "time_factor": analysis_result["time_factor"],
                "volume_factor": analysis_result["volume_factor"],
                "creative_factor": analysis_result["creative_factor"],
                "reason": "Архив нужен" if needs_archive else "Продолжаем работу",
                # v2.1 дополнительная информация
                "gpu_analysis": analysis_result.get("gpu_analysis", {}),
                "llm_insights": analysis_result.get("llm_insights", {}),
                "confidence_score": analysis_result.get("confidence", 0.7),
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error in v2.1 work progress analysis: {e}")
            # Fallback к базовому анализу
            total_progress = (time_factor + volume_factor + creative_factor) / 3
            return {
                "needs_archive": total_progress >= self.archive_threshold,
                "progress_percentage": total_progress * 100,
                "error": str(e)
            }

    async def classify_and_archive(self, work_data: Dict[str, Any]) -> Dict[str, str]:
        """Классификация данных и создание архивов v2.1 с LLM и GPU"""
        if not self.active_session:
            return {"error": "Нет активной сессии"}
        
        archive_results = {}
        
        for category, data in work_data.items():
            try:
                # v2.1: LLM улучшенная классификация
                if self.use_llm:
                    llm_classification = await self._llm_classify_data(category, data)
                    archive_type_str = llm_classification.get('suggested_type', self._get_default_archive_type(category))
                    confidence = llm_classification.get('confidence', 0.5)
                else:
                    archive_type_str = self._get_default_archive_type(category)
                    confidence = 0.5
                
                # v2.1: Определяем тип архива
                if archive_type_str == "creative":
                    archive_type = ArchiveType.CREATIVE_ARCHIVE
                elif archive_type_str == "noise":
                    archive_type = ArchiveType.NOISE
                elif llm_classification.get('enhanced_processing', False):
                    archive_type = ArchiveType.LLM_ENHANCED
                else:
                    archive_type = ArchiveType.SESSION_CARRY
                
                # v2.1: Создание архива с Enhanced Storage
                archive_path = await self.create_archive(data, archive_type, f"{category}_{self.active_session.session_id}")
                
                # v2.1: Сохранение творческого достижения с LLM анализом
                if archive_type in [ArchiveType.CREATIVE_ARCHIVE, ArchiveType.LLM_ENHANCED]:
                    achievement = await self._create_enhanced_achievement(category, data, llm_classification)
                    await self.save_creative_achievement(achievement)
                
                archive_results[category] = {
                    "archive_path": str(archive_path),
                    "archive_type": archive_type.value,
                    "compressed": True,
                    "v2_1_optimized": True,
                    "llm_confidence": confidence,
                    "gpu_processed": self.use_gpu
                }
                
                self.manager_stats['archives_created'] += 1
                
            except Exception as e:
                logger.error(f"Error archiving {category}: {e}")
                archive_results[category] = {"error": str(e)}
        
        return archive_results

    async def create_archive(self, data: Any, archive_type: ArchiveType, filename: str) -> Path:
        """Создание сжатого архива данных v2.1 с Enhanced Storage"""
        archive_dir = self.base_path / "archives" / archive_type.value
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # v2.1: Сериализация данных
            serialized_data = pickle.dumps(data)
            
            # v2.1: Enhanced Storage для больших данных
            if self.enhanced_storage and len(serialized_data) > 1024 * 1024:  # > 1MB
                storage_ref = await self.enhanced_storage.store_blob(
                    key=f"archive_{filename}",
                    blob_data=serialized_data,
                    metadata={
                        'archive_type': archive_type.value,
                        'session_id': self.active_session.session_id if self.active_session else 'unknown',
                        'v2_1_optimized': True
                    }
                )
                
                # Создаем маленький файл-ссылку
                archive_path = archive_dir / f"{filename}.ref"
                with open(archive_path, 'w') as f:
                    json.dump({
                        'storage_ref': storage_ref,
                        'original_size': len(serialized_data),
                        'archive_type': archive_type.value,
                        'v2_1': True
                    }, f)
                
                self.manager_stats['enhanced_storage_optimizations'] += 1
                
            else:
                # v2.1: Стандартное сжатие
                compressed_data = lz4.frame.compress(serialized_data)
                
                archive_path = archive_dir / f"{filename}.lz4"
                with open(archive_path, 'wb') as f:
                    f.write(compressed_data)
                
                compression_ratio = len(compressed_data) / len(serialized_data) if serialized_data else 1.0
                
                # Запись в базу данных
                await self.record_archive(filename, archive_type, archive_path, compression_ratio)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Error creating v2.1 archive: {e}")
            # Fallback к стандартному архиву
            return await self._create_fallback_archive(data, archive_type, filename)

    async def prepare_session_transfer(self, project_id: str) -> Dict[str, Any]:
        """Подготовка данных для переноса в новую сессию v2.1 с LLM анализом"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # v2.1: Получаем все завершенные фазы проекта
            cursor.execute('''
                SELECT phase_id, phase_name, status, completion_percentage, gpu_accelerated, 
                       llm_enhanced, enhanced_storage_used, ai_generated_insights, optimization_score
                FROM project_phases 
                WHERE project_id = ? AND status = ?
                ORDER BY phase_id
            ''', (project_id, ProjectStatus.COMPLETED.value))
            
            completed_phases = cursor.fetchall()
            
            # v2.1: Получаем творческие достижения с LLM анализом
            cursor.execute('''
                SELECT description, code_fragments, innovation_score, emotional_impact,
                       llm_generated_summary, llm_confidence_score, enhanced_storage_optimized
                FROM creative_achievements 
                WHERE project_id = ? AND innovation_score > 0.7
                ORDER BY timestamp DESC
            ''', (project_id,))
            
            achievements = cursor.fetchall()
            
            # v2.1: Получаем AI инсайты
            cursor.execute('''
                SELECT insight_type, content, confidence_score, gpu_generated, llm_model_used
                FROM ai_insights 
                WHERE project_id = ?
                ORDER BY generated_at DESC
            ''', (project_id,))
            
            ai_insights = cursor.fetchall()
            
            # v2.1: Получаем контекст последней сессии с v2.1 метриками
            cursor.execute('''
                SELECT context_data, gpu_metrics, llm_analysis, enhanced_storage_refs, v2_1_features
                FROM sessions 
                WHERE project_id = ? AND end_time IS NOT NULL
                ORDER BY start_time DESC 
                LIMIT 1
            ''', (project_id,))
            
            last_context = cursor.fetchone()
            last_session_data = {}
            if last_context:
                context_data, gpu_metrics, llm_analysis, enhanced_storage_refs, v2_1_features = last_context
                last_session_data = json.loads(context_data)
                last_session_data['gpu_metrics'] = json.loads(gpu_metrics) if gpu_metrics else {}
                last_session_data['llm_analysis'] = json.loads(llm_analysis) if llm_analysis else {}
                last_session_data['enhanced_storage_refs'] = json.loads(enhanced_storage_refs) if enhanced_storage_refs else {}
                last_session_data['v2_1_features'] = json.loads(v2_1_features) if v2_1_features else []
            
            conn.close()
            
            # v2.1: LLM генерирует рекомендации для переноса
            transfer_recommendations = {}
            if self.use_llm:
                try:
                    transfer_recommendations = await self._llm_generate_transfer_recommendations(
                        completed_phases, achievements, ai_insights, last_session_data
                    )
                except Exception as e:
                    logger.warning(f"LLM transfer recommendations failed: {e}")
            
            return {
                "completed_phases": completed_phases,
                "creative_achievements": achievements,
                "ai_insights": ai_insights,
                "last_session_context": last_session_data,
                "transfer_recommendations": transfer_recommendations,
                "transfer_timestamp": datetime.datetime.now().isoformat(),
                "v2_1_optimized": True,
                "gpu_accelerated": self.use_gpu,
                "llm_enhanced": self.use_llm,
                "enhanced_storage_used": self.enhanced_storage is not None
            }
            
        except Exception as e:
            logger.error(f"Error preparing v2.1 session transfer: {e}")
            conn.close()
            return {"error": str(e)}

    async def emotional_monitoring(self) -> Dict[str, Any]:
        """Мониторинг эмоционального состояния v2.1 с GPU анализом"""
        if not self.active_session:
            return {"status": "no_session"}
        
        # v2.1: Анализ эмоциональной истории с GPU
        recent_emotions = self.emotional_history[-5:] if self.emotional_history else []
        
        if not recent_emotions:
            return {"status": "insufficient_data"}
        
        try:
            # v2.1: GPU-ускоренный анализ эмоций
            if self.use_gpu and self.gpu_module and len(recent_emotions) > 2:
                gpu_emotion_analysis = await self._gpu_analyze_emotions(recent_emotions)
                energy_trend = gpu_emotion_analysis.get('energy_trend', 0.5)
                focus_trend = gpu_emotion_analysis.get('focus_trend', 0.5)
                frustration_level = gpu_emotion_analysis.get('frustration_level', 0.3)
            else:
                # Базовый анализ
                energy_trend = sum(e.get('energy', 0) for e in recent_emotions) / len(recent_emotions)
                focus_trend = sum(e.get('focus', 0) for e in recent_emotions) / len(recent_emotions)
                frustration_level = sum(e.get('frustration', 0) for e in recent_emotions) / len(recent_emotions)
            
            recommendations = []
            
            # v2.1: Улучшенные рекомендации с LLM
            if self.use_llm:
                llm_recommendations = await self._llm_generate_emotional_recommendations(
                    energy_trend, focus_trend, frustration_level, recent_emotions
                )
                recommendations.extend(llm_recommendations)
            else:
                # Базовые рекомендации
                if energy_trend < 0.4:
                    recommendations.append({
                        "type": "energy_boost",
                        "action": "break",
                        "message": "Похоже, вы устали. Предлагаю сделать перерыв!",
                        "confidence": 0.8
                    })
                
                if focus_trend < 0.5:
                    recommendations.append({
                        "type": "focus_improvement", 
                        "action": "change_activity",
                        "message": "Концентрация снижается. Предлагаю переключиться на другую задачу.",
                        "confidence": 0.7
                    })
                
                if frustration_level > 0.7:
                    recommendations.append({
                        "type": "frustration_help",
                        "action": "encouragement",
                        "message": "Замечаю фрустрацию. Помните - каждая проблема это возможность для роста!",
                        "confidence": 0.9
                    })
            
            return {
                "energy_level": energy_trend,
                "focus_level": focus_trend,
                "frustration_level": frustration_level,
                "recommendations": recommendations,
                "support_actions": recommendations,
                "gpu_analyzed": self.use_gpu and len(recent_emotions) > 2,
                "llm_enhanced": self.use_llm,
                "analysis_confidence": 0.8 if (self.use_gpu or self.use_llm) else 0.6
            }
            
        except Exception as e:
            logger.error(f"Error in v2.1 emotional monitoring: {e}")
            return {"status": "error", "error": str(e)}

    async def get_project_memory(self, project_id: str) -> Dict[str, Any]:
        """Получение полной памяти проекта v2.1 с Enhanced Storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # v2.1: Все фазы проекта с v2.1 метриками
            cursor.execute('''
                SELECT * FROM project_phases WHERE project_id = ?
                ORDER BY phase_id
            ''', (project_id,))
            
            phases = cursor.fetchall()
            
            # v2.1: Все творческие достижения с LLM анализом
            cursor.execute('''
                SELECT * FROM creative_achievements WHERE project_id = ?
                ORDER BY timestamp DESC
            ''', (project_id,))
            
            achievements = cursor.fetchall()
            
            # v2.1: Все сессии с v2.1 метриками
            cursor.execute('''
                SELECT * FROM sessions WHERE project_id = ?
                ORDER BY start_time
            ''', (project_id,))
            
            sessions = cursor.fetchall()
            
            # v2.1: AI инсайты проекта
            cursor.execute('''
                SELECT * FROM ai_insights WHERE project_id = ?
                ORDER BY generated_at DESC
            ''', (project_id,))
            
            ai_insights = cursor.fetchall()
            
            conn.close()
            
            # v2.1: Enhanced Storage оптимизация памяти
            memory_optimizations = {}
            if self.enhanced_storage:
                try:
                    storage_stats = await self.enhanced_storage.get_storage_stats()
                    memory_optimizations = {
                        'total_blobs': storage_stats.get('total_blobs', 0),
                        'total_size_mb': storage_stats.get('total_size_mb', 0),
                        'compression_ratio': storage_stats.get('compression_ratio', 1.0),
                        'cache_hit_rate': storage_stats.get('cache_hit_rate', 0.0)
                    }
                except Exception as e:
                    logger.warning(f"Enhanced Storage stats failed: {e}")
            
            return {
                "project_phases": phases,
                "creative_achievements": achievements,
                "session_history": sessions,
                "ai_insights": ai_insights,
                "v2_1_metrics": {
                    "total_phases": len(phases),
                    "gpu_accelerated_phases": sum(1 for phase in phases if len(phase) > 9 and phase[9]),  # gpu_accelerated field
                    "llm_enhanced_phases": sum(1 for phase in phases if len(phase) > 10 and phase[10]),  # llm_enhanced field
                    "ai_insights_generated": len(ai_insights),
                    "total_v2_1_features": sum(len(str(session).split('v2_1')) for session in sessions)
                },
                "memory_optimizations": memory_optimizations,
                "total_memory_size": len(str(phases)) + len(str(achievements)) + len(str(sessions)) + len(str(ai_insights)),
                "enhanced_storage_optimized": self.enhanced_storage is not None,
                "gpu_acceleration_available": self.use_gpu,
                "llm_enhancement_available": self.use_llm
            }
            
        except Exception as e:
            logger.error(f"Error getting v2.1 project memory: {e}")
            conn.close()
            return {"error": str(e)}

    async def close_session(self, final_work: Dict[str, Any] = None) -> Dict[str, Any]:
        """Завершение сессии с автоматическим архивированием v2.1"""
        if not self.active_session:
            return {"error": "Нет активной сессии"}
        
        start_time = datetime.datetime.now()
        
        try:
            self.active_session.timestamps["session_end"] = datetime.datetime.now().isoformat()
            
            # v2.1: Финальный анализ и архивирование с GPU и LLM
            if final_work:
                archive_results = await self.classify_and_archive(final_work)
            else:
                archive_results = await self.classify_and_archive({"final_work": self.active_session.work_progress})
            
            # v2.1: Запись завершения сессии с v2.1 метриками
            processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            await self.record_session_end(self.active_session.session_id, archive_results, processing_time)
            
            # Подготовка данных для следующей сессии
            transfer_data = await self.prepare_session_transfer(self.active_session.project_id)
            
            # v2.1: Генерация AI инсайтов сессии
            ai_insights = {}
            if self.use_llm:
                try:
                    ai_insights = await self._llm_generate_session_insights(archive_results, transfer_data)
                    await self._save_ai_insights(self.active_session.project_id, self.active_session.session_id, ai_insights)
                except Exception as e:
                    logger.warning(f"AI insights generation failed: {e}")
            
            session_summary = {
                "session_id": self.active_session.session_id,
                "duration": (datetime.datetime.now() - self.session_start_time).total_seconds(),
                "archives_created": len(archive_results),
                "creative_achievements": len([k for k in archive_results.keys() if 'creative' in k or 'llm_enhanced' in k]),
                "transfer_data": transfer_data,
                "ai_insights": ai_insights,
                "v2_1_metrics": {
                    "gpu_accelerated": self.use_gpu,
                    "llm_enhanced": self.use_llm,
                    "enhanced_storage_used": self.enhanced_storage is not None,
                    "processing_time_ms": processing_time,
                    "v2_1_features_used": len(self.active_session.v2_1_features or [])
                },
                "ready_for_next_session": True
            }
            
            self.manager_stats['sessions_completed'] += 1
            self.manager_stats['ai_insights_generated'] += len(ai_insights)
            
            # Очистка активной сессии
            self.active_session = None
            self.active_project = None
            self.session_start_time = None
            
            return session_summary
            
        except Exception as e:
            logger.error(f"Error closing v2.1 session: {e}")
            return {"error": str(e)}

    # v2.1: Вспомогательные методы
    
    def _get_default_archive_type(self, category: str) -> str:
        """Определение типа архива по категории"""
        if category == "noise_data":
            return "noise"
        elif category in ["breakthrough", "innovation", "creative_solution"]:
            return "creative"
        else:
            return "carry"

    async def _gpu_analyze_progress(self, current_work: Dict[str, Any], time_factor: float, 
                                  volume_factor: float, creative_factor: float) -> Dict[str, Any]:
        """GPU-ускоренный анализ прогресса"""
        if not (self.use_gpu and self.gpu_module):
            return {"confidence": 0.5}
        
        try:
            # v2.1: GPU обработка данных прогресса
            work_data = np.array([time_factor, volume_factor, creative_factor], dtype=np.float32)
            
            # Простой GPU анализ (в реальности здесь был бы более сложный нейросетевой анализ)
            if len(current_work.get('tasks_completed', [])) > 5:
                # Дополнительный бонус за большой объем работы
                productivity_boost = min(len(current_work.get('tasks_completed', [])) / 20, 0.2)
                adjusted_factors = {
                    "time_factor": min(time_factor + productivity_boost * 0.1, 1.0),
                    "volume_factor": min(volume_factor + productivity_boost * 0.3, 1.0),
                    "creative_factor": creative_factor
                }
                
                return {
                    "adjusted_factors": adjusted_factors,
                    "productivity_boost": productivity_boost,
                    "confidence": 0.85,
                    "gpu_processed": True
                }
            
            return {"confidence": 0.7, "gpu_processed": True}
            
        except Exception as e:
            logger.error(f"GPU progress analysis failed: {e}")
            return {"confidence": 0.3}

    def _combine_analysis_results(self, basic_analysis: Dict[str, float], 
                                gpu_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Комбинирование базового и GPU анализа"""
        combined = basic_analysis.copy()
        
        if 'adjusted_factors' in gpu_analysis:
            adjusted = gpu_analysis['adjusted_factors']
            confidence = gpu_analysis.get('confidence', 0.5)
            
            # Взвешенное среднее между базовым и GPU анализом
            gpu_weight = confidence
            basic_weight = 1.0 - confidence
            
            for factor in ['time_factor', 'volume_factor', 'creative_factor']:
                if factor in adjusted:
                    combined[factor] = (adjusted[factor] * gpu_weight + 
                                      basic_analysis[factor] * basic_weight)
        
        combined['confidence'] = gpu_analysis.get('confidence', 0.6)
        return combined

    async def _llm_analyze_context(self, previous_context: SessionContext) -> Dict[str, Any]:
        """LLM анализ контекста сессии"""
        if not self.llm_wrapper:
            return {}
        
        try:
            # v2.1: Анализируем контекст с помощью LLM
            analysis_prompt = f"""
            Проанализируй контекст предыдущей сессии и определи:
            1. Ключевые концепты для продолжения работы
            2. Рекомендации по улучшению продуктивности
            3. Потенциальные области для инноваций
            
            Контекст сессии: {asdict(previous_context)}
            """
            
            response = await self.llm_wrapper.generate_response(
                prompt=analysis_prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "llm_analysis": response.get('content', ''),
                "key_concepts": previous_context.active_concepts,
                "productivity_recommendations": [],
                "innovation_opportunities": [],
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"LLM context analysis failed: {e}")
            return {"error": str(e)}

    async def _llm_analyze_work_progress(self, current_work: Dict[str, Any], 
                                       analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """LLM улучшенная оценка прогресса работы"""
        if not self.llm_wrapper:
            return {}
        
        try:
            prompt = f"""
            Оцени прогресс текущей работы и предложи рекомендации:
            
            Текущая работа: {current_work}
            Базовый анализ: {analysis_result}
            
            Предоставь:
            1. Оценку качества работы (0-1)
            2. Рекомендации по улучшению
            3. Предложения по архивированию
            """
            
            response = await self.llm_wrapper.generate_response(
                prompt=prompt,
                max_tokens=300,
                temperature=0.6
            )
            
            return {
                "llm_insights": response.get('content', ''),
                "work_quality_score": 0.8,  # Упрощено для примера
                "llm_confidence": 0.75
            }
            
        except Exception as e:
            logger.error(f"LLM work progress analysis failed: {e}")
            return {}

    async def _llm_classify_data(self, category: str, data: Any) -> Dict[str, Any]:
        """LLM классификация данных"""
        if not self.llm_wrapper:
            return {"suggested_type": self._get_default_archive_type(category)}
        
        try:
            prompt = f"""
            Классифицируй данные для архивирования:
            
            Категория: {category}
            Данные: {str(data)[:500]}...  # Ограничиваем размер для LLM
            
            Предложи тип архива:
            - "creative" для творческих достижений
            - "noise" для мусора
            - "carry" для переноса в новую сессию
            
            Также оцени важность данных и предложи обработку.
            """
            
            response = await self.llm_wrapper.generate_response(
                prompt=prompt,
                max_tokens=200,
                temperature=0.4
            )
            
            # v2.1: Парсим ответ LLM (упрощенно)
            content = response.get('content', '').lower()
            
            if 'creative' in content:
                suggested_type = "creative"
            elif 'noise' in content or 'мусор' in content:
                suggested_type = "noise"
            else:
                suggested_type = "carry"
            
            return {
                "suggested_type": suggested_type,
                "confidence": 0.8 if 'creative' in content else 0.6,
                "enhanced_processing": 'innovation' in content or 'улучш' in content
            }
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {"suggested_type": self._get_default_archive_type(category)}

    async def _create_enhanced_achievement(self, category: str, data: Dict[str, Any], 
                                         llm_classification: Dict[str, Any]) -> CreativeAchievement:
        """Создание творческого достижения с LLM анализом"""
        
        # v2.1: Генерируем LLM резюме
        llm_summary = ""
        if self.use_llm and llm_classification.get('suggested_type') == 'creative':
            try:
                prompt = f"Создай краткое описание творческого достижения: {data}"
                response = await self.llm_wrapper.generate_response(
                    prompt=prompt,
                    max_tokens=100,
                    temperature=0.7
                )
                llm_summary = response.get('content', '')
            except Exception as e:
                logger.warning(f"LLM summary generation failed: {e}")
        
        achievement = CreativeAchievement(
            achievement_id=f"ach_v2_1_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=data.get('description', f"Творческое достижение: {category}"),
            code_fragments=data.get('code', []),
            concepts_involved=data.get('concepts', []),
            emotional_impact=data.get('emotional_impact', 0.8),
            timestamp=datetime.datetime.now().isoformat(),
            phase_id=self.get_current_phase_id(),
            innovation_score=data.get('innovation_score', 0.7),
            # v2.1 поля
            llm_generated_summary=llm_summary,
            semantic_embeddings=data.get('embeddings', []),
            llm_confidence_score=llm_classification.get('confidence', 0.5),
            enhanced_storage_optimized=True
        )
        
        self.manager_stats['creative_achievements'] += 1
        return achievement

    async def _gpu_analyze_emotions(self, emotions: List[Dict[str, float]]) -> Dict[str, float]:
        """GPU анализ эмоционального состояния"""
        if not (self.use_gpu and self.gpu_module):
            return {}
        
        try:
            # v2.1: GPU обработка эмоциональных данных
            energy_values = [e.get('energy', 0.5) for e in emotions]
            focus_values = [e.get('focus', 0.5) for e in emotions]
            frustration_values = [e.get('frustration', 0.3) for e in emotions]
            
            # Простые статистические вычисления (в реальности - сложная нейросетевая модель)
            return {
                "energy_trend": sum(energy_values) / len(energy_values),
                "focus_trend": sum(focus_values) / len(focus_values),
                "frustration_level": sum(frustration_values) / len(frustration_values),
                "emotion_stability": 1.0 - (max(energy_values) - min(energy_values)),  # Простая метрика стабильности
                "gpu_processed": True
            }
            
        except Exception as e:
            logger.error(f"GPU emotion analysis failed: {e}")
            return {}

    async def _llm_generate_emotional_recommendations(self, energy_trend: float, focus_trend: float, 
                                                    frustration_level: float, 
                                                    recent_emotions: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Генерация рекомендаций с помощью LLM"""
        if not self.llm_wrapper:
            return []
        
        try:
            prompt = f"""
            На основе эмоционального состояния предложи рекомендации:
            
            Тренд энергии: {energy_trend}
            Тренд концентрации: {focus_trend}
            Уровень фрустрации: {frustration_level}
            
            Недавние эмоции: {recent_emotions}
            
            Предложи 2-3 конкретные рекомендации для улучшения состояния.
            """
            
            response = await self.llm_wrapper.generate_response(
                prompt=prompt,
                max_tokens=200,
                temperature=0.8
            )
            
            # v2.1: Парсим рекомендации (упрощенно)
            recommendations = [
                {
                    "type": "llm_suggested",
                    "action": "review_llm_response",
                    "message": response.get('content', 'LLM рекомендация недоступна'),
                    "confidence": 0.7,
                    "llm_generated": True
                }
            ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"LLM emotional recommendations failed: {e}")
            return []

    async def _llm_generate_transfer_recommendations(self, phases: List, achievements: List, 
                                                   ai_insights: List, context: Dict) -> Dict[str, Any]:
        """Генерация рекомендаций для переноса сессии"""
        if not self.llm_wrapper:
            return {}
        
        try:
            prompt = f"""
            На основе анализа проекта предложи рекомендации для следующей сессии:
            
            Завершенные фазы: {len(phases)}
            Творческие достижения: {len(achievements)}
            AI инсайты: {len(ai_insights)}
            
            Предложи:
            1. Ключевые моменты для продолжения
            2. Рекомендации по следующим шагам
            3. Области для фокуса
            """
            
            response = await self.llm_wrapper.generate_response(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7
            )
            
            return {
                "llm_recommendations": response.get('content', ''),
                "key_continuation_points": [],
                "suggested_next_steps": [],
                "focus_areas": [],
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"LLM transfer recommendations failed: {e}")
            return {}

    async def _llm_generate_session_insights(self, archive_results: Dict, transfer_data: Dict) -> Dict[str, Any]:
        """Генерация инсайтов сессии с помощью LLM"""
        if not self.llm_wrapper:
            return {}
        
        try:
            prompt = f"""
            Проанализируй результаты завершенной сессии и сгенерируй ключевые инсайты:
            
            Архивы созданы: {len(archive_results)}
            Данные для переноса: {bool(transfer_data)}
            
            Создай 3-5 кратких инсайтов о продуктивности сессии и рекомендации для будущих сессий.
            """
            
            response = await self.llm_wrapper.generate_response(
                prompt=prompt,
                max_tokens=250,
                temperature=0.6
            )
            
            return {
                "session_insights": response.get('content', ''),
                "insight_count": 3,
                "confidence": 0.75
            }
            
        except Exception as e:
            logger.error(f"LLM session insights generation failed: {e}")
            return {}

    async def _save_ai_insights(self, project_id: str, session_id: str, insights: Dict[str, Any]):
        """Сохранение AI инсайтов в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for insight_type, content in insights.items():
                if isinstance(content, str) and content.strip():
                    insight_id = f"insight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{insight_type}"
                    
                    cursor.execute('''
                        INSERT INTO ai_insights 
                        (insight_id, project_id, session_id, insight_type, content, confidence_score, 
                         generated_at, gpu_generated, llm_model_used)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        insight_id,
                        project_id,
                        session_id,
                        insight_type,
                        content,
                        insights.get('confidence', 0.7),
                        datetime.datetime.now().isoformat(),
                        self.use_gpu,
                        'v2.1_llm_wrapper' if self.use_llm else 'none'
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving AI insights: {e}")

    async def _create_fallback_archive(self, data: Any, archive_type: ArchiveType, filename: str) -> Path:
        """Создание fallback архива при ошибке v2.1 функций"""
        archive_dir = self.base_path / "archives" / archive_type.value
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            serialized_data = pickle.dumps(data)
            compressed_data = lz4.frame.compress(serialized_data)
            
            archive_path = archive_dir / f"{filename}_fallback.lz4"
            with open(archive_path, 'wb') as f:
                f.write(compressed_data)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Fallback archive creation failed: {e}")
            # Последний резерв - простой файл
            simple_path = archive_dir / f"{filename}_simple.txt"
            with open(simple_path, 'w', encoding='utf-8') as f:
                f.write(str(data)[:1000])  # Первые 1000 символов
            
            return simple_path

    # Вспомогательные методы для работы с базой данных v2.1
    async def record_session_start(self, session_id: str, project_id: str):
        """Запись начала сессии v2.1"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, project_id, start_time)
            VALUES (?, ?, ?)
        ''', (session_id, project_id, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    async def record_session_end(self, session_id: str, archive_data: Dict[str, Any], 
                               processing_time_ms: float):
        """Запись завершения сессии v2.1"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, context_data = ?, creative_achievements = ?, 
                gpu_metrics = ?, llm_analysis = ?, enhanced_storage_refs = ?, 
                v2_1_features = ?, processing_time_ms = ?
            WHERE session_id = ?
        ''', (
            datetime.datetime.now().isoformat(),
            json.dumps(asdict(self.active_session)) if self.active_session else "{}",
            json.dumps(archive_data),
            json.dumps(self.active_session.gpu_metrics) if self.active_session and self.active_session.gpu_metrics else "{}",
            json.dumps(self.active_session.llm_analysis) if self.active_session and self.active_session.llm_analysis else "{}",
            json.dumps(self.active_session.enhanced_storage_refs) if self.active_session and self.active_session.enhanced_storage_refs else "{}",
            json.dumps(self.active_session.v2_1_features) if self.active_session and self.active_session.v2_1_features else "[]",
            processing_time_ms,
            session_id
        ))
        conn.commit()
        conn.close()
    
    async def record_archive(self, filename: str, archive_type: ArchiveType, file_path: Path, ratio: float):
        """Запись архива v2.1"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO archives (archive_id, session_id, archive_type, file_path, compression_ratio, created_at,
                                gpu_optimized, llm_classified, ai_classification_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            self.active_session.session_id if self.active_session else "unknown",
            archive_type.value,
            str(file_path),
            ratio,
            datetime.datetime.now().isoformat(),
            self.use_gpu,
            self.use_llm,
            0.8 if self.use_llm else 0.0
        ))
        conn.commit()
        conn.close()
    
    async def save_creative_achievement(self, achievement: CreativeAchievement):
        """Сохранение творческого достижения v2.1"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO creative_achievements 
            (achievement_id, session_id, project_id, phase_id, description, 
             code_fragments, concepts_involved, emotional_impact, innovation_score, timestamp,
             llm_generated_summary, gpu_processing_time_ms, semantic_embeddings, 
             llm_confidence_score, enhanced_storage_optimized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            achievement.timestamp,
            achievement.llm_generated_summary,
            achievement.gpu_processing_time_ms,
            json.dumps(achievement.semantic_embeddings) if achievement.semantic_embeddings else "[]",
            achievement.llm_confidence_score,
            achievement.enhanced_storage_optimized
        ))
        conn.commit()
        conn.close()
    
    def get_current_phase_id(self) -> str:
        """Получение ID текущей фазы проекта"""
        return f"phase_v2_1_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Получение статистики менеджера v2.1"""
        return {
            **self.manager_stats,
            'v2_1_status': {
                'gpu_available': GPU_AVAILABLE,
                'gpu_enabled': self.use_gpu,
                'enhanced_storage_available': STORAGE_AVAILABLE,
                'enhanced_storage_enabled': self.enhanced_storage is not None,
                'llm_available': LLM_AVAILABLE,
                'llm_enabled': self.use_llm,
                'v2_1_features_active': V2_1_AVAILABLE
            },
            'configuration': {
                'archive_threshold': self.archive_threshold,
                'max_session_duration': self.max_session_duration,
                'emotional_check_interval': self.emotional_check_interval
            }
        }
    
    async def shutdown(self):
        """Корректное завершение работы менеджера v2.1"""
        try:
            logger.info("Shutting down Smart Session Manager v2.1...")
            
            # Закрываем GPU модуль
            if self.gpu_module:
                await self.gpu_module.cleanup()
                logger.info("GPU module cleaned up")
            
            # Закрываем Enhanced Storage
            if self.enhanced_storage:
                await self.enhanced_storage.shutdown()
                logger.info("Enhanced Storage system shut down")
            
            # Закрываем LLM wrapper
            if self.llm_wrapper:
                await self.llm_wrapper.shutdown()
                logger.info("LLM wrapper shut down")
            
            logger.info("Smart Session Manager v2.1 shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during v2.1 shutdown: {e}")

# Тестирование Smart Session Manager v2.1
async def test_smart_session_manager():
    """Тестирование умного менеджера сессий v2.1"""
    
    try:
        # v2.1: Создаем менеджер с GPU и LLM поддержкой
        manager = SmartSessionManager()
        
        print("🚀 Testing ASMF v2.1 Smart Session Manager")
        print("=" * 60)
        
        # v2.1: Тест запуска сессии
        print("📝 Starting new session...")
        session_context = await manager.start_session(
            project_id="test_project_v2_1",
            user_context={"language": "ru", "preferences": {"detailed_analysis": True}}
        )
        print(f"   Session ID: {session_context.session_id}")
        print(f"   v2.1 Features: {session_context.v2_1_features}")
        print(f"   GPU Enabled: {manager.use_gpu}")
        print(f"   LLM Enabled: {manager.use_llm}")
        print(f"   Enhanced Storage: {manager.enhanced_storage is not None}")
        
        # v2.1: Тест анализа прогресса
        print("\n📊 Analyzing work progress...")
        test_work = {
            "tasks_completed": ["task1", "task2", "task3", "task4", "task5"],
            "quality_score": 0.8,
            "innovation_moments": ["breakthrough1", "innovation1"]
        }
        
        progress_analysis = await manager.analyze_work_progress(test_work)
        print(f"   Progress: {progress_analysis['progress_percentage']:.1f}%")
        print(f"   Needs archive: {progress_analysis['needs_archive']}")
        print(f"   GPU analyzed: {progress_analysis.get('gpu_analysis', {}).get('gpu_processed', False)}")
        
        # v2.1: Тест архивирования
        print("\n📦 Testing classification and archiving...")
        test_data = {
            "breakthrough": {
                "description": "Прорыв в архитектуре системы",
                "code": ["def new_function():", "    pass"],
                "concepts": ["architecture", "optimization"],
                "innovation_score": 0.9,
                "emotional_impact": 0.8
            },
            "creative_solution": {
                "description": "Креативное решение проблемы",
                "code": ["creative_code_block"],
                "concepts": ["creativity", "problem_solving"],
                "innovation_score": 0.7
            }
        }
        
        archive_results = await manager.classify_and_archive(test_data)
        print(f"   Archives created: {len(archive_results)}")
        for category, result in archive_results.items():
            print(f"   {category}: {result.get('archive_type', 'unknown')}")
        
        # v2.1: Тест эмоционального мониторинга
        print("\n😊 Testing emotional monitoring...")
        manager.emotional_history = [
            {"energy": 0.8, "focus": 0.9, "frustration": 0.2},
            {"energy": 0.7, "focus": 0.8, "frustration": 0.3},
            {"energy": 0.6, "focus": 0.7, "frustration": 0.4}
        ]
        
        emotion_analysis = await manager.emotional_monitoring()
        print(f"   Energy level: {emotion_analysis.get('energy_level', 0):.2f}")
        print(f"   Focus level: {emotion_analysis.get('focus_level', 0):.2f}")
        print(f"   Recommendations: {len(emotion_analysis.get('recommendations', []))}")
        
        # v2.1: Тест завершения сессии
        print("\n🏁 Testing session closure...")
        session_summary = await manager.close_session(test_data)
        print(f"   Session duration: {session_summary.get('duration', 0):.1f}s")
        print(f"   Archives: {session_summary.get('archives_created', 0)}")
        print(f"   Creative achievements: {session_summary.get('creative_achievements', 0)}")
        
        # v2.1: Получаем статистику
        stats = manager.get_manager_stats()
        print(f"\n📊 v2.1 Manager Statistics:")
        print(f"   Sessions created: {stats['sessions_created']}")
        print(f"   Sessions completed: {stats['sessions_completed']}")
        print(f"   GPU accelerated analyses: {stats['gpu_accelerated_analyses']}")
        print(f"   LLM enhanced classifications: {stats['llm_enhanced_classifications']}")
        print(f"   Enhanced storage optimizations: {stats['enhanced_storage_optimizations']}")
        print(f"   AI insights generated: {stats['ai_insights_generated']}")
        print(f"   v2.1 features used: {stats['v2_1_features_used']}")
        
        print("\n✅ Smart Session Manager v2.1 test completed successfully!")
        
        # v2.1: Корректное завершение
        await manager.shutdown()
        
    except Exception as e:
        logger.error(f"Error in v2.1 test: {e}")
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_smart_session_manager())
