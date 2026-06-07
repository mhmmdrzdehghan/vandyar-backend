from rest_framework import serializers
from .models import Group
from chat.serializer import ConversationSerializer

class GroupSerializer(serializers.ModelSerializer):

    chat_room = ConversationSerializer(read_only=True)

    class Meta:
        model = Group
        fields = [
            'id',
            'title',
            'description',
            "chat_room",
            'subproject',
            'members',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            "chat_room",
            'created_at',
            'updated_at',
        ]