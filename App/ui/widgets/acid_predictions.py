# gui/widgets/acid_predictions.py
import tkinter as tk
from tkinter import ttk
from typing import Dict
from ...models.fatty_acid import AcidPrediction, PredictionResult

class AcidPredictionDisplay:
    def __init__(self, parent, controller):
        self.controller = controller
        self.frame = ttk.LabelFrame(parent, text="Результаты прогнозирования", padding="10")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(self.frame, columns=('acid', 'value', 'target', 'status'), show='headings', height=8)
        self.tree.heading('acid', text='Жирная кислота')
        self.tree.heading('value', text='Предсказание, %')
        self.tree.heading('target', text='Целевой диапазон')
        self.tree.heading('status', text='Статус')
        
        self.tree.column('acid', width=150)
        self.tree.column('value', width=120)
        self.tree.column('target', width=120)
        self.tree.column('status', width=100)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def show_prediction(self, prediction_result: PredictionResult):
        """Показывает результаты предсказания"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not prediction_result or not prediction_result.acids:
            self.tree.insert('', 'end', values=('Нет данных', '', '', ''))
            return
        
        for acid_name, acid_pred in prediction_result.acids.items():
            if acid_pred.is_within_target:
                status_text = "✅ В норме"
                status_color = 'green'
            else:
                if acid_pred.predicted_value < acid_pred.target_min:
                    status_text = "❌ Ниже нормы"
                else:
                    status_text = "❌ Выше нормы"
                status_color = 'red'
            
            target_range = f"{acid_pred.target_min:.1f}-{acid_pred.target_max:.1f}%"
            
            item_id = self.tree.insert('', 'end', values=(
                acid_name,
                f"{acid_pred.predicted_value:.2f}%",
                target_range,
                status_text
            ))
            
            if not acid_pred.is_within_target:
                self.tree.set(item_id, 'status', status_text)