from rest_framework import serializers
from .models import Announcement
from account.models import User
from account.serializer import UserSerializer


class AnnouncementSerializer(serializers.ModelSerializer):
    recipients = UserSerializer(many=True, read_only=True)

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
            "deadline",
            "created_at",
            "updated_at",
        ]