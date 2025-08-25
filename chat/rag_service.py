import os
from django.conf import settings
from langchain_community.document_loaders import JSONLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFacePipeline
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class RAGService:
    def __init__(self):
        self.vector_store = None
        self.chain = None
        self._initialize_rag()

    def _initialize_rag(self):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        persist_directory = os.path.join(settings.BASE_DIR, 'chat', 'chroma_db')

        self.vector_store = Chroma(
            collection_name="nena_ai_kb",
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )

        if self.vector_store._collection.count() == 0:
            knowledge_base_path = os.path.join(settings.BASE_DIR, 'chat', 'knowledge_base.jsonl')
            if not os.path.exists(knowledge_base_path):
                return

            loader = JSONLoader(
                file_path=knowledge_base_path,
                jq_schema='.',
                content_key='content',
                json_lines=True)
            documents = loader.load()
            self.vector_store.add_documents(documents)
            self.vector_store.persist()

        model_name = "google/flan-t5-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
        llm = HuggingFacePipeline(pipeline=pipe)

        prompt_template = '''
        You are NENA AI, a friendly, smart, and reliable financial assistant from BPI. Your goal is to help users with their loan-related questions. Always answer in Filipino. Be encouraging and confident in your tone.

        Use the following context to answer the user's question.

        Context:
        {context}

        Question: {question}

        Helpful Answer in Filipino:
        '''
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        self.chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)

    def get_response(self, query: str, chat_history: list):
        if not self.vector_store or not self.chain:
            return "Sorry, the RAG service is not initialized. The knowledge base might be missing."

        docs = self.vector_store.similarity_search(query, k=3)

        response = self.chain(
            {"input_documents": docs, "question": query},
            return_only_outputs=True
        )
        return response['output_text']

rag_service = RAGService()