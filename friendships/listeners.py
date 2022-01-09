"""
To refresh the cache when data is created, changed or deleted,
such as follow and unfollow action.
Called by models.py
"""
def invalidate_following_cache(sender, instance, **kwargs):
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)