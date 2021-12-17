from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'updated_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=255)

    class Meta:
        model = Tweet
        fields = ('content', )

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet


class TweetSerializerWithDetail(TweetSerializer):
    # Adding 'source' equal to
    # add comments property in Tweet model (see tweets/models.py)
    # comments = CommentSerializer(source='comment_set', many=True)
    # comments = CommentSerializer(instance=comments, many=True)

    # Using SerializerMethodField(), get_comments() is for this.
    comments = serializers.SerializerMethodField()
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'updated_at',
            'content',
            'comments_count',
            'comments',
            'likes_count',
            'likes',
            'has_liked',
        )

    def get_comments(self, obj):
        # obj is the tweet
        if self.context['is_preview'] == 'true':
            return CommentSerializer(
                obj.comment_set.all()[:3],
                context={'request': self.context['request']},
                many=True
            ).data
        elif self.context['is_preview'] == 'false':
            return CommentSerializer(
                obj.comment_set.all(),
                context={'request': self.context['request']},
                many=True
            ).data


class TweetSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance