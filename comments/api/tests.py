from utils.testcases import TestCase
from rest_framework.test import APIClient


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