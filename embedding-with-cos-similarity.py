from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

texts = [
    "How are you? I am fine. Thanks.",
    "How are yuu? I am fine. Thanks.",
    "I like pizza!"
]

# Create embeddings (vectors)
vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3,4),   # try (3,5) or (3,4)
    lowercase=True,
    norm="l2"            # cosine-friendly normalization
)
X = vectorizer.fit_transform(texts)

# Compute cosine similarity between all pairs
sim = cosine_similarity(X)

print(sim)