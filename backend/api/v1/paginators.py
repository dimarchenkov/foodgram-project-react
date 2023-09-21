"""Модуль настройки пагинации."""
from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для изменения стиля пагинации.

    Аргументы:
        PageNumberPagination: Базовый класс пагинации.

    Attributes:
        page_size (int): Размер страницы.
        page_size_query_param (str): Позволяет клиенту
        устанавливать размер страницы на основе каждого запроса.
    """
    page_size = 6
    page_size_query_param = 'limit'
