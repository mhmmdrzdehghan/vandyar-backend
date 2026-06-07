from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializer import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Message
# Create your views here.


class MessageView(ModelViewSet):

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_id"]

        return serializer.save(conversation_id=conversation_id ,sender=self.request.user)
    

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]
        return Message.objects.filter(sender=self.request.user ,conversation=conversation_id)


    