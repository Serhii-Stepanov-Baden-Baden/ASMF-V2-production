"""
ASMF v2.0 - Интегратор Мега-Проектов
Управление долгосрочными проектами с множественными сессиями и финальной сборкой
"""

import asyncio
import json
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import pickle

from ..session_manager.smart_session_manager import SmartSessionManager, ProjectStatus
from ..emotional_support.emotional_companion import EmotionalCompanion, EmotionalMetrics


class ProjectPhase(Enum):
    """Фазы большого проекта (пример: разработка автомобиля)"""
    PLANNING = "planning"
    RESEARCH = "research"
    DESIGN = "design"
    PROTOTYPE = "prototype"
    DEVELOPMENT = "development"
    TESTING = "testing"
    OPTIMIZATION = "optimization"
    FINAL_ASSEMBLY = "final_assembly"
    VALIDATION = "validation"
    COMPLETION = "completion"


@dataclass
class ProjectComponent:
    """Компонент большого проекта"""
    component_id: str
    component_name: str
    component_type: str  # "motor", "transmission", "aerodynamics"
    phase_required: ProjectPhase
    sessions_needed: int
    completion_criteria: List[str]
    dependencies: List[str]
    current_status: str
    success_metrics: Dict[str, float]
    creative_achievements: List[Dict[str, Any]]


@dataclass
class MegaProject:
    """Описание мега-проекта"""
    project_id: str
    project_name: str
    description: str
    components: List[ProjectComponent]
    current_phase: ProjectPhase
    total_sessions: int
    completed_sessions: int
    start_date: str
    estimated_completion: str
    creative_moments: List[Dict[str, Any]]
    final_assembly_ready: bool
    memory_archive: Dict[str, Any]


@dataclass
class FinalAssemblySession:
    """Сессия финальной сборки"""
    session_id: str
    components_to_assemble: List[ProjectComponent]
    assembly_order: List[str]
    validation_criteria: List[str]
    quality_thresholds: Dict[str, float]
    success_indicators: List[str]


class MegaProjectIntegrator:
    """Интегратор мега-проектов для координации сложных разработок"""
    
    def __init__(self, base_path: str = "/workspace/ASMF-v2-production/mega_projects"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Инициализация компонентов
        self.session_manager = SmartSessionManager(str(self.base_path / "sessions"))
        self.emotional_companion = EmotionalCompanion()
        
        # Активные проекты
        self.active_projects: Dict[str, MegaProject] = {}
        self.project_progress = {}
        self.assembly_queue = []
        
        # Конфигурация
        self.auto_archive_threshold = 0.90
        self.emotional_monitoring_interval = 300  # 5 минут
        self.component_completion_check = 10  # каждые 10 сессий
        
    async def create_mega_project(self, project_config: Dict[str, Any]) -> str:
        """Создание нового мега-проекта"""
        
        project_id = f"mega_project_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создание компонентов проекта (пример: автомобиль)
        components = []
        for comp_config in project_config.get("components", []):
            component = ProjectComponent(
                component_id=comp_config["id"],
                component_name=comp_config["name"],
                component_type=comp_config["type"],
                phase_required=ProjectPhase(comp_config["phase"]),
                sessions_needed=comp_config.get("sessions_needed", 20),
                completion_criteria=comp_config.get("criteria", []),
                dependencies=comp_config.get("dependencies", []),
                current_status="planned",
                success_metrics=comp_config.get("metrics", {}),
                creative_achievements=[]
            )
            components.append(component)
        
        # Создание мега-проекта
        mega_project = MegaProject(
            project_id=project_id,
            project_name=project_config["name"],
            description=project_config["description"],
            components=components,
            current_phase=ProjectPhase.PLANNING,
            total_sessions=sum(c.sessions_needed for c in components),
            completed_sessions=0,
            start_date=datetime.datetime.now().isoformat(),
            estimated_completion=self._calculate_estimated_completion(components),
            creative_moments=[],
            final_assembly_ready=False,
            memory_archive={}
        )
        
        self.active_projects[project_id] = mega_project
        
        # Сохранение конфигурации
        await self._save_project_config(project_id, mega_project)
        
        return project_id
    
    async def start_project_session(self, project_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Запуск сессии мега-проекта"""
        
        if project_id not in self.active_projects:
            return {"error": "Проект не найден"}
        
        project = self.active_projects[project_id]
        
        # Определение текущего компонента для работы
        current_component = await self._get_current_component(project)
        if not current_component:
            return {"error": "Нет доступных компонентов для работы"}
        
        # Запуск сессии через session_manager
        session_context = await self.session_manager.start_session(project_id, user_context)
        
        # Обновление прогресса проекта
        self.project_progress[project_id] = {
            "current_component": current_component.component_id,
            "phase": project.current_phase.value,
            "sessions_completed": project.completed_sessions,
            "component_progress": {},
            "emotional_status": {},
            "creative_breakthroughs": []
        }
        
        # Мониторинг эмоционального состояния
        await self._start_emotional_monitoring(project_id)
        
        return {
            "session_started": True,
            "session_id": session_context.session_id,
            "project_id": project_id,
            "current_component": current_component.component_name,
            "phase": project.current_phase.value,
            "progress_percentage": (project.completed_sessions / project.total_sessions) * 100,
            "welcome_message": f"Добро пожаловать в разработку {project.project_name}! Сегодня работаем над: {current_component.component_name}"
        }
    
    async def process_work_session(self, project_id: str, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка рабочей сессии"""
        
        if project_id not in self.active_projects:
            return {"error": "Проект не найден"}
        
        project = self.active_projects[project_id]
        current_progress = self.project_progress.get(project_id, {})
        
        # Анализ работы
        work_analysis = await self._analyze_work_progress(project_id, work_data)
        
        # Обновление компонента
        component_update = await self._update_component_progress(project_id, work_data)
        
        # Мониторинг эмоций
        emotional_analysis = await self._monitor_work_emotions(project_id, work_data)
        
        # Проверка готовности к архивированию
        archive_analysis = await self.session_manager.analyze_work_progress(work_data)
        
        # Создание творческих достижений
        creative_achievements = await self._extract_creative_achievements(work_data)
        
        # Формирование ответа
        response = {
            "work_accepted": True,
            "progress_update": component_update,
            "emotional_support": emotional_analysis,
            "creative_recognition": creative_achievements,
            "archive_decision": archive_analysis,
            "next_steps": await self._suggest_next_steps(project_id)
        }
        
        return response
    
    async def conclude_session_with_archive(self, project_id: str, final_work: Dict[str, Any]) -> Dict[str, Any]:
        """Завершение сессии с архивированием"""
        
        # Классификация и архивирование
        archive_results = await self.session_manager.classify_and_archive(final_work)
        
        # Обновление прогресса проекта
        project = self.active_projects[project_id]
        project.completed_sessions += 1
        
        # Завершение сессии
        session_summary = await self.session_manager.close_session(final_work)
        
        # Проверка завершения компонента
        component_completion = await self._check_component_completion(project_id)
        
        # Проверка готовности к следующей фазе
        phase_readiness = await self._assess_phase_readiness(project_id)
        
        return {
            "session_concluded": True,
            "archive_results": archive_results,
            "session_summary": session_summary,
            "component_update": component_completion,
            "phase_readiness": phase_readiness,
            "project_progress": (project.completed_sessions / project.total_sessions) * 100
        }
    
    async def initiate_final_assembly(self, project_id: str) -> Dict[str, Any]:
        """Инициация финальной сборки проекта"""
        
        project = self.active_projects[project_id]
        
        # Проверка готовности всех компонентов
        ready_components = [c for c in project.components if c.current_status == "completed"]
        
        if len(ready_components) < len(project.components) * 0.8:  # 80% готовности
            missing = [c.component_name for c in project.components if c.current_status != "completed"]
            return {
                "assembly_ready": False,
                "missing_components": missing,
                "readiness_percentage": (len(ready_components) / len(project.components)) * 100
            }
        
        # Создание сессии финальной сборки
        assembly_session = FinalAssemblySession(
            session_id=f"final_assembly_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            components_to_assemble=ready_components,
            assembly_order=await self._optimize_assembly_order(ready_components),
            validation_criteria=self._get_assembly_criteria(ready_components),
            quality_thresholds=self._get_quality_thresholds(project),
            success_indicators=self._get_success_indicators(project)
        )
        
        # Подготовка памяти финальной сборки
        assembly_memory = await self._prepare_assembly_memory(project_id, ready_components)
        
        # Запуск специальной сессии сборки
        assembly_context = await self.session_manager.start_session(
            f"{project_id}_assembly", 
            {
                "type": "final_assembly",
                "components": [asdict(c) for c in ready_components],
                "assembly_session": asdict(assembly_session),
                "memory": assembly_memory
            }
        )
        
        return {
            "assembly_session_started": True,
            "assembly_session_id": assembly_context.session_id,
            "components_ready": len(ready_components),
            "total_components": len(project.components),
            "assembly_memory_prepared": True,
            "assembly_instructions": await self._generate_assembly_instructions(ready_components)
        }
    
    async def finalize_project(self, project_id: str, assembly_results: Dict[str, Any]) -> Dict[str, Any]:
        """Финализация проекта после сборки"""
        
        project = self.active_projects[project_id]
        
        # Обновление статуса проекта
        project.final_assembly_ready = True
        project.current_phase = ProjectPhase.COMPLETION
        
        # Создание итогового отчета
        final_report = await self._generate_final_report(project, assembly_results)
        
        # Сохранение в архив творчества
        creative_archive_path = await self._save_to_creative_archive(project, final_report)
        
        # Создание документации проекта
        documentation_path = await self._create_project_documentation(project, final_report)
        
        # Уведомление о завершении
        completion_message = await self.emotional_companion.adaptive_encouragement({
            "completion_rate": 1.0,
            "quality_score": assembly_results.get("quality_score", 0.9),
            "innovation_score": len(project.creative_moments) / max(1, len(project.components))
        })
        
        return {
            "project_completed": True,
            "completion_message": completion_message,
            "final_report": final_report,
            "creative_archive": str(creative_archive_path),
            "documentation": str(documentation_path),
            "total_development_time": (datetime.datetime.now() - datetime.datetime.fromisoformat(project.start_date)).days,
            "achievements": {
                "components_completed": len(project.components),
                "sessions_completed": project.completed_sessions,
                "creative_breakthroughs": len(project.creative_moments),
                "final_quality": assembly_results.get("quality_score", 0.9)
            }
        }
    
    # Вспомогательные методы
    
    def _calculate_estimated_completion(self, components: List[ProjectComponent]) -> str:
        """Расчет примерного времени завершения"""
        total_sessions = sum(c.sessions_needed for c in components)
        estimated_days = total_sessions / 5  # 5 сессий в день максимум
        completion_date = datetime.datetime.now() + datetime.timedelta(days=estimated_days)
        return completion_date.isoformat()
    
    async def _get_current_component(self, project: MegaProject) -> Optional[ProjectComponent]:
        """Получение текущего компонента для работы"""
        for component in project.components:
            if component.current_status in ["planned", "in_progress"]:
                return component
        return None
    
    async def _analyze_work_progress(self, project_id: str, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ прогресса работы"""
        progress = self.project_progress.get(project_id, {})
        
        # Подсчет выполненных задач
        tasks_completed = work_data.get("tasks_completed", [])
        code_written = work_data.get("lines_of_code", 0)
        problems_solved = work_data.get("problems_solved", [])
        
        return {
            "tasks_completed": len(tasks_completed),
            "code_written": code_written,
            "problems_solved": len(problems_solved),
            "progress_score": min(1.0, (len(tasks_completed) + code_written/100 + len(problems_solved)) / 10)
        }
    
    async def _update_component_progress(self, project_id: str, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление прогресса компонента"""
        project = self.active_projects[project_id]
        current_component = await self._get_current_component(project)
        
        if not current_component:
            return {"status": "no_active_component"}
        
        # Обновление статуса (простая логика)
        if current_component.current_status == "planned":
            current_component.current_status = "in_progress"
        elif work_data.get("completion_percentage", 0) > 0.8:
            current_component.current_status = "completed"
        
        return {
            "component": current_component.component_name,
            "status": current_component.current_status,
            "progress": work_data.get("completion_percentage", 0)
        }
    
    async def _monitor_work_emotions(self, project_id: str, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Мониторинг эмоций во время работы"""
        user_text = work_data.get("user_input", "")
        work_context = {
            "work_duration_minutes": work_data.get("session_duration", 30),
            "error_count": work_data.get("errors_encountered", 0),
            "completion_percentage": work_data.get("completion_percentage", 0)
        }
        
        emotional_metrics = await self.emotional_companion.analyze_emotional_state(user_text, work_context)
        support_response = await self.emotional_companion.generate_support_response(emotional_metrics, work_context)
        
        return {
            "emotional_state": support_response.emotional_state.value,
            "energy_level": emotional_metrics.energy_level,
            "focus_level": emotional_metrics.focus_level,
            "support_message": support_response.message,
            "suggested_activities": support_response.suggested_activities,
            "urgency": support_response.urgency_level
        }
    
    async def _extract_creative_achievements(self, work_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлечение творческих достижений"""
        achievements = []
        
        if work_data.get("breakthrough_moment"):
            achievement = {
                "type": "breakthrough",
                "description": work_data["breakthrough_moment"],
                "impact_score": work_data.get("innovation_score", 0.7),
                "code_highlights": work_data.get("innovative_code", []),
                "recognition": "🌟 Поздравляем с прорывом!"
            }
            achievements.append(achievement)
        
        if work_data.get("problem_solved"):
            achievement = {
                "type": "problem_solved",
                "description": f"Решена сложная проблема: {work_data['problem_solved']}",
                "impact_score": 0.8,
                "recognition": "🔧 Мастерская проблем решена!"
            }
            achievements.append(achievement)
        
        return achievements
    
    async def _suggest_next_steps(self, project_id: str) -> List[str]:
        """Предложение следующих шагов"""
        project = self.active_projects[project_id]
        current_component = await self._get_current_component(project)
        
        if not current_component:
            return ["Все компоненты завершены!", "Время финальной сборки!"]
        
        suggestions = [
            f"Продолжаем работу над {current_component.component_name}",
            "Анализируем текущий прогресс",
            "Оптимизируем код",
            "Документируем достижения"
        ]
        
        return suggestions
    
    async def _check_component_completion(self, project_id: str) -> Dict[str, Any]:
        """Проверка завершения компонента"""
        project = self.active_projects[project_id]
        current_component = await self._get_current_component(project)
        
        if not current_component:
            return {"status": "no_components_remaining"}
        
        # Простая логика завершения
        project.completed_sessions += 1
        
        return {
            "component_completed": current_component.current_status == "completed",
            "total_sessions": project.completed_sessions,
            "progress_percentage": (project.completed_sessions / project.total_sessions) * 100
        }
    
    async def _assess_phase_readiness(self, project_id: str) -> Dict[str, Any]:
        """Оценка готовности к следующей фазе"""
        project = self.active_projects[project_id]
        
        completed_components = [c for c in project.components if c.current_status == "completed"]
        total_components = len(project.components)
        completion_rate = len(completed_components) / total_components
        
        phase_transitions = {
            ProjectPhase.PLANNING: 0.1,
            ProjectPhase.RESEARCH: 0.3,
            ProjectPhase.DESIGN: 0.5,
            ProjectPhase.DEVELOPMENT: 0.7,
            ProjectPhase.TESTING: 0.85,
            ProjectPhase.FINAL_ASSEMBLY: 0.9
        }
        
        next_phase_threshold = phase_transitions.get(project.current_phase, 0.9)
        ready_for_next = completion_rate >= next_phase_threshold
        
        return {
            "ready_for_next_phase": ready_for_next,
            "completion_rate": completion_rate,
            "threshold_met": completion_rate >= next_phase_threshold,
            "next_phase_suggestion": self._get_next_phase_suggestion(project.current_phase) if ready_for_next else None
        }
    
    def _get_next_phase_suggestion(self, current_phase: ProjectPhase) -> str:
        """Предложение следующей фазы"""
        phase_mapping = {
            ProjectPhase.PLANNING: "Переходим к исследованию и анализу требований",
            ProjectPhase.RESEARCH: "Начинаем проектирование архитектуры",
            ProjectPhase.DESIGN: "Приступаем к разработке прототипа",
            ProjectPhase.DEVELOPMENT: "Переходим к тестированию",
            ProjectPhase.TESTING: "Оптимизация и доработка",
            ProjectPhase.OPTIMIZATION: "Финальная сборка проекта",
            ProjectPhase.FINAL_ASSEMBLY: "Проект готов!"
        }
        return phase_mapping.get(current_phase, "Продолжаем работу")
    
    async def _optimize_assembly_order(self, components: List[ProjectComponent]) -> List[str]:
        """Оптимизация порядка сборки компонентов"""
        # Простая топологическая сортировка на основе зависимостей
        order = []
        remaining = {c.component_id: c for c in components}
        
        while remaining:
            # Находим компоненты без зависимостей
            ready = [c for c in remaining.values() if not any(dep in remaining for dep in c.dependencies)]
            
            if not ready:
                # Циклическая зависимость, берем любой
                ready = [list(remaining.values())[0]]
            
            # Сортируем по типу компонента
            ready.sort(key=lambda x: (
                0 if x.component_type == "core" else
                1 if x.component_type == "motor" else
                2 if x.component_type == "transmission" else
                3
            ))
            
            next_component = ready[0]
            order.append(next_component.component_id)
            del remaining[next_component.component_id]
        
        return order
    
    def _get_assembly_criteria(self, components: List[ProjectComponent]) -> List[str]:
        """Критерии сборки для компонентов"""
        criteria = ["Все компоненты должны быть совместимы"]
        
        for component in components:
            criteria.append(f"{component.component_name} должен пройти тестирование")
        
        return criteria
    
    def _get_quality_thresholds(self, project: MegaProject) -> Dict[str, float]:
        """Пороговые значения качества"""
        return {
            "overall_quality": 0.9,
            "component_integration": 0.85,
            "performance_score": 0.8,
            "reliability_score": 0.9
        }
    
    def _get_success_indicators(self, project: MegaProject) -> List[str]:
        """Индикаторы успеха проекта"""
        return [
            "Все компоненты успешно интегрированы",
            "Проект проходит все тесты",
            "Качество кода соответствует стандартам",
            "Пользовательские требования выполнены",
            "Проект готов к эксплуатации"
        ]
    
    async def _prepare_assembly_memory(self, project_id: str, components: List[ProjectComponent]) -> Dict[str, Any]:
        """Подготовка памяти для финальной сборки"""
        project = self.active_projects[project_id]
        
        memory = {
            "project_overview": {
                "name": project.project_name,
                "description": project.description,
                "total_components": len(project.components),
                "development_time_days": (datetime.datetime.now() - datetime.datetime.fromisoformat(project.start_date)).days
            },
            "component_details": [
                {
                    "name": c.component_name,
                    "type": c.component_type,
                    "status": c.current_status,
                    "achievements": c.creative_achievements
                }
                for c in components
            ],
            "creative_journey": project.creative_moments,
            "lessons_learned": project.memory_archive.get("lessons", []),
            "optimization_suggestions": project.memory_archive.get("optimizations", [])
        }
        
        return memory
    
    async def _generate_assembly_instructions(self, components: List[ProjectComponent]) -> List[str]:
        """Генерация инструкций по сборке"""
        instructions = [
            "🔧 Подготавливаем рабочее место для финальной сборки",
            "📋 Проверяем наличие всех компонентов",
            "🔍 Проводим финальную проверку совместимости"
        ]
        
        for i, component in enumerate(components, 1):
            instructions.append(f"⚙️  {i}. Интегрируем {component.component_name}")
            if component.creative_achievements:
                instructions.append(f"   🌟 Учитываем достижения: {len(component.creative_achievements)} прорывов")
        
        instructions.extend([
            "🧪 Проводим комплексное тестирование",
            "📊 Оцениваем итоговое качество",
            "🎉 Проект готов к эксплуатации!"
        ])
        
        return instructions
    
    async def _generate_final_report(self, project: MegaProject, assembly_results: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация финального отчета"""
        return {
            "project_summary": {
                "name": project.project_name,
                "description": project.description,
                "development_time": (datetime.datetime.now() - datetime.datetime.fromisoformat(project.start_date)).days,
                "total_sessions": project.completed_sessions,
                "components_completed": len([c for c in project.components if c.current_status == "completed"])
            },
            "achievements": {
                "components_delivered": len(project.components),
                "creative_breakthroughs": len(project.creative_moments),
                "quality_score": assembly_results.get("quality_score", 0.9),
                "innovation_level": len(project.creative_moments) / max(1, len(project.components))
            },
            "creative_archive": project.creative_moments,
            "final_assessment": "Проект успешно завершен с высоким качеством и инновационными решениями!"
        }
    
    async def _save_to_creative_archive(self, project: MegaProject, final_report: Dict[str, Any]) -> Path:
        """Сохранение в архив творчества"""
        archive_path = self.base_path / "creative_archive" / f"{project.project_id}_final_report.json"
        archive_path.parent.mkdir(exist_ok=True)
        
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump({
                "project": asdict(project),
                "final_report": final_report,
                "creative_journey": project.creative_moments,
                "completion_timestamp": datetime.datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return archive_path
    
    async def _create_project_documentation(self, project: MegaProject, final_report: Dict[str, Any]) -> Path:
        """Создание документации проекта"""
        doc_path = self.base_path / "documentation" / f"{project.project_id}_documentation.md"
        doc_path.parent.mkdir(exist_ok=True)
        
        documentation = f"""# {project.project_name} - Итоговая Документация

## Обзор Проекта
{project.description}

## Хронология Разработки
- **Дата начала:** {project.start_date}
- **Общее время разработки:** {(datetime.datetime.now() - datetime.datetime.fromisoformat(project.start_date)).days} дней
- **Всего сессий:** {project.completed_sessions}

## Компоненты Проекта
"""
        
        for component in project.components:
            documentation += f"\n### {component.component_name}\n"
            documentation += f"- Статус: {component.current_status}\n"
            documentation += f"- Фаза: {component.phase_required.value}\n"
            documentation += f"- Завершено сессий: {component.sessions_needed}\n"
        
        documentation += f"""
## Творческие Достижения
Всего инновационных решений: {len(project.creative_moments)}

"""
        
        for moment in project.creative_moments:
            documentation += f"- {moment.get('description', 'Творческое достижение')}\n"
        
        documentation += f"""
## Итоговая Оценка
{final_report['final_assessment']}

## Финальный Отчет
{final_report['project_summary']}

---
*Документация создана автоматически системой ASMF v2.0*
"""
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        return doc_path
    
    async def _save_project_config(self, project_id: str, project: MegaProject):
        """Сохранение конфигурации проекта"""
        config_path = self.base_path / "configs" / f"{project_id}_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(project), f, ensure_ascii=False, indent=2)
    
    async def _start_emotional_monitoring(self, project_id: str):
        """Запуск эмоционального мониторинга проекта"""
        # Запуск фоновой задачи мониторинга
        asyncio.create_task(self._monitor_emotions_continuously(project_id))
    
    async def _monitor_emotions_continuously(self, project_id: str):
        """Непрерывный мониторинг эмоций"""
        while project_id in self.active_projects:
            try:
                # Анализ эмоционального состояния
                summary = await self.emotional_companion.get_emotional_summary(24)
                
                if summary.get("overall_mood") == "needs_attention":
                    # Предоставление поддержки
                    support_response = await self.emotional_companion.emergency_support(0.7)
                    print(f"Эмоциональная поддержка для проекта {project_id}: {support_response.message}")
                
                # Ожидание следующей проверки
                await asyncio.sleep(self.emotional_monitoring_interval)
                
            except Exception as e:
                print(f"Ошибка мониторинга эмоций: {e}")
                break