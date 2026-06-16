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
    admins     = serializers.SerializerMethodField()



    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "is_task",
            "task",
            "admins",
            "is_edited",
            "edited_at",
            "is_deleted",
            "reply_to",
            "deleted_at",
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
            "admins",
            "is_edited",
            "edited_at",
            "is_deleted",
            "deleted_at",
            "task",
            "groupid",
            "created_at",
            "updated_at"
        ]

    def get_groupid(self, obj):
        return obj.conversation.group_id
    
    def get_admins(self, instance):
        return list(
            ConversationMember.objects.filter(
                conversation=instance.conversation,
                is_admin=True
            ).values_list("user_id", flat=True)
        )

        


class ConversationSerializer(serializers.ModelSerializer):
    projectid = serializers.SerializerMethodField(read_only=True)
    admins     = serializers.SerializerMethodField()
    members     = serializers.SerializerMethodField()
    subprojectname = serializers.SerializerMethodField()
    projectname  = serializers.SerializerMethodField()
    groupname  = serializers.SerializerMethodField()
    profiles = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Conversation
        fields = [
            "id",
            "type",
            "title",
            "group",
            "task",
            "admins",
            "created_by",
            "members",
            "subprojectname",
            "profiles",
            "projectname",
            "groupname",
            "projectid",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "admins",
            "subprojectname",
            "members",
            "projectname",
            "groupname",
            "projectid",
            "created_at",
            "updated_at",
        ]

    def get_profiles(self,instance):

        users =  User.objects.filter(conversations__conversation=instance)

        return UserSerializer(
            users,
            many=True
        ).data

    def get_projectid(self, instance):

        if instance.group:
            return instance.group.subproject.project.id
        
        return None
    

    def get_subprojectname(self, instance):

        if instance.group:
            return instance.group.subproject.title
        
        return None
    
    def get_projectname(self, instance):

        if instance.group:
            return instance.group.subproject.project.title
        
        return None
    

    def get_groupname(self, instance):

        if instance.group:
            return instance.group.title
        
        return None
    
    

    def get_admins(self, instance):
        return list(
            ConversationMember.objects.filter(
                conversation=instance,
                is_admin=True
            ).values_list("user_id", flat=True)
        )
    
    def get_members(self, instance):
        return list(
            ConversationMember.objects.filter(
                conversation=instance,
                is_admin=False
            ).values_list("user_id", flat=True)
        )


class UpdateConversationSerializer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )