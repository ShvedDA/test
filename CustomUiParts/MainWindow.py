from tkinter.ttk import Style

from customtkinter import CTk, get_appearance_mode

from Project.AppFrames.AdditionalWindows.WaitingWindow import WaitingWindow
from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox
from Project.task_manager import task_manager
from Project.Services.DataService import prepared_data_to_insert
from Project.settings import IMAGES_DIR, WINDOW_WIDTH, WINDOW_HEIGHT, LOADING_STANDARD_GIF, DARK_LOADING_GIF, \
    BLUE_ELEMENT_COLOR, FONT_ADDITIONAL, TABLE_LIGHT_COLOR, TEXT_LIGHT_TABLE_COLOR, TEXT_DARK_TABLE_COLOR, \
    TABLE_DARK_COLOR, MINSIZE_WINDOW_WIDTH, MINSIZE_WINDOW_HEIGHT
from Project.utils import resource_path


class StandardApp(CTk):
    """
    Стандартное окно всех приложений.
    Не забыть импортировать конфигурирующие файлы!
    """

    def __init__(self, app_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_geometry()
        self.minsize(MINSIZE_WINDOW_WIDTH, MINSIZE_WINDOW_HEIGHT)
        # для загрузочной анимации
        self.loading_animation_active = False

        # для выхода из приложения
        self.active_waiting_window = False
        self.waiting_window = None
        self.after_id = None

        self._start_queue_check()
        self.title(f"рактар - {app_name}")
        self.iconbitmap(resource_path(IMAGES_DIR / "iconRus.ico"))
        self.bind_all("<Key>", self._on_key_release, "+")

        # выставляем стиль таблиц
        self.configure_treeview_style(get_appearance_mode())

        # Приложение закроется только без запущенных потоков
        self.protocol("WM_DELETE_WINDOW", self._close_without_active_threads)

    def set_geometry(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = int((screen_width / 2) - (WINDOW_WIDTH / 2))
        y_pos = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}")

    def _default_error_handler(self, error):
        """Обработчик ошибок по умолчанию (вызывается в главном потоке)"""
        # Безопасный вызов messagebox через main thread
        self.after(0, lambda: ErrorMessageBox(
            self,
            f"Не удалось обновить данные:\n{str(error)}"
        ))

    def async_update_table(self, data_func, headers, update_func, column_sorted_func=None, callback=None,
                           error_handler=None):
        """
        Универсальный метод для обновления таблиц в фоне
        data_func: функция получения данных (вызывается в фоновом потоке)
        headers: заголовки таблицы
        update_func: функция обновления таблицы (вызывается в главном потоке)
        error_handler: опциональный обработчик ошибок
        """

        def background_work():
            try:
                # Получение и подготовка данных в фоне
                data = data_func()
                prepared = prepared_data_to_insert(headers, data)

                if column_sorted_func:
                    prepared = sorted(prepared, key=column_sorted_func, reverse=True)

                # Безопасное обновление UI в главном потоке
                self.after(0, lambda: update_func(prepared))

                if callback:
                    self.after(0, self.update())
                    self.after(50, callback())

            except Exception as e:
                if error_handler:
                    self.after(0, lambda error=e: error_handler(error))
                else:
                    self.after(0, lambda error=e: self._default_error_handler(error))

        # Запуск фонового потока
        task_manager.add_task(target_func=background_work)

    def async_reload_table(self, data_func, table_frame, column_sorted_func=None, callback=None, error_handler=None):
        """
        Универсальный метод для обновления таблиц в фоне и загрузки данных в атрибут "table_data"
        data_func: функция получения данных (вызывается в фоновом потоке)
        headers: заголовки таблицы
        update_func: функция обновления таблицы (вызывается в главном потоке)
        error_handler: опциональный обработчик ошибок
        """

        def background_work():
            try:
                # Получение и подготовка данных в фоне
                data = data_func()
                prepared = prepared_data_to_insert(table_frame.headers, data)

                if column_sorted_func:
                    prepared = sorted(prepared, key=column_sorted_func, reverse=True)

                # Безопасное обновление UI в главном потоке
                self.after(0, lambda: table_frame.table.update_data(prepared))

                if callback:
                    self.after(0, self.update())
                    self.after(50, callback())

            except Exception as e:
                if error_handler:
                    self.after(0, lambda error=e: error_handler(error))
                else:
                    self.after(0, lambda error=e: self._default_error_handler(error))
            finally:
                def update_table_data():
                    table_frame.table_data = table_frame.table.return_all_data()

                self.after(0, lambda: update_table_data())

        # Запуск фонового потока
        task_manager.add_task(target_func=background_work)

    def get_theme_gif(self):
        """Возвращаем гифку в соответсвии теме приложения"""
        theme = get_appearance_mode()
        if theme == "Dark":
            return resource_path(DARK_LOADING_GIF)
        else:
            return resource_path(LOADING_STANDARD_GIF)

    def _show_loading(self):
        """Функция показа анимации загрузки"""
        self.loading_animation_active = True
        if hasattr(self, "menuFrame"):
            self.menuFrame.start_loadgif(self.get_theme_gif())

    def _hide_loading(self):
        """Функция скрытия анимации загрузки"""
        self.loading_animation_active = False
        if hasattr(self, "menuFrame"):
            self.after(0, lambda: self.menuFrame.remove_gif())

    def _start_queue_check(self):
        """Проверка очереди задач не на основном потоке"""

        def check_tasks():
            # Update animation based on active threads
            if task_manager.active_threads > 0 and not self.loading_animation_active:
                self._show_loading()
            elif task_manager.active_threads == 0 and self.loading_animation_active:
                self._hide_loading()

            # Reschedule check
            self.after(100, check_tasks)

        check_tasks()  # Initial call

    def block_while_active_threads(self, on_complete=None):
        """Проверка есть ли активные потоки в приложении"""

        def check_active_threads():
            """Проверяем есть ли активные потоки"""
            if task_manager.active_threads > 0:
                if not self.active_waiting_window:
                    self.active_waiting_window = True
                    self.waiting_window = WaitingWindow(self)
            else:
                if self.active_waiting_window and self.waiting_window.winfo_exists():
                    self.waiting_window.destroy()
                self.active_waiting_window = False
                self.waiting_window = None
                # запускаем callback, если был передан
                if on_complete:
                    on_complete()

            # Запускаем повторно проверку, если есть активные потоки и активировано окно
            if task_manager.active_threads > 0 or self.active_waiting_window:
                self.after_id = self.after(100, check_active_threads)
            else:
                self.after_id = None

        # Отменяем если есть что-то в очереди
        if hasattr(self, 'after_id') and self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(0, check_active_threads)

    def _close_without_active_threads(self):
        """Проверяем открыто ли окно ожидания, и если нет, то закрываем приложение"""
        self.block_while_active_threads(self.destroy)

    def _on_key_release(self, event):
        """
        Фикс бага, не позволяющий вставлять текст с буфера при включенной русской раскладке клавиатуры
        """
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

    def configure_treeview_style(self, dark_theme):
        """Выставляем стиль таблиц"""

        # цвета таблицы для светлой темы
        bg_color = TABLE_LIGHT_COLOR
        text_color = TEXT_LIGHT_TABLE_COLOR

        # цвета таблицы для темной темы
        if dark_theme == "Dark":
            bg_color = TABLE_DARK_COLOR
            text_color = TEXT_DARK_TABLE_COLOR

        style = Style()
        style.theme_use("default")  # Use default ttk theme as base

        # Configure Treeview
        style.configure("Treeview",
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        borderwidth=1,
                        rowheight=25,
                        relief="ridge")
        style.map("Treeview",
                  background=[('selected', BLUE_ELEMENT_COLOR)],
                  foreground=[('selected', "white")])

        # Configure Treeview Heading
        style.configure("Treeview.Heading",
                        background=BLUE_ELEMENT_COLOR,
                        foreground="white",
                        font=FONT_ADDITIONAL)
        style.map("Treeview.Heading",
                  background=[('active', 'grey')])
