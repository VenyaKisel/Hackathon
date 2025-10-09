# services/rec_manager.py
from typing import List
from ..models.diet import Diet
from ..models.fatty_acid import PredictionResult
from ..models.recommendation import Recommendation
from .rec_engine import LinearRecommendationEngine

class RecommendationManager:
    """Управляет генерацией рекомендаций"""
    
    def __init__(self, acid_predictor):
        self.acid_predictor = acid_predictor
        self.engine = LinearRecommendationEngine()
        print("✅ Рекомендательная система инициализирована")
    
    def generate_recommendations(self, diet: Diet, prediction: PredictionResult) -> List[Recommendation]:
        """Генерирует рекомендации используя линейные модели"""
        try:
            recommendations = self.engine.generate_recommendations(diet, prediction)
            print(f"✅ Сгенерировано {len(recommendations)} рекомендаций")
            return self._remove_duplicates(recommendations)
        except Exception as e:
            print(f"❌ Ошибка генерации рекомендаций: {e}")
            return []
    
    def _remove_duplicates(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Удаляет дублирующиеся рекомендации"""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            rec_key = tuple(sorted(
                f"{adj.component_name}:{adj.recommended_amount:.1f}" 
                for adj in rec.adjustments
            ))
            
            if rec_key not in seen:
                seen.add(rec_key)
                unique_recommendations.append(rec)
        
        return unique_recommendations