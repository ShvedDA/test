from customtkinter import CTkTextbox, CTkEntry
from Project.settings import FONT_MENU


class StandardText(CTkTextbox):
    """Стандартное однострочное текстовое поле с заблокированным текстом"""

    def __init__(self, master, new_text, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            height=16,
            border_width=0,
            fg_color='transparent',
            font=FONT_MENU,
            width=300,
            wrap="none",
            state='disabled'
        )
        self.set_text(new_text)

    def set_text(self, new_text):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", new_text)
        self.configure(state="disabled")

    def get_full_text(self):
        return self.get("1.0", "end-1c")

    def delete_all_data(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class EditableText(CTkEntry):
    """Стандартное однострочное текстовое поле с возможностью редактировать текст"""

    def __init__(self, master, new_text, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            height=16,
            width=300,
            placeholder_text=new_text,
            font=FONT_MENU
        )

    def get_full_text(self):
        return self.get()

    def set_text(self, new_text, index=0):
        self.insert(index, new_text)

    def update_text(self, new_text):
        """Обновляем данные в ячейке"""
        if self.get():
            self.delete(0, "end")
            self.insert(0, new_text)

    def delete_last_symbol(self):
        """Удаляем последний символ"""
        current_text = self.get()  # Get current text from CTkEntry
        if current_text:  # Check if there's text to delete
            new_text = current_text[:-1]  # Remove last character
            self.delete(0, "end")  # Clear the entry
            self.insert(0, new_text)  # Insert the modified text

    def clean(self):
        """Чистим ввод"""
        if self.get_full_text():
            self.delete(0, "end")
