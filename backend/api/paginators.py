"""
Модуль настройки пагинации.
"""
from rest_framework.pagination import PageNumberPagination

from foodgram_backend.constants import PAGE_SIZE_PAGINATORS


class PageLimitPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для изменения стиля пагинации.

    Атрибуты:
    --------
    page_size : int
        Размер страницы.
    page_size_query_param : str
        Позволяет клиенту устанавливать размер
        страницы на основе каждого запроса.
    """
    page_size = PAGE_SIZE_PAGINATORS
    page_size_query_param = 'limit'
