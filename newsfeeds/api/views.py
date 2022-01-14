from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.services import NewsFeedService
from utils.pagination import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user).prefetch_related('user', 'tweet')

    def list(self, request):
        queryset = NewsFeedService.get_cached_newsfeeds(request.user.id)

        page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            # for TweetSerializer.get_has_liked()
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)