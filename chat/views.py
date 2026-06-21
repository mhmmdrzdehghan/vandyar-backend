from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView , UpdateAPIView
from .serializer import MessageSerializer , UpdateConversationSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Message , Conversation , ConversationMember
from .serializer import ConversationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from account.models import User
from group.models import Group
from rest_framework import status
from django.db.models import Q
from notification.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from django.shortcuts import get_object_or_404


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

        serializer = MessageSerializer(messages, many=True ,context={"request": request})

        return Response(serializer.data)

class DirectConversationView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        user2_id = request.data.get("user_id")

        user1 = request.user
        user2 = User.objects.get(id=user2_id)

        title = f"{user1.Profile.first_name}-{user2.Profile.first_name}"

        conversation = (
            Conversation.objects
            .filter(type="direct")
            .filter(members__user=user1)
            .filter(members__user=user2)
            .distinct()
            .first()
        )

        if conversation:
            return Response({
                "conversation_id": conversation.id
            })

        conversation = Conversation.objects.create(
            type="direct",
            created_by=user1,
            title=title
        )

        ConversationMember.objects.bulk_create([
            ConversationMember(
                conversation=conversation,
                user=user1
            ),
            ConversationMember(
                conversation=conversation,
                user=user2
            )
        ])

        return Response({
            "conversation_id": conversation.id
        })

class ConversationMemberView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, conversation_id):
        """
        Add member
        """
        serializer = UpdateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        users = serializer.validated_data['users']

        group_users = Group.objects.filter(
            chat_room__id=conversation_id
        ).values_list("members", flat=True)

        group_users = set(group_users)
        users = set(users)

        users_to_add = users - group_users

        group = get_object_or_404(
            Group,
            chat_room__id=conversation_id
        )

        group.members.add(*users_to_add)


        conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )


        for user_id in users_to_add:
            ConversationMember.objects.get_or_create(
                conversation=conversation,
                user_id=user_id,
            )

    
        return Response(
            {"detail": "کاربر با موفقیت اضافه شد"},
            status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def delete(self, request, conversation_id):
        """
        Remove member
        """

        serializer = UpdateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        users = serializer.validated_data['users']

        for user in users:

            chattitle = Conversation.objects.filter(id=conversation_id).first().title


            deleted, _ = ConversationMember.objects.filter(
                conversation_id=conversation_id,
                user_id=user
            ).delete()

            self.CreateNotification(user , "حذف از چت!" , f"شما از چت {chattitle} پاک شدید")


        return Response(
            {"detail": "کاربر با موفقیت حذف شد"},
            status=status.HTTP_200_OK
        )


    def CreateNotification(self, recipient, title, message):

        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"notification_{recipient.id}",
            {
                "type": "send_notification",
                "id": notification.id,
                "title": title,
                "message": message,
                "created_at": notification.created_at.isoformat(),
            }
        )

        return notification
class ConversationData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        conversations = (
        Conversation.objects
        .filter(
            members__user=request.user
        )
        .filter(
            Q(group__isnull=False) |
            Q(type="direct")
        )
        .distinct()
    )

        serializer = ConversationSerializer(
            conversations,
            many=True,
            context={"request": request}

        )

        return Response(serializer.data)
        
    