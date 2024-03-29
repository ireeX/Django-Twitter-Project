from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from tweets.models import Tweet
from likes.models import Like
from utils.cache.memcached_helper import MemcachedHelper


class Comment(models.Model):
    # to be continued: comment to other comments
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'),)

    # for convenience of reverse lookup from comment to like
    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)

    def __str__(self):
        return '{} - {} comments {} at tweet {}'.format(
            self.created_at,
            self.user,
            self.content,
            self.tweet_id
        )