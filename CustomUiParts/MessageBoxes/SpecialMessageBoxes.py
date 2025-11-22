from customtkinter import CTk, CTkFrame

from Project.CustomUiParts.MessageBoxes.MessageBox import OkMessageBox, YesOrNoMessageBox


class SuccessMessageBox(OkMessageBox):
    """Всплывающее окно сигнализирующее об успешной операции"""

    def __init__(self, master: (CTk, CTkFrame), description_text, **kwargs):
        super().__init__(master, 200, 400, "Успех!", description_text)
        self.setup_icon("success_icon.png")


class ErrorMessageBox(OkMessageBox):
    """Всплывающее окно сигнализирующее об ошибке"""

    def __init__(self, master: (CTk, CTkFrame), description_text, **kwargs):
        super().__init__(master, 200, 400, "Ошибка!", description_text)
        self.setup_icon("error_icon.png")


class WarningMessageBox(OkMessageBox):
    """Предупреждающее всплывающее окно"""

    def __init__(self, master: (CTk, CTkFrame), description_text, **kwargs):
        super().__init__(master, 200, 400, "Внимание!", description_text)
        self.setup_icon("warning_icon.png")


class ConfirmMessageBox(YesOrNoMessageBox):
    """Всплывающее окно с подтверждением пользователя"""

    def __init__(self, master: (CTk, CTkFrame), description_text, **kwargs):
        super().__init__(master, 200, 400, "Подтверждение!", description_text)
        self.setup_icon("recheck_icon.png")
