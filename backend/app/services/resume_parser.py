import os
import re
import uuid
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


def extract_text_from_file(file_path: str) -> str:
    """Extract readable plain text from a PDF or DOCX file."""
    if not os.path.exists(file_path):
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if ext == ".pdf" and pypdf is not None:
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            
    elif ext in [".docx", ".doc"] and docx is not None:
        try:
            doc = docx.Document(file_path)

            for p in doc.paragraphs:
                if p.text:
                    text += p.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            
    return text.strip()


class ResumeAnalyzer:
    COMMON_SKILLS = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby",
        "React", "Angular", "Vue", "Node.js", "Express", "FastAPI", "Django", "Flask", "Spring Boot",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
        "AWS", "Docker", "Kubernetes", "Git", "HTML", "CSS", "Tailwind CSS",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-Learn"
    ]

    COMMON_ROLES = {
        "Software Developer": ["software", "developer", "engineer", "full stack", "backend", "frontend", "web"],
        "Data Scientist": ["data scientist", "machine learning", "deep learning", "ai", "models"],
        "Data Analyst": ["data analyst", "bi", "sql", "excel", "tableau", "power bi", "analytics"],
        "AI/ML Engineer": ["mlops", "ai engineer", "neural networks", "nlp", "computer vision"],
        "Product Manager": ["product manager", "agile", "scrum", "roadmap", "stakeholder"]
    }

    @classmethod
    def analyze(cls, text: str) -> dict:
        if not text or len(text.strip()) < 10:
            return {
                "extracted": False,
                "message": "No readable text could be extracted from this resume file.",
                "skills": [],
                "education": None,
                "target_role": None,
                "text_snippet": ""
            }

        text_lower = text.lower()
        
        # 1. Extract skills
        found_skills = []
        for skill in cls.COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)

        # 2. Extract suggested target role
        suggested_role = None
        highest_score = 0
        for role, keywords in cls.COMMON_ROLES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > highest_score:
                highest_score = score
                suggested_role = role

        # 3. Extract education level
        suggested_education = None
        degree_patterns = [
            ("Master's Degree", ["master of science", "master of computer", "master's", "masters", "master", "m.s.", "m.tech", "m.e."]),
            ("Bachelor's Degree", ["bachelor of science", "bachelor of technology", "bachelor's", "bachelors", "bachelor", "b.s.", "b.tech", "b.e."]),
            ("Associate Degree", ["associate degree", "a.s."]),
            ("High School Diploma", ["high school", "secondary education"])
        ]

        for edu_label, keywords in degree_patterns:
            if any(kw in text_lower for kw in keywords):
                suggested_education = edu_label
                break

        snippet = text[:300] + ("..." if len(text) > 300 else "")

        return {
            "extracted": True,
            "skills": found_skills,
            "education": suggested_education,
            "target_role": suggested_role,
            "text_snippet": snippet
        }
