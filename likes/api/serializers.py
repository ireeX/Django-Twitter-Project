from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment
from likes.models import Like
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()

    class Meta:
        model = Like
        fields = ('user', 'created_at')


"""
BaseLikeSerializer is for LikeSerializerForCreate and LikeSerializerForCancel.
"""
class BaseLikeSerializer(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id',)

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        if data['content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({'content_type': 'Content type does not exist.'})
        liked_object = model_class.objects.filter(id=data['object_id']).first()
        if liked_object is None:
            raise ValidationError({'object_id': 'Object does not exist.'})
        return data


class LikeSerializerForCreate(BaseLikeSerializer):

    def get_or_create(self):
        model_class = self._get_model_class(self.validated_data)
        return Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user,
        )


class LikeSerializerForCancel(BaseLikeSerializer):

    def cancel(self):
        model_class = self._get_model_class(self.validated_data)
        Like.objects.filter(
            user=self.context['request'].user,
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
        ).delete()