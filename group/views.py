from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .serializer import GroupSerializer
from chat.models import Conversation , ConversationMember
from rest_framework.response import Response
from django.db import transaction


class GroupViewSet(viewsets.ModelViewSet):
    # serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):

        with transaction.atomic():

            serializer = GroupSerializer(data=request.data)
                
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            members = validated_data.pop("members", [])

            
            group = Group.objects.create(created_by=request.user,**validated_data)



            if members:
                group.members.set(members)



            sub = group.subproject
            project = sub.project
            
            title = f"{sub.title}-{group.title}({project})"

            conversation = Conversation.objects.create(
                type="group",
                title=title,
                group=group,
                created_by=request.user
            )

            ConversationMember.objects.create(
                conversation=conversation,
                user=request.user,
                is_admin=True
            )


            for member in group.members.all():
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=member
                )


        return Response(GroupSerializer(group).data)    


