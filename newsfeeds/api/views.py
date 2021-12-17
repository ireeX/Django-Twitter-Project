from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user).prefetch_related('user', 'tweet')

    def list(self, request):
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            # for TweetSerializer.get_has_liked()
            context={'request': request},
            many=True,
        )
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)