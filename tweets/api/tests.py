from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from utils.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from utils.pagination import EndlessPagination


TWEET_CREATE_URL = '/api/tweets/'
TWEET_LIST_URL = '/api/tweets/'
TWEET_UPDATE_URL = '/api/tweets/{}/'
TWEET_DELETE_URL = '/api/tweets/{}/'
TWEET_RETRIEVE_URL = '/api/tweets/{}/?is_preview={}'

class TweetApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
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
        self.assertEqual(len(response.data['results']), 3)
        response = self.anonymous_user.get(TWEET_LIST_URL, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['results']), 2)

        # test listed tweets order
        self.assertEqual(response.data['results'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['results'][1]['id'], self.tweets2[0].id)


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

    def test_create_tweet_with_photos(self):
        # test create tweet without photos
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'test not photo upload',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # test create tweet with one photo
        file1 = SimpleUploadedFile(
            name='fakeimage1.jpg',
            content=str.encode('first fake image'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'test 1 photo upload',
            'files': [file1]
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # test create tweet with multiple photo
        file2 = SimpleUploadedFile(
            name='fakeimage2.jpg',
            content=str.encode('second fake image'),
            content_type='image/jpeg',
        )
        file3 = SimpleUploadedFile(
            name='fakeimage3.jpg',
            content=str.encode('third fake image'),
            content_type='image/jpeg',
        )
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'test multiple photos upload',
            'files': [file2, file3]
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)

        # test response including the urls of photos
        tweet_id = response.data['tweet']['id']
        retrieve_url = TWEET_RETRIEVE_URL.format(tweet_id, False)
        response = self.user1_client.get(retrieve_url)
        self.assertEqual(len(response.data['photo_urls']), 2)
        self.assertEqual('fakeimage2' in response.data['photo_urls'][0], True)
        self.assertEqual('fakeimage3' in response.data['photo_urls'][1], True)

        # test upload more than 9 phots
        files = [
            SimpleUploadedFile(
                name=f'photo{i}.jpg',
                content_type='image/jpeg',
                content=str.encode(f'upload photo {i}')
            )
            for i in range(10)
        ]
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'test upload photos more than 9',
            'files': files
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)

    def test_tweets_list_pagination(self):
        page_size = EndlessPagination.page_size

        for i in range(page_size * 2 - len(self.tweets1)):
            self.tweets1.append(self.create_tweet(self.user1, 'tweet{}'.format(i)))

        tweets = self.tweets1[::-1]

        # pull the first page
        response = self.user1_client.get(TWEET_LIST_URL, {'user_id': self.user1.id})
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[page_size - 1].id)

        # pull the second page
        response = self.user1_client.get(TWEET_LIST_URL, {
            'created_at__lt': tweets[page_size - 1].created_at,
            'user_id': self.user1.id,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['results'][0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[page_size + 1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[2 * page_size - 1].id)

        # pull latest newsfeeds
        response = self.user1_client.get(TWEET_LIST_URL, {
            'created_at__gt': tweets[0].created_at,
            'user_id': self.user1.id,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet = self.create_tweet(self.user1, 'a new tweet comes in')

        response = self.user1_client.get(TWEET_LIST_URL, {
            'created_at__gt': tweets[0].created_at,
            'user_id': self.user1.id,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_tweet.id)