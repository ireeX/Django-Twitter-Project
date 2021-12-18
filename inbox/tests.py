from utils.testcases import TestCase
from notifications.models import Notification
from inbox.services import NotificationService


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')
        self.tweet = self.create_tweet(self.user1)

    def test_send_comment_notification(self):
        # test dispatch notification when tweet user == comment user
        comment = self.create_comment(self.user1, self.tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)
        
        # test normal dispatch notification process
        comment = self.create_comment(self.user2, self.tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)
    
    def test_send_like_notification(self):
        # test dispatch notification when tweet user == like user
        like = self.create_like(self.user1, self.tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)
        
        # test normal dispatch notification process
        like = self.create_like(self.user2, self.tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 1)