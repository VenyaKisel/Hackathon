# services/rec_engine.py
from typing import List, Dict, Optional, Tuple
from ..models.diet import Diet
from ..models.fatty_acid import PredictionResult
from ..models.recommendation import Recommendation, RecommendationType, PriorityLevel, ComponentAdjustment


class LinearRecommendationEngine:
    """Рекомендательная система на основе линейных моделей кислот"""
    
    def __init__(self):
        self.acid_weights = self._load_acid_weights()
        self.acid_targets = self._load_acid_targets()
    
    def _load_acid_weights(self) -> Dict[str, Dict[str, float]]:
        """Загружает веса линейных моделей для каждой кислоты"""
        return {
            'Лауриновая': {
                'трав_сен': 0.0, 'конц_зерн': 0.0, 'масличн': 0.0, 'жир': 0.0,
                'пром_отх': 0.0, 'мин_техно': 0.0, 'сп': 0.0, 'крахмал': 0.0,
                'andfom': 0.0, 'сахар (вру)': 0.0, 'нву': 0.0, 'ожк': 0.0,
                'k': 0.0, 'intercept': 15.04
            },
            'Олеиновая': {
                'трав_сен': 0.0, 'конц_зерн': 0.0, 'масличн': 0.0, 'жир': 0.0,
                'пром_отх': -0.282, 'мин_техно': 0.256,
                'сп': 0.389, 'крахмал': -0.642,
                'andfom': -0.152, 'сахар (вру)': 0.0,
                'нву': -0.133, 'ожк': 0.0, 'k': -2.479,
                'intercept': 47.60
            },
            'Линолевая': {
                'трав_сен': -0.0086, 'конц_зерн': 0.0,
                'масличн': 0.0062, 'жир': 0.0512,
                'пром_отх': 0.0218, 'мин_техно': 0.0,
                'сп': 0.0334, 'крахмал': 0.0733,
                'andfom': -0.0118, 'сахар (вру)': -0.0829,
                'нву': -0.0422, 'ожк': -0.0650,
                'k': 0.0809, 'intercept': 2.68
            },
            'Линоленовая': {
                'трав_сен': 0.0016, 'конц_зерн': 0.0,
                'масличн': -0.0041, 'жир': -0.0034,
                'пром_отх': 0.0, 'мин_техно': -0.0106,
                'сп': 0.0, 'крахмал': 0.0, 'andfom': -0.0009,
                'сахар (вру)': -0.0037, 'нву': 0.0023,
                'ожк': -0.0145, 'k': 0.0, 'intercept': 0.464
            },
            'Арахиновая': {
                'трав_сен': -0.00001, 'конц_зерн': 0.0,
                'масличн': 0.0, 'жир': 0.0021,
                'пром_отх': -0.0029, 'мин_техно': -0.0069,
                'сп': -0.0053, 'крахмал': 0.0,
                'andfom': -0.0008, 'сахар (вру)': 0.0049,
                'нву': -0.0016, 'ожк': 0.0, 'k': -0.0314,
                'intercept': 0.340
            }
        }
    
    def _load_acid_targets(self) -> Dict[str, Dict[str, float]]:
        """Загружает целевые диапазоны для кислот"""
        return {
            'Лауриновая': {'min': 2.0, 'max': 4.4},
            'Олеиновая': {'min': 20.0, 'max': 28.0},
            'Линолевая': {'min': 2.2, 'max': 5.0},
            'Линоленовая': {'min': 0.0, 'max': 1.5},
            'Арахиновая': {'min': 0.0, 'max': 1.0}
        }
    
    def generate_recommendations(self, diet: Diet, prediction: PredictionResult) -> List[Recommendation]:
        """Генерирует рекомендации на основе линейных моделей"""
        recommendations = []
        
        # Анализируем проблемные кислоты
        problematic_acids = self._get_problematic_acids(prediction)
        
        for acid_name, acid_data in problematic_acids.items():
            acid_recommendations = self._generate_for_acid(acid_name, acid_data, diet)
            recommendations.extend(acid_recommendations)
        
        merged = self._merge_recommendations(recommendations)
        return self._prioritize_recommendations(merged)
    
    def _get_problematic_acids(self, prediction: PredictionResult) -> Dict:
        """Находит кислоты, требующие коррекции"""
        problematic = {}
        
        for acid_name, acid_pred in prediction.acids.items():
            if acid_name not in self.acid_weights:
                continue
                
            if not acid_pred.is_within_target:
                problematic[acid_name] = {
                    'current': acid_pred.predicted_value,
                    'deviation': acid_pred.deviation,
                    'target_min': acid_pred.target_min,
                    'target_max': acid_pred.target_max,
                    'needs_increase': acid_pred.predicted_value < acid_pred.target_min
                }
        
        return problematic
    
    def _generate_for_acid(self, acid_name: str, acid_data: Dict, diet: Diet) -> List[Recommendation]:
        """Генерирует рекомендации для конкретной кислоты"""
        recommendations = []
        weights = self.acid_weights[acid_name]
        
        # Находим компоненты с максимальным влиянием
        influential_comps = self._get_influential_components(weights, acid_data['needs_increase'])
        
        for comp_name, influence in influential_comps:
            if comp_name in diet.components:
                rec = self._create_recommendation(comp_name, influence, acid_name, acid_data, diet)
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def _get_influential_components(self, weights: Dict[str, float], needs_increase: bool) -> List[Tuple[str, float]]:
        """Находит компоненты с наибольшим влиянием"""
        components = []
        
        for comp_name, weight in weights.items():
            if comp_name == 'intercept':
                continue
                
            if (needs_increase and weight > 0) or (not needs_increase and weight < 0):
                components.append((comp_name, weight))
        
        return sorted(components, key=lambda x: abs(x[1]), reverse=True)[:3]
    
    def _create_recommendation(self, comp_name: str, influence: float, 
                             acid_name: str, acid_data: Dict, diet: Diet) -> Optional[Recommendation]:
        """Создает рекомендацию по корректировке компонента"""
        current_amount = diet.components[comp_name].amount
        
        required_change = -acid_data['deviation'] / influence
        
        max_change = current_amount * 0.3
        final_change = max(-max_change, min(required_change, max_change))
        
        if abs(final_change) < 0.1: 
            return None
        
        new_amount = current_amount + final_change
        if new_amount < 0:
            return None
        
        # Рассчитываем влияние на все кислоты
        total_impact = self._calculate_impact(comp_name, final_change)
        
        adjustment = ComponentAdjustment(
            component_name=comp_name,
            current_amount=current_amount,
            recommended_amount=new_amount,
            change_direction='increase' if final_change > 0 else 'decrease',
            expected_impact=total_impact
        )
        
        return Recommendation(
            recommendation_id=f"rec_{comp_name}_{acid_name}",
            type=RecommendationType.COMPONENT_ADJUSTMENT,
            priority=self._get_priority(acid_data['deviation'], influence),
            title=f"Коррекция {comp_name}",
            description=self._get_description(comp_name, acid_name, acid_data, final_change),
            adjustments=[adjustment],
            expected_improvement=total_impact,
            confidence=min(0.3 + abs(influence) * 5, 0.9),
            validation_status='pending'
        )
    
    def _calculate_impact(self, comp_name: str, change: float) -> Dict[str, float]:
        """Рассчитывает влияние изменения на все кислоты"""
        impact = {}
        for acid_name, weights in self.acid_weights.items():
            if comp_name in weights:
                impact[acid_name] = weights[comp_name] * change
        return impact
    
    def _get_priority(self, deviation: float, influence: float) -> PriorityLevel:
        """Определяет приоритет рекомендации"""
        impact_score = abs(deviation * influence)
        
        if impact_score > 2.0:
            return PriorityLevel.CRITICAL
        elif impact_score > 1.0:
            return PriorityLevel.HIGH
        elif impact_score > 0.5:
            return PriorityLevel.WARNING
        else:
            return PriorityLevel.INFO
    
    def _get_description(self, comp_name: str, acid_name: str, 
                        acid_data: Dict, change: float) -> str:
        """Генерирует описание рекомендации"""
        direction = "увеличить" if change > 0 else "уменьшить"
        abs_change = abs(change)
        
        if acid_data['needs_increase']:
            problem = "ниже нормы"
            goal = "повышения"
        else:
            problem = "выше нормы"
            goal = "снижения"
        
        return (f"{direction} {comp_name} на {abs_change:.2f} кг для {goal} {acid_name} "
                f"(сейчас {problem} на {abs(acid_data['deviation']):.2f}%)")
    
    def _merge_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Объединяет рекомендации для одинаковых компонентов"""
        merged = {}
        
        for rec in recommendations:
            comp_name = rec.adjustments[0].component_name
            
            if comp_name not in merged:
                merged[comp_name] = rec
            else:
                existing = merged[comp_name]
                
                existing_adj = existing.adjustments[0]
                new_adj = rec.adjustments[0]
                
                avg_change = ((existing_adj.recommended_amount - existing_adj.current_amount) +
                            (new_adj.recommended_amount - new_adj.current_amount)) / 2
                
                existing_adj.recommended_amount = existing_adj.current_amount + avg_change
                
                for acid, impact in rec.expected_improvement.items():
                    if acid in existing.expected_improvement:
                        existing.expected_improvement[acid] += impact
                    else:
                        existing.expected_improvement[acid] = impact
                
                existing.description = f"Комплексная коррекция {comp_name}"
        
        return list(merged.values())
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Сортирует рекомендации по приоритету"""
        return sorted(recommendations, 
                     key=lambda x: (x.priority.value, 
                                  sum(abs(imp) for imp in x.expected_improvement.values())), 
                     reverse=True)


# Сохраняем обратную совместимость
RecommendationEngine = LinearRecommendationEngine