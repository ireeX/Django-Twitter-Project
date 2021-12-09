from utils.testcases import TestCase
from rest_framework.test import APIClient
from tweets.models import Tweet

TWEET_CREATE_URL = '/api/tweets/'
TWEET_LIST_URL = '/api/tweets/'

class TweetApiTests(TestCase):

    def setUp(self):
        self.anonymous_user = APIClient()

        self.user1 = self.create_user('user1')
        self.tweets1 = [
            self.create_tweet(self.user1, f'content{i} from user1')
            for i in range(3)
        ]

        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.tweets2 = [
            self.create_tweet(self.user2, f'content{j} from user1')
            for j in range(2)
        ]

    def test_list_tweets(self):
        # test invalid request without user_id parameter
        response = self.anonymous_user.get(TWEET_LIST_URL)
        self.assertEqual(response.status_code, 400)

        # test valid request
        response = self.anonymous_user.get(TWEET_LIST_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_user.get(TWEET_LIST_URL, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)

        # test listed tweets order
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)


    def test_create_tweets(self):
        # test post tweet from anonymous user
        response = self.anonymous_user.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, 403)

        # test post a tweet without content
        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, 400)

        # test post tweet normally
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'Hello World!',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['tweet']['user']['id'], self.user1.id)
        self.assertIn(response.data['tweet']['content'], 'Hello World!')
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)


