from friendships.models import Friendship


class FriendshipService:

    @classmethod
    def get_followers(cls, user):

        # It will cause N + 1 Queries using the following query:
        #
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]
        #
        # The above query will make query to DB for every friendship.from_user

        # The following query using prefetch_related() only perform 2 queries in DB.
        # It's equal to using an IN Query:
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]