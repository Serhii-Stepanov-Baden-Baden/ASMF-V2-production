"""
ASMF v2.0 - Emotional State Encoding Protocol (ESEP)
Реальная реализация эмоционального кодирования

Автор: Serhii Stepanov (Baden-Baden, Germany)
Дата: 21 ноября 2025
"""

import asyncio
import hashlib
import json
import logging
import math
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
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
    timestamp: str

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
    Производственный эмоциональный движок
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

    def __init__(self, config_path: str = "config.yaml"):
        """Инициализация с реальными моделями эмоций"""
        self.config = self._load_config(config_path)
        
        # Initialize emotion models
        self._initialize_emotion_models()
        
        # Emotional state tracking
        self.emotional_memory = {}
        self.session_emotions = {}
        
        # Statistics
        self.emotion_stats = {
            'emotions_processed': 0,
            'primary_emotions_detected': {},
            'average_confidence': 0.0,
            'context_sensitivity_changes': 0
        }
        
        logger.info("Production Emotion Engine initialized successfully")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации эмоций"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('emotional', {})
        except FileNotFoundError:
            logger.warning(f"Emotion config not found, using defaults")
            return {
                'sensitivity': 0.5,
                'emotion_model': 'j-hartmann/emotion-english-distilroberta-base',
                'enable_context_factors': True,
                'emotional_memory_depth': 10,
                'volatility_threshold': 0.7
            }

    def _initialize_emotion_models(self):
        """Инициализация моделей для эмоционального анализа"""
        try:
            # Основная модель для эмоций
            emotion_model = self.config.get('emotion_model', 'j-hartmann/emotion-english-distilroberta-base')
            self.emotion_classifier = pipeline(
                "text-classification",
                model=emotion_model,
                return_all_scores=True
            )
            logger.info(f"Emotion classifier loaded: {emotion_model}")
            
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
            raise

    async def detect_emotion(self, text: str, context: str = "") -> str:
        """
        Реальная детекция эмоций с использованием transformers
        Заменяет простой keyword search на advanced emotion detection
        """
        try:
            # Основной анализ эмоций через transformers
            emotion_scores = self.emotion_classifier(text)
            
            # Извлечение топ эмоции
            top_emotion = max(emotion_scores[0], key=lambda x: x['score'])
            
            # Дополнительная проверка через VADER
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Объединение результатов
            primary_emotion = self._refine_emotion_detection(
                top_emotion['label'], 
                top_emotion['score'],
                vader_scores
            )
            
            logger.info(f"Detected primary emotion: {primary_emotion} (confidence: {top_emotion['score']:.3f})")
            return primary_emotion
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
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
        Заменяет простой keyword поиск на контекстуальный анализ
        """
        try:
            # Получение основной эмоции
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
            
            logger.info(f"Detected tone: {base_tone} (emotion: {primary_emotion})")
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
            doc = self.nlp(text)
            
            # Анализ синтаксической структуры
            exclamation_count = sum(1 for sent in doc.sents if sent.text.endswith('!'))
            question_count = sum(1 for sent in doc.sents if sent.text.endswith('?'))
            
            tone_factors['exclamation_level'] = min(exclamation_count / len(text.split()) * 10, 1.0)
            tone_factors['question_level'] = min(question_count / len(text.split()) * 10, 1.0)
        
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
        Заменяет mock векторы на математически обоснованные представления
        """
        try:
            # Контекстуальные факторы
            context_factors = self._analyze_emotional_context(primary, intensity, context)
            
            # Расчет эмоциональных измерений
            valence = self._calculate_valence(primary, context_factors)
            arousal = self._calculate_arousal(primary, intensity, context_factors)  
            dominance = self._calculate_dominance(primary, secondary, context_factors)
            
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
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            self.emotion_stats['emotions_processed'] += 1
            self._update_emotion_statistics(primary, confidence)
            
            logger.info(f"Encoded emotion: {primary} (confidence: {confidence:.3f})")
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
                timestamp=datetime.now(timezone.utc).isoformat()
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
            avg_secondary_dominance = np.mean([
                base_dominance.get(emo, 0.5) for emo in secondary
            ])
            dominance = (dominance + avg_secondary_dominance) / 2
        
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
        context_weight = np.mean(list(context_factors.values()))
        
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
        """Получение статистики эмоционального движка"""
        
        return {
            **self.emotion_stats,
            'models_loaded': {
                'emotion_classifier': self.emotion_classifier is not None,
                'vader_analyzer': self.vader_analyzer is not None,
                'spacy_model': self.nlp is not None
            },
            'supported_emotions': list(self.EMOTION_WHEEL.keys()),
            'config': self.config
        }


# Тестирование эмоционального движка
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
    
    print("🎭 Testing ASMF v2.0 Production Emotion Engine")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        
        # Детекция эмоции
        emotion = await engine.detect_emotion(text)
        print(f"   Primary emotion: {emotion}")
        
        # Детекция тона
        tone = await engine.detect_tone(text)
        print(f"   Tone: {tone}")
        
        # Кодирование эмоционального вектора
        context = {'text_type': 'test', 'user_mood': 'testing'}
        emotion_vector = await engine.encode_emotion(
            primary=emotion,
            secondary=[],
            intensity=0.8,
            context=context
        )
        
        print(f"   Intensity: {emotion_vector.intensity:.2f}")
        print(f"   Confidence: {emotion_vector.confidence:.2f}")
        print(f"   Valence: {emotion_vector.valence:.2f}")
        print(f"   Arousal: {emotion_vector.arousal:.2f}")
        print(f"   Dominance: {emotion_vector.dominance:.2f}")
    
    # Получаем статистику
    stats = engine.get_emotion_stats()
    print(f"\n📊 Engine Statistics:")
    print(f"   Emotions processed: {stats['emotions_processed']}")
    print(f"   Average confidence: {stats['average_confidence']:.3f}")
    print(f"   Primary emotions detected: {stats['primary_emotions_detected']}")
    
    print("\n✅ Production Emotion Engine test completed successfully!")
    

if __name__ == "__main__":
    asyncio.run(test_production_emotion_engine())