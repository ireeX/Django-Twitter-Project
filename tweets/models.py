from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from likes.models import Like

import pytz


class Tweet(models.Model):
    content = models.TextField(max_length=255)
    # who posts this tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        # use Composite Index for faster search
        index_together = (('user', 'created_at'),)
        # order by: user -> created_at -> pk
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        return (datetime.now(tz=pytz.utc) - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    """
    @property
    def comments(self, is_preview):
        return self.comment_set.all()
        # this is equal the following. Django special.
        # return Comment.objects.filter(tweet=self)
    """

    def __str__(self):
        # easy for print tweet
        return f'{self.created_at} {self.user}: {self.content}'