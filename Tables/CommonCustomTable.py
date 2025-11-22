from Project.CustomUiParts.TreeViews import ScrollableVerticalTreeview, SortedTreeView


class CommonCustomTable(ScrollableVerticalTreeview, SortedTreeView):
    """
    Стандартная таблица с вертикальным скролом и сортировкой с нажатием на заголовок.
    Таблица полностью включена в родительский фрейм.
    Обычно используется именно этот вид таблицы
    """

    def __init__(self, master, columns, **kwargs):
        super().__init__(master, columns, **kwargs)
        self.set_objects()
