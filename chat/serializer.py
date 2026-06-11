from rest_framework import serializers
from .models import Conversation, ConversationMember, Message , MessageReaction
from account.models import User
from account.serializer import UserSerializer



class MessageReactionSerializer(serializers.ModelSerializer):


    class Meta:
        model = MessageReaction
        fields = ["id", "message" ,"user", "reaction", "created_at"]
        read_only_fields = ["id" , "user" , "created_at"]


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

    reactions = MessageReactionSerializer(read_only=True , many=True)
    sender    = UserSerializer(read_only=True)
    groupid   = serializers.SerializerMethodField()


    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "is_task",
            "task",
            "reactions",
            "groupid",
            "content",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "conversation",
            "sender",
            "reactions",
            "task",
            "groupid",
            "created_at",
            "updated_at"
        ]

    def get_groupid(self, obj):
        return obj.conversation.group_id


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