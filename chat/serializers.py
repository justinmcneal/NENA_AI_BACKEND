from rest_framework import serializers
from .models import ChatMessage

class ChatRequestSerializer(serializers.Serializer):
    """
    Validates the incoming message from the user.
    """
    message = serializers.CharField(max_length=4000)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)

class ChatResponseSerializer(serializers.Serializer):
    """
    Formats the outgoing reply from the AI.
    """
    reply = serializers.CharField()
    conversation_id = serializers.UUIDField()

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'conversation_id', 'message_text', 'response_text', 'timestamp', 'is_from_user']
        read_only_fields = ['id', 'timestamp']
