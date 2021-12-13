from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from comments.models import Comment
from accounts.api.serializers import UserSerializerForComment
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = ('id', 'tweet_id', 'user', 'content', 'created_at', 'updated_at',)

class CommentSerializerForCreate(serializers.ModelSerializer):
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('tweet_id', 'user_id', 'content',)

    # this function is called by serializer.is_valid() in CommentViewSet
    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({'message': 'tweet does not exist.'})
        return data

    # this function is called by serializer.save() in CommentViewSet
    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )


class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance

class CommentSerializerForTweet(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'created_at', 'updated_at',)