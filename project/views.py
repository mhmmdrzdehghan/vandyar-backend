from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializer import ProjectSerializer , SubProjectSerializer
from .models import SubProject , Project
from rest_framework.response import Response
from chat.models import Conversation
from django.db import transaction
from chat.models import ConversationMember
from chat.serializer import ConversationMemberSerializer

class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)


    queryset = Project.objects.all()



class SubProjetView(ModelViewSet):
    serializer_class = SubProjectSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):

        serializer = SubProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        members = validated_data.pop("members", [])
        managers = validated_data.pop("managers", [])


        with transaction.atomic():

            sub = SubProject.objects.create(
                **validated_data,
                created_by=request.user
            )

            if members:
                sub.members.set(members)

            if managers:
                sub.managers.set(managers)



            project = sub.project
            title = f"{project.title} - {sub.title}"

            conversation = Conversation.objects.create(
                type="group",
                title=title,
                subproject=sub,
                created_by=request.user
            )

            ConversationMember.objects.create(
                conversation=conversation,
                user=request.user,
                is_admin=True
            )


            for manager in sub.managers.all():
                ConversationMember.objects.create(
                conversation=conversation,
                user=manager,
                is_admin=True
            )


            for member in sub.members.all():
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=member
                )

        return Response(SubProjectSerializer(sub).data)





        

