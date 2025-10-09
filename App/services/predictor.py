# services/predictor.py
import os
import pickle
import numpy as np
from typing import Dict, List
from ..models.diet import Diet
from ..models.fatty_acid import AcidPrediction, PredictionResult

class LinearAcidPredictor:
    def __init__(self):
        self.ALL_ACIDS = self._discover_available_acids()

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(project_root, 'app', 'models', 'linear_models')
        components_path = os.path.join(project_root, 'app', 'models', 'component_columns.pkl')
        
        print(f"Ищем линейные модели в: {models_dir}")
        
        self.acid_models: Dict[str, object] = {}
        
        try:
            with open(components_path, 'rb') as f:
                self.expected_components = pickle.load(f)
                
            for acid_name in self.ALL_ACIDS:
                model_path = os.path.join(models_dir, f'{acid_name}_model.pkl')
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.acid_models[acid_name] = pickle.load(f)
                    print(f"✅ Модель для {acid_name} загружена")
                else:
                    print(f"⚠️ Модель для {acid_name} не найдена: {model_path}")
            
            print(f"✅ Загружено {len(self.acid_models)} линейных моделей")
            
            self._check_model_dimensions()
            
        except Exception as e:
            print(f"❌ Ошибка загрузки моделей: {e}")
            self.acid_models = {}
            self.expected_components = []

    def _check_model_dimensions(self):
        """Проверяет размерности загруженных моделей"""
        print("\n🔍 ПРОВЕРКА РАЗМЕРНОСТЕЙ МОДЕЛЕЙ:")
        for acid_name, model in self.acid_models.items():
            if hasattr(model, 'coef_'):
                expected_features = len(model.coef_)
                print(f"  {acid_name}: ожидает {expected_features} признаков")
            else:
                print(f"  {acid_name}: не удалось определить размерность")

    def predict(self, diet: Diet) -> PredictionResult:
        """Прогнозирует уровни всех кислот с использованием отдельных линейных моделей"""
        if not self.acid_models:
            return self._generate_fallback_prediction(diet)
        
        try:
            acid_predictions = {}
            
            for acid_name in self.ALL_ACIDS:
                if acid_name in self.acid_models:
                    model = self.acid_models[acid_name]
                    
                    features = self._diet_to_features_for_model(diet, model, acid_name)
                    
                    predicted_value = float(model.predict(features)[0])
                    
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
                    print(f"✅ {acid_name}: {predicted_value:.2f}%")
                    
                else:
                    # Если модель для кислоты не загружена, используем fallback
                    acid_predictions[acid_name] = self._create_fallback_prediction(acid_name)
                    print(f"⚠️ Для кислоты {acid_name} использовано fallback предсказание")
            
            return PredictionResult(acids=acid_predictions)
            
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_fallback_prediction(diet)
        
    def get_available_acids(self) -> List[str]:
        """Возвращает список кислот, для которых есть модели"""
        return list(self.acid_models.keys())

    def _diet_to_features_for_model(self, diet: Diet, model, acid_name: str) -> np.array:
        """Преобразует Diet в фичи для конкретной модели - УПРОЩЕННАЯ ВЕРСИЯ"""
        features_order = [
            'трав_сен', 'конц_зерн', 'масличн', 'жир', 'пром_отх', 
            'мин_техно', 'сп', 'крахмал', 'andfom', 'сахар (вру)', 
            'нву', 'ожк', 'k'
        ]
        
        features = np.zeros(13)
        
        print(f"🔍 Преобразование для {acid_name}:")
        print(f"   Компоненты в рационе: {list(diet.components.keys())}")
        
        for i, feature_name in enumerate(features_order):
            if feature_name in diet.components:
                amount = diet.components[feature_name].amount
                features[i] = amount
                print(f"   ✅ {feature_name}: {amount:.2f}")
            else:
                print(f"   ❌ {feature_name}: 0.0")
        
        if hasattr(model, 'coef_'):
            expected_features = len(model.coef_)
            if expected_features < 13:
                features = features[:expected_features]
                print(f"🔧 Обрезано до {expected_features} признаков для модели")
        
        print(f"📊 Итоговый вектор: {features}")
        return features.reshape(1, -1)
    def predict_single_acid(self, acid_name: str, diet: Diet) -> AcidPrediction:
        """Прогнозирует уровень только одной конкретной кислоты"""
        if acid_name not in self.acid_models:
            return self._create_fallback_prediction(acid_name)
        
        try:
            model = self.acid_models[acid_name]
            features = self._diet_to_features_for_model(diet, model, acid_name)
            predicted_value = float(model.predict(features)[0])
            
            limits = self._get_acid_limits(acid_name)
            
            if predicted_value < limits['min']:
                deviation = predicted_value - limits['min'] 
            elif predicted_value > limits['max']:
                deviation = predicted_value - limits['max']
            else:
                deviation = 0.0
            
            return AcidPrediction(
                name=acid_name,
                predicted_value=predicted_value,
                target_min=limits['min'],
                target_max=limits['max'],
                deviation=deviation
            )
            
        except Exception as e:
            print(f"❌ Ошибка предсказания для {acid_name}: {e}")
            return self._create_fallback_prediction(acid_name)
    def get_available_acids(self) -> List[str]:
        """Возвращает список кислот, для которых есть модели"""
        return list(self.acid_models.keys())

    def _get_acid_limits(self, acid_name: str) -> dict:
        """Функция для получения пределов кислот"""
        limits_dict = {
            'Масляная': {'min': 2.4, 'max': 4.2},
            'Капроновая': {'min': 1.5, 'max': 3.0},
            'Каприловая': {'min': 1.0, 'max': 2.0},
            'Каприновая': {'min': 2.0, 'max': 3.8},
            'Деценовая': {'min': 0.2, 'max': 0.4},
            'Лауриновая': {'min': 2.0, 'max': 4.4},
            'Миристиновая': {'min': 8.0, 'max': 13.0},
            'Миристолеиновая': {'min': 0.6, 'max': 1.5},
            'Пальмитиновая': {'min': 21.0, 'max': 32.0},
            'Пальмитолеиновая': {'min': 1.3, 'max': 2.4},
            'Стеариновая': {'min': 8.0, 'max': 13.5},
            'Олеиновая': {'min': 20.0, 'max': 28.0},
            'Линолевая': {'min': 2.2, 'max': 5.0},
            'Линоленовая': {'min': 0, 'max': 1.5},
            'Арахиновая': {'min': 0, 'max': 0.3},
            'Бегеновая': {'min': 0, 'max': 0.1},
            'Прочие': {'min': 4.5, 'max': 6.5}
        }
        return limits_dict.get(acid_name, {'min': 0.0, 'max': 100.0})
    
    def _create_fallback_prediction(self, acid_name: str) -> AcidPrediction:
        """Создает fallback предсказание для одной кислоты"""
        limits = self._get_acid_limits(acid_name)
        fallback_value = (limits['min'] + limits['max']) / 2
        
        return AcidPrediction(
            name=acid_name,
            predicted_value=fallback_value,
            target_min=limits['min'],
            target_max=limits['max'],
            deviation=0.0
        )
    
    def _generate_fallback_prediction(self, diet: Diet) -> PredictionResult:
        """Запасной вариант если модели не загрузились"""
        acid_predictions = {}
        
        for acid_name in self.ALL_ACIDS:
            acid_predictions[acid_name] = self._create_fallback_prediction(acid_name)
        
        print("⚠️ Использовано fallback предсказание для всех кислот")
        return PredictionResult(acids=acid_predictions)
    
    def test_prediction(self, diet: Diet) -> PredictionResult:
        """Тестирует предсказание и выводит детальную информацию"""
        print("\n🧪 ТЕСТИРОВАНИЕ ПРЕДСКАЗАНИЯ (Линейные модели)")
        print("=" * 50)
        
        result = self.predict(diet)
        
        print(f"📊 РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЯ:")
        for acid_name, prediction in result.acids.items():
            status = "✅ В норме" if prediction.is_within_target else "❌ Требует коррекции"
            model_status = "✅ Модель" if acid_name in self.acid_models else "⚠️ Fallback"
            print(f"   {acid_name}: {prediction.predicted_value:.2f}% ({status}) [{model_status}]")
            if not prediction.is_within_target:
                print(f"     Отклонение: {prediction.deviation:+.2f}%")
        
        return result
    def _discover_available_acids(self) -> List[str]:
        """Автоматически обнаруживает все доступные кислоты из папки моделей"""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(project_root, 'app', 'models', 'linear_models')
        
        if not os.path.exists(models_dir):
            print(f"❌ Папка с моделями не найдена: {models_dir}")
            return []
        
        model_files = [f for f in os.listdir(models_dir) if f.endswith('_model.pkl')]
        
        acids = []
        for filename in model_files:
            acid_name = filename.replace('_model.pkl', '')
            acids.append(acid_name)
        
        print(f"🔍 Обнаружено моделей для кислот: {len(acids)}")
        for acid in acids:
            print(f"   - {acid}")
        
        return acids
AcidPredictor = LinearAcidPredictor