from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Default pagination: 25 items per page, max 100."""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """For lists that are typically large: 100 items per page, max 500."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500
