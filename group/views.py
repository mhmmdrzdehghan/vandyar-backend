from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .serializer import GroupSerializer , GroupUpdateSerializer
from chat.models import Conversation , ConversationMember
from rest_framework.response import Response
from django.db import transaction
from account.models import User
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.exceptions import ValidationError , NotFound
from .permission import IsGroupCreatorAllowed


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated ,IsGroupCreatorAllowed]
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
    

    def update(self, request, *args, **kwargs):

        groupid = kwargs.get("pk")

        if not groupid:
            raise ValidationError("something went wrong")

        group = Group.objects.filter(id=groupid).first()

        if not group:
            raise NotFound("group not found")

        serializer = GroupUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # -----------------------------
        # old members snapshot
        # -----------------------------
        old_members = set(group.members.all())

        # -----------------------------
        # update simple fields
        # -----------------------------
        members_data = data.pop("members", None)

        for key, value in data.items():
            setattr(group, key, value)

        group.save()

        # -----------------------------
        # update m2m
        # -----------------------------
        if members_data is not None:
            group.members.set(members_data)

        new_members = set(group.members.all())

        add_members = new_members - old_members
        remove_members = old_members - new_members

        conversation = Conversation.objects.filter(group=group).first()

        title = "آپدیت گروه"

        # -----------------------------
        # added members subproject
        # -----------------------------
        subproject = group.subproject

        for member in add_members:
            if not subproject.members.filter(id=member.id).exists():
                subproject.members.add(member)        


        # -----------------------------
        # added members subproject
        # -----------------------------
        for member in remove_members:
            subproject.members.remove(user)



        

        # -----------------------------
        # added members conversation
        # -----------------------------

        for user in add_members:

            ConversationMember.objects.get_or_create(
                conversation=conversation,
                user=user
            )

            self.CreateNotification(
                user,
                title,
                f"شما به گروه {group.title} اضافه شدید"
            )

        # -----------------------------
        # removed members
        # -----------------------------
        for user in remove_members:

            ConversationMember.objects.filter(
                conversation=conversation,
                user=user
            ).delete()

            self.CreateNotification(
                user,
                title,
                f"شما از گروه {group.title} حذف شدید"
            )

        return Response({
            "message": "گروه با موفقیت ویرایش شد"
        })






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
         