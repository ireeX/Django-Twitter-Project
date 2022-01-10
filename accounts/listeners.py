"""
Functions for clear cache signals
"""
def user_changed(sender, instance, **kwargs):
    # import written inside the function to prevent reference loops
    from accounts.services import UserService
    UserService.invalidate_user(instance.id)

def profile_changed(sender, instance, **kwargs):
    # import written inside the function to prevent reference loops
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)