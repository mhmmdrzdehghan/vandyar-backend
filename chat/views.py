from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from .serializer import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Message , Conversation
from .serializer import ConversationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.


# class MessageView(ModelViewSet):

#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         conversation_id = self.kwargs["conversation_id"]

#         return serializer.save(conversation_id=conversation_id ,sender=self.request.user)
    

#     def get_queryset(self):
#         conversation_id = self.kwargs["conversation_id"]
#         return Message.objects.filter(sender=self.request.user ,conversation=conversation_id)



class TaskConversationListView(APIView):
    def get(self, request):
        conversations = Conversation.objects.filter(task__isnull=False)

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)



class GroupConversationListView(APIView):
    def get(self, request):
        conversations = Conversation.objects.filter(group__isnull=False)

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class ConversationMessagesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        if not Conversation.objects.filter(
            id=conversation_id,
            members__user=request.user
        ).exists():
            return Response({"detail": "Forbidden"}, status=403)

        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related(
            "sender",
            "task"
        ).prefetch_related(
            "reactions__user"
        ).order_by("created_at")

        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data)




class ConversationData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        conversations = (
            Conversation.objects
            .filter(members__user=request.user ,group__isnull=False)
            .select_related("created_by", "group", "task")
            .distinct()
        )

        serializer = ConversationSerializer(
            conversations,
            many=True
        )

        return Response(serializer.data)
        
    