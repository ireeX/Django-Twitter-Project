from utils.testcases import TestCase
from rest_framework.test import APIClient
from friendships.models import Friendship
from friendships.api.pagination import FriendshipPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.client1 = APIClient()
        self.client1.force_authenticate(self.user1)
        
        self.user2 = self.create_user('user2')
        self.client2 = APIClient()
        self.client2.force_authenticate(self.user2)

    def test_follow(self):
        url1 = FOLLOW_URL.format(self.user1.id)
        url2 = FOLLOW_URL.format(self.user2.id)

        count = Friendship.objects.count()

        # test authentication
        response = self.anonymous_client.post(url1)
        self.assertEqual(response.status_code, 403)

        # test request method
        response = self.client2.get(url1)
        self.assertEqual(response.status_code, 405)

        # test self follow
        response = self.client1.post(url1)
        self.assertEqual(response.status_code, 400)

        # test success follow
        response = self.client2.post(url1)
        self.assertEqual(response.status_code, 201)

        # test repeated follow
        response = self.client2.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['duplicate'], True)

        # test follow to non-exist user
        url3 = FOLLOW_URL.format(0)
        response = self.client2.post(url3)
        self.assertEqual(response.status_code, 404)

        # test mutual following
        response = self.client1.post(url2)
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
        response = self.client1.get(url1)
        self.assertEqual(response.status_code, 405)
        # test self unfollow
        response = self.client1.post(url1)
        self.assertEqual(response.status_code, 400)
        # test success unfollow
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        response = self.client2.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        # test unfollow a non-exist friendship
        response = self.client2.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        # test unfollow
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        response = self.client1.post(url2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], True)
        # test unfollow for mutual following
        friendship = Friendship.objects.get(from_user=self.user2, to_user=self.user1)
        self.assertEqual(friendship.is_mutual, False)

        # test data decrease for new unfollow request
        count = Friendship.objects.count()
        response = self.client2.post(url1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Friendship.objects.count(), count - 1)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user2.id)

        # create followings and followers for user2
        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

        # test heep methods, only GET is allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)

        # test get all the followings data
        self.assertEqual(len(response.data['results']), 3)

        # test data is ordered by timestamp
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']

        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'user2_following2'
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'user2_following1'
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
            'user2_following0'
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user2.id)

        # create followings and followers for user2
        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

        # test HTTP method, only GET is allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)

        # test retrieved data is ordered by timestamp
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'user2_follower1'
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'user2_follower0'
        )

    def test_followers_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            follower = self.create_user('user1_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user1)
            if follower.id % 2 == 0:
                Friendship.objects.create(from_user=self.user2, to_user=follower)

        url = FOLLOWERS_URL.format(self.user1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # user2 has followed users with even id
        response = self.client2.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            following = self.create_user('user1_following{}'.format(i))
            Friendship.objects.create(from_user=self.user1, to_user=following)
            if following.id % 2 == 0:
                Friendship.objects.create(from_user=self.user2, to_user=following)

        url = FOLLOWINGS_URL.format(self.user1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # user1 has followed all his following users
        response = self.client1.get(url, {'page': 1})  
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

        # user2 has followed users with even id
        response = self.client2.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        # test pagination process
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        # test retrieve page out of range
        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        # test user can not customize page_size exceeds max_page_size
        response = self.anonymous_client.get(url, {'page': 1, 'size': max_page_size + 1})
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # test user can customize page size by param size
        response = self.anonymous_client.get(url, {'page': 1, 'size': 2})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        print()
