import tkinter as tk
from tkinter import ttk
from typing import List

class RecommendationsDisplay:
    def __init__(self, parent, view):
        self.view = view
        
        self.frame = ttk.LabelFrame(parent, text="Рекомендации", padding="10")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        self.create_scrollable_area()
        
    def create_scrollable_area(self):
        """Создает прокручиваемую область для отображения рекомендаций"""
        container = ttk.Frame(self.frame)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(container, height=150)
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
        
    def show_recommendations(self, recommendations: List[str]):
        """Отображает рекомендации"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not recommendations:
            ttk.Label(self.scrollable_frame, text="Нет рекомендаций для отображения").grid(row=0, column=0, sticky=tk.W)
            return
        
        for i, recommendation in enumerate(recommendations):
            if recommendation.startswith("✅"):
                color = "green"
                prefix = "✅"
            elif recommendation.startswith("📊") or recommendation.startswith("💡"):
                color = "white"
                prefix = ""
            elif "УВЕЛИЧИТЬ" in recommendation:
                color = "orange"
                prefix = "⬆️"
            elif "УМЕНЬШИТЬ" in recommendation:
                color = "red" 
                prefix = "⬇️"
            else:
                color = "white"
                prefix = "•"
            
            if prefix:
                text = f"{prefix} {recommendation}" if not recommendation.startswith(prefix) else recommendation
            else:
                text = recommendation
                
            rec_label = ttk.Label(
                self.scrollable_frame, 
                text=text,
                foreground=color,
                wraplength=800,
                justify=tk.LEFT
            )
            rec_label.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))