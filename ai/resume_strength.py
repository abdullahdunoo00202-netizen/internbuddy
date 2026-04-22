import re
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

COMMON_SKILLS = [
    "python", "java", "c++", "machine learning", "deep learning",
    "data science", "flask", "django", "opencv", "nlp",
    "sql", "mongodb", "html", "css", "javascript"
]

def calculate_resume_strength(resume_text):
    resume_text = resume_text.lower()

    # ---------- SKILLS SCORE ----------
    found_skills = [
        skill for skill in COMMON_SKILLS if skill in resume_text
    ]

    skills_score = min(len(found_skills) / 10, 1.0)  # max at 10 skills

    # ---------- EXPERIENCE SCORE ----------
    experience_keywords = ["experience", "project", "internship", "worked", "developed"]
    exp_score = sum(1 for k in experience_keywords if k in resume_text)
    exp_score = min(exp_score / 5, 1.0)

    # ---------- SEMANTIC QUALITY ----------
    generic_good_resume = """
    experienced software developer with strong programming,
    projects, problem solving skills and practical knowledge
    """

    embeddings = model.encode([resume_text, generic_good_resume])
    semantic_score = float((embeddings[0] @ embeddings[1]) /
                           ((embeddings[0] @ embeddings[0]) ** 0.5 *
                            (embeddings[1] @ embeddings[1]) ** 0.5))

    semantic_score = max(0, semantic_score)

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
