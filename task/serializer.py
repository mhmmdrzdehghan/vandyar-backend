from rest_framework import serializers
from .models import Task , Status , TaskAttachment , CheckList , TaskRoutine
from django.db import transaction
from chat.models import Message
from group.serializer import GroupSerializer

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['task' ,'file' , 'file_name' , 'file_path' , 'file_size' , 'file_type' ,'uploaded_by' , 'created_at' , 'updated_at']
        read_only_fields = ['id', 'task' ,'created_at' , 'updated_at']

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
    
    files = TaskAttachmentSerializer(many=True , required=False)
    checklist = CheckListSeializer(many=True , required=False)
    routines = TaskRountineSerializer(required=False)
    message_id = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        write_only=True,
        required=False
    )

    group_detail = GroupSerializer(
            source='group',
            read_only=True
        )


    projectname = serializers.SerializerMethodField()


    name = serializers.SerializerMethodField()



    class Meta:
        model = Task
        fields = ['id' ,'title' , 'name' ,'projectname','group_detail' ,'group' ,'description', 'message_id','is_routine'  ,'planned_start_at' ,'deadline' ,'priority' , 'created_by' , 'files', 'routines' ,'checklist' ,'assigned_to' ,'status' ,'start_time' ,'end_time' ,'quality_rate' ,'parent_id' ,'root_task' ,'can_forward' ,'updated_at','created_at']
        read_only_fields = ['id','projectname','group_detail', 'name' ,'created_at' ,'parent_id' ,'root_task' , 'updated_at']

    def get_name(self, instance):
        full_name = f" {instance.assigned_to.Profile.first_name} {instance.assigned_to.Profile.last_name}"
        return full_name 
    
    def get_projectname(self, instance):
        return instance.group.subproject.project.title

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id','title' , 'created_at' , 'updated_at']
        read_only_fields = ['id','created_at' , 'updated_at']











