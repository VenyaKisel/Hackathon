import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Optional

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
        self.predictor = AcidPredictor()
        self.recommender = DietRecommender()        
        self.frame = ttk.Frame(parent, padding="10")
        self.editor_visible = True 
        self.create_widgets()
        
    def create_widgets(self):
        """Создание интерфейса вкладки"""
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=0) 
        main_container.rowconfigure(1, weight=0)  
        main_container.rowconfigure(2, weight=0)  
        main_container.rowconfigure(3, weight=0) 
        main_container.rowconfigure(4, weight=0) 
        main_container.rowconfigure(5, weight=0) 
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
        
        main_container.rowconfigure(6, weight=2) 
        main_container.rowconfigure(7, weight=1)  
        
        
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
            
            self._update_row_weights(hide_editor=True)
        else:
            self.diet_editor.frame.grid()  
            self.toggle_editor_btn.config(text="▲ Скрыть редактор рациона")
            self.editor_visible = True
            
            self._update_row_weights(hide_editor=False)
    def _update_row_weights(self, hide_editor: bool):
        """Обновление весов строк при скрытии/показе редактора"""
        main_container = self.diet_editor.frame.master
        
        if hide_editor:
            main_container.rowconfigure(6, weight=3)  
            main_container.rowconfigure(7, weight=2) 
        else:
            main_container.rowconfigure(6, weight=2) 
            main_container.rowconfigure(7, weight=1) 
    def create_file_section(self, parent, row: int):
        """Секция загрузки файлов рациона"""
        file_frame = ttk.LabelFrame(parent, text="Загрузка рациона", padding="10")
        file_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, 
                  text="Загрузить CSV с рационами",
                  command=self.load_all_diets).grid(row=0, column=0, padx=(0, 10))
     
        ttk.Button(file_frame,
                  text="Создать новый рацион",
                  command=self.create_new_diet).grid(row=0, column=1, padx=(0, 10))
        
        self.file_status_label = ttk.Label(file_frame, text="Рацион не загружен", foreground='gray')
        self.file_status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
    def create_diet_selection_section(self, parent, row: int):
        """Секция выбора рациона"""
        selection_frame = ttk.LabelFrame(parent, text="Выбор рациона", padding="10")
        selection_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        selection_frame.columnconfigure(1, weight=1)
        
        ttk.Label(selection_frame, text="Выберите рацион:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.diet_combobox = ttk.Combobox(selection_frame, state="readonly")
        self.diet_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.diet_combobox.bind('<<ComboboxSelected>>', self.on_diet_selected)
        
        ttk.Button(selection_frame,
                  text="Обновить",
                  command=self.update_diet_combobox).grid(row=0, column=2, padx=(10, 0))
    
    def on_diet_selected(self, event):
        """Обработчик выбора рациона из списка"""
        selected_index = self.diet_combobox.current()
        if selected_index >= 0 and selected_index < len(self.app.diets):
            selected_diet = self.app.diets[selected_index]
            self.app.set_current_diet(selected_diet)
            self.update_diet_display()
            self.file_status_label.config(text=f"Выбран: {selected_diet.diet_id}")
            
    def update_diet_combobox(self):
        """Обновляет выпадающий список с рационами"""
        diet_names = self.app.get_diet_display_names()
        self.diet_combobox['values'] = diet_names
        
        if self.app.current_diet and self.app.current_diet in self.app.diets:
            current_index = self.app.diets.index(self.app.current_diet)
            self.diet_combobox.current(current_index)
    
    def load_all_diets(self):
        """Загружает все рационы из CSV файла"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите CSV файл с рационами",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if not file_path:
                return
                
            print(f"\n🔄 Загрузка всех рационов из: {file_path}")
            
            all_diets = self.app.load_all_diets_from_csv(file_path)
            
            if all_diets:
                self.update_diet_combobox()
                self.update_diet_display()
                self.file_status_label.config(text=f"Загружено рационов: {len(all_diets)}")
                print(f"✅ Загружено {len(all_diets)} рационов")
            else:
                self.file_status_label.config(text="Ошибка загрузки файла")
                print("❌ Не удалось загрузить рационы")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки всех рационов: {e}")
            import traceback
            traceback.print_exc()
    
    def load_diet_file(self) -> Optional[Diet]:
        """Загружает одиночный рацион (для обратной совместимости)"""
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
                self.app.set_current_diet(diet)
                self.update_diet_combobox()
                self.update_diet_display()
                self.file_status_label.config(text=f"Загружен: {file_name}")
                self.print_current_diet_info()
                return diet
            else:
                self.file_status_label.config(text="Ошибка загрузки файла")
                return None
                
        except Exception as e:
            print(f"ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_new_diet(self):
        """Создание нового пустого рациона"""
        diet = self.app.create_new_diet()
        self.update_diet_combobox()
        self.update_diet_display()
        self.file_status_label.config(text="Создан новый рацион")
        
    def update_diet_display(self):
        """Обновление отображения рациона"""
        if self.app.current_diet:
            self.diet_editor.load_diet(self.app.current_diet)
            
    def calculate_prediction(self):
        """Расчет прогноза на основе текущего рациона"""
        if not self.app.current_diet:
            self.main_window.show_info("Внимание", "Сначала загрузите или создайте рацион")
            return
            
        try:
            self.main_window.set_status("Расчет прогноза...")
            
            prediction_result = self.predictor.predict(self.app.current_diet)
            
            recommendations = self.recommender.generate_recommendations(
                self.app.current_diet, prediction_result)
                
            self.prediction_display.show_prediction(prediction_result)
            self.recommendations_display.show_recommendations(recommendations)
            
            self.main_window.set_status("Прогноз рассчитан")
            
        except Exception as e:
            self.main_window.show_error("Ошибка", f"Ошибка расчета: {str(e)}")
            
    def print_current_diet_info(self):
        """Выводит информацию о текущем рационе в терминал"""
        diet = self.app.current_diet
        print("\n" + "="*60)
        print(f"ID: {diet.diet_id}")
        print(f"Название: {diet.name}")
        print("\nКОМПОНЕНТЫ РАЦИОНА:")
        
        if diet.components:
            sorted_components = sorted(diet.components.items(), key=lambda x: x[0])
            for comp_name, component in sorted_components:
                print(f"   • {comp_name}: {component.amount} кг")
        print("="*60)
        print()
        
    def update_diet_component(self, component_name: str, new_value: float):
        """Обновление компонента рациона"""
        if self.app.current_diet:
            self.app.current_diet.update_component(component_name, new_value)