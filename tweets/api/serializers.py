from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializerForTweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'content', 'created_at', 'updated_at')

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


class TweetSerializerWithComments(TweetSerializer):
    # Adding 'source' equal to
    # add comments property in Tweet model (see tweets/models.py)
    # comments = CommentSerializer(source='comment_set', many=True)
    # comments = CommentSerializer(instance=comments, many=True)

    # Using SerializerMethodField(), get_comments() is for this.
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'content', 'created_at', 'updated_at', 'comments')

    def get_comments(self, obj):
        # obj is the tweet
        if self.context['is_preview'] == 'true':
            return CommentSerializerForTweet(obj.comment_set.all()[:3], many=True).data
        elif self.context['is_preview'] == 'false':
            return CommentSerializerForTweet(obj.comment_set.all(), many=True).data


class TweetSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ('content',)

    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance