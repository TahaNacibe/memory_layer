from sentence_transformers import SentenceTransformer

class Embedder:
    #? load an embedding model there's better but i'm on 16Gb RAM a cpu and a dream don't judge me
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # also did the class so the model can be reused without reloading it every time my ram can't take that
        self.model = SentenceTransformer(model_name)
        
    
    def encode(self, texts):
        #? Accept either a single string or list of strings, why just in case i want to use it in a loop
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts, convert_to_numpy=True)
