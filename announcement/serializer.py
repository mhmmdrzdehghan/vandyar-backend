from rest_framework import serializers

from .models import Announcement
from account.models import User
from account.serializer import UserSerializer


class AnnouncementSerializer(serializers.ModelSerializer):
    recipients = UserSerializer(
        many=True,
        read_only=True
    )

    recipient_ids = serializers.PrimaryKeyRelatedField(
        source="recipients",
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "message",
            "recipients",
            "recipient_ids",
            "is_active",
            "start_at",
            "end_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_at = attrs.get("start_at")
        end_at = attrs.get("end_at")

        if start_at and end_at and start_at > end_at:
            raise serializers.ValidationError(
                {"end_at": "end_at must be greater than start_at."}
            )

        return attrs