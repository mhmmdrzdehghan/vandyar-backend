from rest_framework import serializers
from .models import Project, SubProject
from group.serializer import GroupSerializer
from group.models import Group
from account.serializer import UserSerializer
from account.models import User


class GroupCreateSerializer(serializers.ModelSerializer):

    members_Profile = UserSerializer( source="members",many=True,read_only=True)

    class Meta:
        model = Group
        fields = [
            "title",
            "description",
            "members",
            "members_Profile"
        ]

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
            "groups",
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

class ProjectSerializer(serializers.ModelSerializer):
    subprojects = SubProjectSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = [
            "id",
            "title",
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
  



