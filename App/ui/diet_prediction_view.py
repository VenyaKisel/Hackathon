import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, List

from ..models.diet import Diet
from ..services.predictor import AcidPredictor
from ..services.recommender import DietRecommender
from .widgets.diet_editor import DietEditor
from .widgets.acid_predictions import AcidPredictionDisplay
from .widgets.recommendations import RecommendationsDisplay
from ..services.excel_parser import ExcelParser


class DietPredictionView:
    """Вкладка для загрузки рациона и прогнозирования"""
    
    def __init__(self, parent, app, main_window):
        self.app = app
        self.main_window = main_window
        
        self.current_diets = [] 
        self.current_diet = None 
        
        self.predictor = AcidPredictor()
        self.recommender = DietRecommender(self.predictor)
        
        self.frame = ttk.Frame(parent, padding="10")
        self.editor_visible = True 
        self.create_widgets()
        
        self._test_model_loading()

    def _test_model_loading(self):
        """Тестирует загрузку моделей и выводит статус"""
        if hasattr(self.predictor, 'acid_models') and self.predictor.acid_models:
            print("✅ Линейные модели успешно загружены")
            print(f"📊 Загружено моделей для кислот: {len(self.predictor.acid_models)}")
            print(f"📊 Ожидаемые компоненты: {len(self.predictor.expected_components)}")
            
            print("Загруженные модели для кислот:")
            for i, acid_name in enumerate(self.predictor.acid_models.keys()):
                print(f"  {i+1}. {acid_name}")

            print("Первые 10 компонентов модели:")
            for i, comp in enumerate(self.predictor.expected_components[:10]):
                print(f"  {i+1}. {comp}")
        else:
            print("❌ Линейные модели не загружены - используются fallback предсказания")
            if hasattr(self.predictor, 'acid_models'):
                print(f"   Доступно моделей: {len(self.predictor.acid_models)}")

    def create_widgets(self):
        """Создание интерфейса вкладки"""
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        main_container.columnconfigure(0, weight=1)
        for i in range(8):
            main_container.rowconfigure(i, weight=0)
        main_container.rowconfigure(6, weight=1)
        main_container.rowconfigure(7, weight=1)
        
        title_label = ttk.Label(main_container,
                               text="Прогнозирование жирнокислотного состава молока",
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        self.create_file_section(main_container, row=1)
        self.create_diet_selection_section(main_container, row=2)
        
        self.diet_editor = DietEditor(main_container, self)
        self.diet_editor.frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))        
        self.create_editor_control_section(main_container, row=4)
        
        ttk.Button(main_container, 
                  text="Рассчитать прогноз",
                  command=self.calculate_prediction,
                  style='Accent.TButton').grid(row=5, column=0, pady=20)
        
        self.prediction_display = AcidPredictionDisplay(main_container, self)
        self.prediction_display.frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.recommendations_display = RecommendationsDisplay(main_container, self)
        self.recommendations_display.frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_editor_control_section(self, parent, row: int):
        """Секция управления видимостью редактора"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        control_frame.columnconfigure(0, weight=1)
        
        self.toggle_editor_btn = ttk.Button(
            control_frame,
            text="▲ Скрыть редактор рациона",
            command=self.toggle_editor_visibility
        )
        self.toggle_editor_btn.grid(row=0, column=0, sticky=tk.W)
        
    def toggle_editor_visibility(self):
        """Переключение видимости редактора рациона"""
        if self.editor_visible:
            self.diet_editor.frame.grid_remove()
            self.toggle_editor_btn.config(text="▼ Показать редактор рациона")
            self.editor_visible = False
        else:
            self.diet_editor.frame.grid()
            self.toggle_editor_btn.config(text="▲ Скрыть редактор рациона")
            self.editor_visible = True
        
    def create_file_section(self, parent, row: int):
        """Секция загрузки файлов рациона"""
        file_frame = ttk.LabelFrame(parent, text="Загрузка рациона", padding="10")
        file_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, 
                text="Загрузить рацион (PDF/Excel/CSV)",
                command=self.load_diet_file).grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        ttk.Button(file_frame, 
                text="Загрузить CSV с рационами",
                command=self.load_all_diets).grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        ttk.Button(file_frame,
                text="Создать новый рацион",
                command=self.create_new_diet).grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        
        self.file_status_label = ttk.Label(file_frame, text="Рацион не загружен", foreground='gray')
        self.file_status_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def create_diet_selection_section(self, parent, row: int):
        """Секция выбора рациона"""
        selection_frame = ttk.LabelFrame(parent, text="Выбор рациона", padding="10")
        selection_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        selection_frame.columnconfigure(1, weight=1)
        
        ttk.Label(selection_frame, text="Выберите рацион:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.diet_combobox = ttk.Combobox(selection_frame, state="readonly", width=30)
        self.diet_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.diet_combobox.bind('<<ComboboxSelected>>', self.on_diet_selected)
        
        ttk.Button(selection_frame,
                  text="Обновить",
                  command=self.update_diet_combobox).grid(row=0, column=2, padx=(10, 0))
    
    def on_diet_selected(self, event):
        """Обработчик выбора рациона из списка"""
        selected_index = self.diet_combobox.current()
        if 0 <= selected_index < len(self.current_diets):
            selected_diet = self.current_diets[selected_index]
            self.set_current_diet(selected_diet)
            self.update_diet_display()
            self.file_status_label.config(text=f"Выбран: {selected_diet.diet_id}")
            
    def update_diet_combobox(self):
        """Обновляет выпадающий список с рационами"""
        diet_names = [diet.name for diet in self.current_diets]
        self.diet_combobox['values'] = diet_names
        
        if self.current_diet and self.current_diet in self.current_diets:
            current_index = self.current_diets.index(self.current_diet)
            self.diet_combobox.current(current_index)
        elif self.current_diets:
            self.diet_combobox.current(0)
    
    def load_all_diets(self):
        """Загружает все рационы из CSV файла"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите CSV файл с рационами",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
                
            print(f"\n🔄 Загрузка всех рационов из: {file_path}")
            
            parser = ExcelParser()
            all_diets = parser.parse_all_diets(file_path)
            
            if all_diets:
                self.current_diets = all_diets  # Заменяем, а не добавляем
                if all_diets:
                    self.set_current_diet(all_diets[0])
                
                self.update_diet_combobox()
                self.update_diet_display()
                self.file_status_label.config(text=f"Загружено рационов: {len(all_diets)}")
                print(f"✅ Загружено {len(all_diets)} рационов")
            else:
                self.file_status_label.config(text="Ошибка загрузки файла")
                messagebox.showerror("Ошибка", "Не удалось загрузить рационы из файла")
                
        except Exception as e:
            error_msg = f"Ошибка загрузки всех рационов: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
    
    def load_diet_file(self) -> Optional[Diet]:
        """Загружает одиночный рацион"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл с рационом",
                filetypes=[
                    ("Все поддерживаемые форматы", "*.pdf *.csv *.xlsx *.xls"),
                    ("PDF files", "*.pdf"),
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return None
                
            parser = ExcelParser()            
            diet = parser.parse_diet(file_path)
            
            if diet:
                file_name = os.path.basename(file_path)
                diet.name = f"Рацион из {file_name}"
                self.current_diets.append(diet)
                self.set_current_diet(diet)
            
                self.update_diet_combobox()
                self.update_diet_display()
                self.file_status_label.config(text=f"Загружен: {file_name}")
                self.print_current_diet_info()
                return diet
            else:
                self.file_status_label.config(text="Ошибка загрузки файла")
                messagebox.showerror("Ошибка", "Не удалось загрузить рацион из файла")
                return None
                
        except Exception as e:
            error_msg = f"Ошибка загрузки файла: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
            return None
    
    def create_new_diet(self):
        """Создание нового пустого рациона"""
        from ..models.diet import DietComponent 
        
        new_diet = Diet(
            diet_id=f"diet_{len(self.current_diets) + 1}",
            name=f"Новый рацион {len(self.current_diets) + 1}",
            components={}
        )
        self.current_diets.append(new_diet)
        self.set_current_diet(new_diet)
        self.update_diet_combobox()
        self.update_diet_display()
        self.file_status_label.config(text="Создан новый рацион")
        
    def set_current_diet(self, diet: Diet):
        """Устанавливает текущий рацион"""
        self.current_diet = diet
        if hasattr(self, 'diet_editor'):
            self.diet_editor.load_diet(diet)
        
    def update_diet_display(self):
        """Обновление отображения рациона"""
        if self.current_diet and hasattr(self, 'diet_editor'):
            self.diet_editor.load_diet(self.current_diet)
            
    def calculate_prediction(self):
        """Расчет прогноза на основе текущего рациона"""
        if not self.current_diet:
            messagebox.showwarning("Внимание", "Сначала загрузите или создайте рацион")
            return
            
        try:
            if hasattr(self.main_window, 'set_status'):
                self.main_window.set_status("Расчет прогноза...")
            
            prediction_result = self.predictor.predict(self.current_diet)
            
            recommendations = self.recommender.generate_recommendations(
                self.current_diet, prediction_result)
                
            self.prediction_display.show_prediction(prediction_result)
            self.recommendations_display.show_recommendations(recommendations)
            
            if hasattr(self.main_window, 'set_status'):
                self.main_window.set_status("Прогноз рассчитан")
            
        except Exception as e:
            error_msg = f"Ошибка расчета прогноза: {str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
            
    def print_current_diet_info(self):
        """Выводит информацию о текущем рационе в терминал"""
        if not self.current_diet:
            print("Текущий рацион не установлен")
            return
            
        diet = self.current_diet
        print("\n" + "="*60)
        print(f"ID: {diet.diet_id}")
        print(f"Название: {diet.name}")
        print("\nКОМПОНЕНТЫ РАЦИОНА:")
        
        if diet.components:
            sorted_components = sorted(diet.components.items(), key=lambda x: x[0])
            for comp_name, component in sorted_components:
                print(f"   • {comp_name}: {component.amount} кг")
        else:
            print("   • Компоненты отсутствуют")
        print("="*60)
        
    def update_diet_component(self, component_name: str, new_value: float):
        """Обновление компонента рациона"""
        from ..models.diet import DietComponent  # Добавляем импорт
        
        if self.current_diet:
            if component_name in self.current_diet.components:
                self.current_diet.components[component_name].amount = new_value
            else:
                self.current_diet.components[component_name] = DietComponent(component_name, new_value)