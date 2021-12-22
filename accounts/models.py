from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # OneToOneField can be treated as "ForeignKey + Unique Index"
    # It is used to make sure one user has only one userprofile and vice versa
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    avatar = models.FileField(null=True)
    nickname = models.CharField(null=True, max_length=20)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# The 'get_profile()' method is a monkey patch for User model from django
# As long as the user instance exists, the profile will be cached.
# No need to retrieve data from DB for the second time.
def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    setattr(user, '_cached_user_profile', profile)
    return profile

# We can get user profile by calling 'user_instance.profile'
User.profile = property(get_profile)