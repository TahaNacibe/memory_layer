import faiss
import numpy as np
from .embedder import Embedder


class FAISS_SEARCH:
    def __init__(self, ids, vectors):
        
        # safety neth to ensure the vectors are in the correct format
        if len(vectors.shape) != 2:
            raise ValueError(f"Expected a 2D array for vectors, but got shape {self.vectors.shape}")
        
        self.embedder = Embedder()
        self.ids = np.array(ids, dtype='int64')  # FAISS expects int64 IDs
        self.vectors = np.array(vectors, dtype='float32')  # Ensure float32
        self.index = self.build_faiss_index()

    def build_faiss_index(self):
        dim = 384
        index = faiss.IndexIDMap(faiss.IndexFlatL2(dim))  # ID mapping
        index.add_with_ids(self.vectors, self.ids)
        return index

    def search(self, query, top_k):
        query_vector = np.array(self.embedder.encode(query), dtype='float32').reshape(1, -1)
        distances, retrieved_ids = self.index.search(query_vector, top_k)
        return retrieved_ids[0], distances[0]  # 1D arrays of results





