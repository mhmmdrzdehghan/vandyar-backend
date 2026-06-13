from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .serializer import GroupSerializer
from chat.models import Conversation , ConversationMember
from rest_framework.response import Response
from django.db import transaction
from account.models import User
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status



class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()


    def create(self, request, *args, **kwargs):

        with transaction.atomic():

            serializer = GroupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data
            members = validated_data.pop("members", [])

            group = Group.objects.create(
                created_by=request.user,
                **validated_data
            )

            if members:
                group.members.set(members)

            subproject = group.subproject
            project = subproject.project

            for member in members:
                if not subproject.members.filter(id=member.id).exists():
                    subproject.members.add(member)

            title = f"{group.title}-{subproject.title}-{project.title}"

            conversation = Conversation.objects.create(
                type="group",
                title=title,
                group=group,
                created_by=request.user
            )

            admins = User.objects.filter(role="owner")

            # ----------------------------
            # owners (safe)
            # ----------------------------
            for admin in admins:
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=admin,
                    defaults={"is_admin": True}
                )


                # NOTIFICATIONS
                self.CreateNotification(
                    admin,
                    "گروه جدید ایجاد شد",
                    f"گروه {group.title} در زیر پروژه {subproject.title} ایجاد شد"
                )

            # ----------------------------
            # creator (safe)
            # ----------------------------
            ConversationMember.objects.get_or_create(
                conversation=conversation,
                user=request.user,
                defaults={"is_admin": True}
            )

            # ----------------------------
            # group members (safe)
            # ----------------------------
            for member in group.members.all():
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=member,
                    defaults={"is_admin": False}
                )

                # NOTIFICATIONS
                self.CreateNotification(
                    member,
                    "شما به یک گروه اضافه شدید",
                    f"شما به گروه {group.title} در زیر پروژه {subproject.title} اضافه شدید"
                )


        return Response(
            GroupSerializer(group).data,
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
         