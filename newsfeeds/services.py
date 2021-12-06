from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService:

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        # add the newsfeed to yourself
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
