import os
import re
import requests
from flask import Flask, request, render_template
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from serpapi import GoogleSearch

app = Flask(__name__)


SERPAPI_KEY = os.getenv("SERPAPI_KEY")

FALLBACK_JOBS = [
    {
        "title": "Python Developer",
        "company": "Tech Corp",
        "description": "We need a Python developer experienced with Flask, REST APIs, SQL databases, Git, and writing clean, testable code.",
        "url": "#",
    },
    {
        "title": "Marketing Coordinator",
        "company": "Growth Co",
        "description": "Looking for a marketing coordinator skilled in social media, content creation, SEO basics, and campaign reporting.",
        "url": "#",
    },
    {
        "title": "Graphic Designer",
        "company": "Studio Nine",
        "description": "Graphic designer needed with strong skills in Adobe Illustrator, Photoshop, branding, and layout design.",
        "url": "#",
    },
    {
        "title": "Registered Nurse",
        "company": "City Health Group",
        "description": "Registered nurse role requiring patient care experience, clinical documentation, and strong communication skills.",
        "url": "#",
    }
]

def strip_html(text):
    """Remove HTML tags from job descriptions returned by the API."""
    if not text:
        return ""
    return re.sub(r'<[^>]+>', ' ', text)

CATEGORY_IMAGES = {
    "tech": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=60",
    "data": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&q=60",
    "design": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&q=60",
    "marketing": "https://images.unsplash.com/photo-1533750349088-cd871a92f312?w=400&q=60",
    "health": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&q=60",
    "finance": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400&q=60",
    "generic": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=400&q=60"
}

def categorize_job(title, tags=None):
    """Assign a broad category to a job so the frontend can show a matching icon/image."""
    tags = tags or []
    text = (title + " " + " ".join(tags)).lower()

    if any(k in text for k in ["developer", "engineer", "software", "programmer", "backend", "frontend", "devops", "python", "java"]):
        return "tech"
    if any(k in text for k in ["data", "analyst", "scientist", "sql", "machine learning"]):
        return "data"
    if any(k in text for k in ["design", "ux", "ui", "graphic", "creative"]):
        return "design"
    if any(k in text for k in ["marketing", "seo", "content", "social media", "sales"]):
        return "marketing"
    if any(k in text for k in ["nurse", "health", "medical", "doctor", "clinical"]):
        return "health"
    if any(k in text for k in ["finance", "accountant", "account", "bank"]):
        return "finance"
    return "generic"

def fetch_live_jobs(query, limit=8):
    """Fetch real, current job postings from Google Jobs via SerpApi."""
    if not query:
        query = "Software Developer" 

    # 1. Forcing google to search for jobs in Pune.
    search_query = f"{query} jobs"
    print(f"[SerpApi] Searching for: '{search_query}' in Pune")
    
    params = {
        "engine": "google_jobs",
        "q": search_query,
        "location": "Pune, Maharashtra, India",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # 2. Checking api errors  
        if "error" in results:
            print(f"[SerpApi] Hidden API Error: {results['error']}")
            return []

        all_jobs = results.get("jobs_results", [])
        print(f"[SerpApi] Fetched {len(all_jobs)} total jobs from API")
        
        deduped = []
        seen = set()

        for j in all_jobs:
            title = j.get("title", "")
            company = j.get("company_name", "Unknown Company")
            
            key = (title, company)
            if key not in seen:
                seen.add(key)
                category = categorize_job(title)
                
                job_dict = {
                    "title": title,
                    "company": company,
                    "description": strip_html(j.get("description", "")),
                    "category": category,
                    "image": CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["generic"]),
                    "url": j.get("share_link", "#"),
                }
                deduped.append(job_dict)
                
            if len(deduped) >= limit:
                break
                
        return deduped

    except Exception as e:
        print(f"[SerpApi] Python request failed: {e}")
        return []

def calculate_match_score(resume_text, job_description):
    """Compare resume text to a job description using TF-IDF cosine similarity."""
    if not resume_text.strip() or not job_description.strip():
        return 0

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100)

def find_missing_keywords(resume_text, job_description, top_n=6):
    """Return important words from the job description not found in the resume."""
    if not resume_text.strip() or not job_description.strip():
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    vectorizer.fit([job_description])
    job_keywords = vectorizer.get_feature_names_out()

    resume_lower = resume_text.lower()
    missing = [word for word in job_keywords if word not in resume_lower]
    return missing[:top_n]

def extract_resume_text(request):
    """Pull resume text from an uploaded PDF if present, otherwise from pasted text."""
    if 'pdf_upload' in request.files:
        file = request.files['pdf_upload']
        if file.filename != '':
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            if text.strip():
                return text

    return request.form.get('resume', '')

def add_category_and_image(job):
    category = categorize_job(job["title"])
    return {**job, "category": category, "image": CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["generic"])}

@app.route('/')
def home():
    # 1. This now ONLY serves your new landing page with the video background.
    return render_template('index.html')

@app.route('/match', methods=['GET', 'POST'])
def match():
    # 2. If the user just clicked "Start Engine" and is loading the page for the first time:
    if request.method == 'GET':
        jobs = [{**add_category_and_image(job), "score": 0} for job in FALLBACK_JOBS]
        return render_template('match.html', jobs=jobs, custom_score=None, missing_keywords=[], jobs_source="sample")

    # 3. If the user is submitting their resume (POST request):
    resume_text = extract_resume_text(request)
    job_description = request.form.get('job_description', '')
    target_role = request.form.get('target_role', '').strip()

    # Always try to attempt the live API
    live_jobs = fetch_live_jobs(target_role)

    if live_jobs:
        source_jobs = live_jobs
        jobs_source = "live"
    else:
        source_jobs = [add_category_and_image(job) for job in FALLBACK_JOBS]
        jobs_source = "sample"

    jobs = []
    for job in source_jobs:
        score = calculate_match_score(resume_text, job['description'])
        jobs.append({**job, "score": score})

    jobs.sort(key=lambda j: j['score'], reverse=True)

    custom_score = None
    missing_keywords = []
    if job_description.strip():
        custom_score = calculate_match_score(resume_text, job_description)
        missing_keywords = find_missing_keywords(resume_text, job_description)

    # Make sure this renders 'match.html', not 'index.html'
    return render_template('match.html', jobs=jobs, custom_score=custom_score, 
                           missing_keywords=missing_keywords, jobs_source=jobs_source)

if __name__ == '__main__':
    app.run(debug=True)
    