from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
)
from tweets.models import Tweet

class TweetViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    # The authorization level is set to "IsAuthenticated()" in get_permissions() function
    def create(self, request):
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
        return Response({
            'success': True,
            'tweet': TweetSerializer(tweet).data,
        }, status=201)

    # The authorization level is set to "AllowAny()" in get_permissions() function
    # return all tweets from the user
    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('cannot find user', status=400)
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id,).order_by('-created_at')

        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})