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

                # ----------------------------
                # safe membership (NO duplicates)
                # ----------------------------
                group.members.set(members)
                group.members.add(*managers)
                group.members.add(*group_members)

                sub.members.add(*group_members)

                # ----------------------------
                # create conversation
                # ----------------------------
                conversation = Conversation.objects.create(
                    type="group",
                    title=f"{group.title}-چت",
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


    




        

