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
    """
    Retrieves relevant information from the knowledge base.
    1. Tries to find an exact match for a question in the FAQ section.
    2. If no FAQ match, searches for a product name in the query.
    3. If no product match, returns an empty string.
    """
    import difflib
    query_lower = query.strip().lower()
    lines = KNOWLEDGE_BASE.splitlines()

    # 1. FAQ Retrieval (fuzzy matching)
    in_faq_section = False
    faq_questions = []
    faq_answers = []
    for i, line in enumerate(lines):
        if "[frequently asked questions (faqs)]" in line.lower():
            in_faq_section = True
            continue
        if in_faq_section:
            if line.lower().startswith("question:"):
                question_text = line.split("Question:", 1)[-1].strip().lower()
                faq_questions.append((i, question_text))
            if line.lower().startswith("answer:"):
                answer_text = line.split("Answer:", 1)[-1].strip()
                faq_answers.append((i, answer_text))

    # Find the best matching question using difflib
    best_score = 0
    best_answer = ""
    for q_idx, question_text in faq_questions:
        score = difflib.SequenceMatcher(None, query_lower, question_text).ratio()
        if query_lower in question_text or question_text in query_lower:
            score += 0.2  # boost for substring match
        if score > best_score and score > 0.6:  # threshold for fuzzy match
            # Find the next answer after this question
            for a_idx, answer_text in faq_answers:
                if a_idx > q_idx:
                    best_score = score
                    best_answer = answer_text
                    break
    if best_answer:
        return best_answer
    
    # 2. Product Retrieval
    in_product_section = False
    product_info_lines = []
    for i, line in enumerate(lines):
        if "[bpi loan products]" in line.lower():
            in_product_section = True
            continue
        if "[frequently asked questions (faqs)]" in line.lower():
            in_product_section = False
            break
        if in_product_section:
            product_info_lines.append(line)

    # Split product info into individual products
    products = []
    current_product = []
    for line in product_info_lines:
        if line.lower().startswith("product name:") and current_product:
            products.append("\n".join(current_product))
            current_product = [line]
        else:
            current_product.append(line)
    if current_product:
        products.append("\n".join(current_product))

    for product in products:
        product_lines = product.splitlines()
        if product_lines:
            product_name_line = product_lines[0]
            if product_name_line.lower().startswith("product name:"):
                product_name = product_name_line.split("Product Name:", 1)[-1].strip().lower()
                if product_name in query_lower:
                    return product

    return ""

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

            # If an exact answer is found in FAQ, return it directly
            if relevant_info and user_message.lower() in KNOWLEDGE_BASE.lower():
                 response_data = {'reply': relevant_info}
                 response_serializer = ChatResponseSerializer(data=response_data)
                 response_serializer.is_valid(raise_exception=True)
                 return Response(response_serializer.data, status=status.HTTP_200_OK)

            # 2. Construct the prompt for the language model
            if relevant_info:
                prompt = f"""
Ikaw si NENA AI, isang napaka-friendly, matalino, at maaasahang financial assistant mula sa BPI. Sagutin mo ang tanong ng user sa Filipino, simple at malinaw, parang kausap mo siya sa personal. Gamitin ang impormasyon mula sa knowledge base kung makakatulong. Kung may English na tanong, sagutin mo pa rin sa Filipino at ipaliwanag ng mabuti. Bigyan mo ng inspirasyon at kumpiyansa ang user sa bawat sagot mo.

Impormasyon mula sa knowledge base:
{relevant_info}

Tanong ng User: {user_message}

Mabait na Sagot ni NENA AI sa Filipino:"""
            else:
                # If no relevant info is found, ask the user to rephrase or ask about something else.
                # This avoids hallucination.
                ai_reply = "Pasensya na, hindi ko mahanap ang impormasyon tungkol diyan. Maaari mo bang subukang magtanong sa ibang paraan, o magtanong tungkol sa aming mga produkto at serbisyo?"
                response_data = {'reply': ai_reply}
                response_serializer = ChatResponseSerializer(data=response_data)
                response_serializer.is_valid(raise_exception=True)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

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
