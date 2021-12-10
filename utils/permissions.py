from rest_framework.permissions import BasePermission


"""
This Permission is responsible for checking if obj.user equals to the request.user.
If an action with 'detail=False', only has_permission() will be called,
while an action with 'detail=True', both has_permission() and has_object_permission()
will be called. 
When the authentication fails, the 'message' will display in 'errors'.
"""
class IsObjectOwner(BasePermission):
    message = "You don't have permission to access this object."

    def has_permission(self, request, view):
        return True


    def has_object_permission(self, request, view, obj):
        return request.user == obj.user