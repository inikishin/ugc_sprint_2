def decode_pagination(page_number: int, page_size: int) -> (int, int):
    """Функция валидации преобразования данных для пагинации. Номер страницы и
    число записей на лист, преобразуются в начальный и конечный индекс для
    выборки.

    Keyword arguments:
    page_number -- Номер страницы.

    page_size -- Число записей на лист.

    return -- Два индекса, начальный и конечный.
    """
    number = page_number if page_number > 0 else 1
    size = page_size if page_size > 0 else 50

    start_index = (number - 1) * size
    end_index = size * number
    return start_index, end_index