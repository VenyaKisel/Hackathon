import os
import pickle
import numpy as np
from catboost import CatBoostRegressor
from ..models.diet import Diet
from ..models.fatty_acid import AcidPrediction, PredictionResult
from ..utils.config import AppConfig

class AcidPredictor:
    def __init__(self):
        self.MAIN_ACIDS = ['Лауриновая', 'Пальмитиновая', 'Стеариновая', 'Олеиновая']
        self.ADDITIONAL_ACIDS = ['Линолевая', 'Линоленовая']
        
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(project_root, 'app', 'models', 'catboost_acid_model.cbm')
        components_path = os.path.join(project_root, 'app', 'models', 'component_columns.pkl')
        
        print(f"Ищем модель по пути: {model_path}")
        
        try:
            self.model = CatBoostRegressor()
            self.model.load_model(model_path)
            
            with open(components_path, 'rb') as f:
                self.expected_components = pickle.load(f)
                
            print("✅ Модель CatBoost загружена")
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            self.model = None
    
    def predict(self, diet: Diet) -> PredictionResult:
        if not self.model:
            return self._generate_fallback_prediction(diet)
        
        try:
            features = self._diet_to_features(diet)
            
            predictions_array = self.model.predict(features)
            
            acid_predictions = {}
            all_acids = self.MAIN_ACIDS + self.ADDITIONAL_ACIDS
            
            for i, acid_name in enumerate(all_acids):
                if i < len(predictions_array[0]):
                    predicted_value = float(predictions_array[0][i])
                    limits = self._get_acid_limits(acid_name)
                    
                    if predicted_value < limits['min']:
                        deviation = predicted_value - limits['min'] 
                    elif predicted_value > limits['max']:
                        deviation = predicted_value - limits['max']
                    else:
                        deviation = 0.0 
                    
                    acid_predictions[acid_name] = AcidPrediction(
                        name=acid_name,
                        predicted_value=predicted_value,
                        target_min=limits['min'],
                        target_max=limits['max'],
                        deviation=deviation
                    )
            
            return PredictionResult(acids=acid_predictions)
            
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            return self._generate_fallback_prediction(diet)
    
    def _get_acid_limits(self, acid_name: str) -> dict:
        """Временная функция для получения пределов кислот"""
        limits_dict = {
            'Лауриновая': {'min': 2.0, 'max': 4.4},
            'Пальмитиновая': {'min': 21.0, 'max': 32.0},
            'Стеариновая': {'min': 8.0, 'max': 13.5},
            'Олеиновая': {'min': 20.0, 'max': 28.0},
            'Линолевая': {'min': 2.2, 'max': 5.0},
            'Линоленовая': {'min': 0, 'max': 1.5},
        }
        return limits_dict.get(acid_name, {'min': 0.0, 'max': 100.0})
    
    def _diet_to_features(self, diet: Diet) -> np.array:
        """Преобразует объект Diet в вектор фич для модели"""
        features = np.zeros(len(self.expected_components))
        
        for i, comp_name in enumerate(self.expected_components):
            if comp_name in diet.components:
                features[i] = diet.components[comp_name].amount
        
        return features.reshape(1, -1)
    
    def _generate_fallback_prediction(self, diet: Diet) -> PredictionResult:
        """Запасной вариант если модель не загрузилась"""
        acid_predictions = {}
        all_acids = self.MAIN_ACIDS + self.ADDITIONAL_ACIDS
        
        for acid_name in all_acids:
            limits = self._get_acid_limits(acid_name)
            fallback_value = (limits['min'] + limits['max']) / 2
            
            acid_predictions[acid_name] = AcidPrediction(
                name=acid_name,
                predicted_value=fallback_value,
                target_min=limits['min'],
                target_max=limits['max'],
                deviation=0.0
            )
        
        return PredictionResult(acids=acid_predictions)