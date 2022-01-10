"""
Function for clear cache signals of UserProfile
"""
def profile_changed(sender, instance, **kwargs):
    # import written inside the function to prevent reference loops
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)