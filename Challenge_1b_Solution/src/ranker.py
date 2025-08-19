import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple


def rank_sections(
    task_embedding: np.ndarray,
    section_embeddings: np.ndarray,
    section_metadata: List[Dict],
    top_n: int = 5
) -> List[Tuple[Dict, float]]:
    """
    Ranks document sections based on cosine similarity to the persona-task query.

    Args:
        task_embedding: Embedding vector for the task query (1D)
        section_embeddings: Array of section vectors (2D)
        section_metadata: List of metadata for each section (doc name, page, title)
        top_n: Number of top sections to return

    Returns:
        List of tuples: (section_metadata, similarity_score), sorted by relevance
    """
    # Ensure the shape
    if task_embedding.ndim == 1:
        task_embedding = task_embedding.reshape(1, -1)

    similarities = cosine_similarity(task_embedding, section_embeddings)[0]
    ranked = sorted(
        zip(section_metadata, similarities),
        key=lambda x: x[1],
        reverse=True
    )
    return ranked[:top_n]
