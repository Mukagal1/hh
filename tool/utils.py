import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Загружаем предобученную модель
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def text_to_vector(text):
    """Преобразует текст в векторное представление."""
    if not text:
        return torch.zeros(model.get_sentence_embedding_dimension())
    return model.encode([text])[0]

def compute_similarity(text1, text2):
    """Вычисляет косинусное сходство между двумя текстами."""
    vec1 = text_to_vector(text1).reshape(1, -1)
    vec2 = text_to_vector(text2).reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]
