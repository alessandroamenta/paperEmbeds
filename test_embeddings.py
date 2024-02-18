import json
import logging
from store import EmbeddingStorage
from dotenv import load_dotenv
import os

# Ensure the .env file is loaded to use environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger('test_embeddings')
logging.basicConfig(level=logging.INFO)

# Specify the path to your papers JSON file
JSON_FILE_PATH = 'papers_repo.json'  # Change this if your file has a different name or path

# Load the papers from the JSON file
with open(JSON_FILE_PATH, 'r') as file:
    papers = json.load(file)[:5]  # Load only the first 5 papers for the test

logger.info(f"Loaded {len(papers)} papers for embedding.")

# Initialize EmbeddingStorage with your Pinecone and OpenAI API keys
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)

# Generate embeddings for the titles and abstracts of the loaded papers and store them
embedding_storage.store_embeddings(papers)

logger.info("Embeddings stored successfully.")

# Perform a query with a sample text
sample_query = "Towards Attack-tolerant Federated Learning via Critical Parameter Analysis"
logger.info(f"Performing semantic search for '{sample_query}'...")
results = embedding_storage.semantic_search(sample_query, top_k=3)
logger.info(f"Query results for '{sample_query}':")
for match in results['matches']:  # Safe to iterate over 'matches' as it's always a list
    logger.info(f"{match['id']}, {match['score']}")
