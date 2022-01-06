from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService


class FollowerSerializer(serializers.ModelSerializer):
    # use 'source=xxx' to identify the xxx field in model.
    user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'is_mutual', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        # the following will bring N+1 Queries.
        # to be optimized
        return FriendshipService.has_followed(
            self.context['request'].user,
            obj.from_user,
        )


class FollowingSerializer(FollowerSerializer):
    user = UserSerializerForFriendship(source='to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'is_mutual', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        # the following will bring N+1 Queries.
        # to be optimized
        return FriendshipService.has_followed(
            self.context['request'].user,
            obj.to_user,
        )


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id', "is_mutual",)

    def validate(self, attrs):

        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'from_user and to_user should be different.',
            })

        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cannot follow a non-exist user.'
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        is_mutual = validated_data['is_mutual']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            is_mutual=is_mutual,
        )

