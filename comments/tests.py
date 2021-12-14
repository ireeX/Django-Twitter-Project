from utils.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')
        self.tweet = self.create_tweet(self.user1)
        self.comment = self.create_comment(self.user1, self.tweet)

    def test_comment_model(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        # test normal like for a comment
        self.create_like(self.user1, self.comment)
        self.create_like(self.user2, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)

        # test like repeatedly for a comment
        self.create_like(self.user1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)