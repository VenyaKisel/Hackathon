# services/recommender.py
from typing import List, Dict
from ..models.diet import Diet
from ..models.fatty_acid import PredictionResult
from .rec_manager import RecommendationManager

class DietRecommender:
    """Рекомендательная система для рациона коров"""
    
    def __init__(self, acid_predictor=None): 
        if acid_predictor:
            self.acid_predictor = acid_predictor
        else:
            from .predictor import AcidPredictor
            self.acid_predictor = AcidPredictor()
            
        self.recommendation_manager = RecommendationManager(self.acid_predictor)
        print("✅ Рекомендательная система инициализирована")
    
    def generate_recommendations(self, diet: Diet, prediction: PredictionResult) -> List[str]:
        """Генерирует текстовые рекомендации на основе предсказаний"""
        try:
            structured_recommendations = self.recommendation_manager.generate_recommendations(diet, prediction)
            
            return self._format_recommendations(structured_recommendations, prediction)
            
        except Exception as e:
            print(f"❌ Ошибка генерации рекомендаций: {e}")
            return ["⚠️ Временные технические работы. Рекомендации будут доступны позже."]
    
    def _format_recommendations(self, recommendations: List, prediction: PredictionResult) -> List[str]:
        """Форматирует структурированные рекомендации в текстовый вид"""
        if not recommendations:
            return self._get_no_recommendations_message(prediction)
        
        formatted = []
        
        problematic_count = self._count_problematic_acids(prediction)
        formatted.append(f"📊 АНАЛИЗ РАЦИОНА:")
        formatted.append(f"Обнаружено проблем: {problematic_count}")
        
        problematic_acids = self._get_problematic_acids(prediction)
        if problematic_acids:
            formatted.append("\n🔍 ПРОБЛЕМНЫЕ КИСЛОТЫ:")
            for acid_name, acid_pred in problematic_acids:
                status = "ниже нормы" if acid_pred.predicted_value < acid_pred.target_min else "выше нормы"
                formatted.append(
                    f"• {acid_name}: {status} "
                    f"({acid_pred.predicted_value:.1f}% при норме {acid_pred.target_min:.1f}-{acid_pred.target_max:.1f}%)"
                )
        
        formatted.append("\n💡 РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(recommendations[:5], 1):  # Ограничиваем 5 рекомендациями
            if rec.adjustments:
                adjustment = rec.adjustments[0]
                direction = "увеличить" if adjustment.change_direction == 'increase' else "уменьшить"
                formatted.append(
                    f"{i}. {direction} {adjustment.component_name} "
                    f"с {adjustment.current_amount:.1f}кг до {adjustment.recommended_amount:.1f}кг"
                )
        
        if len(recommendations) > 5:
            formatted.append(f"\n... и еще {len(recommendations) - 5} рекомендаций")
        
        return formatted
    
    def _get_no_recommendations_message(self, prediction: PredictionResult) -> List[str]:
        """Возвращает сообщение когда рекомендаций нет"""
        problematic_count = self._count_problematic_acids(prediction)
        
        if problematic_count == 0:
            return ["✅ Все показатели в норме! Текущий рацион оптимален."]
        else:
            return [
                "📊 АНАЛИЗ РАЦИОНА:",
                f"Обнаружено проблем: {problematic_count}",
                "\n💡 СОВЕТ:",
            ]
    
    def _count_problematic_acids(self, prediction: PredictionResult) -> int:
        """Считает количество кислот вне целевого диапазона"""
        return sum(1 for acid_pred in prediction.acids.values() if not acid_pred.is_within_target)
    
    def _get_problematic_acids(self, prediction: PredictionResult) -> List:
        """Возвращает список проблемных кислот"""
        return [
            (acid_name, acid_pred) 
            for acid_name, acid_pred in prediction.acids.items() 
            if not acid_pred.is_within_target
        ]