from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from twitter.cache import NEWSFEEDS_PATTERNN
from utils.cache.redis_helper import RedisHelper


class NewsFeedService:

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        # add user's tweets to newsfeed
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
        # since `bulk_create()` method will not trigger post_save signal,
        # the newsfeeds need to be push to cache manually
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = NEWSFEEDS_PATTERNN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = NEWSFEEDS_PATTERNN.format(user_id=newsfeed.user_id)
        return RedisHelper.push_object(key, newsfeed, queryset)