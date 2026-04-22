from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_match_percentage(resume_data, internship):
    resume_text = resume_data.get("raw_text", "")
    internship_text = internship.get("description", "")

    if not resume_text or not internship_text:
        return 0.0

    embeddings = model.encode([resume_text, internship_text])
    score = cosine_similarity(
        [embeddings[0]], [embeddings[1]]
    )[0][0]

    return round(score * 100, 2)
