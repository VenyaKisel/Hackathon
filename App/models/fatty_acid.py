# models/fatty_acid.py
from typing import Dict
from dataclasses import dataclass

@dataclass
class AcidPrediction:
    """Предсказание для одной жирной кислоты"""
    name: str
    predicted_value: float
    target_min: float
    target_max: float
    deviation: float
    
    @property
    def is_within_target(self) -> bool:
        """Вычисляемое свойство - находится ли значение в целевом диапазоне"""
        return self.target_min <= self.predicted_value <= self.target_max

@dataclass
class PredictionResult:
    """Результат предсказания для всех кислот"""
    acids: Dict[str, AcidPrediction]