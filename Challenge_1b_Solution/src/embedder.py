from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

model = None  


def load_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Loads a compact sentence embedding model for semantic similarity.
    """
    global model
    if model is None:
        model = SentenceTransformer(model_name)
    return model


def encode_texts(texts: List[str], normalize: bool = True) -> np.ndarray:
    """
    Encodes a list of texts into dense vectors using the loaded model.
    Normalizes embeddings if required (for cosine similarity).
    """
    if model is None:
        raise ValueError("Model not loaded. Call load_model() first.")

    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=normalize)
    return embeddings


def encode_single(text: str, normalize: bool = True) -> np.ndarray:
    """
    Encodes a single string (e.g., persona + task).
    """
    return encode_texts([text], normalize=normalize)[0]
