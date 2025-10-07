import tkinter as tk
from typing import List, Dict, Any, Optional

from .models.diet import Diet, DietComponent
from .models.fatty_acid import AcidPrediction, PredictionResult
from .utils.config import AppConfig
from .services.predictor import AcidPredictor
from .services.recommender import DietRecommender
from .services.excel_parser import ExcelParser

class CowDietApp:
    
    def __init__(self):
        self.diets: List[Diet] = []
        self.current_diet: Optional[Diet] = None
        self.predictor = AcidPredictor()
        self.recommender = DietRecommender()
        self.current_prediction: Optional[PredictionResult] = None
        
    def load_all_diets_from_csv(self, file_path: str) -> List[Diet]:
        """Загружает все рационы из CSV файла"""
        try:
            parser = ExcelParser()
            all_diets = parser.parse_all_diets(file_path)
            
            if all_diets:
                self.diets = all_diets
                if all_diets:
                    self.set_current_diet(all_diets[0])
                return all_diets
            return []
            
        except Exception as e:
            print(f"Ошибка загрузки всех рационов: {e}")
            return []
    
    def get_diet_by_id(self, diet_id: str) -> Optional[Diet]:
        """Находит рацион по ID"""
        for diet in self.diets:
            if diet.diet_id == diet_id:
                return diet
        return None
    
    def get_diet_ids(self) -> List[str]:
        """Возвращает список всех ID рационов"""
        return [diet.diet_id for diet in self.diets]
    
    def get_diet_display_names(self) -> List[str]:
        """Возвращает список имен для отображения в выпадающем списке"""
        return [f"{diet.diet_id} - {diet.name}" for diet in self.diets]
    
    def set_current_diet_by_id(self, diet_id: str) -> bool:
        """Устанавливает текущий рацион по ID"""
        diet = self.get_diet_by_id(diet_id)
        if diet:
            self.current_diet = diet
            return True
        return False
    
    def load_diet_from_file(self, file_path: str) -> Optional[Diet]:
        """
        Загружает данные рациона из Excel
        """
        try:
            csv_parser = ExcelParser()
            diet = csv_parser.parse_diet_from_csv(file_path)
            
            if diet:
                diet.name = f"Рацион из {os.path.basename(file_path)}"
                self.set_current_diet(diet)
            return diet
            
        except Exception as e:
            print(f"Ошибка загрузки Excel: {e}")
            return None
    
    def create_new_diet(self) -> Diet:
        """Создает новый пустой рацион"""
        diet = Diet()
        diet.diet_id = f"new_{len(self.diets) + 1}"
        diet.name = "Новый рацион"
        self.set_current_diet(diet)
        return diet
    
    def set_current_diet(self, diet: Diet):
        """Устанавливает текущий рацион"""
        existing_diet = self.get_diet_by_id(diet.diet_id)
        if not existing_diet:
            self.diets.append(diet)
        else:
            index = self.diets.index(existing_diet)
            self.diets[index] = diet
            
        self.current_diet = diet
    
    def predict_acids(self, diet: Optional[Diet] = None) -> PredictionResult:
        """Прогнозирует жирнокислотный состав для рациона"""
        target_diet = diet or self.current_diet
        if not target_diet:
            raise ValueError("Не задан рацион для прогнозирования")
        
        prediction = self.predictor.predict(target_diet)
        self.current_prediction = prediction
        return prediction
    
    def get_recommendations(self, diet: Optional[Diet] = None, 
                          prediction: Optional[PredictionResult] = None) -> List[str]:
        """Получает рекомендации для рациона"""
        target_diet = diet or self.current_diet
        target_prediction = prediction or self.current_prediction
        
        if not target_diet or not target_prediction:
            return ["Загрузите рацион и выполните прогнозирование для получения рекомендаций"]
        
        return self.recommender.generate_recommendations(target_diet, target_prediction)
    
    def update_diet_component(self, diet: Diet, component_name: str, new_value: float):
        """Обновляет компонент рациона"""
        if component_name in diet.components:
            diet.components[component_name].amount = new_value
    
    def get_acid_targets(self, acid_name: str) -> Dict[str, float]:
        """Возвращает целевые значения для кислоты"""
        return AppConfig.get_acid_targets(acid_name)
    
    def get_main_acids(self) -> List[str]:
        """Возвращает список основных кислот"""
        return AppConfig.MAIN_ACIDS
    
    def get_additional_acids(self) -> List[str]:
        """Возвращает список дополнительных кислот"""
        return AppConfig.ADDITIONAL_ACIDS
    
    def get_all_acids(self) -> List[str]:
        """Возвращает все кислоты"""
        return AppConfig.MAIN_ACIDS + AppConfig.ADDITIONAL_ACIDS
    
    def get_standard_components(self) -> List[str]:
        """Возвращает стандартные компоненты рациона"""
        return AppConfig.STANDARD_COMPONENTS
    
    def get_nutrition_indicators(self) -> List[str]:
        """Возвращает показатели питательности"""
        return AppConfig.NUTRITION_INDICATORS