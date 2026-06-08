from rest_framework import serializers
from .models import Task , Status , TaskAttachment , CheckList , TaskRoutine
from django.db import transaction
from chat.models import Message


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['task' ,'file' , 'file_name' , 'file_path' , 'file_size' , 'file_type' ,'uploaded_by' , 'created_at' , 'updated_at']
        read_only_fields = ['id', 'task' ,'created_at' , 'updated_at']

# class TaskAssignmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TaskAssignment
#         fields = ['task' , 'assigned_to' , 'status' , 
#                  'start_time' ,
#                 'end_time' ,'quality_rate' ,'action_log' , 
#                 'created_at' , 'updated_at'
#                 ]
#         read_only_fields = ['id','task' , 'created_at' , 'updated_at']


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
    source="message",
    write_only=True,
    required=False,
    allow_null=True
)



    class Meta:
        model = Task
        fields = ['title' , 'group' ,'description', 'message_id','is_routine'  ,'planned_start_at' ,'deadline' ,'priority' , 'created_by' , 'files', 'routines' ,'checklist' ,'assigned_to' ,'status' ,'start_time' ,'end_time' ,'quality_rate' ,'parent_id' ,'root_task' ,'can_forward' ,'updated_at','created_at']
        read_only_fields = ['id' , 'created_at' ,'parent_id' ,'root_task' , 'updated_at']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['title' , 'created_at' , 'updated_at']
        read_only_fields = ['id','created_at' , 'updated_at']











