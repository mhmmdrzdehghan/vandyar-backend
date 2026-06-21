from rest_framework import serializers
from .models import Project, SubProject
from group.serializer import GroupSerializer
from group.models import Group
from account.serializer import UserSerializer
from account.models import User


class GroupCreateSerializer(serializers.ModelSerializer):

    members_Profile = UserSerializer( source="members",many=True,read_only=True)
    conversationid = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = [
            "id",
            "title",
            "description",
            "conversationid",
            "members",
            "members_Profile"
        ]

        read_only_fields =["id" , "conversationid"]

    def get_conversationid(self, instance):
        return instance.chat_room.id


class SubProjectSerializer(serializers.ModelSerializer):
    groups  = GroupCreateSerializer(many=True ,required=False)


    members_profiles = UserSerializer(
            source="members",
            many=True,
            read_only=True
        )

    managers_profiles = UserSerializer(
        source="managers",
        many=True,
        read_only=True
    )

    class Meta:
        model = SubProject
        fields = [
            "id",
            "project",
            "title",
            "description",
            "managers_profiles",
            "members_profiles",
            "managers",
            "avatar",
            "groups",
            "status",
            "members",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "managers_profiles",
            "members_profiles",
            "created_at",
            "updated_at",
        ]


    def get_fields(self):
            fields = super().get_fields()
            request = self.context.get("request")

            if request and request.method == "POST":
                fields.pop("status", None)

            return fields

class SubProjectUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubProject
        fields = [
            "title",
            "description",
            "managers",
            "members",
        ]




class ProjectSerializer(serializers.ModelSerializer):
    subprojects = SubProjectSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "avatar",
            "subprojects",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "subprojects",
            "created_at",
            "updated_at",
        ]
  



