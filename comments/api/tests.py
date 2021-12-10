from utils.testcases import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from comments.models import Comment


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):
    
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user_client1 = APIClient()
        self.user_client1.force_authenticate(self.user1)
        
        self.user2 = self.create_user('user2')
        self.user_client2 = APIClient()
        self.user_client2.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_create(self):
        # test authentication
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # test no parameters
        response = self.user_client1.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # test missing parameters
        response = self.user_client1.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        print(response.data)
        self.assertEqual(response.status_code, 400)

        # test normal post comment
        response = self.user_client2.post(COMMENT_URL, {
                'tweet_id': self.tweet.id,
                'content': 'hello',
            })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user2.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], 'hello')

    def test_list(self):
        # test required parameter: tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # test nor list method
        response = self.anonymous_client.get(
            COMMENT_URL,
            {'tweet_id': self.tweet.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # test comment order by created timestamp
        self.create_comment(self.user1, self.tweet, 'user1 comment')
        self.create_comment(self.user2, self.tweet, 'user2 comment')
        response = self.anonymous_client.get(
            COMMENT_URL,
            {'tweet_id': self.tweet.id},
        )

        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], 'user1 comment')
        self.assertEqual(response.data['comments'][1]['content'], 'user2 comment')

        # test only filter by tweet_id
        self.create_comment(self.user2, self.create_tweet(self.user2), 'hello')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.user2.id,
        })

    def test_update(self):
        comment = self.create_comment(self.user1, self.tweet, {'content': 'origin'})
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # test authentication required
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)

        # test authorization required
        response = self.user_client2.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()   # the comment in cache is not refreshed. need to reload from db.
        self.assertNotEqual(comment.content, 'new')

        # test normal update comment
        response = self.user_client1.put(url, {'content': 'new'})
        comment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.content, 'new')

        # cannot update data other than content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        another_tweet = self.create_tweet(user=self.user2)
        response = self.user_client1.put(url, {
            'content': 'latest',
            'user_id': self.user2.id,
            'tweet_id': another_tweet.id,
            'created_at': now,

        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'latest')
        self.assertEqual(comment.user, self.user1)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.updated_at, before_updated_at)


    def test_destroy(self):
        comment = self.create_comment(self.user1, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # test authentication required
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # test authorization required
        response = self.user_client2.delete(url)
        self.assertEqual(response.status_code, 403)

        # test normal delete comment
        count = Comment.objects.count()
        response = self.user_client1.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)
