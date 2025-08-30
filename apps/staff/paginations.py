from rest_framework import pagination


class StaffListPagination(pagination.PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'size'
    page_size = 10
    max_page_size = 20