from notifications.models import Notification
from utils.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTests(TestCase):

    def setUp(self):
        self.user1, self.user_client1 = self.create_user_and_client('user1')
        self.user2, self.user_client2 = self.create_user_and_client('user2')
        self.tweet1 = self.create_tweet(self.user1)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user_client2.post(COMMENT_URL, {
            'tweet_id': self.tweet1.id,
            'content': 'hello',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user_client2.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet1.id,
        })
        self.assertEqual(Notification.objects.count(), 1)