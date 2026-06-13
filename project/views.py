from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializer import ProjectSerializer , SubProjectSerializer
from .models import Project , SubProject
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from group.models import Group
from django.db import transaction
from django.db.models import Count
from chat.models import Conversation , ConversationMember
from account.models import User
from rest_framework import status
from notification.models import Notification
from task.models import Task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from task.models import Status
from task.serializer import StatusSerializer


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        response =  super().create(request, *args, **kwargs)
        owners   =  User.objects.filter(role = 'owner')
        title_project = response.data['title']

        message = f"یک پروژه با نام {title_project} ایجاد شد "

        for owner in owners :
            
            self.CreateNotification(owner ,"پروژه ی جدید ایجاد شد !!" , message)

        return response

        



    

    def CreateNotification(self, recipient, title, message):

        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"notification_{recipient.id}",
            {
                "type": "send_notification",
                "id": notification.id,
                "title": title,
                "message": message,
                "created_at": notification.created_at.isoformat(),
            }
        )

        return notification
        


    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)



class SubProjetView(ModelViewSet):
    serializer_class = SubProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = SubProject.objects.all()

    # ----------------------------
    # helper: normalize input to queryset
    # ----------------------------
    def get_users_qs(self, value):
        if not value:
            return User.objects.none()

        # already queryset
        if hasattr(value, "filter"):
            return value

        # list of User objects
        if isinstance(value[0], User):
            value = [u.id for u in value]

        return User.objects.filter(id__in=value)

    # ----------------------------
    # create subproject
    # ----------------------------
    def create(self, request, *args, **kwargs):

        with transaction.atomic():

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data

            # ----------------------------
            # normalize inputs
            # ----------------------------
            members = self.get_users_qs(data.pop("members", []))
            managers = self.get_users_qs(data.pop("managers", []))
            groups = data.pop("groups", [])

            # ----------------------------
            # create subproject
            # ----------------------------
            sub = SubProject.objects.create(
                created_by=request.user,
                **data
            )

            sub.members.set(members)
            sub.managers.set(managers)

            owners = User.objects.filter(role="owner")

            # ----------------------------
            # create groups
            # ----------------------------
            for group_data in groups:

                group_members = self.get_users_qs(
                    group_data.get("members", [])
                )

                group = Group.objects.create(
                    title=group_data.get("title"),
                    description=group_data.get("description"),
                    subproject=sub,
                    created_by=request.user
                )

                group.members.add(*group_members)

                sub.members.add(*group_members)


                # ----------------------------
                # create conversation
                # ----------------------------

                subproject = group.subproject
                project = subproject.project

                title = f"{group.title}-{subproject.title}-{project.title}"
 
                conversation = Conversation.objects.create(
                    type="group",
                    title=title,
                    group=group,
                    created_by=request.user
                )

                # ----------------------------
                # owners (admin)
                # ----------------------------
                for owner in owners:
                    ConversationMember.objects.get_or_create(
                        conversation=conversation,
                        user=owner,
                        defaults={"is_admin": True}
                    )

                # ----------------------------
                # managers (admin)
                # ----------------------------
                for manager in managers:
                    ConversationMember.objects.get_or_create(
                        conversation=conversation,
                        user=manager,
                        defaults={"is_admin": True}
                    )

                # ----------------------------
                # members (non-admin)
                # ----------------------------
                for member in group_members:
                    ConversationMember.objects.get_or_create(
                        conversation=conversation,
                        user=member,
                        defaults={"is_admin": False}
                    )

                # ----------------------------
                # notification for group members
                # ----------------------------
                for member in group_members:
                    self.CreateNotification(
                        member,
                        "شما به یک گروه اضافه شدید",
                        f"شما به گروه {group.title} در زیر پروژه {sub.title} اضافه شدید"
                    )

            # =====================================================
            # SUBPROJECT NOTIFICATIONS
            # =====================================================

            # اطلاع به owner ها
            for owner in owners:
                self.CreateNotification(
                    owner,
                    "زیر پروژه جدید ایجاد شد",
                    f"یک زیر پروژه با نام {sub.title} ایجاد شد"
                )

            # اطلاع به manager ها
            for manager in set(managers):
                self.CreateNotification(
                    manager,
                    "شما سرگروه یک زیر پروژه شدید",
                    f"شما به عنوان سرگروه در زیر پروژه {sub.title} اضافه شدید"
                )

            # اطلاع به member ها
            for member in set(members):
                self.CreateNotification(
                    member,
                    "شما به یک زیر پروژه اضافه شدید",
                    f"شما به زیر پروژه {sub.title} اضافه شدید"
                )

        return Response(
            self.get_serializer(sub).data,
            status=status.HTTP_201_CREATED
        )

    def CreateNotification(self, recipient, title, message):

        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"notification_{recipient.id}",
            {
                "type": "send_notification",
                "id": notification.id,
                "title": title,
                "message": message,
                "created_at": notification.created_at.isoformat(),
            }
        )

        return notification
         
#data:
class ProjectDataView(APIView):

    def get(self, request, *args, **kwargs):

        project_id = kwargs.get('project_id')

        if project_id:
            project = Project.objects.prefetch_related(
                'subprojects__groups'
            ).get(id=project_id)

            serializer = ProjectSerializer(project)
            return Response(serializer.data)

        projects = Project.objects.prefetch_related(
            'subprojects__groups'
        ).all()

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

class SubProjectReport(APIView):
    def get(self, request, *args, **kwargs):
        subproject_id = kwargs.get('subproject_id')
        sub          = SubProject.objects.filter(id=subproject_id).prefetch_related("groups").first()
        groupCount   = sub.groups.count()
        membercount  = sub.members.count() 
        managercount  = sub.managers.count() 

        # task = Task.objects.filter(group__subproject__id=subproject_id).values('status__title' , 'status__id').annotate(count=Count("id"))
        statuses = Status.objects.filter(
            task_assignments__group__subproject_id=subproject_id
        ).annotate(
            count=Count("task_assignments")
        )

        response = {
                    'groupCount':groupCount ,
                    'membercount':membercount , 
                    'managercount':managercount,
                    'subproject':SubProjectSerializer(sub).data,
                    "statusdata":StatusSerializer(statuses , many=True).data

                    }

        return Response(response)




        

