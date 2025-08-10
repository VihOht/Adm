from datetime import timedelta

from django.db import models
from django.utils import timezone

from Adm import settings


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def is_expired(self):
        """Check if conversation is older than 10 minutes"""
        return timezone.now() - self.updated_at > timedelta(minutes=10)

    def deactivate_if_expired(self):
        """Deactivate conversation if it's expired"""
        if self.is_expired():
            self.is_active = False
            self.save()
            return True
        return False

    @classmethod
    def get_or_create_active_conversation(cls, user):
        """Get active conversation or create new one if expired"""
        # Get the most recent conversation
        conversation = cls.objects.filter(user=user, is_active=True).first()

        if conversation and not conversation.is_expired():
            return conversation

        # Deactivate expired conversation if exists
        if conversation:
            conversation.is_active = False
            conversation.save()

        # Create new conversation
        return cls.objects.create(user=user)


class Message(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return (
            f"{self.sender}: {self.content[:50]}..."
            if len(self.content) > 50
            else f"{self.sender}: {self.content}"
        )
