import logging
import os
from store import EmbeddingStorage  # Assuming your class is in a file named embedding_storage.py
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


# Initialize EmbeddingStorage
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)

# Single paper to test
test_paper = {
    "title": "Unpaired Image-to-Image Translation via Neural Schrödinger Bridge",
    "authors": "Beomsu Kim, Gihyun Kwon, Kwanyoung Kim, Jong Chul Ye",
    "abstract": "Diffusion models are a powerful class of generative models which simulate stochastic differential equations (SDEs) to generate data from noise. Although diffusion models have achieved remarkable progress in recent years, they have limitations in the unpaired image-to-image translation tasks due to the Gaussian prior assumption. Schrödinger Bridge (SB), which learns an SDE to translate between two arbitrary distributions, have risen as an attractive solution to this problem. However, none of SB models so far have been successful at unpaired translation between high-resolution images. In this work, we propose the Unpaired Neural Schrödinger Bridge (UNSB), which expresses SB problem as a sequence of adversarial learning problems. This allows us to incorporate advanced discriminators and regularization to learn a SB between unpaired data. We demonstrate that UNSB is scalable and successfully solves various unpaired image-to-image translation tasks.",
    "url": "https://openreview.net/forum?id=No ID provided",
    "conference_name": "ICLR",
    "conference_year": "2024"
}

# Test embedding and storing process for the single paper
embedding_storage.store_embeddings([test_paper], batch_size=1)
