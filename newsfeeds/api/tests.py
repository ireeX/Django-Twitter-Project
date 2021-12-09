from utils.testcases import TestCase
from rest_framework.test import APIClient
from friendships.models import Friendship

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTests(TestCase):
    
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        
        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        
        for i in range(2):
            follower = self.create_user('user1_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user1)
        
        for i in range(3):
            following = self.create_user('user1_following{}'.format(i))
            Friendship.objects.create(from_user=self.user1, to_user=following)
        
    def test_list(self):
        
        # test authentication view newsfeeds
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        
        # test HTTP method, only GET is allowed
        response = self.user2_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        
        # nothing in user2 at the beginning
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # user can see the tweet posted by himself in his newsfeed
        self.user2_client.post(POST_TWEETS_URL, {'content': "Hello, I'm user2"})
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # the followers can see the tweet in their newsfeed
        self.user2_client.post(FOLLOW_URL.format(self.user1.id))
        response = self.user1_client.post(POST_TWEETS_URL, {'content': "Hello, I'm user1"})
        posted_tweet_id = response.data['tweet']['id']
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)