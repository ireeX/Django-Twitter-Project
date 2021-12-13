from utils.testcases import TestCase
from rest_framework.test import APIClient
from tweets.models import Tweet

TWEET_CREATE_URL = '/api/tweets/'
TWEET_LIST_URL = '/api/tweets/'
TWEET_UPDATE_URL = '/api/tweets/{}/'
TWEET_DELETE_URL = '/api/tweets/{}/'
TWEET_RETRIEVE_URL = '/api/tweets/{}/?is_preview={}'

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

        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

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

    def test_update_tweets(self):
        tweet = self.tweets1[0]
        # test update tweet from anonymous user
        response = self.anonymous_client.put(
            TWEET_UPDATE_URL.format(tweet.id),
            {'content': 'hello', }
        )
        self.assertEqual(response.status_code, 403)

        # test update tweet from unauthorized user
        response = self.user2_client.put(
            TWEET_UPDATE_URL.format(tweet.id),
            {'content': 'hello', }
        )
        self.assertEqual(response.status_code, 403)

        # test normal update tweet
        before_updated_at = tweet.updated_at
        response = self.user1_client.put(
            TWEET_UPDATE_URL.format(tweet.id),
            {'content': 'hello',}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['content'], 'hello')
        self.assertNotEqual(response.data['updated_at'], before_updated_at)

    def test_destroy_tweets(self):
        tweet = self.tweets2[0]
        url = TWEET_DELETE_URL.format(tweet.id)

        # test authentication required
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # test authorization required
        response = self.user1_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # test normal delete tweet
        count = Tweet.objects.count()
        response = self.user2_client.delete(url)
        self.assertEqual(response.status_code, 200)
        tweet.refresh_from_db()
        self.assertEqual(tweet.is_deleted, True)
        self.assertEqual(Tweet.objects.count(), count)

    def test_retrieve_tweet(self):
        tweet = self.tweets1[0]
        # test retrieve a non-exist tweet
        url = TWEET_RETRIEVE_URL.format(-1, 'False')
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # test retrieve without is_preview attribute
        url = '/api/tweets/{}/'.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)

        # test retrieve tweet with all comment
        url = TWEET_RETRIEVE_URL.format(tweet.id, 'False')
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)
        self.create_comment(self.user1, tweet, 'hello1')
        self.create_comment(self.user2, tweet, 'hello2')
        self.create_comment(self.user1, tweet, 'hello3')
        self.create_comment(self.user2, tweet, 'hello4')
        url = TWEET_RETRIEVE_URL.format(tweet.id, 'False')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 4)

        # test retrieve tweet with preview comment
        url = TWEET_RETRIEVE_URL.format(tweet.id, 'True')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 3)