import csv
import os
import re
import pandas as pd
from typing import Dict, Optional, List, Union, Tuple
from ..models.diet import Diet, DietComponent

class ExcelParser:
    """Парсер для CSV, Excel и PDF файлов с рационами"""
    
    def parse_diet(self, file_path: str) -> Optional[Diet]:
        """Парсит один рацион из файла (первый найденный)"""
        try:            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                return self._parse_single_diet_from_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                csv_path = self._excel_to_csv(file_path)
                return self._parse_single_diet_from_csv(csv_path)
            elif file_ext == '.pdf':
                # Для PDF пытаемся несколько способов
                result = self._parse_pdf_single(file_path)
                if result:
                    return result
                else:
                    # Fallback: конвертируем в CSV
                    csv_path = self._pdf_to_csv(file_path)
                    if csv_path:
                        return self._parse_single_diet_from_csv(csv_path)
                    return None
            else:
                print(f"❌ Неподдерживаемый формат файла: {file_ext}")
                return None

        except Exception as e:
            print(f"❌ Ошибка парсинга файла {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_all_diets(self, file_path: str) -> List[Diet]:
        """Парсит все рационы из файла"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                return self._parse_all_diets_from_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                csv_path = self._excel_to_csv(file_path)
                return self._parse_all_diets_from_csv(csv_path)
            elif file_ext == '.pdf':
                return self._parse_pdf_all(file_path)
            else:
                print(f"❌ Неподдерживаемый формат файла: {file_ext}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка парсинга всех рационов из {file_path}: {e}")
            return []
    
    def _parse_single_diet_from_csv(self, file_path: str) -> Optional[Diet]:
        """Парсит первый рацион из CSV файла"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                
                if not rows:
                    print("ℹ️ Файл пустой")
                    return None
                
                # Берем первую строку
                first_row = rows[0]
                ration_id = first_row.get('ration_id', '1')
                diet = self._create_diet_from_row(first_row, os.path.basename(file_path), ration_id)
                
                if diet and diet.components:
                    print(f"✅ Успешно создан рацион с {len(diet.components)} компонентами")
                    return diet
                else:
                    print("⚠️ Не удалось создать рацион из данных")
                    return None
                    
        except Exception as e:
            print(f"❌ Ошибка парсинга CSV: {e}")
            return None
    
    def _parse_all_diets_from_csv(self, file_path: str) -> List[Diet]:
        """Парсит все рационы из CSV файла"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                
                if not rows:
                    print("ℹ️ Файл пустой")
                    return []
                
                all_diets = []
                for i, row in enumerate(rows):
                    ration_id = row.get('ration_id', f'row_{i+1}')
                    diet = self._create_diet_from_row(row, os.path.basename(file_path), ration_id)
                    if diet and diet.components:
                        all_diets.append(diet)
                        print(f"✅ Рацион {ration_id}: {len(diet.components)} компонентов")
                
                print(f"📊 Создано рационов: {len(all_diets)}")
                return all_diets
                
        except Exception as e:
            print(f"❌ Ошибка парсинга всех рационов: {e}")
            return []
    
    def _parse_pdf_single(self, pdf_path: str) -> Optional[Diet]:
        """Парсит один рацион из PDF файла нового формата"""
        try:
            # Пытаемся несколько способов парсинга
            result = self._parse_nds_pdf_format(pdf_path)
            if result:
                return result
            
            # Fallback на существующие методы
            return self._parse_pdf_tables_fallback(pdf_path)
            
        except Exception as e:
            print(f"❌ Ошибка парсинга PDF {pdf_path}: {e}")
            return None

    def _parse_nds_pdf_format(self, pdf_path: str) -> Optional[Diet]:
        """Парсит NDS Professional формат PDF"""
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                if not full_text:
                    return None
                
                # Парсим ингредиенты из текста
                components = self._extract_components_from_nds_text(full_text)
                
                if components:
                    return Diet(
                        diet_id=f"diet_{os.path.basename(pdf_path)}",
                        name=f"Рацион из {os.path.basename(pdf_path)}",
                        components=components
                    )
                
                return None
                
        except Exception as e:
            print(f"❌ Ошибка парсинга NDS формата: {e}")
            return None

    def _extract_components_from_nds_text(self, text: str) -> Dict[str, DietComponent]:
        """Извлекает компоненты из текста NDS формата"""
        components = {}
        
        # Разделяем текст на строки
        lines = text.split('\n')
        
        # Ищем начало таблицы ингредиентов
        start_index = -1
        for i, line in enumerate(lines):
            if 'Ингредиенты' in line:
                start_index = i
                break
        
        if start_index == -1:
            print("❌ Не найдена таблица ингредиентов")
            return {}
        
        # Парсим ингредиенты - ищем строки с данными после заголовка
        i = start_index + 1
        while i < len(lines):
            line = lines[i].strip()
            
            # Пропускаем пустые строки и заголовки столбцов
            if not line or any(keyword in line for keyword in ['СВ %', 'ГП кг', 'СВ кг', '% ГП', '% СВ', '₽/Tonne']):
                i += 1
                continue
            
            # Пытаемся извлечь данные ингредиента
            ingredient_data = self._parse_ingredient_line(lines, i)
            if ingredient_data:
                name, amount = ingredient_data
                if name and amount > 0:
                    components[name] = DietComponent(name, amount)
                    print(f"✅ Извлечен ингредиент: {name} - {amount} кг")
                i += 7  # Пропускаем блок данных (название + 6 строк данных)
            else:
                i += 1
        
        return components

    def _parse_ingredient_line(self, lines: List[str], start_idx: int) -> Optional[Tuple[str, float]]:
        """Парсит блок данных ингредиента"""
        try:
            if start_idx + 6 >= len(lines):
                return None
            
            # Первая строка - название ингредиента
            name = lines[start_idx].strip()
            
            # Вторая строка - СВ %, третья - ГП кг (нам нужна эта)
            amount_line = lines[start_idx + 2].strip()  # ГП кг
            
            # Очищаем и конвертируем количество
            amount_str = amount_line.replace(',', '.').replace(' ', '')
            amount = float(amount_str)
            
            # Проверяем валидность названия (должно содержать буквы или быть кодом)
            if not self._is_valid_ingredient_name(name):
                return None
                
            return name, amount
            
        except (ValueError, IndexError, AttributeError):
            return None

    def _is_valid_ingredient_name(self, name: str) -> bool:
        """Проверяет, является ли строка валидным названием ингредиента"""
        if not name or len(name.strip()) < 2:
            return False
        
        # Исключаем явно неингредиентные строки
        excluded_keywords = ['СВ %', 'ГП кг', 'СВ кг', '% ГП', '% СВ', '₽/Tonne', 
                           'Общие значения', 'Стоимость', 'Нутриент', 'Единица']
        
        if any(keyword in name for keyword in excluded_keywords):
            return False
        
        # Должны быть либо буквы, либо код вида "XXXX.XX.XX.XX.XX"
        if re.match(r'^[а-яА-Яa-zA-Z]', name) or re.match(r'^\d+\.\d+\.\d+\.\d+\.\d+', name):
            return True
            
        return False

    def _parse_pdf_tables_fallback(self, pdf_path: str) -> Optional[Diet]:
        """Резервный метод парсинга через извлечение таблиц"""
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            diet = self._parse_nds_table(table)
                            if diet:
                                return diet
            return None
            
        except Exception as e:
            print(f"❌ Ошибка резервного парсинга PDF: {e}")
            return None

    def _parse_nds_table(self, table: List[List[str]]) -> Optional[Diet]:
        """Парсит таблицу в NDS формате"""
        components = {}
        
        for row in table:
            if len(row) >= 3 and row[0] and self._is_valid_ingredient_name(str(row[0])):
                try:
                    name = str(row[0]).strip()
                    # Пытаемся найти количество в различных столбцах
                    amount = self._find_amount_in_row(row)
                    if amount > 0:
                        components[name] = DietComponent(name, amount)
                except (ValueError, TypeError):
                    continue
        
        if components:
            return Diet(
                diet_id="diet_from_table",
                name="Рацион из таблицы",
                components=components
            )
        
        return None

    def _find_amount_in_row(self, row: List[str]) -> float:
        """Находит количество ингредиента в строке таблицы"""
        for cell in row[1:4]:  # Проверяем столбцы 1-3
            if cell:
                try:
                    amount_str = str(cell).replace(',', '.').replace(' ', '').strip()
                    return float(amount_str)
                except (ValueError, TypeError):
                    continue
        return 0.0

    def _parse_pdf_all(self, pdf_path: str) -> List[Diet]:
        """Парсит все рационы из PDF файла"""
        diet = self._parse_pdf_single(pdf_path)
        return [diet] if diet else []
    
    def _create_diet_from_row(self, data: Dict, source_name: str, ration_id: str) -> Diet:
        """Создает объект Diet из строки данных"""
        diet_id = f"diet_{ration_id}"
        name = f"Рацион {ration_id} из {source_name}"
        components = {}
        
        print(f"📋 Компоненты рациона {ration_id}:")
        total_components = 0
        total_amount = 0.0
        
        for key, value in data.items():
            if key != 'ration_id' and key:
                try:
                    amount = float(value) if value and str(value).strip() else 0.0
                    if amount > 0:
                        components[key] = DietComponent(key, amount)
                        total_components += 1
                        total_amount += amount
                        print(f"  ✅ {key}: {amount} кг")
                except (ValueError, TypeError):
                    print(f"  ⚠️ {key}: '{value}' (не число)")
        
        print(f"📊 Статистика для ration_id {ration_id}:")
        print(f"   • Компонентов: {total_components}")
        print(f"   • Общий вес: {total_amount:.2f} кг")
        
        return Diet(
            diet_id=str(diet_id),
            name=str(name),
            components=components,
        )
    
    def _excel_to_csv(self, excel_file_path: str) -> str:
        """Конвертирует Excel в CSV"""
        csv_file_path = excel_file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
        df = pd.read_excel(excel_file_path)
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print(f"✅ Excel сконвертирован в: {csv_file_path}")
        return csv_file_path
    
    def _pdf_to_csv(self, pdf_file_path: str) -> Optional[str]:
        """Конвертирует PDF в CSV (резервный метод)"""
        try:
            import pdfplumber
            
            csv_file_path = pdf_file_path.replace('.pdf', '_converted.csv')
            
            print(f"🔄 Конвертируем PDF в CSV...")
            
            with pdfplumber.open(pdf_file_path) as pdf:
                all_tables = []
                
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            all_tables.extend(table)
                
                if all_tables:
                    with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(all_tables)
                    
                    print(f"✅ PDF успешно конвертирован в: {csv_file_path}")
                    return csv_file_path
                else:
                    print("❌ В PDF не найдено табличных данных")
                    return None
                    
        except ImportError:
            print("❌ Для работы с PDF установите: pip install pdfplumber")
            return None
        except Exception as e:
            print(f"❌ Ошибка конвертации PDF: {e}")
            return None

    def parse_pdf_directories(self, root_directories, output_dir=None) -> Dict:
        """Парсит PDF файлы из директорий включая NDS формат"""
        results = {
            'diets': [],
            'statistics': {
                'total_files': 0,
                'successful_parses': 0,
                'failed_parses': 0
            }
        }
        
        try:
            for root_dir in root_directories:
                for file_path in self._find_pdf_files(root_dir):
                    results['statistics']['total_files'] += 1
                    
                    diet = self._parse_pdf_single(file_path)
                    if diet:
                        results['diets'].append(diet)
                        results['statistics']['successful_parses'] += 1
                        print(f"✅ Успешно распарсен: {os.path.basename(file_path)}")
                    else:
                        results['statistics']['failed_parses'] += 1
                        print(f"❌ Не удалось распарсить: {os.path.basename(file_path)}")
            
            return results
            
        except Exception as e:
            print(f"❌ Ошибка обработки PDF директорий: {e}")
            return results

    def _find_pdf_files(self, directory: str) -> List[str]:
        """Находит все PDF файлы в директории"""
        pdf_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files