from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkFrame
from tkinter import Checkbutton, Radiobutton

from Project.settings import DISABLE_TEXT_COLOR


def disable_frame(frame):
    """Команда отключения фрейма"""

    # Отключаем виджеты по-одиночке
    def disable_widgets(widget):
        for child in widget.winfo_children():
            # Отключаем виджеты
            if isinstance(child, (CTkButton, CTkEntry, Checkbutton, Radiobutton)):
                child.configure(state='disabled')
            # Для лейблов просто меняем цвет
            elif isinstance(child, CTkLabel):
                child.configure(text_color=DISABLE_TEXT_COLOR)
            # идем по рекурсии дальше
            elif isinstance(child, CTkFrame):
                disable_widgets(child)

    disable_widgets(frame)


def enable_frame(frame):
    """Команда включения фрейма"""

    def enable_widgets(widget):
        for child in widget.winfo_children():

            if isinstance(child, (CTkButton, CTkEntry, Checkbutton, Radiobutton)):
                child.configure(state='normal')
            elif isinstance(child, CTkLabel):
                child.configure(text_color="black")
            elif isinstance(child, CTkFrame):
                enable_widgets(child)

    enable_widgets(frame)
