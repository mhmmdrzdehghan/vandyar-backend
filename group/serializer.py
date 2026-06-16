from rest_framework import serializers
from .models import Group
from chat.serializer import ConversationSerializer

class GroupSerializer(serializers.ModelSerializer):

    chat_room      = ConversationSerializer(read_only=True)
    projectname    = serializers.SerializerMethodField(read_only=True)
    subprojectname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = [
            'id',
            'title',
            'description',
            "chat_room",
            'subproject',
            "projectname",
            "subprojectname",
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


    def get_projectname(self, instance):
        if instance.subproject and instance.subproject.project:
            return instance.subproject.project.title
        return None

    def get_subprojectname(self, instance):
        if instance.subproject:
            return instance.subproject.title
        return None


class GroupUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = [
            'id',
            'title',
            'description',
            'members',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
        ]
        
