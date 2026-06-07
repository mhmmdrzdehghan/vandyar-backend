from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializer import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Message , Conversation
from .serializer import ConversationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
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



class ConversationData(APIView):
    def get(self, request, *args, **kwargs):


        conversations = Conversation.objects.filter(
            members__user=request.user
        ).distinct()

        return Response(ConversationSerializer(conversations , many=True).data)
        
    