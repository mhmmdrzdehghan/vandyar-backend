from rest_framework import serializers
from .models import Task , Status , TaskAttachment , CheckList , TaskRoutine
from django.db import transaction
from chat.models import Message
from group.serializer import GroupSerializer
from note.models import Note

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['task' ,'file' , 'file_name' , 'file_path' , 'file_size' , 'file_type' ,'uploaded_by' , 'created_at' , 'updated_at']
        read_only_fields = ['id', 'task', 'file_name' , 'file_path' , 'file_size' , 'file_type','uploaded_by' ,'created_at' , 'updated_at']

class CheckListSeializer(serializers.ModelSerializer):
    class Meta:
        model = CheckList
        fields = ['id','task', 'title' ,'is_done' ,'created_at' , 'updated_at']
        read_only_fields =['id' ,'task' , 'created_at', 'updated_at']


class TaskRountineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskRoutine
        fields = ['id' , 'task' ,'period' ,'start_date' ,'end_date' , 'next_run_at' ,'is_active' ,'created_at' ,'updated_at']
        read_only_fields = ['id' , 'task', 'next_run_at' ,'created_at' ,'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    
    files = TaskAttachmentSerializer(many=True,  read_only=True)
    checklist = CheckListSeializer(many=True ,  read_only=True)
    routines = TaskRountineSerializer(read_only=True)
    message_id = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        write_only=True,
        required=False
    )

    note_id = serializers.PrimaryKeyRelatedField(
        queryset=Note.objects.all(),
        write_only=True,
        required=False
    )

    conversations_id = serializers.SerializerMethodField()

    group_detail = GroupSerializer(
            source='group',
            read_only=True
        )


    projectname = serializers.SerializerMethodField()


    name = serializers.SerializerMethodField()

    avatar = serializers.SerializerMethodField()




    class Meta:
        model = Task
        fields = [
                  'id' ,'title' , 'name','voice' ,'projectname' ,
                  'conversations_id','group_detail' ,'group' ,
                  'description', 'message_id','note_id','is_routine'  ,
                  'planned_start_at' ,'deadline' ,'priority' , 
                  'created_by' , 'files', 'routines' ,'checklist' 
                  ,'assigned_to' ,'status' ,'start_time' 
                  ,'end_time' ,'quality_rate' ,'parent_id' 
                  ,'root_task' ,'can_forward','avatar'
                  ,'updated_at','created_at'

                ]
        read_only_fields = [
                            'id','projectname' ,'group_detail',
                            'conversations_id' ,'name' ,'created_at' ,'avatar'
                            ,'parent_id' ,'root_task' , 'updated_at'
                            ]

    def get_name(self, instance):
        full_name = f" {instance.assigned_to.Profile.first_name} {instance.assigned_to.Profile.last_name}"
        return full_name 
    
    def get_projectname(self, instance):
        return instance.group.subproject.project.title
    
    def get_conversations_id(self, instance):
        if hasattr(instance, "chat_room"):
            return instance.chat_room.id
        return None

    
    def get_avatar(self, instance):
        profile = getattr(instance.assigned_to, "Profile", None)

        if not profile or not profile.avatar:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(profile.avatar.url)

        return profile.avatar.url


class StatusSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:

        model = Status
        fields = ['id','title','count' , 'created_at' , 'updated_at']
        read_only_fields = ['id','count' ,'created_at' , 'updated_at']











