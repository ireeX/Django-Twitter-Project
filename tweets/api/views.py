from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForUpdate,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class TweetViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    serializer_class = TweetSerializerForUpdate
    queryset = Tweet.objects.all() 

    def get_permissions(self):
        if self.action == 'list':
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
            'tweet': TweetSerializer(tweet).data,
        }, status=201)

    # The authorization level is set to "AllowAny()" in get_permissions() function
    # return all tweets from the user
    @required_params(params=['user_id'])
    def list(self, request):
        user_id = request.query_params['user_id']
        # prefetch_related('user') is called because it can optimize the TweetSerializer
        # if it is not used, TweetSerializer will call UserSerializer
        # and make as many query as the tweet count to retrieve user information from db
        # after using prefetch_related(), there will only be one query
        tweets = Tweet.objects.filter(user_id=user_id, is_deleted=False).prefetch_related('user').order_by('-created_at')

        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})

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
            TweetSerializer(tweet).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        tweet = self.get_object()
        tweet.is_deleted = True
        tweet.save()
        return Response({'success': True}, status=status.HTTP_200_OK)