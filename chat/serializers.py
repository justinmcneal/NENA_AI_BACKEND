from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    """
    Validates the incoming message from the user.
    """
    message = serializers.CharField(max_length=4000)

class ChatResponseSerializer(serializers.Serializer):
    """
    Formats the outgoing reply from the AI.
    """
    reply = serializers.CharField(max_length=4000)