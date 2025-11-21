"""
ASMF v2.1 - Enhanced LLM Wrapper with Error Handling
Универсальный wrapper для любого LLM с оптимизированной памятью

Автор: Serhii Stepanov
Дата: 21 ноября 2025
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# ASMF v2.1 imports with fallback
try:
    from asmf_v2.bigbook_v2 import ASMFV2BigBook
    from asmf_v2.session_manager.smart_session_manager import SmartSessionManager
except ImportError:
    # Fallback for direct import
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from bigbook_v2 import ASMFV2BigBook
    from session_manager.smart_session_manager import SmartSessionManager

# LLM Provider imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)

class ASMFv21LLMWrapper:
    """
    Универсальный wrapper для интеграции ASMF v2.1 с любым LLM
    Поддерживает: OpenAI, Anthropic, Google, Groq, локальные модели
    """
    
    def __init__(self, asmf_config_path: str = "config.yaml", 
                 provider: str = "openai", 
                 api_key: Optional[str] = None,
                 **provider_kwargs):
        """
        Инициализация wrapper'а
        
        Args:
            asmf_config_path: Путь к конфигу ASMF
            provider: 'openai', 'anthropic', 'google', 'groq', 'local'
            api_key: API ключ провайдера
            **provider_kwargs: Дополнительные параметры для провайдера
        """
        
        # Initialize ASMF v2.1 with optimizations
        logger.info("Initializing ASMF v2.1 with optimizations...")
        self.asm_memory = ASMFV2BigBook(asmf_config_path)
        
        # Initialize session manager
        self.session_mgr = SmartSessionManager(self.asm_memory)
        
        # Initialize LLM provider
        self.provider = provider.lower()
        self.client = self._setup_llm_provider(provider, api_key, **provider_kwargs)
        
        logger.info(f"ASMF v2.1 LLM Wrapper initialized with {provider}")
    
    def _setup_llm_provider(self, provider: str, api_key: Optional[str], **kwargs):
        """Настройка LLM клиента"""
        try:
            if provider == "openai":
                if not OPENAI_AVAILABLE:
                    raise ImportError("openai package not installed. Run: pip install openai")
                
                api_key = api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key required")
                
                return openai.OpenAI(api_key=api_key, **kwargs)
            
            elif provider == "anthropic":
                if not ANTHROPIC_AVAILABLE:
                    raise ImportError("anthropic package not installed. Run: pip install anthropic")
                
                api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key required")
                
                return anthropic.Anthropic(api_key=api_key, **kwargs)
            
            elif provider == "google":
                if not GOOGLE_AVAILABLE:
                    raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
                
                api_key = api_key or os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("Google API key required")
                
                genai.configure(api_key=api_key)
                return genai.GenerativeModel(kwargs.get('model', 'gemini-pro'))
            
            elif provider == "groq":
                if not GROQ_AVAILABLE:
                    raise ImportError("groq package not installed. Run: pip install groq")
                
                api_key = api_key or os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError("Groq API key required")
                
                return Groq(api_key=api_key, **kwargs)
            
            elif provider == "local":
                # Placeholder for local model integration
                logger.warning("Local model integration not yet implemented")
                return None
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to setup LLM provider {provider}: {e}")
            raise
    
    async def chat_with_memory(self, user_id: str, message: str, 
                              model: Optional[str] = None,
                              conversation_history: Optional[List[Dict]] = None,
                              **kwargs) -> Dict[str, Any]:
        """
        Чат с ASMF памятью и LLM
        
        Returns:
            Dict с ответом и метаданными
        """
        try:
            # 1. Загружаем или создаём сессию + всю прошлую память
            session = self.session_mgr.get_or_create_session(user_id)
            
            # 2. Добавляем новое сообщение в память ASMF
            self.asm_memory.add_interaction(user_id, "user", message)
            
            # 3. Получаем релевантные воспоминания с оптимизированным поиском
            if hasattr(self.asm_memory, 'semantic_search_optimized'):
                # v2.1 optimized search
                context_memories = self.asm_memory.semantic_search_optimized(user_id, message, top_k=12)
            else:
                # v2.0 fallback
                context_memories = self.asm_memory.semantic_memory.semantic_search(user_id, message, top_k=12)
            
            # 4. Форматируем контекст памяти
            memory_text = self._format_memory_context(context_memories)
            
            # 5. Формируем системный промпт
            system_prompt = self._create_system_prompt(memory_text, user_id)
            
            # 6. Отправляем в LLM
            response_text = await self._call_llm(provider=self.provider, 
                                                model=model or self._get_default_model(),
                                                system_prompt=system_prompt,
                                                user_message=message,
                                                conversation_history=conversation_history or [],
                                                **kwargs)
            
            # 7. Сохраняем ответ LLM в память
            self.asm_memory.add_interaction(user_id, "assistant", response_text)
            
            # 8. Возвращаем результат с метаданными
            result = {
                'response': response_text,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider,
                'memory_context_used': len(context_memories),
                'session_id': session.get('session_id', 'unknown'),
                'asmf_version': '2.1'
            }
            
            logger.info(f"Chat completed for user {user_id} with {len(context_memories)} memory contexts")
            return result
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory: {e}")
            return {
                'response': "Извините, произошла ошибка при обработке вашего сообщения.",
                'error': str(e),
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _format_memory_context(self, memories: List[Dict]) -> str:
        """Форматирование контекста памяти для промпта"""
        if not memories:
            return "Пользователь новый, контекст памяти отсутствует."
        
        formatted_memories = []
        for memory in memories[:12]:  # Топ-12 воспоминаний
            timestamp = memory.get('created_at', memory.get('timestamp', ''))
            content = memory.get('content', '')
            role = memory.get('role', 'unknown')
            emotion = memory.get('emotion', 0.0)
            
            formatted_memories.append(
                f"[{timestamp}] {role}: {content} (эмоциональность: {emotion:.2f})"
            )
        
        return "\n".join(formatted_memories)
    
    def _create_system_prompt(self, memory_context: str, user_id: str) -> str:
        """Создание системного промпта для LLM"""
        return f"""Ты — умный ИИ-ассистент с идеальной долгосрочной памятью и эмоциональным интеллектом.

Контекст памяти о пользователе:
{memory_context}

Инструкции:
1. Используй контекст памяти для персонализированного общения
2. Учитывай эмоциональное состояние пользователя
3. Помни детали предыдущих разговоров
4. Будь дружелюбным, понимающим и полезным
5. Если пользователь грустит — поддержи, если радуется — радуйся вместе
6. Не повторяйся и не забывай важную информацию

Веди себя как старый друг, который помнит все важные моменты."""

    async def _call_llm(self, provider: str, model: str, system_prompt: str, 
                       user_message: str, conversation_history: List[Dict], **kwargs):
        """Вызов соответствующего LLM API"""
        
        if provider == "openai":
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.9),
                max_tokens=kwargs.get('max_tokens', 1024)
            )
            return response.choices[0].message.content
        
        elif provider == "anthropic":
            # Convert messages for Claude
            messages = []
            for msg in conversation_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            response = self.client.messages.create(
                model=model,
                system=system_prompt,
                messages=messages + [{"role": "user", "content": user_message}],
                temperature=kwargs.get('temperature', 0.9),
                max_tokens=kwargs.get('max_tokens', 1024)
            )
            return response.content[0].text
        
        elif provider == "google":
            chat = self.client.start_chat(history=[])
            
            full_prompt = f"{system_prompt}\n\nUser: {user_message}"
            
            response = self.client.generate_content(full_prompt)
            return response.text
        
        elif provider == "groq":
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in conversation_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.9),
                max_tokens=kwargs.get('max_tokens', 1024)
            )
            return response.choices[0].message.content
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _get_default_model(self) -> str:
        """Получение модели по умолчанию для провайдера"""
        defaults = {
            'openai': 'gpt-4o-mini',
            'anthropic': 'claude-3-sonnet-20240229',
            'google': 'gemini-pro',
            'groq': 'mixtral-8x7b-32768',
            'local': 'local-model'
        }
        return defaults.get(self.provider, 'gpt-4o-mini')
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Получение статистики памяти ASMF"""
        try:
            # Get ASMF system stats
            asmf_stats = self.asm_memory.get_stats()
            
            # Get database stats if available
            db_stats = {}
            if hasattr(self.asm_memory, 'db_manager'):
                db_stats = self.asm_memory.db_manager.get_database_stats()
            
            return {
                'asmf_version': '2.1',
                'llm_provider': self.provider,
                'asmf_stats': asmf_stats,
                'database_stats': db_stats,
                'optimization_enabled': {
                    'gpu_acceleration': hasattr(self.asm_memory, 'gpu_processor'),
                    'optimized_db': hasattr(self.asm_memory, 'db_manager'),
                    'semantic_search': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {'error': str(e)}

# Convenience functions for easy use
def create_llm_wrapper(provider: str = "openai", **kwargs) -> ASMFv21LLMWrapper:
    """Фабричная функция для создания wrapper'а"""
    return ASMFv21LLMWrapper(provider=provider, **kwargs)

async def quick_chat(user_id: str, message: str, provider: str = "openai", **kwargs) -> str:
    """Быстрый чат без настройки"""
    wrapper = create_llm_wrapper(provider=provider, **kwargs)
    result = await wrapper.chat_with_memory(user_id, message)
    return result['response']

# Example usage
if __name__ == "__main__":
    async def demo():
        print("🚀 ASMF v2.1 LLM Wrapper Demo")
        print("=" * 50)
        
        # Initialize with different providers
        providers = ["openai"]  # Add more providers as needed
        
        for provider in providers:
            try:
                print(f"\n🤖 Testing with {provider.upper()}")
                
                # Create wrapper
                wrapper = ASMFv21LLMWrapper(provider=provider)
                
                # Chat example
                result = await wrapper.chat_with_memory(
                    user_id="demo_user_123",
                    message="Привет! Помнишь, что мы говорили про ASMF v2.1?",
                    model="gpt-4o-mini"
                )
                
                print(f"Response: {result['response']}")
                print(f"Memory contexts used: {result['memory_context_used']}")
                
                # Memory stats
                stats = wrapper.get_memory_stats()
                print(f"ASMF version: {stats['asmf_version']}")
                print(f"GPU enabled: {stats['optimization_enabled']['gpu_acceleration']}")
                
            except Exception as e:
                print(f"❌ Error with {provider}: {e}")
        
        print("\n✅ Demo completed!")
    
    # Run demo
    asyncio.run(demo())
