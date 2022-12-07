from fastapi import HTTPException


def generate_sort_field(sort_data: str, sort_fields: list[str]) -> str:
    """
            Создаем строкове представление поля сортировки для elastic.

            sort_data: Представление сортировки из API

            return: Представление сортировки для elastic
            """
    sort_directions = ['+', '-']
    sort_direction, sort_field = sort_data[:1], sort_data[1:]

    if sort_direction not in sort_directions:
        raise HTTPException(
            status_code=400,
            detail=f'Unknown sort direction {sort_direction}'
        )

    if sort_field not in sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f'Unknown sort field {sort_field}'
        )

    sort_direction = 'desc' if sort_direction == '-' else 'asc'
    return f'{sort_field}:{sort_direction}'