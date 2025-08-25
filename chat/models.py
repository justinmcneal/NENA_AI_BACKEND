from django.db import models
from django.conf import settings
import uuid

class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'chat_messages'
    )
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    message_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_from_user = models.BooleanField(default=True) # True for user message, False for AI response

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"Conversation {self.conversation_id} - {self.user.username}: {self.message_text[:50]}..."
