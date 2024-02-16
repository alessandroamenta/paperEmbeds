import os
import abc
from typing import List, Dict

import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

class LocalFileStorage:
    """
    Local file system storage backend.
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def read_papers(self):
        """
        Read existing papers from the CSV file.
        """
        if os.path.exists(self.file_path):
            return pd.read_csv(self.file_path)
        return pd.DataFrame()

    def save_papers(self, papers):
        """
        Save a list of paper details to the CSV file.
        """
        if not papers.empty:
            papers.to_csv(self.file_path, mode='a', header=not os.path.exists(self.file_path), index=False)

        
class BaseDAL(abc.ABC):
    """
    Abstract base class for data access layers.
    """

    @abc.abstractmethod
    def store_papers(self, papers: List[Dict]):
        """
        Store a list of paper details.
        """
        pass

    @abc.abstractmethod
    def store_embeddings(self, embeddings: List):
        """
        Store a list of paper embeddings.
        """
        pass

    @abc.abstractmethod
    def search_papers(self, query: str):
        """
        Search for papers based on a query.
        """
        pass

class FirebaseDAL(BaseDAL):
    """
    Firebase data access layer implementation.
    """

    def __init__(self):
        # Check if Firebase has already been initialized
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__), 'firebasecreds.json')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()

    def store_papers(self, papers: List[Dict]):
        papers_collection = self.db.collection('papers')
        for paper in papers:
            papers_collection.document(paper['arxiv_id']).set(paper)

    def get_papers(self):
        papers_collection = self.db.collection('papers')
        documents = papers_collection.stream()
        return [doc.to_dict() for doc in documents]

    def search_papers(self, query: str):
        # Basic search implementation (more complex queries can be added later)
        papers_collection = self.db.collection('papers')
        query_results = papers_collection.where('title', '==', query).stream()
        return [doc.to_dict() for doc in query_results]
    
    def store_embeddings(self, embeddings: List):
    # Dummy implementation for store_embeddings
        pass

class WeaviateDAL(BaseDAL):
    """
    Weaviate data access layer implementation for embeddings.
    """

    def __init__(self, weaviate_url, weaviate_api_key):
        # Initialize Weaviate connection here
        pass

    def store_embeddings(self, embeddings: List):
        # Implement logic to store embeddings in Weaviate
        pass

    def search_papers(self, query: str):
        # Implement search logic using Weaviate
        pass



if __name__ == "__main__":
    # Test Store Papers
    test_papers = [
        {'arxiv_id': '1234', 'title': 'Sample Paper 1', 'abstract': 'Abstract 1'},
        {'arxiv_id': '5678', 'title': 'Sample Paper 2', 'abstract': 'Abstract 2'}
    ]
    dal = FirebaseDAL()
    dal.store_papers(test_papers)

    # Test Get Papers
    papers = dal.get_papers()
    print("Papers in Firestore:")
    for paper in papers:
        print(paper)

    # Test Search Papers
    search_results = dal.search_papers('Sample Paper 1')
    print("Search Results for 'Sample Paper 1':")
    for result in search_results:
        print(result)