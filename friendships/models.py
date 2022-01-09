from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from friendships.listeners import invalidate_following_cache


class Friendship(models.Model):
    # related_name must set explicitly since there are two User foreignkey
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_mutual = models.BooleanField(default=False)

    class Meta:
        index_together = (
            # retrieve followings, order by time
            ('from_user_id', 'created_at'),
            # retrieve followers, order by time
            ('to_user_id', 'created_at'),
        )
        # prevent follow a user twice
        unique_together = (
            ('from_user_id', 'to_user_id'),
        )
        ordering = ('-created_at',)

# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_following_cache, sender=Friendship)
post_save.connect(invalidate_following_cache, sender=Friendship)