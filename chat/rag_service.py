import os
from django.conf import settings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFacePipeline
from langchain.chains.question_answering import load_qa_chain
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class RAGService:
    def __init__(self):
        self.vector_store = None
        self.chain = None
        self._initialize_rag()

    def _initialize_rag(self):
        knowledge_base_path = os.path.join(settings.BASE_DIR, 'chat', 'knowledge_base.txt')
        if not os.path.exists(knowledge_base_path):
            # Handle case where knowledge base is missing
            return

        # 1. Load and split documents
        loader = TextLoader(knowledge_base_path, encoding='utf-8')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)

        # 2. Create embeddings and vector store
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = FAISS.from_documents(docs, embeddings)

        # 3. Initialize LLM and QA chain
        model_name = "google/flan-t5-small"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
        llm = HuggingFacePipeline(pipeline=pipe)

        self.chain = load_qa_chain(llm, chain_type="stuff")

    def get_response(self, query: str, chat_history: list):
        if not self.vector_store or not self.chain:
            return "Sorry, the RAG service is not initialized. The knowledge base might be missing."

        # Format chat history for context (optional, but can be helpful)
        # history_str = "\n".join([f"{('User' if msg.is_from_user else 'NENA AI')}: {msg.message_text if msg.is_from_user else msg.response_text}" for msg in chat_history])

        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(query, k=3)

        # Generate response
        # The chat history is not directly used in the chain anymore, but was retrieved for potential future use.
        response = self.chain(
            {"input_documents": docs, "question": query},
            return_only_outputs=True
        )
        return response['output_text']

# Instantiate the service so it's loaded on startup
rag_service = RAGService()