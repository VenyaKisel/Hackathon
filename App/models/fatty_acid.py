from dataclasses import dataclass
from typing import Dict

@dataclass
class AcidPrediction:
    """Прогноз для одной жирной кислоты"""
    name: str
    predicted_value: float
    target_min: float
    target_max: float
    deviation: float
    
    @property
    def is_within_target(self) -> bool:
        return self.target_min <= self.predicted_value <= self.target_max
    
    @property 
    def status(self) -> str:
        if self.is_within_target:
            return "в норме"
        elif self.predicted_value < self.target_min:
            return "ниже нормы"
        else:
            return "выше нормы"

@dataclass
class PredictionResult:
    """Результат прогнозирования всех кислот"""
    acids: Dict[str, AcidPrediction]
    
    def get_acids_outside_target(self) -> Dict[str, AcidPrediction]:
        """Кислоты вне целевого диапазона"""
        return {name: acid for name, acid in self.acids.items() 
                if not acid.is_within_target}