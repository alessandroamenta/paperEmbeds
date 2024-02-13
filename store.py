import logging
import os
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logger = logging.getLogger('papers')
logging.basicConfig(level=logging.INFO)

class EmbeddingStorage:
    def __init__(self, pinecone_api_key, openai_api_key, pinecone_index_name):
        # Configure Pinecone
        pinecone.configure(api_key=pinecone_api_key)
        # Check if the index exists, create if not
        self.index_name = pinecone_index_name
        if self.index_name not in pinecone.list_indexes():
            # Set dimension to 768 for OpenAI embeddings (adjust if needed)
            pinecone.create_index(name=self.index_name, dimension=768, metric="cosine")
        # Connect to the index
        self.index = pinecone.Index(name=self.index_name)

        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)

    def generate_embeddings(self, texts):
        # Generate embeddings for the given texts
        return self.embeddings.embed_documents(texts)

    def store_embeddings(self, papers):
        # Store the embeddings in Pinecone
        for paper in papers:
            paper_embedding = self.generate_embeddings([paper['abstract']])[0]
            # Upsert the vector and metadata into Pinecone
            self.index.upsert(vectors=[(paper['title'], paper_embedding.tolist(), paper)])

    def semantic_search(self, query_text, top_k=1):
        # Perform a semantic search in Pinecone
        query_embedding = self.generate_embeddings([query_text])[0]
        return self.index.query(queries=[query_embedding], top_k=top_k)

# Example usage
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)

# papers = <result from your scraping logic>
# abstracts = [paper['abstract'] for paper in papers]
# paper_embeddings = embedding_storage.generate_embeddings(abstracts)
# embedding_storage.store_papers(papers, paper_embeddings)
