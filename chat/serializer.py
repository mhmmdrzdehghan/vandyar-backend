from rest_framework import serializers
from .models import Conversation, ConversationMember, Message
from account.models import User


class ConversationMemberSerializer(serializers.ModelSerializer):


    class Meta:
        model = ConversationMember
        fields = [
            "id",
            "conversation",
            "user",
            "is_admin",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "conversation",
            "created_at",
            "updated_at"

        ]


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "is_task",
            "content",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "conversation",
            "sender",
            "created_at",
            "updated_at"
        ]



class ConversationSerializer(serializers.ModelSerializer):
    projectid = serializers.SerializerMethodField(read_only=True)

    
    class Meta:
        model = Conversation
        fields = [
            "id",
            "type",
            "title",
            "group",
            "task",
            "created_by",
            "projectid",
            "members",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "projectid",
            "created_at",
            "updated_at",
        ]


    def get_projectid(self, instance):
        return instance.group.subproject.project.id