from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer, ChatResponseSerializer
import os
import logging
import threading
from transformers import AutoTokenizer, AutoModelForCausalLM
from rest_framework.permissions import AllowAny

# --- AI Model and Knowledge Base Loading ---


# Health check for knowledge base
def check_knowledge_base():
    file_path = os.path.join(settings.BASE_DIR, 'chat', 'knowledge_base.txt')
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        logging.error("Knowledge base file is missing or empty!")
        return False
    return True

knowledge_base_ok = check_knowledge_base()

# Health check for model
def check_model():
    try:
        print("Loading GPT2 Tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token # Set pad token
        print("GPT2 Tokenizer Loaded.")
        print("Loading GPT2 Model...")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        print("GPT2 Model Loaded.")
        return tokenizer, model, True
    except Exception as e:
        logging.exception("Model failed to load: %s", e)
        return None, None, False

TOKENIZER, MODEL, model_ok = check_model()

def load_knowledge_base():
    """Loads the knowledge base from the text file."""
    file_path = os.path.join(settings.BASE_DIR, 'chat', 'knowledge_base.txt')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Knowledge base not found."

KNOWLEDGE_BASE = load_knowledge_base()

# --- Simple Retriever ---
def retrieve_relevant_info(query):
    """A simple keyword-based retriever to find relevant info from the knowledge base."""
    query_words = set(query.lower().split())
    best_match = ""
    max_score = 0

    # Split the knowledge base into sections
    sections = KNOWLEDGE_BASE.split('\n\n')
    for section in sections:
        section_words = set(section.lower().split())
        score = len(query_words.intersection(section_words))
        if score > max_score:
            max_score = score
            best_match = section

    return best_match

class ChatView(APIView):
    """
    Handles chat messages from the user and returns a response from the AI.
    """
    permission_classes = [AllowAny]

    def post(self, request):
            serializer = ChatRequestSerializer(data=request.data)
            if not knowledge_base_ok:
                return Response({'reply': 'Sorry, the knowledge base is missing or empty.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            if not model_ok:
                return Response({'reply': 'Sorry, the AI model failed to load.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            if serializer.is_valid():
                user_message = serializer.validated_data['message']
                # Input validation & sanitization
                if not user_message or not user_message.strip():
                    return Response({'reply': 'Pakilagay ang iyong tanong.'}, status=status.HTTP_400_BAD_REQUEST)
                user_message = user_message.strip()
                # Optionally limit message length (not truncating, just warning)
                if len(user_message) > 512:
                    logging.warning('User message is very long.')

                # 1. Retrieve relevant information from the knowledge base
                relevant_info = retrieve_relevant_info(user_message)
                if not relevant_info:
                    relevant_info = "Walang karagdagang impormasyon mula sa knowledge base."

                # 2. Construct the prompt for the language model
                prompt = f"""
Ikaw si NENA AI, isang napaka-friendly, matalino, at maaasahang financial assistant mula sa BPI. Sagutin mo ang tanong ng user sa Filipino, simple at malinaw, parang kausap mo siya sa personal. Gamitin ang impormasyon mula sa knowledge base kung makakatulong. Kung may English na tanong, sagutin mo pa rin sa Filipino at ipaliwanag ng mabuti. Bigyan mo ng inspirasyon at kumpiyansa ang user sa bawat sagot mo.

Impormasyon mula sa knowledge base:
{relevant_info}

Tanong ng User: {user_message}

Mabait na Sagot ni NENA AI sa Filipino:"""
                # Truncate prompt to avoid tokenization errors (GPT-2 max length is 1024)
                max_length = 1024
                prompt = prompt[:max_length]

                # --- AI LOGIC GOES HERE ---
                # Model inference with timeout
                ai_reply = None
                def run_model():
                    nonlocal ai_reply
                    try:
                        inputs = TOKENIZER.encode_plus(prompt, return_tensors='pt', padding=True)
                        outputs = MODEL.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=100, num_return_sequences=1)
                        raw_ai_reply = TOKENIZER.decode(outputs[0], skip_special_tokens=True)
                        # Extract only the answer part, using the last occurrence of 'Answer:'
                        answer_prefix = "Answer:"
                        if answer_prefix in raw_ai_reply:
                            ai_reply = raw_ai_reply.rsplit(answer_prefix, 1)[-1].strip()
                        else:
                            ai_reply = raw_ai_reply.strip()
                        # Remove excessive newlines, spaces, and repeated phrases
                        ai_reply = " ".join(ai_reply.split())
                        # Remove repeated answer if present
                        if ai_reply.lower().startswith(user_message.lower()):
                            ai_reply = ai_reply[len(user_message):].strip()
                    except Exception as e:
                        logging.exception("AI model error: %s", e)
                        ai_reply = None

                # Run model with timeout
                thread = threading.Thread(target=run_model)
                thread.start()
                thread.join(timeout=10)  # 10 seconds timeout
                if ai_reply is None:
                    # Graceful fallback
                    ai_reply = "Pasensya na, may problema sa AI model. Subukan muli o magtanong ng iba."

                response_data = {'reply': ai_reply}
                response_serializer = ChatResponseSerializer(data=response_data)
                response_serializer.is_valid(raise_exception=True)

                return Response(response_serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
