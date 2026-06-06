from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializer import ProjectSerializer , SubProjectSerializer
from .models import SubProject , Project

class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)


    queryset = Project.objects.all()



class SubProjetView(ModelViewSet):
    serializer_class = SubProjectSerializer
    permission_classes = [IsAuthenticated]

    queryset = SubProject.objects.all()

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)




        

