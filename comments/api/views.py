from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from tweets.models import Tweet
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForUpdate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ('destroy', 'update'):
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request):
        queryset = self.get_queryset()
        # to be continued, order by likes count
        comments = self.filter_queryset(queryset).prefetch_related('user').order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'success': True,
            'comments': serializer.data,
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # self.get_object() will raise 404 if cannot find the object
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input.',
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response({'success': True,}, status=status.HTTP_200_OK )
