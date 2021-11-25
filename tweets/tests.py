from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from tweets.models import Tweet

import pytz


class TweetTests(TestCase):


    def test_hours_to_now(self):
        user = User.objects.create_user(username='tweet_test')
        tweet = Tweet.objects.create(user=user, content="This is a hours to now test for tweet")
        tweet.created_at = datetime.now(pytz.utc) - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
        