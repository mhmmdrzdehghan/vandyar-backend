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
from django.db.models import Count , Q
from django.utils import timezone
from datetime import timedelta
from account.models import User
from group.models import Group
from chat.models import Message , Conversation
from django.shortcuts import get_object_or_404
from rest_framework import status as s 
from chat.serializer import MessageSerializer







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



            routines = None
            routines_response = None 
            if is_routine:
                routines = data.pop("routines" , [])

            message_id = data.pop("message_id", None)



            task = Task.objects.create(**data)

            if message_id:
                message =  Message.objects.filter(id=message_id.id).first()
                message.is_task = True
                message.task = task
                message.save()


            title = f" {task.title}-چت"

            
            if routines != None:

                routines_response = self.CreateRoutineTask(task,routines)

            files_response     =  self.CreateFile(task , files_data , user)
            checklist_response =  self.CreateCheklist(task , checklist_data)
        
            conversation       = self.CreateChat(title ,task , user)


            response = {'task':TaskSerializer(task).data ,  'file':TaskAttachmentSerializer(files_response , many=True).data,  'checklist':CheckListSeializer(checklist_response , many=True).data  ,'routine':TaskRountineSerializer(routines_response).data}

            return Response(response)
        
    def update(self, request, *args, **kwargs):
        with transaction.atomic():

            task = Task.objects.get(id=kwargs.get('pk'))

            serializer = TaskSerializer(
                instance=task,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)

            task = serializer.save()

            data = serializer.validated_data

            is_routine = data.get("is_routine", False)
            files_data = data.get('files', [])
            checklist_data = data.get('checklist', [])

            routines = None
            routines_response = None

            if is_routine:
                routines = data.get("routines", [])

            TaskRoutine.objects.filter(task=task).delete()
            TaskAttachment.objects.filter(task=task).delete()
            CheckList.objects.filter(task=task).delete()

            if routines is not None:
                routines_response = self.CreateRoutineTask(task, routines)

            files_response = self.CreateFile(task, files_data, request.user)
            checklist_response = self.CreateCheklist(task, checklist_data)

            response = {
                'task': TaskSerializer(task).data,
                'file': TaskAttachmentSerializer(files_response, many=True).data,
                'checklist': CheckListSeializer(checklist_response, many=True).data,
                'routine': TaskRountineSerializer(routines_response).data if routines_response else None
            }

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
  
    def CreateChat(self ,title ,task , user):
        conversation = Conversation.objects.create(
            type="group",
            title=title,
            task=task,
            created_by=user
        )

        return conversation

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
    
class ForwardTaskView(APIView):

    def post(self, request, task_id, *args, **kwargs):

        with transaction.atomic():

            

            task = get_object_or_404(Task, id=task_id)

            assigned_to_id = request.data.get("assigned_to")
            can_forward = task.can_forward

            if  not can_forward:
                return Response({'message':'این تسک نمیتواند به فرد دیگری منتقل گردد'})
            
            status = Status.objects.filter(id=6).first()


            task.status = status
            task.save()


            if assigned_to_id:
                assigned_to = User.objects.filter(id=assigned_to_id).first()



            # root task
            root = task.root_task if task.root_task else task

            new_task = Task.objects.create(
                group=task.group,
                title=task.title,
                description=task.description,
                priority=task.priority,
                is_routine=task.is_routine,
                forwarded_by=request.user,

                planned_start_at=task.planned_start_at,
                deadline=task.deadline,

                assigned_to=assigned_to ,
                status_id  =1,

                start_time=None,
                end_time=None,
                quality_rate=None,

                parent_id=task,
                root_task=root,

                can_forward=task.can_forward,

                created_by=task.created_by
            )

            return Response({
                "message": "تسک با موفقیت منتقل شد ",
                "task_id": new_task.id
            }, status=s.HTTP_201_CREATED)


#data :

class UsersTask(APIView):
    def get(self, request, *args, **kwargs):

        project_id = request.query_params.get("project_id")

        users = User.objects.all()

        response = []

        for user in users:

            task_filter = Q(task_assignments__assigned_to=user)

            # optional project filter
            if project_id:
                task_filter &= Q(
                    task_assignments__group__subproject__project_id=project_id
                )

            tasks = (
                Status.objects
                .annotate(
                    count=Count(
                        "task_assignments",
                        filter=task_filter
                    )
                )
                .values("id", "title", "count")
            )

            profile = getattr(user, "Profile", None)

            response.append({
                "user": user.id,
                "first_name": getattr(profile, "first_name", None),
                "last_name": getattr(profile, "last_name", None),
                "username": user.username,
                "phone": getattr(profile, "phone", None),
                "task": list(tasks)
            })

        return Response(response)


class TaskDataView(APIView):
    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id")

        task_filter = Q()

        # optional project filter
        if project_id:
            task_filter &= Q(
                task_assignments__group__subproject__project_id=project_id
            )

        # permission filter
        if request.user.role != "owner":
            task_filter &= Q(task_assignments__assigned_to=request.user)

        data = (
            Status.objects
            .annotate(
                count=Count(
                    "task_assignments",
                    filter=task_filter
                )
            )
            .values("id", "title", "count")
        )

        return Response(data)

class EmergencyTask(APIView):
    def get(self, request):
        now = timezone.now()
        two_days_later = now + timedelta(days=2)

        project_id = request.query_params.get("project_id")

        # base query
        tasks = Task.objects.filter(
            deadline__gte=now,
            deadline__lte=two_days_later,
        ).exclude(status__id=3)

        # optional filter
        if project_id:
            tasks = tasks.filter(
                group__subproject__project_id=project_id
            )

        # permission filter
        if request.user.role != "owner":
            tasks = tasks.filter(assigned_to=request.user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskGroupPerson(APIView):

    STATUSES = [
        "شروع نشده",
        "درحال انجام",
        "انجام شده",
        "کنسل شده",
    ]

    def empty_status_dict(self):
        return {
            status.title: []
            for status in Status.objects.all()
        }

    def task_data(self, task):
        return {
            "id": task.id,
            "title": task.title,
            "assigned": {
                "name": task.assigned_to.username,
                "first_nme": task.assigned_to.Profile.first_name,
                "last_name": task.assigned_to.Profile.last_name,
                "avatar": (
                    task.assigned_to.Profile.avatar.url
                    if task.assigned_to.Profile.avatar
                    else None
                ),

            } if task.assigned_to else None,
            "priority": task.priority,
            "date": task.deadline,
        }

    def get(self, request, *args, **kwargs):

        response = {}

        # personal
        personal = {
            "title": "شخصی",
            "tasks": self.empty_status_dict()
        }

        my_tasks = (
            Task.objects
            .select_related("status", "assigned_to")
        )

        for task in my_tasks:
            personal["tasks"][task.status.title].append(
                self.task_data(task)
            )

        response["personal"] = personal

        # groups
        groups = (
            Group.objects
            .filter(members=request.user)
            .prefetch_related(
                "tasks",
                "tasks__status",
                "tasks__assigned_to",
                "subproject"
            )
        )

        for group in groups:

            group_data = {
                "groupid":group.id,
                "title": group.title,
                "tasks": self.empty_status_dict(),
                "subproject":group.subproject.title
            }

            for task in group.tasks.all():

                group_data["tasks"][task.status.title].append(
                    self.task_data(task)
                )

            response[group.title] = group_data
            

        return Response(response)     
    


class TaskGroupDefined(APIView):
    def get(self, request, chat_id):

        statuses = Status.objects.all()

        data = {
            status.title: []
            for status in statuses
        }

        tasks = (
            Task.objects
            .filter(group__chat_room__id=chat_id)
            .select_related("status", "assigned_to")
        )

        for task in tasks:
            data[task.status.title].append({
                "id": task.id,
                "groupid":task.group.id,
                "title": task.title,
                "assigned": {
                    "name": task.assigned_to.username,
                    "first_name": task.assigned_to.Profile.first_name,
                    "last_name": task.assigned_to.Profile.last_name,
                    "avatar": (
                        task.assigned_to.Profile.avatar.url
                        if task.assigned_to.Profile.avatar
                        else None
                    ),
                } if task.assigned_to else None,
                "priority": task.priority,
                "date": task.deadline,
            })

        return Response(data)     


# Create your views here.
