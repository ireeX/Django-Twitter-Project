from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from accounts.listeners import profile_changed
from utils.listeners import invalidate_object_cache


class UserProfile(models.Model):
    # OneToOneField can be treated as "ForeignKey + Unique Index"
    # It is used to make sure one user has only one userprofile and vice versa
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    avatar = models.FileField(null=True)
    nickname = models.CharField(null=True, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# The 'get_profile()' method is a monkey patch for User model from django
# As long as the user instance exists, the profile will be cached.
# No need to retrieve data from DB for the second time.
def get_profile(user):
    from accounts.services import UserService

    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile = UserService.get_profile_through_cache(user.id)
    setattr(user, '_cached_user_profile', profile)
    return profile

# We can get user profile by calling 'user_instance.profile'
User.profile = property(get_profile)


# For memcached
# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_object_cache, sender=User)
post_save.connect(invalidate_object_cache, sender=User)
pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)