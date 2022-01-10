from notifications.models import Notification
from utils.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_BASE_URL = '/api/notifications/{}/'


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
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


class NotificationApiTests(TestCase):

    def setUp(self):
        self.user1, self.client1 = self.create_user_and_client('user1')
        self.user2, self.client2 = self.create_user_and_client('user2')
        self.tweet1 = self.create_tweet(self.user1)
        self.comment1 = self.create_comment(self.user1, self.tweet1)

    def test_unread_count(self):
        url = NOTIFICATION_BASE_URL.format('unread-count')

        self.client2.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet1.id,
        })
        response = self.client1.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        self.client2.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': self.comment1.id,
        })
        response = self.client1.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        self.client2.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet1.id
        })
        self.client2.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': self.comment1.id
        })
        unread_url = NOTIFICATION_BASE_URL.format('unread-count')
        mark_url = NOTIFICATION_BASE_URL.format('mark-all-as-read')

        response = self.client1.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # test HTTP method
        response = self.client1.get(mark_url)
        self.assertEqual(response.status_code, 405)

        # test normal mark all as read process
        response = self.client1.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.client1.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

        response = self.client2.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_update_notifications(self):
        self.client2.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet1.id,
        })
        self.client2.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': self.comment1.id,
        })
        notification = self.user1.notifications.first()
        url = NOTIFICATION_BASE_URL.format(notification.id)

        # test HTTP method
        response = self.client1.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)

        # test unauthenticated update notification
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)

        # test other user update notification
        # since there is no notification for user2, it will return 404
        response = self.client2.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)

        # test update notification from unread to read
        response = self.client1.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = NOTIFICATION_BASE_URL.format('unread-count')
        response = self.client1.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # test update notification from read to unread
        response = self.client1.put(url, {'unread': True})
        self.assertEqual(response.status_code, 200)
        unread_url = NOTIFICATION_BASE_URL.format('unread-count')
        response = self.client1.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # test required parameter: unread
        response = self.client1.put(url, {'test': 'test'})
        self.assertEqual(response.status_code, 400)

        # test change other attributes of a notification, which is not allowed
        response = self.client1.put(url, {'unread': False, 'verb': 'test'})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'test')
