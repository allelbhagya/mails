from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

DEFAULT_TAGS = {
    "Newsletter": "newsletter, blog post, digest, promotional email, weekly update, marketing, unsubscribe, duolingo, washington post, medium, substack",
    "Learning": "course update, lesson, tutorial, deep learning, batch, progress, streak, certificate, assignment",
    "General": "anything else that does not fit above categories"
}

def classify_email(email_text, tags):
    tag_names = list(tags.keys())
    tag_descriptions = list(tags.values())
    email_embedding = model.encode([email_text])
    tag_embeddings = model.encode(tag_descriptions)
    similarities = cosine_similarity(email_embedding, tag_embeddings)[0]
    best_idx = np.argmax(similarities)
    return tag_names[best_idx], round(float(similarities[best_idx]), 2)

def summarize_email(subject, body):
    text = f"{subject}. {body}"
    sentences = text.replace("\n", " ").split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences[0] if sentences else subject