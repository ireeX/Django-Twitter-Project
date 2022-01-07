from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from friendships.api.pagination import FriendshipPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    # Friendship module is based on users
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    pagination_class = FriendshipPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).prefetch_related('from_user').order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    # url: /api/friendship/1/followings/
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).prefetch_related('to_user').order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        following_user = self.get_object()

        data = {
            'from_user_id': request.user.id,
            'to_user_id': following_user.id,
            'is_mutual': False,
        }

        # the friendship already exist
        if Friendship.objects.filter(from_user=data['from_user_id'], to_user=data['to_user_id']).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_200_OK)

        # set mutual following
        if self.set_mutual_following(data, follow_type='follow'):
            data['is_mutual'] = True

        serializer = FriendshipSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
                'success': True,
                'is_mutual': data['is_mutual'],
            }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # raise 404 if no user with id=pk
        unfollow_user = self.get_object()

        data = {
            'from_user_id': request.user.id,
            'to_user_id': unfollow_user.id,
        }

        # pk is string
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': "You cannot unfollow yourself",
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted, attr = Friendship.objects.filter(
            from_user=data['from_user_id'],
            to_user=data['to_user_id'],
        ).delete()

        self.set_mutual_following(data, follow_type='unfollow')

        return Response({
            'success': True,
            'deleted': deleted,
        })

    def set_mutual_following(self, data, follow_type):
        # Set is_mutual attribute for the other user in the friendship
        # Return boolean type. True indicates the other user is also a follower,
        # while False indicates the other user is not a follower.
        from_user=data['from_user_id']
        to_user = data['to_user_id']
        friendship = None
        try:
            friendship = Friendship.objects.get(from_user=to_user, to_user=from_user)
        except Friendship.DoesNotExist:
            pass

        if not friendship:
            return False

        if follow_type == 'follow':
            friendship.is_mutual = True
        elif follow_type == 'unfollow':
            friendship.is_mutual = False
        friendship.save()
        return True


    # Another way is to use list() to perform the functions
    # url: /api/friendships/?type=followers&to_user_id=1
    # url: /api/friendships/?type=followings&from_user_id=1
    def list(self, request):
        return Response({'message': 'function to be continued'})
