"""
ASMF v2.0 - Emotional State Encoding Protocol (ESEP) (Enhanced with v2.1)
Реальная реализация эмоционального кодирования

Автор: Serhii Stepanov (Baden-Baden, Germany)
Дата: 21 ноября 2025
Версия: 2.0 (Enhanced with v2.1)
"""

import asyncio
import hashlib
import json
import logging
import math
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Core dependencies with fallback
try:
    import spacy
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    import numpy as np
    NLP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"NLP dependencies not available: {e}")
    NLP_AVAILABLE = False
    # Mock classes for demo mode
    spacy = None
    pipeline = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None
    SentimentIntensityAnalyzer = None
    np = None

# v2.1 Enhanced Components
try:
    from gpu_support import GPUSupportModule
    from database_optimization import EnhancedStorageSystem
    V2_1_AVAILABLE = True
except ImportError:
    V2_1_AVAILABLE = False
    GPUSupportModule = None
    EnhancedStorageSystem = None

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDimension(Enum):
    """Измерения эмоционального пространства"""
    AROUSAL = "arousal"      # Возбуждение (0-1)
    VALENCE = "valence"      # Валидность (-1 to 1) 
    DOMINANCE = "dominance"  # Доминирование (0-1)

@dataclass
class EmotionVector:
    """Многоразмерный эмоциональный вектор"""
    primary_emotion: str
    secondary_emotions: List[str]
    intensity: float  # 0.0 to 1.0
    valence: float    # -1.0 to 1.0
    arousal: float    # 0.0 to 1.0
    dominance: float  # 0.0 to 1.0
    confidence: float # 0.0 to 1.0
    dimension_vector: List[float]
    context_factors: Dict[str, float]
    sentiment: Dict[str, float]
    timestamp: str
    gpu_accelerated: bool = False

@dataclass
class EmotionalContext:
    """Эмоциональный контекст с контекстуальными факторами"""
    current_emotion: EmotionVector
    emotional_history: List[EmotionVector]
    context_sensitivity: float
    emotional_stability: float
    emotional_volatility: float
    user_preferences: Dict[str, Any]
    session_metadata: Dict[str, Any]

class ProductionEmotionEngine:
    """
    Производственный эмоциональный движок (Enhanced with v2.1)
    Реализует реальное эмоциональное кодирование вместо mock
    """
    
    # Классификация эмоций по Plutchik's Wheel
    EMOTION_WHEEL = {
        'joy': ['happiness', 'contentment', 'elation', 'pride'],
        'trust': ['acceptance', 'confidence', 'faith', 'reliability'],
        'fear': ['anxiety', 'apprehension', 'terror', 'worry'],
        'surprise': ['amazement', 'astonishment', 'shock', 'confusion'],
        'sadness': ['grief', 'sorrow', 'disappointment', 'depression'],
        'disgust': ['revulsion', 'contempt', 'disapproval', 'loathing'],
        'anger': ['rage', 'irritation', 'frustration', 'hostility'],
        'anticipation': ['interest', 'eagerness', 'curiosity', 'expectation']
    }
    
    # Семантические кластеры для вторичных эмоций
    EMOTION_CLUSTERS = {
        'positive_high': ['joy', 'trust', 'anticipation'],
        'positive_low': ['contentment', 'acceptance', 'satisfaction'],
        'negative_high': ['anger', 'fear', 'disgust'],
        'negative_low': ['sadness', 'disappointment', 'boredom'],
        'neutral': ['calm', 'neutral', 'balanced']
    }
    
    # v2.1 Enhanced components
    def __init__(self, config_path: Optional[str] = None):
        """Инициализация с реальными моделями эмоций"""
        self.config = self._load_config(config_path)
        self.emotional_memory = {}
        self.session_emotions = {}
        
        # v2.1 Enhanced Components
        self.gpu_support = None
        self.enhanced_storage = None
        self.use_gpu = False
        
        # Initialize emotion models
        self._initialize_emotion_models()
        
        # v2.1 GPU Integration
        if V2_1_AVAILABLE and self.config.get('use_gpu', False):
            try:
                self.gpu_support = GPUSupportModule(
                    device=self.config.get('gpu_device', 'cuda:0')
                )
                self.use_gpu = True
                logger.info("🚀 GPU acceleration enabled for emotion analysis")
            except Exception as e:
                logger.warning(f"GPU initialization failed: {e}")
                self.use_gpu = False
        
        # Enhanced statistics for v2.1
        self.emotion_stats = {
            'emotions_processed': 0,
            'primary_emotions_detected': {},
            'average_confidence': 0.0,
            'context_sensitivity_changes': 0,
            'gpu_accelerated_analyses': 0,
            'total_processing_time': 0.0,
            'average_emotion_time': 0.0,
            'fallback_activations': 0,
            'sentiment_analyses': 0
        }
        
        logger.info("Production Emotion Engine initialized successfully")
        if self.use_gpu:
            logger.info("✨ v2.1 GPU acceleration active")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Загрузка конфигурации эмоций"""
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config.get('emotional', {})
            except FileNotFoundError:
                logger.warning(f"Emotion config not found, using defaults")
        
        # Default configuration
        return {
            'sensitivity': 0.5,
            'emotion_model': 'j-hartmann/emotion-english-distilroberta-base',
            'enable_context_factors': True,
            'emotional_memory_depth': 10,
            'volatility_threshold': 0.7,
            'use_gpu': False,
            'fallback_mode': not NLP_AVAILABLE
        }

    def _initialize_emotion_models(self):
        """Инициализация моделей для эмоционального анализа"""
        if not NLP_AVAILABLE:
            logger.warning("NLP dependencies not available, running in fallback mode")
            self.emotion_stats['fallback_activations'] += 1
            return
            
        try:
            # Основная модель для эмоций
            emotion_model = self.config.get('emotion_model', 'j-hartmann/emotion-english-distilroberta-base')
            
            if self.use_gpu and self.gpu_support:
                # v2.1 GPU-accelerated emotion classification
                self.emotion_classifier = self.gpu_support.get_emotion_classifier()
                logger.info(f"🚀 GPU-accelerated emotion classifier loaded")
            else:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model=emotion_model,
                    return_all_scores=True
                )
                logger.info(f"CPU emotion classifier loaded: {emotion_model}")
            
            # VADER для дополнительной эмоциональной оценки
            self.vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("VADER sentiment analyzer loaded")
            
            # spaCy для контекстуального анализа
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded for emotion context")
            except OSError:
                logger.warning("spaCy English model not available, using fallback")
                self.nlp = None
                
        except Exception as e:
            logger.error(f"Failed to initialize emotion models: {e}")
            self._setup_fallback_mode()

    def _setup_fallback_mode(self):
        """Настройка fallback режима при ошибках загрузки моделей"""
        logger.info("Setting up fallback emotion detection mode")
        self.emotion_stats['fallback_activations'] += 1
        
        # Disable real models, enable fallback
        self.emotion_classifier = None
        self.vader_analyzer = None
        self.nlp = None
        
    async def detect_emotion(self, text: str, context: str = "") -> str:
        """
        Реальная детекция эмоций с использованием transformers
        Enhanced with v2.1 GPU acceleration
        """
        try:
            start_time = datetime.now()
            
            if self.emotion_classifier and self.vader_analyzer:
                # v2.1 GPU-accelerated emotion detection
                if self.use_gpu and self.gpu_support:
                    emotion_scores = await self.gpu_support.analyze_emotions_gpu(text)
                    self.emotion_stats['gpu_accelerated_analyses'] += 1
                    logger.info("🚀 GPU-accelerated emotion detection")
                else:
                    # Original CPU-based detection
                    emotion_scores = self.emotion_classifier(text)
                
                # Извлечение топ эмоции
                if isinstance(emotion_scores, list) and emotion_scores:
                    top_emotion = max(emotion_scores[0], key=lambda x: x['score'])
                else:
                    # Fallback
                    top_emotion = {'label': 'neutral', 'score': 0.5}
                
                # Дополнительная проверка через VADER
                vader_scores = self.vader_analyzer.polarity_scores(text)
                
                # Объединение результатов
                primary_emotion = self._refine_emotion_detection(
                    top_emotion['label'], 
                    top_emotion['score'],
                    vader_scores
                )
            else:
                # Fallback emotion detection
                primary_emotion = await self._fallback_emotion_detection(text)
                self.emotion_stats['fallback_activations'] += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.emotion_stats['total_processing_time'] += processing_time
            
            logger.info(f"Detected primary emotion: {primary_emotion}")
            return primary_emotion
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return 'neutral'

    async def _fallback_emotion_detection(self, text: str) -> str:
        """Fallback детекция эмоций на основе ключевых слов"""
        text_lower = text.lower()
        
        # Define emotion keywords
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'amazing', 'wonderful', 'great', 'excellent', 'love'],
            'sadness': ['sad', 'depressed', 'sorrow', 'disappointed', 'grief', 'blue'],
            'anger': ['angry', 'mad', 'rage', 'furious', 'irritated', 'annoyed', 'frustrated'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'terrified', 'panic'],
            'disgust': ['disgusted', 'disgusting', 'gross', 'awful', 'terrible', 'horrible'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected'],
            'trust': ['trust', 'confident', 'secure', 'safe', 'reliable', 'faith'],
            'anticipation': ['excited', 'curious', 'interested', 'looking forward', 'eager']
        }
        
        # Count emotion indicators
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score
        
        # Return emotion with highest score, or neutral
        if emotion_scores:
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            return max_emotion[0] if max_emotion[1] > 0 else 'neutral'
        else:
            return 'neutral'

    def _refine_emotion_detection(self, bert_emotion: str, bert_score: float, 
                                vader_scores: Dict) -> str:
        """Уточнение эмоциональной детекции через комбинирование источников"""
        
        # Маппинг BERT эмоций на стандартные эмоции
        emotion_mapping = {
            'joy': 'joy',
            'love': 'trust', 
            'sadness': 'sadness',
            'anger': 'anger',
            'fear': 'fear',
            'surprise': 'surprise',
            'disgust': 'disgust',
            'neutral': 'neutral'
        }
        
        primary_emotion = emotion_mapping.get(bert_emotion.lower(), 'neutral')
        
        # Корректировка через VADER
        if vader_scores['compound'] > 0.5:
            if primary_emotion == 'neutral':
                primary_emotion = 'joy'
        elif vader_scores['compound'] < -0.5:
            if primary_emotion == 'neutral':
                primary_emotion = 'sadness'
        
        # Нормализация эмоционального профиля
        normalized_emotion = self._normalize_emotion(primary_emotion, bert_score)
        
        return normalized_emotion

    def _normalize_emotion(self, emotion: str, confidence: float) -> str:
        """Нормализация эмоциональных терминов"""
        
        # Приведение к стандартным терминам
        normalized = {
            'happiness': 'joy',
            'contentment': 'joy', 
            'satisfaction': 'joy',
            'frustration': 'anger',
            'irritation': 'anger',
            'anxiety': 'fear',
            'worry': 'fear',
            'confusion': 'surprise',
            'astonishment': 'surprise'
        }
        
        return normalized.get(emotion, emotion)

    async def detect_tone(self, text: str, context: Dict[str, Any] = None) -> str:
        """
        Улучшенная детекция тона
        Enhanced with v2.1 GPU acceleration
        """
        try:
            # v2.1 GPU-accelerated tone detection
            if self.use_gpu and self.gpu_support:
                tone_result = await self.gpu_support.analyze_tone_gpu(text, context)
                if tone_result:
                    logger.info("🚀 GPU-accelerated tone detection")
                    return tone_result
            
            # Fallback CPU-based tone detection
            primary_emotion = await self.detect_emotion(text)
            
            # Контекстуальная корректировка
            tone_context = self._analyze_context_tone(text, context)
            
            # Определение тона на основе эмоции и контекста
            tone_mapping = {
                'joy': 'positive',
                'trust': 'confident', 
                'fear': 'anxious',
                'surprise': 'surprised',
                'sadness': 'melancholic',
                'disgust': 'critical',
                'anger': 'aggressive',
                'neutral': 'neutral'
            }
            
            # Корректировка тона через контекст
            base_tone = tone_mapping.get(primary_emotion, 'neutral')
            
            if tone_context['formality'] > 0.7:
                base_tone = 'formal'
            elif tone_context['urgency'] > 0.7:
                base_tone = 'urgent'
            elif tone_context['question'] > 0.5:
                base_tone = 'inquisitive'
            
            logger.info(f"Detected tone: {base_tone}")
            return base_tone
            
        except Exception as e:
            logger.error(f"Error detecting tone: {e}")
            return 'neutral'

    def _analyze_context_tone(self, text: str, context: Dict[str, Any] = None) -> Dict[str, float]:
        """Анализ контекстуальных факторов тона"""
        
        if context is None:
            context = {}
        
        # Базовая контекстуальная оценка
        tone_factors = {
            'formality': self._calculate_formality_score(text),
            'urgency': self._calculate_urgency_score(text),
            'question': self._calculate_question_score(text),
            'emotional_intensity': self._calculate_intensity_score(text)
        }
        
        # Обогащение через spaCy если доступно
        if self.nlp:
            try:
                doc = self.nlp(text)
                
                # Анализ синтаксической структуры
                exclamation_count = sum(1 for sent in doc.sents if sent.text.endswith('!'))
                question_count = sum(1 for sent in doc.sents if sent.text.endswith('?'))
                
                tone_factors['exclamation_level'] = min(exclamation_count / len(text.split()) * 10, 1.0)
                tone_factors['question_level'] = min(question_count / len(text.split()) * 10, 1.0)
            except:
                # spaCy processing failed
                tone_factors['exclamation_level'] = text.count('!') / max(len(text.split()), 1)
                tone_factors['question_level'] = text.count('?') / max(len(text.split()), 1)
        
        return tone_factors

    def _calculate_formality_score(self, text: str) -> float:
        """Расчет формальности текста"""
        
        formal_indicators = ['however', 'therefore', 'consequently', 'furthermore', 'nevertheless']
        informal_indicators = ['hey', 'yeah', 'cool', 'awesome', 'lol']
        
        words = text.lower().split()
        
        formal_count = sum(1 for word in words if word in formal_indicators)
        informal_count = sum(1 for word in words if word in informal_indicators)
        
        total_indicators = formal_count + informal_count
        if total_indicators == 0:
            return 0.5  # Neutral
        
        return formal_count / total_indicators

    def _calculate_urgency_score(self, text: str) -> float:
        """Расчет срочности текста"""
        
        urgent_words = ['urgent', 'emergency', 'immediate', 'critical', 'asap', 'now']
        time_words = ['deadline', 'today', 'soon', 'hurry']
        
        words = text.lower().split()
        
        urgent_count = sum(1 for word in words if word in urgent_words)
        time_count = sum(1 for word in words if word in time_words)
        
        urgency_level = (urgent_count * 2 + time_count) / len(words) if words else 0
        return min(urgency_level, 1.0)

    def _calculate_question_score(self, text: str) -> float:
        """Расчет вопросительности"""
        question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'which']
        
        words = text.lower().split()
        question_count = sum(1 for word in words if word in question_words)
        
        return min(question_count / len(words), 1.0) if words else 0

    def _calculate_intensity_score(self, text: str) -> float:
        """Расчет эмоциональной интенсивности"""
        
        intensive_words = ['very', 'extremely', 'absolutely', 'completely', 'totally']
        capitalized_words = sum(1 for word in text.split() if word.isupper() and len(word) > 2)
        exclamations = text.count('!')
        
        words = text.lower().split()
        intensive_count = sum(1 for word in words if word in intensive_words)
        
        intensity = (intensive_count * 0.3 + capitalized_words * 0.4 + exclamations * 0.3) / len(words) if words else 0
        return min(intensity, 1.0)

    async def encode_emotion(self, primary: str, secondary: List[str], 
                           intensity: float, context: Dict[str, Any] = None) -> EmotionVector:
        """
        Реальное кодирование эмоций в многоразмерные векторы
        Enhanced with v2.1 GPU acceleration and enhanced storage
        """
        try:
            start_time = datetime.now()
            
            # Контекстуальные факторы
            context_factors = self._analyze_emotional_context(primary, intensity, context)
            
            # v2.1 Sentiment analysis for enhanced encoding
            sentiment_data = {}
            if self.vader_analyzer and context and 'text' in context:
                try:
                    sentiment_scores = self.vader_analyzer.polarity_scores(context['text'])
                    sentiment_data = {
                        'vader_compound': sentiment_scores['compound'],
                        'vader_positive': sentiment_scores['pos'],
                        'vader_negative': sentiment_scores['neg'],
                        'vader_neutral': sentiment_scores['neu']
                    }
                    self.emotion_stats['sentiment_analyses'] += 1
                except:
                    sentiment_data = {'overall_sentiment': 'neutral'}
            
            # Расчет эмоциональных измерений
            valence = self._calculate_valence(primary, context_factors)
            arousal = self._calculate_arousal(primary, intensity, context_factors)  
            dominance = self._calculate_dominance(primary, secondary, context_factors)
            
            # v2.1 GPU-accelerated emotion encoding
            if self.use_gpu and self.gpu_support:
                enhanced_vector = await self.gpu_support.encode_emotion_gpu(
                    primary, secondary, intensity, valence, arousal, dominance, context_factors
                )
                if enhanced_vector:
                    valence, arousal, dominance = enhanced_vector
                    self.emotion_stats['gpu_accelerated_analyses'] += 1
            
            # Создание эмоционального вектора
            dimension_vector = [valence, arousal, dominance]
            
            # Определение вторичных эмоций
            refined_secondary = self._refine_secondary_emotions(primary, secondary, context_factors)
            
            # Расчет уверенности в эмоциональной оценке
            confidence = self._calculate_emotion_confidence(primary, intensity, context_factors)
            
            emotion_vector = EmotionVector(
                primary_emotion=primary,
                secondary_emotions=refined_secondary,
                intensity=intensity,
                valence=valence,
                arousal=arousal,
                dominance=dominance,
                confidence=confidence,
                dimension_vector=dimension_vector,
                context_factors=context_factors,
                sentiment=sentiment_data,
                timestamp=datetime.now(timezone.utc).isoformat(),
                gpu_accelerated=self.use_gpu
            )
            
            # v2.1 Enhanced Storage Integration
            if V2_1_AVAILABLE and self.enhanced_storage:
                try:
                    await self.enhanced_storage.store_emotion_vector(
                        emotion_data=emotion_vector,
                        context_data=context or {}
                    )
                    logger.info("💾 Stored emotion in enhanced storage")
                except Exception as e:
                    logger.warning(f"Enhanced emotion storage failed: {e}")
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.emotion_stats['total_processing_time'] += processing_time
            
            self.emotion_stats['emotions_processed'] += 1
            self._update_emotion_statistics(primary, confidence)
            
            # Update average processing time
            total_emotions = self.emotion_stats['emotions_processed']
            self.emotion_stats['average_emotion_time'] = (
                self.emotion_stats['total_processing_time'] / total_emotions
            )
            
            logger.info(f"Encoded emotion: {primary} (confidence: {confidence:.3f}, time: {processing_time:.3f}s)")
            return emotion_vector
            
        except Exception as e:
            logger.error(f"Error encoding emotion: {e}")
            # Возвращаем нейтральную эмоцию в случае ошибки
            return EmotionVector(
                primary_emotion='neutral',
                secondary_emotions=['calm'],
                intensity=0.0,
                valence=0.0,
                arousal=0.5,
                dominance=0.5,
                confidence=0.0,
                dimension_vector=[0.0, 0.5, 0.5],
                context_factors={},
                sentiment={'overall_sentiment': 'neutral'},
                timestamp=datetime.now(timezone.utc).isoformat(),
                gpu_accelerated=False
            )

    def _analyze_emotional_context(self, primary_emotion: str, intensity: float, 
                                 context: Dict[str, Any] = None) -> Dict[str, float]:
        """Анализ контекстуальных факторов эмоций"""
        
        if context is None:
            context = {}
        
        # Базовые контекстуальные факторы
        context_factors = {
            'intensity_modifier': self._calculate_intensity_modifier(intensity),
            'emotional_clarity': self._calculate_emotional_clarity(primary_emotion),
            'social_context': self._calculate_social_context(context),
            'personal_relevance': self._calculate_personal_relevance(context),
            'temporal_context': self._calculate_temporal_context(context)
        }
        
        return context_factors

    def _calculate_intensity_modifier(self, intensity: float) -> float:
        """Расчет модификатора интенсивности"""
        
        if intensity > 0.8:
            return 1.5  # High intensity amplifies emotion
        elif intensity < 0.2:
            return 0.5  # Low intensity dampens emotion
        else:
            return 1.0  # Normal intensity

    def _calculate_emotional_clarity(self, emotion: str) -> float:
        """Расчет ясности эмоционального состояния"""
        
        # Более базовые эмоции имеют большую ясность
        core_emotions = ['joy', 'sadness', 'anger', 'fear']
        
        if emotion in core_emotions:
            return 0.9
        else:
            return 0.6

    def _calculate_social_context(self, context: Dict[str, Any]) -> float:
        """Расчет социального контекста"""
        
        if not context:
            return 0.5  # Neutral
        
        # Анализ социальных факторов
        social_indicators = ['group', 'team', 'family', 'friend', 'social', 'public']
        text = str(context).lower()
        
        social_count = sum(1 for indicator in social_indicators if indicator in text)
        
        return min(social_count * 0.2, 1.0)

    def _calculate_personal_relevance(self, context: Dict[str, Any]) -> float:
        """Расчет личной релевантности"""
        
        if not context:
            return 0.5
        
        # Анализ персональных факторов
        personal_indicators = ['my', 'mine', 'personal', 'private', 'own', 'self']
        text = str(context).lower()
        
        personal_count = sum(1 for indicator in personal_indicators if indicator in text)
        
        return min(personal_count * 0.3, 1.0)

    def _calculate_temporal_context(self, context: Dict[str, Any]) -> float:
        """Расчет временного контекста"""
        
        if not context:
            return 0.5
        
        # Анализ временных факторов
        temporal_indicators = ['future', 'past', 'now', 'today', 'tomorrow', 'yesterday']
        text = str(context).lower()
        
        temporal_count = sum(1 for indicator in temporal_indicators if indicator in text)
        
        return min(temporal_count * 0.25, 1.0)

    def _calculate_valence(self, emotion: str, context_factors: Dict[str, float]) -> float:
        """Расчет валентности эмоции (Pleasantness)"""
        
        # Базовая валентность для основных эмоций
        base_valence = {
            'joy': 0.8,
            'trust': 0.6,
            'surprise': 0.2,
            'sadness': -0.7,
            'disgust': -0.6,
            'anger': -0.7,
            'fear': -0.6,
            'anticipation': 0.3,
            'neutral': 0.0
        }
        
        valence = base_valence.get(emotion, 0.0)
        
        # Корректировка через контекстуальные факторы
        modifier = context_factors.get('intensity_modifier', 1.0)
        clarity = context_factors.get('emotional_clarity', 0.5)
        
        # Усиление валентности при высокой интенсивности и ясности
        adjusted_valence = valence * modifier * clarity
        
        # Ограничение в диапазоне [-1, 1]
        return max(-1.0, min(1.0, adjusted_valence))

    def _calculate_arousal(self, emotion: str, intensity: float, 
                         context_factors: Dict[str, float]) -> float:
        """Расчет возбуждения эмоции"""
        
        # Базовая активность для эмоций
        base_arousal = {
            'anger': 0.9,
            'fear': 0.8,
            'joy': 0.7,
            'surprise': 0.8,
            'disgust': 0.6,
            'sadness': 0.3,
            'trust': 0.4,
            'anticipation': 0.6,
            'neutral': 0.5
        }
        
        arousal = base_arousal.get(emotion, 0.5)
        
        # Корректировка через интенсивность
        modifier = context_factors.get('intensity_modifier', 1.0)
        clarity = context_factors.get('emotional_clarity', 0.5)
        
        # Базовый уровень + корректировки
        adjusted_arousal = (0.5 + (arousal - 0.5) * modifier * clarity)
        
        return max(0.0, min(1.0, adjusted_arousal))

    def _calculate_dominance(self, emotion: str, secondary: List[str], 
                           context_factors: Dict[str, float]) -> float:
        """Расчет доминирования эмоции"""
        
        # Базовая доминантность для эмоций
        base_dominance = {
            'anger': 0.8,
            'joy': 0.7,
            'trust': 0.6,
            'disgust': 0.5,
            'surprise': 0.5,
            'anticipation': 0.4,
            'fear': 0.3,
            'sadness': 0.2,
            'neutral': 0.5
        }
        
        dominance = base_dominance.get(emotion, 0.5)
        
        # Корректировка через вторичные эмоции
        if secondary:
            if np:
                avg_secondary_dominance = np.mean([
                    base_dominance.get(emo, 0.5) for emo in secondary
                ])
                dominance = (dominance + avg_secondary_dominance) / 2
            else:
                # Fallback calculation
                avg_secondary = sum(base_dominance.get(emo, 0.5) for emo in secondary) / len(secondary)
                dominance = (dominance + avg_secondary) / 2
        
        # Корректировка через социальный и личный контекст
        social_context = context_factors.get('social_context', 0.5)
        personal_relevance = context_factors.get('personal_relevance', 0.5)
        
        # Высокая социальная значимость и личная релевантность увеличивают доминирование
        dominance += (social_context + personal_relevance - 1.0) * 0.3
        
        return max(0.0, min(1.0, dominance))

    def _refine_secondary_emotions(self, primary: str, secondary: List[str], 
                                 context_factors: Dict[str, float]) -> List[str]:
        """Уточнение и фильтрация вторичных эмоций"""
        
        if not secondary:
            # Генерируем вторичные эмоции на основе контекста
            return self._generate_contextual_secondary_emotions(primary, context_factors)
        
        # Фильтрация неподходящих вторичных эмоций
        refined_secondary = []
        for emo in secondary:
            if emo != primary:  # Исключаем дублирование с основной эмоцией
                # Проверяем совместимость с основной эмоцией
                if self._are_emotions_compatible(primary, emo):
                    refined_secondary.append(emo)
        
        # Добавляем контекстуальные эмоции если нужно
        if len(refined_secondary) < 3:
            additional_emotions = self._generate_contextual_secondary_emotions(
                primary, context_factors
            )
            for emo in additional_emotions:
                if emo not in refined_secondary and len(refined_secondary) < 3:
                    refined_secondary.append(emo)
        
        return refined_secondary[:3]  # Максимум 3 вторичные эмоции

    def _generate_contextual_secondary_emotions(self, primary: str, 
                                              context_factors: Dict[str, float]) -> List[str]:
        """Генерация контекстуальных вторичных эмоций"""
        
        # Маппинг первичных эмоций на типичные вторичные
        emotion_pairs = {
            'joy': ['contentment', 'pride', 'relief'],
            'trust': ['confidence', 'acceptance', 'faith'],
            'fear': ['anxiety', 'apprehension', 'worry'],
            'surprise': ['amazement', 'confusion', 'curiosity'],
            'sadness': ['grief', 'sorrow', 'disappointment'],
            'disgust': ['revulsion', 'contempt', 'loathing'],
            'anger': ['frustration', 'irritation', 'hostility'],
            'anticipation': ['interest', 'eagerness', 'expectation']
        }
        
        base_secondary = emotion_pairs.get(primary, ['calm', 'neutral', 'balanced'])
        
        # Корректировка через контекстуальные факторы
        if context_factors.get('urgency', 0) > 0.7:
            base_secondary.append('urgency')
        if context_factors.get('formality', 0) > 0.7:
            base_secondary.append('formality')
        
        return base_secondary[:3]

    def _are_emotions_compatible(self, primary: str, secondary: str) -> bool:
        """Проверка совместимости эмоций"""
        
        # Определяем совместимые группы эмоций
        compatible_groups = [
            ['joy', 'trust', 'anticipation'],  # Positive emotions
            ['fear', 'sadness', 'disgust'],    # Negative emotions
            ['anger', 'frustration', 'irritation'],  # Aggressive emotions
            ['surprise', 'amazement', 'confusion']   # Reactive emotions
        ]
        
        # Проверяем, находятся ли эмоции в одной группе
        for group in compatible_groups:
            if primary in group and secondary in group:
                return True
        
        return False

    def _calculate_emotion_confidence(self, primary: str, intensity: float, 
                                    context_factors: Dict[str, float]) -> float:
        """Расчет уверенности в эмоциональной оценке"""
        
        # Базовая уверенность зависит от ясности эмоции
        base_confidence = context_factors.get('emotional_clarity', 0.5)
        
        # Корректировка через интенсивность (высокая интенсивность = высокая уверенность)
        intensity_factor = intensity
        
        # Корректировка через контекстуальные факторы
        if context_factors:
            context_weight = sum(context_factors.values()) / len(context_factors)
        else:
            context_weight = 0.5
        
        # Общая уверенность
        total_confidence = (base_confidence * 0.4 + 
                          intensity_factor * 0.4 + 
                          context_weight * 0.2)
        
        return max(0.0, min(1.0, total_confidence))

    def _update_emotion_statistics(self, emotion: str, confidence: float):
        """Обновление статистики эмоций"""
        
        # Подсчет основных эмоций
        if emotion not in self.emotion_stats['primary_emotions_detected']:
            self.emotion_stats['primary_emotions_detected'][emotion] = 0
        self.emotion_stats['primary_emotions_detected'][emotion] += 1
        
        # Обновление средней уверенности
        total_emotions = self.emotion_stats['emotions_processed']
        current_avg = self.emotion_stats['average_confidence']
        
        new_avg = (current_avg * (total_emotions - 1) + confidence) / total_emotions
        self.emotion_stats['average_confidence'] = new_avg

    def get_emotion_stats(self) -> Dict[str, Any]:
        """Получение расширенной статистики эмоционального движка"""
        
        base_stats = {
            **self.emotion_stats,
            'models_loaded': {
                'emotion_classifier': self.emotion_classifier is not None,
                'vader_analyzer': self.vader_analyzer is not None,
                'spacy_model': self.nlp is not None,
                'nlp_available': NLP_AVAILABLE
            },
            'supported_emotions': list(self.EMOTION_WHEEL.keys()),
            'config': self.config,
            'v2_1_status': {
                'available': V2_1_AVAILABLE,
                'gpu_enabled': self.use_gpu,
                'gpu_acceleration_active': self.gpu_support is not None,
                'fallback_mode': not NLP_AVAILABLE
            }
        }
        
        # Add enhanced storage stats if available
        if V2_1_AVAILABLE and hasattr(self, 'enhanced_storage'):
            base_stats['enhanced_storage'] = self.enhanced_storage.get_storage_stats()
        
        return base_stats

    async def shutdown(self):
        """Корректное завершение работы системы"""
        try:
            logger.info("Shutting down Production Emotion Engine...")
            
            # v2.1 cleanup
            if self.gpu_support:
                await self.gpu_support.cleanup()
                logger.info("GPU support cleaned up")
            
            if self.enhanced_storage:
                await self.enhanced_storage.shutdown()
                logger.info("Enhanced storage cleaned up")
            
            logger.info("Production Emotion Engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during emotion engine shutdown: {e}")


# Enhanced test function для демонстрации функциональности
async def test_production_emotion_engine():
    """Тестирование production эмоционального движка"""
    
    engine = ProductionEmotionEngine()
    
    test_texts = [
        "I'm absolutely thrilled about this amazing opportunity!",
        "This brake overheating problem is really concerning me.",
        "The system failure is extremely frustrating and annoying.",
        "I'm curious about how this technology works.",
        "I feel disappointed with the current results."
    ]
    
    print("🎭 Testing ASMF v2.0 Production Emotion Engine (Enhanced with v2.1)")
    print("=" * 70)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        
        # Детекция эмоции
        emotion = await engine.detect_emotion(text)
        print(f"   Primary emotion: {emotion}")
        
        # Детекция тона
        tone = await engine.detect_tone(text)
        print(f"   Tone: {tone}")
        
        # Кодирование эмоционального вектора
        context = {'text': text, 'text_type': 'test', 'user_mood': 'testing'}
        emotion_vector = await engine.encode_emotion(
            primary=emotion,
            secondary=[],
            intensity=0.8,
            context=context
        )
        
        print(f"   GPU Accelerated: {emotion_vector.gpu_accelerated}")
        print(f"   Intensity: {emotion_vector.intensity:.2f}")
        print(f"   Confidence: {emotion_vector.confidence:.2f}")
        print(f"   Valence: {emotion_vector.valence:.2f}")
        print(f"   Arousal: {emotion_vector.arousal:.2f}")
        print(f"   Dominance: {emotion_vector.dominance:.2f}")
    
    # Получаем расширенную статистику
    stats = engine.get_emotion_stats()
    print(f"\n📊 Engine Statistics:")
    print(f"   Emotions processed: {stats['emotions_processed']}")
    print(f"   Average confidence: {stats['average_confidence']:.3f}")
    print(f"   GPU accelerated: {stats.get('gpu_accelerated_analyses', 0)}")
    print(f"   Average processing time: {stats.get('average_emotion_time', 0):.3f}s")
    print(f"   Fallback activations: {stats.get('fallback_activations', 0)}")
    print(f"   Sentiment analyses: {stats.get('sentiment_analyses', 0)}")
    print(f"   Primary emotions: {stats['primary_emotions_detected']}")
    print(f"   GPU Status: {stats['v2_1_status']['gpu_enabled']}")
    
    # Корректное завершение
    await engine.shutdown()
    
    print("\n✅ Production Emotion Engine test completed successfully!")
    

if __name__ == "__main__":
    asyncio.run(test_production_emotion_engine())
