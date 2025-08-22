from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer, ChatResponseSerializer

class ChatView(APIView):
    """
    Handles chat messages from the user and returns a response from the AI.
    """
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data['message']

            # --- AI LOGIC GOES HERE ---
            # This is where you would integrate with your AI model (Mistral, LangChain, etc.)
            # For now, we will return a simple, simulated response.

            ai_reply = f"You said: '{user_message}'. This is a placeholder response from NENA AI."

            # --------------------------

            response_data = {'reply': ai_reply}
            response_serializer = ChatResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True) # Should always be valid

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)