from django.contrib.auth.models import User
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import UserProfile
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
    UserSerializerWithProfile,
    UserProfileSerializerForUpdate,
)
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR'],
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        # use serializer to valid user input
        # is_valid() function will call run_validate() and create validated data
        if not serializer.is_valid():
            return Response({'success': False,
                             'message': "Please check input",
                             'error': serializer.errors,
                             },
                            status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # make usr authentication
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({'success': False,
                             'message': "Username and password does not match.",
                             },
                            status=400)

        # user is good, make login
        django_login(request, user)
        return Response({'success': True,
                         'user': UserSerializer(instance=user).data,
                         })

    @action(methods=["POST"], detail=False)
    def signup(self, request):
        # check user input
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False,
                             'message': "Please check input",
                             'error': serializer.errors,
                             },
                            status=400)

        # user input is validated, save user information
        user = serializer.save()

        # login user
        django_login(request, user)
        return Response({'success': True,
                         'user': UserSerializer(instance=user).data,
                         },
                        status=201)


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = [IsAuthenticated, IsObjectOwner,]
    serializer_class = UserProfileSerializerForUpdate