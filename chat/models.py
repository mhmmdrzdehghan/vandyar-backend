from django.db import models
from group.models import Group
from account.models import User

# Create your models here.
class Conversation(models.Model):

    TYPE_CHOICES = (("direct", "Direct"),("group", "Group"),)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255, blank=True, null=True)
    group = models.OneToOneField(Group,on_delete=models.CASCADE,null=True,blank=True,related_name="chat_room")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="created_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title or f"Conversation {self.id}"



class ConversationMember(models.Model):

    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name="members")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="conversations")
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("conversation", "user")
        indexes = [
            models.Index(fields=["conversation", "user"]),
        ]


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    is_task = models.BooleanField()

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["conversation", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.sender} -> {self.conversation_id}"


class MessageReaction(models.Model):

    REACTION_CHOICES = [
        ("like", "👍"),
        ("love", "❤️"),
        ("laugh", "😂"),
        ("wow", "😮"),
        ("sad", "😢"),
        ("angry", "😡"),
    ]

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="message_reactions"
    )

    reaction = models.CharField(
        max_length=20,
        choices=REACTION_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")
        indexes = [
            models.Index(fields=["message"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user} reacted {self.reaction} to {self.message_id}"
