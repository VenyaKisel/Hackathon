import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("Анализ рационов коров")
        self.root.geometry("1200x800") 
        self.root.minsize(1000, 600)  
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def create_widgets(self):
        """Создание виджетов"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)
        
        self.prediction_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.prediction_frame, text="Прогнозирование")
        
        self.prediction_frame.columnconfigure(0, weight=1)
        self.prediction_frame.rowconfigure(0, weight=1)
        
        from .diet_prediction_view import DietPredictionView
        self.diet_prediction_view = DietPredictionView(
            self.prediction_frame, self.app, self
        )
        self.diet_prediction_view.frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.set_status("Готов")
    
    def set_status(self, message: str):
        """Установка статуса"""
        self.status_var.set(message)
    
    def show_info(self, title: str, message: str):
        """Показать информационное сообщение"""
        tk.messagebox.showinfo(title, message)
    
    def show_error(self, title: str, message: str):
        """Показать сообщение об ошибке"""
        tk.messagebox.showerror(title, message)