from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import ChatRequestSerializer, ChatResponseSerializer
from .models import ChatMessage
from .rag_service import rag_service # Import the singleton instance
import uuid
from django.contrib.auth import get_user_model

class ChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']
        conversation_id_str = serializer.validated_data.get('conversation_id')

        # Determine conversation_id
        if conversation_id_str:
            if isinstance(conversation_id_str, uuid.UUID):
                conversation_id = conversation_id_str
            else:
                conversation_id = uuid.UUID(str(conversation_id_str))
        else:
            conversation_id = uuid.uuid4()

        # Get or create a guest user if not authenticated
        if request.user.is_authenticated:
            user = request.user
        else:
            User = get_user_model()
            user, _ = User.objects.get_or_create(username='chatbot_guest')

        # Save user message
        ChatMessage.objects.create(
            user=user,
            conversation_id=conversation_id,
            message_text=user_message,
            is_from_user=True
        )

        # Get chat history
        chat_history = ChatMessage.objects.filter(
            conversation_id=conversation_id
        ).order_by('timestamp')

        # Get response from RAG service
        ai_reply = rag_service.get_response(query=user_message, chat_history=list(chat_history))

        # Save AI response
        ChatMessage.objects.create(
            user=user,
            conversation_id=conversation_id,
            response_text=ai_reply,
            is_from_user=False
        )

        response_data = {'reply': ai_reply, 'conversation_id': str(conversation_id)}
        response_serializer = ChatResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
