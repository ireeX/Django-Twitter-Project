from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForUpdate,
    TweetSerializerWithDetail,
)
from tweets.models import Tweet
from tweets.services import TweetService
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.permissions import IsObjectOwner
from utils.pagination import EndlessPagination


class TweetViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action in ('update', 'destroy'):
            return [IsAuthenticated(), IsObjectOwner()]
        return [IsAuthenticated()]

    # The authorization level is set to "IsAuthenticated()" in get_permissions() function
    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)

        # serializer.save() will call create() method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response({
            'success': True,
            'tweet': TweetSerializer(tweet, context={'request': request},).data,
        }, status=201)

    # The authorization level is set to "AllowAny()" in get_permissions() function
    # return all tweets from the user
    @required_params(params=['user_id'])
    def list(self, request):
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @required_params(params=['is_preview'])
    def retrieve(self, request, *args, **kwargs):
        # if 'is_preview' set to True, the tweet will carry top 3 comments
        # else, the tweet will carry all the comments
        tweet = self.get_object()
        if tweet.is_deleted:
            return Response({
                'success': False,
                'error': 'The tweet does not exists.',
            }, status=status.HTTP_400_BAD_REQUEST)

        is_preview = request.query_params.get('is_preview').lower()
        return Response(
            TweetSerializerWithDetail(
                tweet,
                context={'is_preview': is_preview, 'request': request}).data
        )

    def update(self, request, *args, **kwargs):
        serializer = TweetSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input.',
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        tweet = serializer.save()
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        tweet = self.get_object()
        tweet.is_deleted = True
        tweet.save()
        return Response({'success': True}, status=status.HTTP_200_OK)