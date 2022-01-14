from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from dateutil import parser


class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    def paginate_ordered_list(self, ordered_list, request):
        """
        This function is based on presumption that all the data is in cache.
        """
        if 'created_at__gt' in request.query_params:
            # ISO time standard: 2021-12-10T03:54:08.607630Z
            created_at__gt = parser.isoparse(request.query_params['created_at__gt'])
            objects = []
            for obj in ordered_list:
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next_page = False
            return objects

        index = 0
        if 'created_at__lt' in request.query_params:
            created_at__lt = parser.isoparse(request.query_params['created_at__lt'])
            for index, obj in enumerate(ordered_list):
                if obj.created_at < created_at__lt:
                    break
            else:
                ordered_list = []
            self.has_next_page = len(ordered_list) > index + self.page_size
            return ordered_list[index: index + self.page_size]

        self.has_next_page = len(ordered_list) > self.page_size
        return ordered_list[:self.page_size]

    def paginate_queryset(self, queryset, request, view=None):
        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)

        # refresh to get latest tweets
        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)

        # scroll down to get previous tweets
        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'has_next_page': self.has_next_page,
            'results': data,
        })