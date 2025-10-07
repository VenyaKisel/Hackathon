# services/recommendation_manager.py
from typing import List, Dict, Optional
from ..models.diet import Diet
from ..models.fatty_acid import PredictionResult
from ..models.recommendation import Recommendation
from .rec_engine import BaseRecommendationStrategy, InfluenceMatrixStrategy


class RecommendationManager:
    """Управляет генерацией и валидацией рекомендаций"""
    
    def __init__(self):
        self.strategies: List[BaseRecommendationStrategy] = []
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Инициализирует доступные стратегии рекомендаций"""
        self.strategies.append(InfluenceMatrixStrategy())

    def generate_recommendations(self, diet: Diet, 
                               prediction: PredictionResult) -> List[Recommendation]:
        """Генерирует рекомендации используя все доступные стратегии"""
        all_recommendations = []
        
        for strategy in self.strategies:
            try:
                recommendations = strategy.generate_recommendations(diet, prediction)
                validated_recs = [
                    rec for rec in recommendations 
                    if strategy.validate_recommendation(rec, diet, prediction)
                ]
                all_recommendations.extend(validated_recs)
            except Exception as e:
                print(f"Ошибка в стратегии {type(strategy).__name__}: {e}")
        
        return self._remove_duplicates(all_recommendations)
    
    def _remove_duplicates(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Удаляет дублирующиеся рекомендации"""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            # Создаем уникальный ключ на основе содержания
            rec_key = tuple(sorted(
                f"{adj.component_name}:{adj.recommended_amount}" 
                for adj in rec.adjustments
            ))
            
            if rec_key not in seen:
                seen.add(rec_key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def apply_recommendation(self, diet: Diet, 
                           recommendation: Recommendation) -> Diet:
        """Применяет рекомендацию к рациону"""
        modified_diet = Diet(
            diet_id=f"{diet.diet_id}_modified",
            name=f"{diet.name} (с рекомендациями)",
            components=diet.components.copy()
        )
        
        for adjustment in recommendation.adjustments:
            if adjustment.component_name in modified_diet.components:
                modified_diet.components[adjustment.component_name].amount = (
                    adjustment.recommended_amount
                )
        
        return modified_diet
    
    def evaluate_recommendation_impact(self, original_diet: Diet,
                                     modified_diet: Diet,
                                     original_prediction: PredictionResult,
                                     new_prediction: PredictionResult) -> Dict:
        """Оценивает эффективность примененной рекомендации"""
        improvements = {}
        
        for acid_name, original_acid in original_prediction.acids.items():
            new_acid = new_prediction.acids.get(acid_name)
            if new_acid:
                improvement = self._calculate_improvement(original_acid, new_acid)
                improvements[acid_name] = improvement
        
        return {
            'improvements': improvements,
            'overall_score': sum(improvements.values()),
            'successful_corrections': sum(1 for imp in improvements.values() if imp > 0)
        }
    
    def _calculate_improvement(self, original_acid, new_acid) -> float:
        """Рассчитывает улучшение для одной кислоты"""
        original_dev = self._deviation_from_target(original_acid)
        new_dev = self._deviation_from_target(new_acid)
        return original_dev - new_dev  # Положительное = улучшение
    
    def _deviation_from_target(self, acid_pred) -> float:
        """Рассчитывает отклонение от целевого диапазона"""
        if acid_pred.is_within_target:
            return 0
        elif acid_pred.predicted_value < acid_pred.target_min:
            return acid_pred.target_min - acid_pred.predicted_value
        else:
            return acid_pred.predicted_value - acid_pred.target_max