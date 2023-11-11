import numpy as np
import openai


def get_embedding(input_str: str) -> list[float]:
    result = openai.embeddings.create(
        model='text-embedding-ada-002',
        input=input_str,
    )
    return result.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_cosine_simarity(doc1: str, doc2: str) -> float:
    doc1_embedding = get_embedding(doc1)
    doc2_embedding = get_embedding(doc2)
    return cosine_similarity(doc1_embedding, doc2_embedding)
