import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from utils.config import Config

class RAGEngine:
    def __init__(self, persist_directory=None):
        self.persist_directory = persist_directory or Config.CHROMA_DB_PATH
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vector_db = None
        self._initialize_db()

    def _initialize_db(self):
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

    def ingest_json_data(self, file_path, category):
        """Ingests data from a JSON file into the vector database."""
        if not os.path.exists(file_path):
            return False, f"File {file_path} not found."

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []
        for item in data:
            content = f"Category: {category}\n"
            for key, value in item.items():
                content += f"{key}: {value}\n"
            
            documents.append(Document(page_content=content, metadata={"category": category}))

        self.vector_db.add_documents(documents)
        self.vector_db.persist()
        return True, f"Ingested {len(documents)} items into {category}."

    def query(self, text, category=None, k=3):
        """Queries the vector database for relevant documents."""
        if category:
            results = self.vector_db.similarity_search(
                text, k=k, filter={"category": category}
            )
        else:
            results = self.vector_db.similarity_search(text, k=k)
        
        return results
