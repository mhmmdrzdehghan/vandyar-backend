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
from chat.models import Conversation , ConversationMember
from account.models import User
from rest_framework import status

class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()


    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)





class SubProjetView(ModelViewSet):
    serializer_class = SubProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = SubProject.objects.all()

    def create(self, request, *args, **kwargs):

        with transaction.atomic():

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data

            members = data.pop("members", [])
            managers = data.pop("managers", [])
            groups = data.pop("groups", [])

            sub = SubProject.objects.create(
                created_by=request.user,
                **data
            )

            # add members and managers to subproject
            sub.members.set(members)
            sub.managers.set(managers)

            owners = User.objects.filter(role="owner")

            # create groups and conversations
            for group_data in groups:

                group = Group.objects.create(
                    title=group_data.get('title'),
                    description=group_data.get('description'),
                    subproject=sub,
                    created_by=request.user
                )

                # add both managers and members

                group_members = group_data.get('members', [])

                group.members.add(*members)
                group.members.add(*managers)
                group.members.add(group_members)

                sub.members.add(*group_members)


                conversation = Conversation.objects.create(
                    type="group",
                    title=f"{group.title}-چت",
                    group=group,
                    created_by=request.user
                )

                # managers -> admins
                for manager in managers:
                    ConversationMember.objects.get_or_create(
                        conversation=conversation,
                        user=manager,
                        defaults={
                            "is_admin": True
                        }
                    )

                # group members
                for member in group.members.all():
                    ConversationMember.objects.get_or_create(
                        conversation=conversation,
                        user=member
                    )

                # owners
                for owner in owners:
                    ConversationMember.objects.get_or_create(
                        conversation=conversation,
                        user=owner,
                        defaults={
                            "is_admin": True
                        }
                    )

        return Response(
            self.get_serializer(sub).data,
            status=status.HTTP_201_CREATED
        )

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


    




        

