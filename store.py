import logging
import os
import re
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Logging configuration
logger = logging.getLogger('papers')
logging.basicConfig(level=logging.INFO)

class EmbeddingStorage:
    def __init__(self, pinecone_api_key, openai_api_key, pinecone_index_name):
        logger.info("Initializing EmbeddingStorage with Pinecone index: %s", pinecone_index_name)

        # Create an instance of the Pinecone class
        pc = Pinecone(api_key=pinecone_api_key)

        # Check if the index exists, create if not
        if pinecone_index_name not in pc.list_indexes().names():
            pc.create_index(
                name=pinecone_index_name, 
                dimension=1536,  # Example dimension, adjust as needed
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
        logger.info("Starting embedding generation for %d texts...", len(texts))
        embeddings = self.embeddings.embed_documents(texts)
        logger.info("Embeddings generation completed.")
        return embeddings
    
    def sanitize_string(self, s):
    # Replace non-ASCII characters with an underscore or another placeholder
        return re.sub(r'[^\x00-\x7F]+', '_', s)

    def store_embeddings(self, papers, batch_size=100):
        logger.info("Beginning to store embeddings...")
        total_papers = len(papers)
        for i in range(0, total_papers, batch_size):
            batch_papers = papers[i:i+batch_size]
            vectors_to_upsert = []
            for paper in batch_papers:
                sanitized_title = self.sanitize_string(paper['title']) 
                text_to_embed = sanitized_title + ". " + paper['abstract']
                logger.info("Generating embedding for paper: %s", paper['title'])
                paper_embedding = self.generate_embeddings([text_to_embed])[0]
                vector_dict = {
                    "id": sanitized_title,
                    "values": paper_embedding,
                    "metadata": {
                        "url": paper["url"],
                        "authors": paper["authors"],
                        "conference_name": paper.get("conference_name", ""),
                        "conference_year": paper.get("conference_year", "")
                    }
                }
                vectors_to_upsert.append(vector_dict)
            logger.info("Storing batch of embeddings...")
            self.index.upsert(vectors=vectors_to_upsert)
            logger.info(f"Batch {i//batch_size+1}/{(total_papers+batch_size-1)//batch_size} stored successfully.")


    def semantic_search(self, query_text, top_k=15):
        logger.info("Semantic search initiated for query: '%s'", query_text)
        query_embedding = self.generate_embeddings([query_text])[0]
        results = self.index.query(vector=query_embedding, top_k=top_k, include_values=True)
        if results is None or 'matches' not in results:
            logger.info("No results found for query: '%s'", query_text)
            return {'matches': []}  # Return an empty list of matches if none are found
        else:
            logger.info("Semantic search completed for query: '%s'. Results found: %d", query_text, len(results['matches']))
            for match in results['matches']:
                logger.info("Match: %s with score: %f", match['id'], match['score'])
        return results
    
    def fetch_all_embeddings(self):
        logger.info("Fetching up to 10,000 embeddings from Pinecone...")
        all_embeddings = []
        dummy_vector = [0] * 1536  # Adjust the dimensionality as needed

        try:
            # Fetch the first 10,000 embeddings
            results = self.index.query(vector=dummy_vector, top_k=10000, include_values=True, include_metadata=True)
            if results is None or 'matches' not in results:
                logger.info("No embeddings found.")
                return []
            all_embeddings = [
                {
                    'id': match['id'],
                    'values': match['values'],
                    'conference_name': match['metadata']['conference_name']  # Include conference year
                }
                for match in results['matches']
            ]
            
            logger.info(f"Fetched {len(all_embeddings)} embeddings.")
            if all_embeddings:
                logger.info(f"Sample embedding ID: {all_embeddings[0]['id']}, Values: {all_embeddings[0]['values'][:10]}")  # Log first 10 values of the first embedding
            return all_embeddings
        except Exception as e:
            logger.error(f"An error occurred while fetching embeddings: {e}")
            return []


# Initialize EmbeddingStorage with your Pinecone and OpenAI API keys
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)
