from tkinter import Label
from itertools import count, cycle
from PIL import Image, ImageTk
from pathlib import Path


class ImageLabel(Label):
    """Класс для работы с картинками и гифками"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = None
        self.after_id = None
        self.delay = 0

    def load(self, im):
        """
        Загружаем объект:
        если изображение - статичный фрейм напрямую,
        если гиф - бесконечная анимация, что в аттрибуте frames
        """
        # Проверяем является ли im директорией изображения
        if isinstance(im, (str, Path)):
            im = Image.open(im)

        # тут храним фреймы
        image_frames = []

        # загружаем фреймы в лист выше
        try:
            for i in count(1):
                image_frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        # храним фреймы в классе как итератор
        self.frames = cycle(image_frames)

        # взависимости является ли изображением, применяем разные подходы инициализации
        if len(image_frames) == 1:
            self.config(image=next(self.frames), borderwidth=0, highlightthickness=0)
        else:
            self.delay = im.info.get('duration', 100)  # считаем, что 100 стандартый дилей в гиф
            self.next_frame()

    def unload(self):
        """Выгружаем объект и останавливаем анимацию"""
        # проверка наличия фреймов в ожидании прорисовки
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.config(image='')
        self.frames = None

    def next_frame(self):
        """Показать следующий фрейм в гиф"""

        if not self.frames:
            return
        self.config(image=next(self.frames), borderwidth=0, highlightthickness=0)
        self.after_id = self.after(self.delay, self.next_frame)
