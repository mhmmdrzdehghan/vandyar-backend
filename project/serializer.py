from rest_framework import serializers
from .models import Project, SubProject
from group.serializer import GroupSerializer


class SubProjectSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True ,required=False)
    class Meta:
        model = SubProject
        fields = [
            "id",
            "project",
            "title",
            "description",
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
  



