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

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = SubProjectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data =  serializer.validated_data

            members = data.pop('members',[])
            managers = data.pop('managers',[])


            sub = SubProject.objects.create(created_by = request.user ,**data)

            #add member and manager in sub:

            if members:
                sub.members.set(members)

            if managers:
                sub.managers.set(managers)


            #add memeber and manager of sub in group member:    

            group = Group.objects.create(title="گروه مدیریت" ,subproject=sub , created_by = request.user) 
            group.members.set(managers)
            group.members.set(members) 

            
            project = sub.project
            
            title = f"{sub.title}-{group.title}({project})"

            # add members and managers and owners in chat:

            conversation = Conversation.objects.create(
                type="group",
                title=title,
                group=group,
                created_by=request.user
            )

            for manager in sub.managers.all():
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=manager,
                    is_admin=True
                )

            for member in group.members.all():
                ConversationMember.objects.get_or_create(
                    conversation=conversation,
                    user=member
                )   

            admins = User.objects.filter(role = 'owner')
            for admin in admins :
                ConversationMember.objects.get_or_create(conversation=conversation,user=admin)
                
  


        return Response(SubProjectSerializer(sub).data)         


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


    




        

