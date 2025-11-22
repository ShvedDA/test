from customtkinter import get_appearance_mode

from Project.CustomUiParts.AdditionalWindows import AdditionalWindow
from Project.CustomUiParts.ImageLabels import ImageLabel
from Project.CustomUiParts.Labels import StandardLabel
from Project.settings import IMAGES_DIR
from Project.utils import resource_path


class WaitingWindow(AdditionalWindow):
    """Окно для ожидания заверешения необходимых процессов. Окно невозможно закрыть вручную"""

    def __init__(self, master):
        super().__init__(master, "Ожидание", 300, 150)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # описание
        self.description = StandardLabel(self,
                                         "Выполняется завершение сеанса,\nожидайте...")
        self.description.grid(row=0, column=0, sticky="ns")

        # основная гифка с загрузкой
        self.loading_gif = ImageLabel(self)
        self.loading_gif.grid(row=1, column=0)

        # гифка отличается от стандратной задним фоном, так как в стандартном окне он светлее
        if get_appearance_mode() == "Dark":
            gif = resource_path(IMAGES_DIR / "loading_dark_default_background.gif")
        else:
            gif = resource_path(IMAGES_DIR / "loading_light_default_background.gif")

        self.loading_gif.load(gif)
