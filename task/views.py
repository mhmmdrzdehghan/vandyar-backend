from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import UpdateAPIView
from .serializer import TaskSerializer , StatusSerializer  , TaskAttachmentSerializer , CheckListSeializer , TaskRountineSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Task , Status , TaskAttachment , TaskRoutine , CheckList
from django.db import transaction
from rest_framework.response import Response
from datetime import timedelta
from rest_framework.views import APIView
from project.models import SubProject
from django.db.models import Count


class TaskView(ModelViewSet):
    serializer_class  = TaskSerializer
    permission_classes = [IsAuthenticated]

    queryset = Task.objects.all()


    def create(self, request, *args, **kwargs):
        with transaction.atomic():

            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            user = request.user
            data['created_by'] = user


            is_routine = data.get("is_routine" , False)
            files_data = data.pop('files' , [])
            checklist_data = data.pop('checklist' , [])

            # return Response(is_routine)

            routines = None
            routines_response = None 
            if is_routine:
                routines = data.pop("routines" , [])

 


            task = Task.objects.create(**data)
            
            if routines != None:

                routines_response = self.CreateRoutineTask(task,routines)

            files_response =  self.CreateFile(task , files_data , user)
            checklist_response =  self.CreateCheklist(task , checklist_data)


            response = {'task':TaskSerializer(task).data ,  'file':TaskAttachmentSerializer(files_response , many=True).data,  'checklist':CheckListSeializer(checklist_response , many=True).data  ,'routine':TaskRountineSerializer(routines_response).data}

            return Response(response)
        
    def update(self, request, *args, **kwargs):

        with transaction.atomic():
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            user = request.user
            data['created_by'] = user


            is_routine = data.get("is_routine" , False)
            files_data = data.pop('files' , [])
            checklist_data = data.pop('checklist' , [])


            routines = None
            routines_response = None 

            if is_routine:
                routines = data.pop("routines" , [])

 


            task = Task.objects.get(id=kwargs.get('pk'))

            for attr, value in data.items():
                setattr(task, attr, value)

            task.save()
            
            TaskRoutine.objects.filter(task=task).delete()
            TaskAttachment.objects.filter(task=task).delete()
            CheckList.objects.filter(task=task).delete()

            if routines != None:
                routines_response = self.CreateRoutineTask(task,routines)

            files_response =  self.CreateFile(task , files_data , user)
            checklist_response =  self.CreateCheklist(task , checklist_data)

            response = {'task':TaskSerializer(task).data  ,  'file':TaskAttachmentSerializer(files_response , many=True).data,  'checklist':CheckListSeializer(checklist_response , many=True).data  ,'routine':TaskRountineSerializer(routines_response).data}



            return Response(response)            

    def CreateRoutineTask(self ,task ,data):
        period = data["period"]
        start_date = data["start_date"]

        if period == "daily":
            delta = timedelta(days=1)
        elif period == "weekly":
            delta = timedelta(weeks=1)
        elif period == "monthly":
            delta = timedelta(days=30)

        routine =  TaskRoutine.objects.create(
            task=task,
            period=period,
            start_date=start_date,
            end_date=data.get("end_date"),
            next_run_at=start_date + delta,
            is_active=True
        )

        return routine

    def CreateFile(self ,task , files_data , user):
        response = []
        for file in files_data:
            file =  TaskAttachment.objects.create(
                task=task,
                file=file,
                file_name=file.name,
                file_size=file.size,
                file_type=file.content_type,
                uploaded_by=user
            )

            response.append(file)

        return response   
  

    def CreateCheklist(self ,task, checklist_data):
        response = []
        for item in checklist_data:
            checklist = CheckList.objects.create(task=task ,**item) 
            response.append(checklist)

        return response     


class StatusView(ModelViewSet):
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]
    queryset = Status.objects.all()
    



#data :

class TaskDataView(APIView):
    def get(self, request, *args, **kwargs):
        peoject_id = request.query_params.get("project_id")
        tasks = Task.objects.filter(group__subproject__project_id=peoject_id).select_related('status')

        

        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)
         


    



        

        
        


        
    

# Create your views here.
