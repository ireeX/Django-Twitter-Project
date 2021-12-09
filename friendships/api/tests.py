from utils.testcases import TestCase
from rest_framework.test import APIClient
from friendships.models import Friendship


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        
        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # create followings and followers for user2
        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_follow(self):
        url1 = FOLLOW_URL.format(self.user1.id)
        url2 = FOLLOW_URL.format(self.user2.id)

        count = Friendship.objects.count()

        # test authentication
        response = self.anonymous_client.post(url1)
        self.assertEqual(response.status_code, 403)

        # test request method
        response = self.user2_client.get(url1)
        self.assertEqual(response.status_code, 405)

        # test self follow
        response = self.user1_client.post(url1)
        self.assertEqual(response.status_code, 400)

        # test success follow
        response = self.user2_client.post(url1)
        self.assertEqual(response.status_code, 201)

        # test repeated follow
        response = self.user2_client.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['duplicate'], True)

        # test follow to non-exist user
        url3 = FOLLOW_URL.format(0)
        response = self.user2_client.post(url3)
        self.assertEqual(response.status_code, 404)

        # test mutual following
        response = self.user1_client.post(url2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['is_mutual'], True)

        # test data increase after new follow requests
        self.assertEqual(Friendship.objects.count(), count + 2)

    def test_unfollow(self):
        url1 = UNFOLLOW_URL.format(self.user1.id)
        url2 = UNFOLLOW_URL.format(self.user2.id)

        # test authentication
        response = self.anonymous_client.post(url1)
        self.assertEqual(response.status_code, 403)
        # test request method
        response = self.user1_client.get(url1)
        self.assertEqual(response.status_code, 405)
        # test self unfollow
        response = self.user1_client.post(url1)
        self.assertEqual(response.status_code, 400)
        # test success unfollow
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        response = self.user2_client.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        # test unfollow a non-exist friendship
        response = self.user2_client.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        # test unfollow
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        response = self.user1_client.post(url2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], True)
        # test unfollow for mutual following
        friendship = Friendship.objects.get(from_user=self.user2, to_user=self.user1)
        self.assertEqual(friendship.is_mutual, False)

        # test data decrease for new unfollow request
        count = Friendship.objects.count()
        response = self.user2_client.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Friendship.objects.count(), count - 1)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user2.id)

        # test heep methods, only GET is allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)

        # test get all the followings data
        self.assertEqual(len(response.data['followings']), 3)

        # test data is ordered by timestamp
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']

        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'user2_following2'
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'user2_following1'
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'user2_following0'
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user2.id)

        # test HTTP method, only GET is allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)

        # test retrieved data is ordered by timestamp
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'user2_follower1'
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'user2_follower0'
        )