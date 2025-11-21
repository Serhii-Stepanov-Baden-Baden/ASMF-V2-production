#!/usr/bin/env python3
"""
ASMF v2.1 - Advanced Semantic Memory Framework
Main entry point with GPU acceleration and universal LLM integration

Автор: Serhii Stepanov
Дата: 21 ноября 2025
Версия: v2.1 (Production Grade)
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Core ASMF v2.0 components
from bigbook_v2 import ASMF
from production_memory import ProductionMemory
from production_emotion_engine import ProductionEmotionEngine
from advanced_recovery import AdvancedRecoverySystem
from smart_session_manager import SmartSessionManager
from emotional_companion import EmotionalCompanion
from mega_project_integrator import MegaProjectIntegrator

# New v2.1 components
from database_optimization import OptimizedStorage
from gpu_support import GPUSupport

# Optional: Universal LLM wrapper
try:
    from examples.llm_wrapper_v2_1 import UniversalLLM
    LLM_AVAILABLE = True
except ImportError:
    print("⚠️  LLM wrapper not available - install requirements_v2_1.txt")
    LLM_AVAILABLE = False

# Logging
import logging
from loguru import logger

class ASMFApplication:
    """
    Enhanced ASMF v2.1 with GPU acceleration and universal LLM integration
    
    Features:
    - GPU-accelerated semantic processing
    - FAISS vector search with BLOB storage
    - Universal LLM integration (OpenAI, Anthropic, Groq, xAI)
    - Async processing for production scalability
    """
    
    def __init__(self, gpu_enabled: bool = True, db_path: str = "asmf_v2_1.db"):
        """
        Initialize ASMF v2.1 with all enhancements
        
        Args:
            gpu_enabled: Enable GPU acceleration
            db_path: Path to optimized database
        """
        self.version = "2.1.0"
        self.gpu_enabled = gpu_enabled
        self.db_path = db_path
        self.start_time = datetime.now()
        
        # Initialize logging
        logger.remove()
        logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level:8} | {message}")
        
        # Core v2.0 components
        self.asm_core = ASMF()
        self.memory_engine = ProductionMemory()
        self.emotion_engine = ProductionEmotionEngine()
        self.recovery_system = AdvancedRecoverySystem()
        self.session_manager = SmartSessionManager()
        self.emotional_companion = EmotionalCompanion()
        self.project_integrator = MegaProjectIntegrator()
        
        # New v2.1 components
        self.gpu_support = GPUSupport() if self.gpu_enabled else None
        self.storage = OptimizedStorage(db_path)
        self.llm = None
        
        # Performance metrics
        self.metrics = {
            "memories_processed": 0,
            "gpu_operations": 0,
            "vector_searches": 0,
            "llm_calls": 0,
            "start_time": self.start_time
        }
        
        logger.info(f"🚀 ASMF v{self.version} initialized")
        logger.info(f"   GPU Enabled: {self.gpu_enabled}")
        logger.info(f"   Database: {self.db_path}")
        logger.info(f"   LLM Available: {LLM_AVAILABLE}")
        
    async def initialize(self):
        """Initialize all components asynchronously"""
        try:
            # Initialize database optimization
            await self.storage.initialize()
            logger.info("✅ Database optimization ready")
            
            # Check GPU
            if self.gpu_support and self.gpu_support.is_available():
                gpu_info = self.gpu_support.get_memory_info()
                logger.info(f"✅ GPU acceleration active: {self.gpu_support.device}")
                logger.info(f"   GPU Memory: {gpu_info['used']}/{gpu_info['total']}MB")
            elif self.gpu_enabled:
                logger.warning("⚠️  GPU requested but not available - falling back to CPU")
            
            # Initialize core components
            await self.memory_engine.initialize()
            await self.emotion_engine.initialize()
            await self.recovery_system.initialize()
            await self.session_manager.initialize()
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def process_memory(self, text: str, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2") -> Dict[str, Any]:
        """
        Process semantic memory with GPU acceleration and optimized storage
        
        Args:
            text: Input text to process
            embedding_model: Model for embeddings
            
        Returns:
            Dict with processing results
        """
        start_time = datetime.now()
        
        try:
            # Generate embeddings (GPU-accelerated if available)
            if self.gpu_support and self.gpu_support.is_available():
                embedding = self.gpu_support.bert_embeddings([text], embedding_model)[0]
                self.metrics["gpu_operations"] += 1
                logger.debug("🖥️  Used GPU for embeddings")
            else:
                # Fallback to CPU processing
                embedding = self.memory_engine.generate_embedding(text, embedding_model)
            
            # Store in optimized database (BLOB + FAISS)
            memory_id = await self.storage.store_embedding(
                text=text,
                embedding=embedding,
                metadata={
                    "model": embedding_model,
                    "processed_at": datetime.now().isoformat(),
                    "gpu_used": self.gpu_support and self.gpu_support.is_available()
                }
            )
            
            # Process emotions
            emotion_result = await self.emotion_engine.analyze_emotion(text)
            
            # Update session
            session_id = await self.session_manager.update_session(
                memory_id=memory_id,
                content=text,
                emotion_vector=emotion_result["vector"]
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "memory_id": memory_id,
                "session_id": session_id,
                "embedding": embedding,
                "emotion": emotion_result,
                "processing_time": processing_time,
                "gpu_accelerated": self.gpu_support and self.gpu_support.is_available()
            }
            
            self.metrics["memories_processed"] += 1
            
            logger.info(f"💾 Memory {memory_id} processed in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Memory processing failed: {e}")
            raise
    
    async def search(self, query: str, top_k: int = 10, use_faiss: bool = True) -> List[Dict[str, Any]]:
        """
        Fast semantic search with FAISS optimization
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_faiss: Use FAISS index for speed
            
        Returns:
            List of similar memories with scores
        """
        try:
            # Generate query embedding
            if self.gpu_support and self.gpu_support.is_available():
                query_embedding = self.gpu_support.bert_embeddings([query])[0]
            else:
                query_embedding = self.memory_engine.generate_embedding(query)
            
            # Search using FAISS (fast) or fallback method
            if use_faiss:
                results = await self.storage.similarity_search(
                    query_embedding=query_embedding,
                    top_k=top_k
                )
                self.metrics["vector_searches"] += 1
                logger.debug(f"🔍 FAISS search: {len(results)} results")
            else:
                # Fallback to standard search
                results = await self.storage.fallback_search(
                    query_embedding=query_embedding,
                    top_k=top_k
                )
            
            # Add emotion context
            for result in results:
                if "memory_id" in result:
                    emotion = await self.emotion_engine.analyze_emotion(result["text"])
                    result["emotion"] = emotion
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
    
    async def integrate_llm(self, provider: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Integrate with LLM provider using universal wrapper
        
        Args:
            provider: LLM provider (openai, anthropic, groq, xai)
            model: Model name
            **kwargs: Additional LLM parameters
            
        Returns:
            Dict with LLM configuration
        """
        if not LLM_AVAILABLE:
            raise ImportError("LLM wrapper not available - install requirements_v2_1.txt")
        
        try:
            self.llm = UniversalLLM(provider=provider, model=model, **kwargs)
            
            # Test connection
            test_response = await self.llm.generate(
                prompt="Hello! This is a test of ASMF v2.1 LLM integration.",
                max_tokens=50
            )
            
            result = {
                "provider": provider,
                "model": model,
                "connection_status": "active",
                "test_response": test_response,
                "available_models": self.llm.get_available_models()
            }
            
            self.metrics["llm_calls"] += 1
            
            logger.info(f"🤖 LLM {provider}/{model} integrated successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM integration failed: {e}")
            raise
    
    async def generate_response(self, prompt: str, context_memories: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate LLM response with ASMF context
        
        Args:
            prompt: User prompt
            context_memories: Relevant memories for context
            
        Returns:
            Dict with LLM response and metadata
        """
        if not self.llm:
            raise RuntimeError("LLM not integrated - call integrate_llm() first")
        
        try:
            # Prepare context from memories
            context_text = ""
            if context_memories:
                context_parts = []
                for memory in context_memories[:5]:  # Limit context
                    context_parts.append(f"Memory: {memory.get('text', '')}")
                context_text = "\n".join(context_parts)
            
            # Generate response
            response = await self.llm.generate(
                prompt=f"Context: {context_text}\n\nUser: {prompt}",
                temperature=0.7,
                max_tokens=500
            )
            
            self.metrics["llm_calls"] += 1
            
            result = {
                "prompt": prompt,
                "response": response,
                "context_memories": len(context_memories) if context_memories else 0,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"💬 LLM response generated ({len(response)} chars)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            raise
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        stats = {
            **self.metrics,
            "uptime_seconds": uptime,
            "gpu_available": self.gpu_support and self.gpu_support.is_available(),
            "database_path": self.db_path,
            "version": self.version
        }
        
        if self.gpu_support and self.gpu_support.is_available():
            gpu_info = self.gpu_support.get_memory_info()
            stats["gpu_memory"] = gpu_info
        
        return stats
    
    async def demo_complete_workflow(self):
        """Demonstrate complete ASMF v2.1 workflow"""
        logger.info("🎬 Starting ASMF v2.1 Complete Workflow Demo")
        
        try:
            # 1. Process multiple memories
            logger.info("\n📝 Step 1: Processing semantic memories")
            
            memories = [
                "ASMF v2.1 introduces GPU acceleration for semantic processing",
                "FAISS enables sub-second vector search for large datasets",
                "Universal LLM wrapper supports multiple providers seamlessly",
                "BLOB storage optimizes memory footprint for production use",
                "Async processing enables concurrent operations at scale"
            ]
            
            processed_ids = []
            for i, memory in enumerate(memories, 1):
                result = await self.process_memory(memory)
                processed_ids.append(result["memory_id"])
                logger.info(f"   Memory {i}: {result['memory_id']} (GPU: {result['gpu_accelerated']})")
            
            # 2. Perform semantic search
            logger.info("\n🔍 Step 2: Semantic search with FAISS")
            
            search_queries = [
                "GPU acceleration benefits",
                "vector search optimization",
                "LLM integration capabilities"
            ]
            
            for query in search_queries:
                results = await self.search(query, top_k=3)
                logger.info(f"   Query: '{query}'")
                for result in results[:2]:  # Show top 2
                    logger.info(f"     → {result['text'][:60]}... (score: {result.get('similarity', 0):.3f})")
            
            # 3. Test LLM integration (if available)
            if LLM_AVAILABLE:
                logger.info("\n🤖 Step 3: LLM Integration")
                
                # Try Groq first (often faster)
                try:
                    await self.integrate_llm("groq", "llama3-70b-8192")
                    provider = "Groq"
                except:
                    # Fallback to OpenAI
                    await self.integrate_llm("openai", "gpt-3.5-turbo")
                    provider = "OpenAI"
                
                # Generate contextual response
                context_results = await self.search("ASMF v2.1 features", top_k=3)
                response = await self.generate_response(
                    "What are the main benefits of ASMF v2.1?",
                    context_memories=context_results
                )
                
                logger.info(f"   Provider: {provider}")
                logger.info(f"   Response: {response['response'][:100]}...")
            
            # 4. Performance statistics
            logger.info("\n📊 Step 4: Performance Statistics")
            
            stats = await self.get_performance_stats()
            logger.info(f"   Memories processed: {stats['memories_processed']}")
            logger.info(f"   GPU operations: {stats['gpu_operations']}")
            logger.info(f"   Vector searches: {stats['vector_searches']}")
            logger.info(f"   LLM calls: {stats['llm_calls']}")
            logger.info(f"   Uptime: {stats['uptime_seconds']:.1f}s")
            
            if stats.get('gpu_memory'):
                gpu_mem = stats['gpu_memory']
                logger.info(f"   GPU Memory: {gpu_mem['used']}/{gpu_mem['total']}MB")
            
            logger.info("\n✅ Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self.storage, 'cleanup'):
                await self.storage.cleanup()
            
            if self.gpu_support:
                self.gpu_support.cleanup()
            
            logger.info("🧹 Cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ASMF v2.1 - Advanced Semantic Memory Framework")
    parser.add_argument("--mode", choices=["demo", "interactive", "benchmark"], 
                       default="demo", help="Operation mode")
    parser.add_argument("--gpu-enabled", action="store_true", 
                       help="Enable GPU acceleration")
    parser.add_argument("--no-gpu", action="store_true", 
                       help="Disable GPU acceleration")
    parser.add_argument("--db-path", default="asmf_v2_1.db", 
                       help="Database path")
    parser.add_argument("--llm-provider", default="groq", 
                       help="LLM provider (openai, anthropic, groq)")
    parser.add_argument("--llm-model", default="llama3-70b-8192", 
                       help="LLM model name")
    
    args = parser.parse_args()
    
    # Configure GPU
    gpu_enabled = True
    if args.no_gpu:
        gpu_enabled = False
    elif args.gpu_enabled:
        gpu_enabled = True
    
    # Initialize ASMF
    asmf = ASMFApplication(gpu_enabled=gpu_enabled, db_path=args.db_path)
    
    try:
        await asmf.initialize()
        
        if args.mode == "demo":
            await asmf.demo_complete_workflow()
            
        elif args.mode == "interactive":
            logger.info("🎯 Interactive mode - type 'quit' to exit")
            while True:
                try:
                    user_input = input("\n🔮 Your query: ").strip()
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if user_input:
                        # Search for relevant memories
                        results = await asmf.search(user_input, top_k=5)
                        
                        if results:
                            logger.info(f"Found {len(results)} relevant memories:")
                            for i, result in enumerate(results[:3], 1):
                                logger.info(f"  {i}. {result['text'][:80]}...")
                        else:
                            logger.info("No relevant memories found. Processing new memory...")
                            result = await asmf.process_memory(user_input)
                            logger.info(f"New memory stored: {result['memory_id']}")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"❌ Error: {e}")
        
        elif args.mode == "benchmark":
            logger.info("⚡ Running benchmark...")
            
            # Benchmark processing
            test_text = "ASMF v2.1 performance benchmark text" * 10
            iterations = 100
            
            start_time = datetime.now()
            for i in range(iterations):
                await asmf.process_memory(f"{test_text} {i}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Benchmark search
            start_time = datetime.now()
            for i in range(iterations // 10):
                await asmf.search(f"benchmark query {i}", top_k=10)
            search_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"📊 Benchmark Results:")
            logger.info(f"   Processing: {iterations} memories in {processing_time:.2f}s ({iterations/processing_time:.1f}/sec)")
            logger.info(f"   Search: {iterations//10} queries in {search_time:.2f}s ({(iterations//10)/search_time:.1f}/sec)")
        
        # Show final stats
        stats = await asmf.get_performance_stats()
        logger.info(f"\n🏁 Final Statistics: {stats['memories_processed']} memories processed")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
        
    finally:
        await asmf.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Unhandled error: {e}")
        sys.exit(1)
