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

            for member in members:
                if not subproject.members.filter(id=member.id).exists():
                    subproject.members.add(member)

            title = f"{group.title}-چت"

            conversation = Conversation.objects.create(
                type="group",
                title=title,
                group=group,
                created_by=request.user
            )

            admins = User.objects.filter(role='owner')

            # ----------------------------
            # owners (safe)
            # ----------------------------
            for admin in admins:
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=admin,
                    defaults={"is_admin": True}
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

        return Response(GroupSerializer(group).data)