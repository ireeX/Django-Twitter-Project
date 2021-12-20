from rest_framework import serializers
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType


class NotificationSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_type',
            'target_object_id',
            'timestamp',
            'unread',
        )

    def get_target_type(self, obj):
        return obj.target_content_type.model


class NotificationSerializerForUpdate(serializers.ModelSerializer):
    unread = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ('unread', )

    def update(self, instance, validated_data):
        instance.unread = validated_data['unread']
        instance.save()
        return instance