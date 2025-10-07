from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class RecommendationType(Enum):
    COMPONENT_ADJUSTMENT = "adjust_component"  
    COMPONENT_REPLACEMENT = "replace_component" 
    STRATEGIC_ADVICE = "strategic"         
    OPTIMIZATION = "optimization"            

class PriorityLevel(Enum):
    CRITICAL = "critical"    
    WARNING = "warning"     
    INFO = "info"            

@dataclass
class ComponentAdjustment:
    component_name: str
    current_amount: float
    recommended_amount: float
    change_direction: str 
    expected_impact: Dict[str, float] 


@dataclass
class Recommendation:
    recommendation_id: str
    type: RecommendationType
    priority: PriorityLevel
    title: str
    description: str
    adjustments: List[ComponentAdjustment]
    expected_improvement: Dict[str, float] 
    confidence: float 
    validation_status: str 
    
    @property
    def total_impact_score(self) -> float:
        """Общая оценка эффективности рекомендации"""
        return sum(abs(impact) for impact in self.expected_improvement.values())