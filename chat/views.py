from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer, ChatResponseSerializer
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from rest_framework.permissions import AllowAny

# --- AI Model and Knowledge Base Loading ---

# Load the tokenizer and model once when the server starts
print("Loading GPT2 Tokenizer...")
TOKENIZER = AutoTokenizer.from_pretrained("gpt2")
TOKENIZER.pad_token = TOKENIZER.eos_token # Set pad token
print("GPT2 Tokenizer Loaded.")

print("Loading GPT2 Model...")
MODEL = AutoModelForCausalLM.from_pretrained("gpt2")
print("GPT2 Model Loaded.")

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
        if serializer.is_valid():
            user_message = serializer.validated_data['message']

            # 1. Retrieve relevant information from the knowledge base
            relevant_info = retrieve_relevant_info(user_message)

            # 2. Construct the prompt for the language model
            prompt = f"""You are NENA AI, a friendly and helpful financial assistant from BPI.
            Based on the following information, answer the user's question concisely.
            
            Information:
            {relevant_info}
            
            User's Question: {user_message}
            
            Answer:"""

            # --- AI LOGIC GOES HERE ---
            # Generate a response using the loaded language model
            try:
                inputs = TOKENIZER.encode_plus(prompt, return_tensors='pt', padding=True)
                outputs = MODEL.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=100, num_return_sequences=1)
                raw_ai_reply = TOKENIZER.decode(outputs[0], skip_special_tokens=True)
                
                # Extract only the answer part
                answer_prefix = "Answer:"
                if answer_prefix in raw_ai_reply:
                    ai_reply = raw_ai_reply.split(answer_prefix, 1)[1].strip()
                else:
                    ai_reply = raw_ai_reply.strip() # Fallback if prefix not found

            except Exception as e:
                ai_reply = f"Sorry, I encountered an error: {e}"
            # --------------------------

            response_data = {'reply': ai_reply}
            response_serializer = ChatResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
