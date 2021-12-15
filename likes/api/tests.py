from utils.testcases import TestCase


LIKE_BASE_URL = '/api/likes/'

class LikeApiTests(TestCase):
    
    def setUp(self):
        self.user1, self.user_client1 = self.create_user_and_client('user1')
        self.user2, self.user_client2 = self.create_user_and_client('user2')

    def test_tweet_like(self):
        tweet = self.create_tweet(self.user1)
        data = {
            'content_type': 'tweet',
            'object_id': tweet.id,
        }

        # test unauthenticated user create like
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # test HTTP method, only POST allowed
        response = self.user_client1.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # test wrong content type
        response = self.user_client1.post(LIKE_BASE_URL, {
            'content_type': 'xyz',
            'object_id': tweet.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # test wrong object id
        response = self.user_client1.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # test normal like function
        response = self.user_client1.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # test like repeatedly
        response = self.user_client2.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 2)
        response = self.user_client1.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_like(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        data = {
            'content_type': 'comment',
            'object_id': comment.id,
        }

        # test unauthenticated like
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # test HTTP methods
        response = self.user_client1.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # test wrong content type
        response = self.user_client1.post(LIKE_BASE_URL, {
            'content_type': 'xyz',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # test wrong object id
        response = self.user_client1.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # test normal like process
        response = self.user_client1.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # test like repeatedly
        response = self.user_client1.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
