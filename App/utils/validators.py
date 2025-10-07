from typing import Any, Optional

class DataValidators:
    """Валидаторы данных"""
    
    @staticmethod
    def validate_float(value: Any, min_val: float = 0.0, max_val: float = 100.0) -> Optional[float]:
        """Валидирует float значение"""
        try:
            num = float(value)
            if min_val <= num <= max_val:
                return num
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_acid_value(value: Any) -> Optional[float]:
        """Валидирует значение жирной кислоты (0-100%)"""
        return DataValidators.validate_float(value, 0.0, 100.0)
    
    @staticmethod
    def validate_diet_component(value: Any) -> Optional[float]:
        """Валидирует значение компонента рациона (кг)"""
        return DataValidators.validate_float(value, 0.0, 1000.0)