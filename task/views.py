from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import UpdateAPIView
from .serializer import TaskSerializer , StatusSerializer , TaskAssignmentSerializer , TaskAttachmentSerializer , CheckListSeializer , TaskRountineSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Task , Status , TaskAssignment , TaskAttachment , TaskRoutine , CheckList
from django.db import transaction
from rest_framework.response import Response
from datetime import timedelta


class TaskView(ModelViewSet):
    serializer_class  = TaskSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            user = request.user
            data['created_by'] = user


            is_routine = data.get("is_routine" , False)
            assignments_data = data.pop('assignments' , [])
            files_data = data.pop('files' , [])
            checklist_data = data.pop('checklist' , [])

            # return Response(is_routine)

            routines = None
            if is_routine:
                routines = data.pop("routines" , [])

 


            task = Task.objects.create(**data)
            
            if routines != None:

                routines_response = self.CreateRoutineTask(task,routines)

            assignments_response = self.CreateAssignment(task , assignments_data)
            files_response =  self.CreateFile(task , files_data , user)
            checklist_response =  self.CreateCheklist(task , checklist_data)





            response = {'task':TaskSerializer(task).data , 'assignment':TaskAssignmentSerializer(assignments_response , many=True).data ,  'file':TaskAttachmentSerializer(files_response , many=True).data,  'checklist':CheckListSeializer(checklist_response , many=True).data  ,'routine':TaskRountineSerializer(routines_response).data}

            return Response(response)
        
    def update(self, request, *args, **kwargs):

        with transaction.atomic():
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data
            user = request.user
            data['created_by'] = user


            is_routine = data.get("is_routine" , False)
            assignments_data = data.pop('assignments' , [])
            files_data = data.pop('files' , [])
            checklist_data = data.pop('checklist' , [])


            routines = None
            if is_routine:
                routines = data.pop("routines" , [])

 


            task = Task.objects.get(id=kwargs.get('pk'))

            for attr, value in data.items():
                setattr(task, attr, value)

            task.save()
            
            TaskRoutine.objects.filter(task=task).delete()
            TaskAssignment.objects.filter(task=task).delete()
            TaskAttachment.objects.filter(task=task).delete()
            CheckList.objects.filter(task=task).delete()

            if routines != None:
                routines_response = self.CreateRoutineTask(task,routines)

            assignments_response = self.CreateAssignment(task , assignments_data)
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

    def CreateAssignment(self ,task ,assignments_data):
        response = []
        for assignment_data in assignments_data:
            assignment =  TaskAssignment.objects.create(
                task=task,
                **assignment_data
            )  

            response.append(assignment)

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
    

class TaskAssignmentView(UpdateAPIView):
    serializer_class =  TaskAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskAssignment.objects.filter(assigned_to=self.request.user)
    

class RateTask(UpdateAPIView):
    serializer_class =  TaskAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskAssignment.objects.filter(task__created_by=self.request.user , status=3)
    




    



        

        
        


        
    

# Create your views here.
