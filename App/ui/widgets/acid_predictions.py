import tkinter as tk
from tkinter import ttk
from ...models.fatty_acid import PredictionResult

class AcidPredictionDisplay:
    def __init__(self, parent, view):
        self.view = view
        
        self.frame = ttk.LabelFrame(parent, text="Прогноз жирных кислот", padding="10")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        self.create_scrollable_area()
        
    def create_scrollable_area(self):
        """Создает прокручиваемую область для отображения прогнозов"""
        container = ttk.Frame(self.frame)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(container, height=200)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.prediction_widgets = {}
    
    def show_prediction(self, prediction_result: PredictionResult):
        """Отображает прогноз жирных кислот"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.prediction_widgets.clear()
        
        if not prediction_result.acids:
            ttk.Label(self.scrollable_frame, text="Нет данных для отображения").grid(row=0, column=0, sticky=tk.W)
            return
        
        ttk.Label(self.scrollable_frame, text="Кислота", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=(0, 10))
        ttk.Label(self.scrollable_frame, text="Прогноз %", font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=(0, 10))
        ttk.Label(self.scrollable_frame, text="Целевой диапазон", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 20), pady=(0, 10))
        ttk.Label(self.scrollable_frame, text="Статус", font=('Arial', 10, 'bold')).grid(row=0, column=3, sticky=tk.W, pady=(0, 10))
        
        sorted_acids = sorted(prediction_result.acids.items(), key=lambda x: x[0])
        
        for i, (acid_name, acid_pred) in enumerate(sorted_acids, start=1):
            name_label = ttk.Label(self.scrollable_frame, text=acid_name)
            name_label.grid(row=i, column=0, sticky=tk.W, padx=(0, 20), pady=5)
            
            value_label = ttk.Label(self.scrollable_frame, text=f"{acid_pred.predicted_value:.2f}%")
            value_label.grid(row=i, column=1, sticky=tk.W, padx=(0, 20), pady=5)
            
            range_label = ttk.Label(self.scrollable_frame, text=f"{acid_pred.target_min}-{acid_pred.target_max}%")
            range_label.grid(row=i, column=2, sticky=tk.W, padx=(0, 20), pady=5)
            
            status_text = acid_pred.status
            if status_text == "в норме":
                status_color = "green"
            elif status_text == "ниже нормы":
                status_color = "orange"
            else:
                status_color = "red"
                
            status_label = ttk.Label(self.scrollable_frame, text=status_text, foreground=status_color)
            status_label.grid(row=i, column=3, sticky=tk.W, pady=5)
            
            self.prediction_widgets[acid_name] = {
                'name_label': name_label,
                'value_label': value_label,
                'range_label': range_label,
                'status_label': status_label
            }
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))