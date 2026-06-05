from rest_framework import serializers
from .models import Task , TaskAssignment , Status , TaskAttachment , CheckList , TaskRoutine
from django.db import transaction


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['task' ,'file' , 'file_name' , 'file_path' , 'file_size' , 'file_type' ,'uploaded_by' , 'created_at' , 'updated_at']
        read_only_fields = ['id', 'task' ,'created_at' , 'updated_at']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = ['task' , 'assigned_to' , 'status' , 
                 'start_time' ,
                'end_time' ,'quality_rate' ,'action_log' , 
                'created_at' , 'updated_at'
                ]
        read_only_fields = ['id','task' , 'created_at' , 'updated_at']

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
    
    assignments = TaskAssignmentSerializer(many=True)
    files = TaskAttachmentSerializer(many=True , required=False)
    checklist = CheckListSeializer(many=True , required=False)
    routines = TaskRountineSerializer(required=False)


    class Meta:
        model = Task
        fields = ['title' , 'description', 'is_routine'  ,'planned_start_at' ,'deadline' ,'priority' , 'created_by','assignments' , 'files', 'routines' ,'checklist','created_at' , 'updated_at']
        read_only_fields = ['id' , 'created_at' , 'updated_at']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['title' , 'created_at' , 'updated_at']
        read_only_fields = ['id','created_at' , 'updated_at']









