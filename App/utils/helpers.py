import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class Helpers:
    """Вспомогательные функции"""
    
    @staticmethod
    def create_sample_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Создает DataFrame из списка словарей"""
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    
    @staticmethod
    def format_date(date_str: str) -> datetime:
        """Форматирует дату из строки"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%d.%m.%Y')
            except ValueError:
                return datetime.now()
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Рассчитывает процентное изменение"""
        if old_value == 0:
            return 0.0
        return ((new_value - old_value) / old_value) * 100