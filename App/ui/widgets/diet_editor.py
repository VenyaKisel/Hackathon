import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from ...models.diet import Diet, DietComponent

class DietEditor:
    def __init__(self, parent, view):
        self.view = view
        self.current_diet = None
        
        self.frame = ttk.LabelFrame(parent, text="Редактор рациона", padding="10")
        self.frame.columnconfigure(1, weight=1)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов редактора"""
        title_label = ttk.Label(self.frame, text="Состав рациона (кг)", font=('Arial', 10, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        self.create_scrollable_components()
        
        # Статус
        self.status_label = ttk.Label(self.frame, text="Рацион не загружен", foreground='gray')
        self.status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def create_scrollable_components(self):
        """Создает прокручиваемую область для компонентов"""
        container = ttk.Frame(self.frame)
        container.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(container, height=200)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.component_widgets = {}
    
    def load_diet(self, diet: Diet):
        """Загружает рацион в редактор"""
        self.current_diet = diet
        self.status_label.config(text=f"Редактируется: {diet.name}")
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.component_widgets.clear()
        
        if not diet.components:
            ttk.Label(self.scrollable_frame, text="Рацион пуст").grid(row=0, column=0, sticky=tk.W)
            return
        
        sorted_components = sorted(diet.components.items(), key=lambda x: x[0])
        
        for i, (comp_name, component) in enumerate(sorted_components):
            name_label = ttk.Label(self.scrollable_frame, text=comp_name)
            name_label.grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            amount_var = tk.DoubleVar(value=component.amount)
            amount_entry = ttk.Entry(
                self.scrollable_frame, 
                textvariable=amount_var, 
                width=10
            )
            amount_entry.grid(row=i, column=1, padx=(0, 10), pady=2)
            
            unit_label = ttk.Label(self.scrollable_frame, text="кг")
            unit_label.grid(row=i, column=2, sticky=tk.W, pady=2)
            
            update_btn = ttk.Button(
                self.scrollable_frame,
                text="Обновить",
                command=lambda name=comp_name, var=amount_var: self.update_component(name, var.get())
            )
            update_btn.grid(row=i, column=3, padx=(10, 0), pady=2)
            
            self.component_widgets[comp_name] = {
                'name_label': name_label,
                'amount_var': amount_var,
                'amount_entry': amount_entry,
                'unit_label': unit_label,
                'update_btn': update_btn
            }
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def update_component(self, component_name: str, new_value: float):
        """Обновляет компонент рациона"""
        if self.current_diet:
            try:
                new_value = float(new_value)
                if new_value >= 0:
                    self.view.update_diet_component(component_name, new_value)
                    self.status_label.config(text=f"Обновлено: {component_name} = {new_value} кг")
                else:
                    self.status_label.config(text="Ошибка: значение не может быть отрицательным", foreground='red')
            except ValueError:
                self.status_label.config(text="Ошибка: введите числовое значение", foreground='red')