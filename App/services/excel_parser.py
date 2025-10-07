import csv
import os
import pandas as pd
from typing import Dict, Optional, List
from ..models.diet import Diet, DietComponent
from ..utils.config import AppConfig

class ExcelParser:
    """Парсер для CSV и Excel файлов с рационами"""
    
    def parse_diet(self, file_path: str) -> Optional[Diet]:
        try:            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                return self._parse_rations_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                csv_path = self._excel_to_csv(file_path)
                return self._parse_rations_csv(csv_path)
            else:
                return None

        except Exception as e:
            print(f"Ошибка парсинга файла {file_path}: {e}")
            return None
    
    def _excel_to_csv(self, excel_file_path: str) -> str:
        csv_file_path = excel_file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
        df = pd.read_excel(excel_file_path)
        df.to_csv(csv_file_path, index=False, encoding='utf-8')        
        return csv_file_path
    
    def _parse_rations_csv(self, file_path: str) -> Optional[Diet]:
        """Парсит CSV файл с рационами и выводит информацию по всем ration_id"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                
                if not rows:
                    return None
                
                all_diets = []
                for i, row in enumerate(rows):
                    ration_id = row.get('ration_id', f'row_{i+1}')                    
                    diet = self._create_diet_from_rations_row(row, os.path.basename(file_path), ration_id)
                    if diet and diet.components: 
                        all_diets.append(diet)
                    
                    print("-" * 60)
                
                
                if all_diets:
                    return all_diets[0]
                else:
                    return None
                
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_diet_from_rations_row(self, data: Dict, source_name: str, ration_id: str) -> Diet:
        """Создает объект Diet из строки данных рациона"""
        
        diet_id = f"diet_{ration_id}"
        name = f"Рацион {ration_id} из {source_name}"

        components = {}
        
        print(f"КОМПОНЕНТЫ РАЦИОНА {ration_id}:")
        
        # Счетчики для статистики
        total_components = 0
        total_amount = 0.0
        
        # Проходим по всем полям кроме ration_id
        for key, value in data.items():
            if key != 'ration_id' and key:
                try:
                    amount = float(value) if value else 0.0
                    if amount > 0:
                        components[key] = DietComponent(key, amount)
                        total_components += 1
                        total_amount += amount
                        print(f" ✅ {key}: {amount} кг")
                    elif amount == 0:
                        print(f"{key}: 0 кг (пропущен)")
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️{key}: '{value}'")
        
        print(f"СТАТИСТИКА ДЛЯ RATION_ID {ration_id}:")
        print(f"   • Компонентов: {total_components}")
        print(f"   • Общий вес: {total_amount:.2f} кг")
        
        return Diet(
            diet_id=str(diet_id),
            name=str(name),
            components=components,
        )
    
    def parse_all_diets(self, file_path: str) -> List[Diet]:
        """Парсит все рационы из CSV файла и возвращает список"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                
                if not rows:
                    print("CSV файл пустой")
                    return []
                
                all_diets = []
                for i, row in enumerate(rows):
                    ration_id = row.get('ration_id', f'row_{i+1}')
                    diet = self._create_diet_from_rations_row(row, os.path.basename(file_path), ration_id)
                    if diet and diet.components:
                        all_diets.append(diet)
                
                print(f"Создано рационов: {len(all_diets)}")
                return all_diets
                
        except Exception as e:
            print(f"Ошибка парсинга всех рационов: {e}")
            return []