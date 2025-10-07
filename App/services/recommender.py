# services/recommender.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from typing import List, Dict
from ..models.diet import Diet
from ..models.fatty_acid import PredictionResult
from .rec_manager import RecommendationManager
from .predictor import AcidPredictor


class DietRecommender:
    """Обновленный класс с интеграцией рекомендательной системы"""
    
    def __init__(self):
        self.recommendation_manager = RecommendationManager()
        self.predictor = AcidPredictor()
    
    def generate_recommendations(self, diet: Diet, 
                               prediction: PredictionResult) -> List[str]:
        """Генерирует текстовые рекомендации (обратная совместимость)"""
        structured_recommendations = self.recommendation_manager.generate_recommendations(
            diet, prediction
        )
        
        return self._format_recommendations(structured_recommendations)
    
    def _format_recommendations(self, recommendations: List) -> List[str]:
        """Форматирует структурированные рекомендации в текст"""
        if not recommendations:
            return ["✅ Все жирные кислоты в пределах целевых значений"]
        
        formatted = ["📊 РЕКОМЕНДАЦИИ ПО КОРРЕКЦИИ РАЦИОНА:"]
        
        for i, rec in enumerate(recommendations, 1):
            # Эмодзи для приоритета
            priority_emoji = {
                'critical': '🔴',
                'warning': '🟡', 
                'info': '🟢'
            }.get(rec.priority.value, '⚪')
            
            formatted.append(f"\n{priority_emoji} Рекомендация {i}: {rec.title}")
            formatted.append(f"   {rec.description}")
            
            for adj in rec.adjustments:
                change = adj.recommended_amount - adj.current_amount
                direction = "увеличить" if change > 0 else "уменьшить"
                formatted.append(
                    f"   • {direction} {adj.component_name} с {adj.current_amount:.1f} "
                    f"до {adj.recommended_amount:.1f} кг"
                )
            
            # Ожидаемое улучшение
            for acid, impact in rec.expected_improvement.items():
                if impact != 0:
                    formatted.append(f"   → {acid}: {impact:+.2f}%")
        
        formatted.append("\n💡 Примените рекомендации и пересчитайте прогноз")
        return formatted
    
    def generate_structured_recommendations(self, diet: Diet, 
                                          prediction: PredictionResult):
        """Возвращает структурированные рекомендации (для нового UI)"""
        return self.recommendation_manager.generate_recommendations(diet, prediction)
    
    def apply_and_evaluate_recommendation(self, diet: Diet, 
                                        recommendation) -> Dict:
        """Применяет рекомендацию и оценивает ее эффективность"""
        modified_diet = self.recommendation_manager.apply_recommendation(
            diet, recommendation
        )
        
        original_prediction = self.predictor.predict(diet)
        new_prediction = self.predictor.predict(modified_diet)
        
        impact = self.recommendation_manager.evaluate_recommendation_impact(
            diet, modified_diet, original_prediction, new_prediction
        )
        
        return {
            'modified_diet': modified_diet,
            'new_prediction': new_prediction,
            'impact_analysis': impact
        }