from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

"""
The Like model can be applied to both Comment and Tweet.
"""
class Like(models.Model):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    object_id = models.PositiveIntegerField()   # object_id = comment_id or tweet_id
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # using this order is benefit for query different objects liked by a certain user
        unique_together = (('user', 'content_type', 'object_id',),)
        index_together = (
            # all the likes for a certain object
            ('content_type', 'object_id', 'created_at'),
            # all the objects liked by a certain user
            ('user', 'content_type', 'created_at',),
        )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )