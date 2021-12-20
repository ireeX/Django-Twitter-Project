from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from comments.models import Comment
from tweets.models import Tweet


class NotificationService:

    @classmethod
    def send_like_notification(cls, like):
        target = like.content_object
        if like.user == target.user:
            return
        verb = 'liked your {}'.format(target.__class__.__name__).lower()
        notify.send(
            sender=like.user,
            recipient=target.user,
            verb=verb,
            target=target,
        )

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.tweet.user:
            return
        notify.send(
            sender=comment.user,
            recipient=comment.tweet.user,
            verb='commented your tweet',
            target=comment.tweet,
        )