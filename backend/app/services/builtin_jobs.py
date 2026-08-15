"""Small offline fallback catalog used when public job APIs are unavailable."""

BUILTIN_JOBS = [
    ("Junior Python Developer", "OpenTech Labs", "entry", "Python, Django, REST APIs, Git, SQL. Fresh graduates welcome. Build and maintain backend services.", ["python", "django", "rest", "git", "sql"], 0),
    ("Frontend React Developer", "WebWorks", "entry", "Build responsive applications using React, JavaScript, HTML, CSS and REST APIs. 0-2 years preferred.", ["react", "javascript", "html", "css", "rest"], 1),
    ("Data Analyst", "Insight Analytics", "entry", "Analyze business data with Python, SQL, Pandas, NumPy, Tableau and Power BI. 0-2 years preferred.", ["python", "sql", "pandas", "numpy", "tableau", "power bi"], 1),
    ("Machine Learning Engineer", "AI Systems", "mid", "Develop machine learning systems with Python, scikit-learn, PyTorch or TensorFlow, NLP and data analysis. 2+ years.", ["python", "machine learning", "scikit-learn", "pytorch", "tensorflow", "nlp"], 2),
    ("Backend Engineer", "CloudScale", "mid", "Develop APIs and scalable services with Python, FastAPI, PostgreSQL, Docker, AWS and REST. 2+ years.", ["python", "fastapi", "postgresql", "docker", "aws", "rest"], 2),
    ("Full Stack Developer", "LaunchPad", "mid", "Work across React, Node.js, TypeScript, PostgreSQL, Docker and REST APIs. 2+ years of experience.", ["react", "node", "typescript", "postgresql", "docker", "rest"], 2),
    ("Data Engineer", "DataGrid", "mid", "Build data pipelines using Python, SQL, Spark, Airflow and cloud platforms. 3+ years preferred.", ["python", "sql", "spark", "airflow", "aws"], 3),
    ("DevOps Engineer", "InfraWorks", "mid", "Automate cloud infrastructure using AWS, Docker, Kubernetes, Terraform, Linux and Jenkins. 3+ years.", ["aws", "docker", "kubernetes", "terraform", "linux", "jenkins"], 3),
    ("Computer Vision Engineer", "VisionAI", "mid", "Build computer vision models with Python, OpenCV, PyTorch, TensorFlow and deep learning. 2+ years.", ["python", "computer vision", "pytorch", "tensorflow", "deep learning"], 2),
    ("Senior Python Backend Engineer", "ScaleTech", "senior", "Lead backend engineering with Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes and AWS. 5+ years.", ["python", "fastapi", "postgresql", "redis", "docker", "kubernetes", "aws"], 5),
    ("NLP Engineer", "LanguageAI", "mid", "Develop NLP and deep learning solutions using Python, PyTorch, Transformers and data processing. 2+ years.", ["python", "nlp", "deep learning", "pytorch"], 2),
    ("Cloud Software Engineer", "CloudNova", "mid", "Design cloud-native services using Python, Java, Docker, Kubernetes, AWS and REST APIs. 3+ years.", ["python", "java", "docker", "kubernetes", "aws", "rest"], 3),
]


def builtin_rows():
    rows = []
    for idx, (title, company, level, description, skills, years) in enumerate(BUILTIN_JOBS, 1):
        rows.append({
            "external_id": f"builtin-{idx}",
            "source": "Demo fallback",
            "title": title,
            "company": company,
            "level": level,
            "description": description,
            "url": None,
            "location": "Remote / Demo",
            "employment_type": "Full-time",
            "remote": True,
            "extracted_data": {
                "required_skills": skills,
                "preferred_skills": [],
                "qualifications": [],
                "min_experience_years": years,
                "responsibilities": [description],
            },
        })
    return rows
