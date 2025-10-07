
# точка входа в приложение
import os
import warnings

os.environ['TK_SILENCE_DEPRECATION'] = '1'
warnings.filterwarnings("ignore", category=DeprecationWarning)

import tkinter as tk
from app.application import CowDietApp
from app.ui.main_window import MainWindow

def main():
    """Точка входа в приложение"""
    try:
        root = tk.Tk()
        
        app = CowDietApp()
        
        main_window = MainWindow(root, app)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()