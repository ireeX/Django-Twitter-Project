from utils.testcases import TestCase
from datetime import datetime, timedelta
from tweets.models import Tweet

import pytz


class TweetModelTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')
        self.tweet = self.create_tweet(user=self.user1, content='test tweet model')

    def test_hours_to_now(self):
        self.tweet.created_at = datetime.now(pytz.utc) - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        # test normal like for a tweet
        self.create_like(self.user1, self.tweet)
        self.create_like(self.user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

        # test like repeatedly for a tweet
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)