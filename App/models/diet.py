from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DietComponent:
    """Компонент рациона"""
    name: str
    amount: float  # в кг
    unit: str = "кг"

@dataclass 
class Diet:
    """Модель рациона коровы"""
    diet_id: str
    name: str
    components: Dict[str, DietComponent]
    
    def to_dict(self) -> dict:
        """Для отображения в таблице"""
        data = {'diet_id': self.diet_id, 'name': self.name}
        
        # Компоненты
        for comp_name, component in self.components.items():
            data[f'comp_{comp_name}'] = component.amount
            
        return data
    
    def update_component(self, component_name: str, amount: float):
        """Обновление компонента"""
        if component_name in self.components:
            self.components[component_name].amount = amount