import re

# ❌ DO NOT load model here
model = None

COMMON_SKILLS = [
    "python", "java", "c++", "machine learning", "deep learning",
    "data science", "flask", "django", "opencv", "nlp",
    "sql", "mongodb", "html", "css", "javascript"
]


def get_model():
    global model
    if model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print("⚠️ Model load failed:", e)
            model = False
    return model


def calculate_resume_strength(resume_text):
    resume_text = resume_text.lower()

    # ---------- SKILLS SCORE ----------
    found_skills = [
        skill for skill in COMMON_SKILLS if skill in resume_text
    ]
    skills_score = min(len(found_skills) / 10, 1.0)

    # ---------- EXPERIENCE SCORE ----------
    experience_keywords = ["experience", "project", "internship", "worked", "developed"]
    exp_score = sum(1 for k in experience_keywords if k in resume_text)
    exp_score = min(exp_score / 5, 1.0)

    # ---------- SEMANTIC SCORE (SAFE) ----------
    semantic_score = 0.5  # default fallback

    model = get_model()

    if model:
        try:
            generic_good_resume = """
            experienced software developer with strong programming,
            projects, problem solving skills and practical knowledge
            """

            embeddings = model.encode([resume_text, generic_good_resume])

            semantic_score = float(
                (embeddings[0] @ embeddings[1]) /
                ((embeddings[0] @ embeddings[0]) ** 0.5 *
                 (embeddings[1] @ embeddings[1]) ** 0.5)
            )

            semantic_score = max(0, semantic_score)

        except Exception as e:
            print("⚠️ Encoding failed:", e)
            semantic_score = 0.5

    # ---------- FINAL SCORE ----------
    final_score = (
        0.4 * skills_score +
        0.3 * exp_score +
        0.3 * semantic_score
    )

    return {
        "score": round(final_score * 100, 2),
        "skills_found": found_skills
    }
