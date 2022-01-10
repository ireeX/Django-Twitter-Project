from utils.testcases import TestCase


LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/?is_preview={}'
NEWSFEED_LIST_API = '/api/newsfeeds/'

class LikeApiTests(TestCase):
    
    def setUp(self):
        self.clear_cache()
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

    def test_cancel(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)
        like_comment_data = {'content_type': 'comment', 'object_id': comment.id}
        like_tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
        self.user_client1.post(LIKE_BASE_URL, like_comment_data)
        self.user_client2.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # test unauthenticated cancel like
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        # test HTTP method
        response = self.user_client1.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        # test wrong content_type
        response = self.user_client1.post(LIKE_CANCEL_URL, {
            'content_type': 'xyz',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 400)

        # test wrong object_id
        response = self.user_client1.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)

        # test cancel an non-exist like for comment
        response = self.user_client2.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # test normal cancel like process for comment
        response = self.user_client1.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        #  test cancel an non-exist like for tweet
        response = self.user_client1.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # test normal cancel like process for tweet
        response = self.user_client2.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)

    def test_likes_in_comments_api(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)

        # test unauthorized like
        response = self.anonymous_client.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        # test list comments with detail
        response = self.user_client2.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.user2, comment)
        response = self.user_client2.get(COMMENT_LIST_API, {'tweet_id': tweet.id})
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # test retrieve tweet with detail
        self.create_like(self.user1, comment)
        url = TWEET_RETRIEVE_API.format(tweet.id, False)
        response = self.user_client1.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)

    def test_likes_in_tweets_api(self):
        tweet = self.create_tweet(self.user1)

        # test tweet retrieve api
        url = TWEET_RETRIEVE_API.format(tweet.id, False)
        response = self.user_client2.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.user2, tweet)
        response = self.user_client2.get(url)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # test tweets list api
        response = self.user_client2.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], True)
        self.assertEqual(response.data['results'][0]['likes_count'], 1)

        # test newsfeeds list api
        self.create_like(self.user1, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user_client2.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['has_liked'], True)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 2)

        # test retrieve tweet with detail
        url = TWEET_RETRIEVE_API.format(tweet.id, False)
        response = self.user_client2.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes'][0]['user']['id'], self.user1.id)
        self.assertEqual(response.data['likes'][1]['user']['id'], self.user2.id)