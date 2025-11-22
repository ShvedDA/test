def prepared_data_to_insert(columns, data: list):
    """Функция, которая подготоваливает значения к экспорту в таблицу"""
    # возвращаем коллекцию с кортежами для экспорта
    return list(map(
        lambda x: tuple(x.get(column, "") for column in columns),
        data
    ))


def update_data_table(datafunction, table_headers, tablefunction):
    """
    Функция обновления таблиц в программе:
    datafunction: функция, которая получает и возвращает массив данных;
    table_headers: заголовки в таблице;
    tablefunction: функция, которая обновляет данные в таблице;
    """
    # получаем данные
    data = datafunction()
    update_table = prepared_data_to_insert(table_headers, data)
    tablefunction(update_table)
