# services/recommendation_engine.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from ..models.diet import Diet
from ..models.fatty_acid import PredictionResult
from ..models.recommendation import Recommendation, RecommendationType, PriorityLevel, ComponentAdjustment



class BaseRecommendationStrategy(ABC):
    """Абстрактный класс для стратегий рекомендаций"""
    
    @abstractmethod
    def generate_recommendations(self, 
                               diet: Diet, 
                               prediction: PredictionResult) -> List[Recommendation]:
        pass
    
    @abstractmethod
    def validate_recommendation(self, 
                              recommendation: Recommendation,
                              diet: Diet,
                              prediction: PredictionResult) -> bool:
        pass


class InfluenceMatrixStrategy(BaseRecommendationStrategy):
    """Стратегия на основе матрицы влияния"""
    
    def __init__(self):
        self.influence_matrix = self._load_influence_matrix()
    
    def _load_influence_matrix(self) -> Dict:
        """Загружает матрицу влияния компонентов на кислоты"""
        return {
            'кукуруза': {
                'Олеиновая': 0.25,  # +0.25% на 1 кг
                'Пальмитиновая': 0.3,
                'Линолевая': 0.15
            },
            'силос': {
                'Олеиновая': 0.15,
                'Пальмитиновая': -0.2,  # -0.2% на 1 кг
                'Стеариновая': 0.1
            }
            # ... другие компоненты
        }
    
    def generate_recommendations(self, diet: Diet, prediction: PredictionResult) -> List[Recommendation]:
        """Генерирует рекомендации на основе матрицы влияния"""
        recommendations = []
        
        # Анализ проблемных кислот
        problematic_acids = self._identify_problematic_acids(prediction)
        
        for acid_name, deviation in problematic_acids.items():
            acid_recommendations = self._generate_acid_recommendations(
                acid_name, deviation, diet, prediction
            )
            recommendations.extend(acid_recommendations)
        
        return self._prioritize_recommendations(recommendations)
    
    def _identify_problematic_acids(self, prediction: PredictionResult) -> Dict[str, float]:
        """Определяет кислоты, требующие коррекции"""
        problematic = {}
        for acid_name, acid_pred in prediction.acids.items():
            if not acid_pred.is_within_target:
                if acid_pred.predicted_value < acid_pred.target_min:
                    deviation = acid_pred.predicted_value - acid_pred.target_min
                else:
                    deviation = acid_pred.predicted_value - acid_pred.target_max
                problematic[acid_name] = deviation
        return problematic
    
    def _generate_acid_recommendations(self, acid_name: str, deviation: float, 
                                     diet: Diet, prediction: PredictionResult) -> List[Recommendation]:
        """Генерирует рекомендации для конкретной кислоты"""
        recommendations = []
        
        influencing_components = self._find_influencing_components(acid_name)
        
        for comp_name, influence_strength in influencing_components.items():
            if comp_name in diet.components:
                recommendation = self._create_component_adjustment(
                    comp_name, acid_name, deviation, influence_strength, diet
                )
                if recommendation:
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _find_influencing_components(self, acid_name: str) -> Dict[str, float]:
        """Находит компоненты, влияющие на указанную кислоту"""
        influencers = {}
        for comp_name, acids in self.influence_matrix.items():
            if acid_name in acids:
                influencers[comp_name] = acids[acid_name]
        return influencers
    
    def _create_component_adjustment(self, comp_name: str, acid_name: str, 
                                   deviation: float, influence: float, diet: Diet) -> Optional[Recommendation]:
        """Создает рекомендацию по корректировке компонента"""
        current_amount = diet.components[comp_name].amount
        
        required_change = -deviation / influence
        
        max_change = current_amount * 0.3 
        recommended_change = max(-max_change, min(required_change, max_change))
        
        if abs(recommended_change) < 0.1:
            return None
        
        new_amount = current_amount + recommended_change
        if new_amount < 0:  # Не может быть отрицательным
            return None
        
        adjustment = ComponentAdjustment(
            component_name=comp_name,
            current_amount=current_amount,
            recommended_amount=new_amount,
            change_direction='increase' if recommended_change > 0 else 'decrease',
            expected_impact={acid_name: influence * recommended_change}
        )
        
        return Recommendation(
            recommendation_id=f"rec_{comp_name}_{acid_name}",
            type=RecommendationType.COMPONENT_ADJUSTMENT,
            priority=self._calculate_priority(deviation, influence),
            title=f"Скорректировать {comp_name}",
            description=f"Изменение {comp_name} для коррекции {acid_name}",
            adjustments=[adjustment],
            expected_improvement={acid_name: influence * recommended_change},
            confidence=0.7,  # Базовая уверенность
            validation_status='pending'
        )
    
    def _calculate_priority(self, deviation: float, influence: float) -> PriorityLevel:
        """Рассчитывает приоритет рекомендации"""
        impact_score = abs(deviation * influence)
        if impact_score > 1.0:
            return PriorityLevel.CRITICAL
        elif impact_score > 0.5:
            return PriorityLevel.WARNING
        else:
            return PriorityLevel.INFO
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Сортирует рекомендации по приоритету и эффективности"""
        return sorted(recommendations, 
                     key=lambda x: (x.priority.value, x.total_impact_score), 
                     reverse=True)
    
    def validate_recommendation(self, recommendation: Recommendation,
                              diet: Diet, prediction: PredictionResult) -> bool:
        """Валидирует рекомендацию (заглушка)"""
        return True