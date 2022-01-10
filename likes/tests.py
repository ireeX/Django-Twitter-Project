from utils.testcases import TestCase
from likes.models import Like
from comments.models import Comment
from tweets.models import Tweet


class LikeModelTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user = self.create_user('user')
        self.tweet = self.create_tweet(self.user, 'tweet for testing like model')
        self.comment = self.create_comment(self.user, self.tweet, 'comment for testing like model')

    def test_like_model(self):
        # test create like for tweet
        self.create_like(self.user, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        # test create like for comment
        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        # test like repeatedly for tweet
        self.create_like(self.user, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        # test like repeatedly for comment
        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)