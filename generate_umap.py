import os
import json
import numpy as np
from dotenv import load_dotenv
import umap
from store import EmbeddingStorage

load_dotenv()

# Initialize the EmbeddingStorage
embedding_storage = EmbeddingStorage(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    pinecone_index_name="ml-conferences"
)

# Fetch all embeddings
all_embeddings = embedding_storage.fetch_all_embeddings()

# Prepare the embeddings list for t-SNE
embeddings_list = [embedding['values'] for embedding in all_embeddings]
print(f"Embeddings list size: {len(embeddings_list)}")
embeddings_array = np.array(embeddings_list)  # Convert list to NumPy array
print(f"Embeddings array shape: {embeddings_array.shape}")

# Ensure there are valid embeddings before proceeding
if embeddings_array.size > 0:
    # Perform UMAP
    umap_model = umap.UMAP(n_neighbors=50, n_components=2, min_dist=0.1, metric='cosine', n_epochs=500, random_state=42)
    umap_results = umap_model.fit_transform(embeddings_array)

    # Combine UMAP results with paper IDs
    umap_data = [
        {
            'id': embedding['id'],
            'x': float(result[0]),
            'y': float(result[1]),
            'conference_name': embedding['conference_name'] 
        } 
        for embedding, result in zip(all_embeddings, umap_results)
    ]

    # Save the UMAP results
    with open('umap_results.json', 'w') as f:
        json.dump(umap_data, f)
else:
    print("No valid embeddings to process with UMAP.")
