import logging
import os
from pinecone import Pinecone, ServerlessSpec
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logger = logging.getLogger('papers')
logging.basicConfig(level=logging.INFO)

class EmbeddingStorage:
    def __init__(self, pinecone_api_key, openai_api_key, pinecone_index_name):
        logger.info("Initializing EmbeddingStorage...")

        # Create an instance of the Pinecone class
        pc = Pinecone(api_key=pinecone_api_key)

        # Check if the index exists, create if not
        if pinecone_index_name not in pc.list_indexes().names():
            pc.create_index(
                name=pinecone_index_name, 
                dimension=768,  # Example dimension, adjust as needed
                metric='cosine',  # Example metric, adjust as needed
                spec=ServerlessSpec(
                    cloud='aws', 
                    region='us-west-2'
                )
            )
        
        # Connect to the existing index
        self.index = pc.Index(pinecone_index_name)

        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)

        logger.info("EmbeddingStorage initialized.")

    def generate_embeddings(self, texts):
        logger.info("Generating embeddings...")
        return self.embeddings.embed_documents(texts)

    def store_embeddings(self, papers):
        logger.info("Storing embeddings...")
        vectors_to_upsert = []  # Prepare vectors for upsert
        for paper in papers:
            paper_embedding = self.generate_embeddings([paper['abstract']])[0]
            logger.info(f"Embedding for '{paper['title']}': {paper_embedding}")
            vector_dict = {
                "id": paper["title"],
                "values": paper_embedding,
                "metadata": {
                    "url": paper["url"],
                    "authors": paper["authors"]
                }
            }
            vectors_to_upsert.append(vector_dict)
        
        # Upsert vectors into the index
        self.index.upsert(vectors=vectors_to_upsert)
        logger.info("Embeddings stored.")

    def semantic_search(self, query_text, top_k=1):
        logger.info(f"Performing semantic search for '{query_text}'...")
        query_embedding = self.generate_embeddings([query_text])[0]
        results = self.index.query(vector=query_embedding, top_k=top_k, include_values=True)
        if results is None or 'matches' not in results:
            logger.info("No results found.")
            return {'matches': []}  # Return an empty list of matches if none are found
        return results

# Initialize EmbeddingStorage with your Pinecone and OpenAI API keys
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)

# papers = <result from your scraping logic>
# abstracts = [paper['abstract'] for paper in papers]
# paper_embeddings = embedding_storage.generate_embeddings(abstracts)
# embedding_storage.store_embeddings(papers)
