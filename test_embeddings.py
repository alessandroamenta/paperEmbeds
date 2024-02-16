import json
import os
import logging
from store import EmbeddingStorage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('test')
logging.basicConfig(level=logging.INFO)

# Load the papers from the JSON file
with open('papers_repository.json', 'r') as file:
    papers = json.load(file)[:10]  # Load only the first 10 papers

logger.info(f"Loaded {len(papers)} papers.")

# Initialize EmbeddingStorage
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)

# Generate embeddings and store them in Pinecone
embedding_storage.store_embeddings(papers)

logger.info("Embeddings stored successfully.")

# Perform a query with a sample text
sample_query = "Stochastic Segmentation"
logger.info(f"Performing semantic search for '{sample_query}'...")
results = embedding_storage.semantic_search(sample_query, top_k=3)
logger.info(f"Query results for '{sample_query}':")
for match in results['matches']:  # Safe to iterate over 'matches' as it's always a list
    logger.info(f"{match['id']}, {match['score']}")
