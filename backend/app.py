import os
import json
import tempfile
import re
from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

SKILL_CANDIDATES = [
    ('Python', [r'\bpython\b']),
    ('Java', [r'\bjava\b']),
    ('SQL', [r'\bsql\b']),
    ('HTML', [r'\bhtml\b']),
    ('CSS', [r'\bcss\b']),
    ('JavaScript', [r'\bjavascript\b']),
    ('React', [r'\breact\b']),
    ('Node.js', [r'\bnode\s*\.\s*js\b', r'\bnode\s*js\b', r'\bnodejs\b']),
    ('Machine Learning', [r'\bmachine learning\b', r'\bai\b', r'\bartificial intelligence\b', r'\bml\b']),
    ('Data Science', [r'\bdata science\b', r'\banalytics\b', r'\bdata analytics\b', r'\bdata engineering\b']),
    ('Database', [r'\bdatabase\b', r'\bsupabase\b', r'\bsql\b', r'\bpostgres\b', r'\bpostgresql\b', r'\bmongodb\b', r'\bfirebase\b']),
    ('Web Development', [r'\bweb development\b', r'\bfrontend\b', r'\bbackend\b', r'\bfull[- ]stack\b', r'\bweb application\b', r'\bweb app\b', r'\bhtml\b', r'\bcss\b', r'\bjavascript\b']),
    ('C++', [r'\bc\+\+\b']),
    ('C#', [r'\bc#\b']),
    ('C', [r'\bc(?!\+|#)\b']),
    ('Git', [r'\bgit\b'])
]

TOOL_CANDIDATES = [
    ('Supabase', [r'\bsupabase\b']),
    ('VS Code', [r'\bvs code\b', r'\bvisual studio code\b']),
    ('Docker', [r'\bdocker\b']),
    ('AWS', [r'\baws\b']),
    ('Azure', [r'\bazure\b']),
    ('GCP', [r'\bgcp\b', r'\bgoogle cloud\b']),
    ('GitHub', [r'\bgithub\b']),
    ('PostgreSQL', [r'\bpostgresql\b', r'\bpostgres\b']),
    ('MongoDB', [r'\bmongodb\b']),
    ('Firebase', [r'\bfirebase\b']),
    ('Tailwind CSS', [r'\btailwind\b', r'\btailwind css\b']),
    ('React', [r'\breact\b']),
    ('Node.js', [r'\bnode\s*\.\s*js\b', r'\bnode\s*js\b', r'\bnodejs\b'])
]

DOMAIN_CONCEPTS = [
    ('Web Development', [r'\bweb development\b', r'\bfrontend\b', r'\bbackend\b', r'\bfull[- ]stack\b', r'\bweb app\b', r'\bweb application\b', r'\bwebsite\b']),
    ('AI / Machine Learning', [r'\bmachine learning\b', r'\bai\b', r'\bartificial intelligence\b', r'\bml\b', r'\bdeep learning\b']),
    ('Data Science', [r'\bdata science\b', r'\banalytics\b', r'\bdata analytics\b', r'\bdata engineering\b']),
    ('Mobile Development', [r'\bmobile app\b', r'\bandroid\b', r'\bios\b', r'\bmobile development\b'])
]

INFERRED_MATCH_GROUPS = {
    'Web Development': {'HTML', 'CSS', 'JavaScript', 'React', 'Node.js'},
    'AI / Machine Learning': {'Machine Learning', 'Data Science', 'Python'},
    'Data Science': {'Data Science', 'Python', 'SQL'},
    'DevOps': {'Docker', 'Git', 'AWS', 'Azure', 'GCP'}
}

PROJECT_TERMS = [
    r'\bproject\b', r'\bbuilt\b', r'\bdeveloped\b', r'\bcreated\b', r'\blaunched\b',
    r'\bimplemented\b', r'\bengineered\b', r'\bdesigned\b', r'\bdeployed\b', r'\bowned\b'
]

ROLE_TERMS = [
    r'\bdeveloper\b', r'\bengineer\b', r'\bspecialist\b', r'\banalyst\b', r'\bconsultant\b', r'\bmanager\b'
]

# Skill Variations and Synonyms
SKILL_VARIATIONS = {
    'python': ['python', 'py'],
    'javascript': ['javascript', 'js'],
    'java': ['java'],
    'sql': ['sql', 'database'],
    'html': ['html'],
    'css': ['css'],
    'react': ['react', 'reactjs'],
    'node.js': ['node', 'nodejs', 'node.js'],
    'machine learning': ['machine learning', 'ml', 'ai', 'artificial intelligence'],
    'data science': ['data science', 'data analysis', 'analytics'],
    'web development': ['web development', 'web app', 'full stack'],
    'docker': ['docker', 'containerization'],
    'aws': ['aws', 'amazon web services'],
    'git': ['git', 'github', 'gitlab'],
    'postgresql': ['postgresql', 'postgres'],
    'mongodb': ['mongodb', 'mongo'],
    'pandas': ['pandas'],
    'numpy': ['numpy'],
    'scikit-learn': ['scikit-learn', 'sklearn'],
    'tensorflow': ['tensorflow'],
    'pytorch': ['pytorch'],
    'matplotlib': ['matplotlib'],
    'seaborn': ['seaborn'],
    'plotly': ['plotly'],
    'power bi': ['power bi', 'powerbi'],
    'jupyter': ['jupyter'],
    'spark': ['spark'],
    'c++': ['c++'],
    'c#': ['c#', 'csharp'],
    'typescript': ['typescript', 'ts']
}

# Skill Importance Weights
SKILL_WEIGHTS = {
    'python': 3,
    'javascript': 2,
    'java': 3,
    'sql': 3,
    'html': 1,
    'css': 1,
    'react': 2,
    'node.js': 2,
    'machine learning': 3,
    'data science': 3,
    'web development': 2,
    'docker': 2,
    'aws': 2,
    'git': 1,
    'postgresql': 2,
    'mongodb': 2,
    'pandas': 2,
    'numpy': 2,
    'scikit-learn': 3,
    'tensorflow': 3,
    'pytorch': 3,
    'matplotlib': 2,
    'seaborn': 2,
    'plotly': 2,
    'power bi': 2,
    'jupyter': 1,
    'spark': 2,
    'c++': 3,
    'c#': 2,
    'typescript': 2
}

# Skill Categories
SKILL_CATEGORIES = {
    'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'typescript'],
    'web': ['html', 'css', 'javascript', 'react', 'node.js', 'web development'],
    'data': ['data science', 'machine learning', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'matplotlib', 'seaborn', 'plotly', 'spark'],
    'devops': ['docker', 'git', 'aws', 'postgresql', 'mongodb', 'azure', 'gcp']
}

# Data Science Specific Libraries
DATA_SCIENCE_LIBRARIES = [
    'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch',
    'matplotlib', 'seaborn', 'plotly', 'power bi', 'jupyter', 'spark'
]

# Machine Learning Libraries
ML_LIBRARIES = ['scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras']

# Data Tools
DATA_TOOLS = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'power bi', 'spark']


def allowed_file(filename):
    return filename.lower().endswith('.pdf')


def extract_text_from_pdf(file_path):
    """Extract text content from a PDF file path."""
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                page_text = page.extract_text() or ''
                text += page_text + '\n'
            return text.strip()
    except Exception as e:
        raise Exception(f'Error reading PDF: {str(e)}')

def extract_text_from_txt(file_stream):
    """Extract text content from TXT file"""
    try:
        return file_stream.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_stream.read().decode('latin-1')
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+#]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text, top_n=25):
    """Extract keyword candidates from text."""
    words = clean_text(text).split()
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
        'do', 'does', 'did', 'doing', 'not', 'this', 'that', 'these', 'those', 'from', 'as',
        'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'over',
        'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same',
        'than', 'too', 'very', 'just', 'so', 'well', 'now'
    }
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return [word for word, _ in Counter(keywords).most_common(top_n)]

def extract_tools(text):
    """Extract tool and technology mentions from text."""
    cleaned = clean_text(text)
    found_tools = []
    for display_name, patterns in TOOL_CANDIDATES:
        for pattern in patterns:
            if re.search(pattern, cleaned):
                found_tools.append(display_name)
                break
    return found_tools


def detect_concepts(text, concept_list):
    """Detect broader domain concepts in text."""
    cleaned = clean_text(text)
    found = []
    for display_name, patterns in concept_list:
        if any(re.search(pattern, cleaned) for pattern in patterns):
            found.append(display_name)
    return found


def has_project_mention(text):
    cleaned = clean_text(text)
    return any(re.search(pattern, cleaned) for pattern in PROJECT_TERMS)


def has_role_terms(text):
    cleaned = clean_text(text)
    return any(re.search(pattern, cleaned) for pattern in ROLE_TERMS)


def find_skill_variations(text, skill_variations_dict):
    """Find skills using variations/synonyms mapping."""
    cleaned = clean_text(text)
    found_skills = {}
    
    for skill_name, variations in skill_variations_dict.items():
        for variation in variations:
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, cleaned):
                found_skills[skill_name] = True
                break
    
    return list(found_skills.keys())


def calculate_weighted_score(job_skills, resume_skills):
    """Calculate weighted match score."""
    if not job_skills:
        return 0.0
    
    total_weight = sum(SKILL_WEIGHTS.get(skill, 1) for skill in job_skills)
    matched_weight = sum(SKILL_WEIGHTS.get(skill, 1) for skill in job_skills if skill in resume_skills)
    
    if total_weight == 0:
        return 0.0
    
    return (matched_weight / total_weight) * 100


def calculate_category_breakdown(job_skills, resume_skills, resume_text):
    """Calculate match percentage for each skill category."""
    breakdown = {}
    data_tools_present = len(detect_data_tools(resume_text)) > 0
    ml_libs_present = len(detect_ml_libraries(resume_text)) > 0
    data_valid = data_tools_present or ml_libs_present
    
    for category, skills in SKILL_CATEGORIES.items():
        category_job_skills = [s for s in job_skills if s in skills]
        if not category_job_skills:
            breakdown[category] = 0
            continue
        
        category_resume_skills = [s for s in resume_skills if s in skills]
        if category == 'data' and not data_valid:
            breakdown[category] = 0
            continue
        
        matched = len([s for s in category_job_skills if s in category_resume_skills])
        breakdown[category] = round((matched / len(category_job_skills)) * 100)
    
    return breakdown


def calculate_confidence_score(matched_skills_count, job_skills_count, resume_length, match_score, missing_skills_count):
    """Calculate confidence based on skill detection and resume completeness."""
    if job_skills_count == 0:
        base_confidence = 50
    else:
        base_confidence = (matched_skills_count / job_skills_count) * 100
    
    resume_completeness_bonus = min(20, len(resume_length) / 100)
    confidence = min(100, max(40, int(base_confidence + resume_completeness_bonus)))
    
    if match_score < 50 and missing_skills_count >= 2:
        confidence = min(90, max(70, confidence))
    
    return confidence
    """Calculate confidence based on skill detection and resume completeness."""
    if job_skills_count == 0:
        base_confidence = 50
    else:
        base_confidence = (matched_skills_count / job_skills_count) * 100
    
    resume_completeness_bonus = min(20, len(resume_length) / 100)
    
    return min(100, max(40, int(base_confidence + resume_completeness_bonus)))


def generate_course_recommendations(missing_skills, is_data_role):
    """Generate course recommendations based on missing skills."""
    courses = []
    mapping = {
        'react': 'Take a React course focused on building dashboards and REST API integration.',
        'aws': 'Complete an AWS fundamentals course covering Lambda, S3, and CloudFormation.',
        'docker': 'Finish a Docker course on containerizing full-stack applications.',
        'machine learning': 'Take a machine learning course with scikit-learn and model evaluation.',
        'data science': 'Complete a data science course covering Pandas, NumPy, and visualization.',
        'python': 'Complete an advanced Python course for data analysis and automation.',
        'sql': 'Take a SQL course focused on joins, aggregation, and database design.',
        'postgresql': 'Complete a PostgreSQL course on schema design and query optimization.'
    }
    for skill in missing_skills:
        course = mapping.get(skill.lower())
        if course and course not in courses:
            courses.append(course)
    if is_data_role and not courses:
        courses.append('Take a data science course with Pandas, NumPy, and visualization labs.')
    if not courses:
        courses.append('Take a practical course that covers the key missing skills from this job description.')
    return courses


def generate_project_recommendations(missing_skills, job_skills, is_data_role):
    """Generate project suggestions based on missing skills and job focus."""
    projects = []
    if 'react' in job_skills or 'web development' in job_skills:
        projects.append('Build a React dashboard connected to a REST API to demonstrate frontend development.')
    if 'aws' in job_skills or 'docker' in job_skills:
        projects.append('Create a containerized app with Docker and deploy it to AWS to show cloud readiness.')
    if is_data_role or 'machine learning' in job_skills or 'data science' in job_skills:
        projects.append('Build a dataset analysis project using Pandas and scikit-learn to demonstrate data skills.')
    if not projects:
        projects.append('Create a small end-to-end project using the key tools from the job description.')
    return list(dict.fromkeys(projects))


def detect_data_science_libraries(text):
    """Detect data science specific libraries in text."""
    cleaned = clean_text(text)
    found_libs = []
    for lib in DATA_SCIENCE_LIBRARIES:
        if re.search(r'\b' + re.escape(lib) + r'\b', cleaned):
            found_libs.append(lib)
    return found_libs


def detect_ml_libraries(text):
    """Detect machine learning libraries (scikit-learn, TensorFlow, PyTorch)."""
    cleaned = clean_text(text)
    found_ml = []
    for lib in ML_LIBRARIES:
        if re.search(r'\b' + re.escape(lib) + r'\b', cleaned):
            found_ml.append(lib)
    return found_ml


def detect_data_tools(text):
    """Detect data science tools (Pandas, NumPy, etc.)."""
    cleaned = clean_text(text)
    found_tools = []
    for tool in DATA_TOOLS:
        if re.search(r'\b' + re.escape(tool) + r'\b', cleaned):
            found_tools.append(tool)
    return found_tools


def is_data_science_project(text):
    """Validate if project is actually a data science project."""
    cleaned = clean_text(text)
    
    # Check for data science keywords
    data_keywords = [
        r'\bdataset\b', r'\bdata analysis\b', r'\banalytic\b',
        r'\bmodel\b', r'\bprediction\b', r'\bclassification\b',
        r'\bregression\b', r'\btraining\b', r'\bvisuali[sz]ation\b'
    ]
    
    # Check for data tools
    data_tools_present = len(detect_data_tools(text)) > 0
    
    # Check for data keywords
    keyword_match = any(re.search(kw, cleaned) for kw in data_keywords)
    
    return data_tools_present or keyword_match


def is_valid_python_for_data_science(text):
    """Check if Python is used for data science (not just general programming)."""
    data_libs = detect_data_tools(text)
    return len(data_libs) > 0


def validate_machine_learning_claim(text):
    """Validate if Machine Learning claim is genuine."""
    ml_libs = detect_ml_libraries(text)
    return len(ml_libs) > 0


def is_data_science_role(job_description):
    """Determine if job description is for a data science role."""
    cleaned = clean_text(job_description)
    
    data_role_keywords = [
        r'\bdata scientist\b', r'\bdata analyst\b', r'\bml engineer\b',
        r'\bmachine learning\b', r'\bdata science\b', r'\banalytics\b'
    ]
    
    return any(re.search(kw, cleaned) for kw in data_role_keywords)



def extract_skills(text):
    """Extract skills from cleaned text using a predefined skill list."""
    cleaned = clean_text(text)
    found_skills = []
    for display_name, patterns in SKILL_CANDIDATES:
        for pattern in patterns:
            if re.search(pattern, cleaned):
                found_skills.append(display_name)
                break
    return found_skills






def parse_numeric_score(value, default=0):
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip().replace('%', '')
    try:
        score = float(value)
        if score != score:
            return default
        return int(max(0, min(100, round(score))))
    except Exception:
        return default


def normalize_analysis_result(raw_result):
    if isinstance(raw_result, str):
        print('Raw AI response string:', raw_result)
        try:
            raw_result = json.loads(raw_result)
        except Exception as e:
            raise Exception(f'Invalid AI response JSON: {str(e)}')
    elif isinstance(raw_result, dict):
        print('Raw AI response dict:', raw_result)
    else:
        raise Exception('Unsupported analysis result format')

    match_score = parse_numeric_score(raw_result.get('match_score'))
    confidence_score = raw_result.get('confidence_score')
    confidence_score = parse_numeric_score(confidence_score, default=None)
    if confidence_score is None:
        confidence_score = max(40, min(100, match_score + 10))

    if match_score >= 75:
        match_level = raw_result.get('match_level', 'High')
    elif match_score >= 50:
        match_level = raw_result.get('match_level', 'Medium')
    else:
        match_level = raw_result.get('match_level', 'Low')

    strong_matches = raw_result.get('strong_matches') or []
    missing_skills = raw_result.get('missing_skills') or []
    analysis_summary = raw_result.get('analysis_summary') or 'Resume match analysis completed.'
    recommendations = raw_result.get('recommendations') or []
    category_breakdown = raw_result.get('category_breakdown') or {cat: 0 for cat in SKILL_CATEGORIES.keys()}
    course_recommendations = raw_result.get('course_recommendations') or []
    project_recommendations = raw_result.get('project_recommendations') or []

    return {
        'match_score': match_score,
        'match_level': match_level,
        'confidence_score': confidence_score,
        'strong_matches': strong_matches,
        'missing_skills': missing_skills,
        'analysis_summary': analysis_summary,
        'recommendations': recommendations,
        'category_breakdown': category_breakdown,
        'course_recommendations': course_recommendations,
        'project_recommendations': project_recommendations
    }


def analyze_match(resume_text, job_description):
    """Analyze match between resume and job description using smart matching with data science validation."""
    
    # Handle edge cases
    if not resume_text or not resume_text.strip():
        return {
            'match_score': 0,
            'match_level': 'Low',
            'confidence_score': 20,
            'matched_skills': [],
            'missing_skills': [],
            'category_breakdown': {cat: 0 for cat in SKILL_CATEGORIES.keys()},
            'analysis_summary': 'Resume is empty. Please provide resume content.',
            'recommendations': ['Upload a complete resume with skills and experience']
        }
    
    if not job_description or not job_description.strip():
        return {
            'match_score': 0,
            'match_level': 'Low',
            'confidence_score': 20,
            'matched_skills': [],
            'missing_skills': [],
            'category_breakdown': {cat: 0 for cat in SKILL_CATEGORIES.keys()},
            'analysis_summary': 'Job description is empty. Please provide job description.',
            'recommendations': ['Enter a valid job description for matching']
        }
    
    resume_text = resume_text.strip()
    job_description = job_description.strip()
    
    # Check if job is for data science role
    is_data_role = is_data_science_role(job_description)
    
    # Extract skills, tools, and concepts from both texts
    job_skills_by_variation = find_skill_variations(job_description, SKILL_VARIATIONS)
    resume_skills_by_variation = find_skill_variations(resume_text, SKILL_VARIATIONS)
    job_tools = extract_tools(job_description)
    resume_tools = extract_tools(resume_text)
    job_concepts = detect_concepts(job_description, DOMAIN_CONCEPTS)
    resume_concepts = detect_concepts(resume_text, DOMAIN_CONCEPTS)
    
    # Data science validation rules
    if is_data_role:
        # For data science roles, apply strict validation
        
        # Rule 1: Python alone is NOT enough - must have data tools
        if 'python' in resume_skills_by_variation and 'machine learning' not in resume_skills_by_variation:
            has_data_libs = is_valid_python_for_data_science(resume_text)
            if not has_data_libs:
                # Remove Python from matches for data science role if no data libraries
                resume_skills_by_variation = [s for s in resume_skills_by_variation if s != 'python']
        
        # Rule 2: Machine Learning must have actual ML libraries
        if 'machine learning' in resume_skills_by_variation:
            has_ml_libs = validate_machine_learning_claim(resume_text)
            if not has_ml_libs:
                # Downgrade to weak match
                resume_skills_by_variation = [s for s in resume_skills_by_variation if s != 'machine learning']
                if 'data science' not in resume_skills_by_variation:
                    resume_skills_by_variation.append('python')  # Fallback to general Python
        
        # Rule 3: Validate data science projects
        if has_project_mention(resume_text):
            if not is_data_science_project(resume_text):
                # Project exists but not data science related - don't count as strong
                pass
    
    # Get matched and missing skills
    matched_skills = [skill for skill in job_skills_by_variation if skill in resume_skills_by_variation]
    missing_skills = [skill for skill in job_skills_by_variation if skill not in resume_skills_by_variation]
    
    job_requirements = []
    job_requirements.extend(job_skills_by_variation)
    job_requirements.extend([tool.lower() for tool in job_tools])
    job_requirements.extend([concept.lower() for concept in job_concepts])
    
    resume_requirements = set(resume_skills_by_variation)
    resume_requirements.update(tool.lower() for tool in resume_tools)
    resume_requirements.update(concept.lower() for concept in resume_concepts)
    
    missing_requirements = []
    seen = set()
    for requirement in job_requirements:
        if not requirement:
            continue
        norm = requirement.lower().strip()
        if norm in seen:
            continue
        if norm not in resume_requirements:
            missing_requirements.append(norm)
            seen.add(norm)
    missing_skills = missing_requirements
    
    # STRICT PENALTY FOR DATA SCIENCE ROLES
    if is_data_role and len(missing_skills) >= 2:
        # If 2+ core requirements missing for data science → score must be < 70
        match_score = calculate_weighted_score(job_skills_by_variation, resume_skills_by_variation)
        match_score = max(0, min(69, round(match_score)))
    elif is_data_role:
        # Check for critical missing data tools
        data_libs_in_job = any(lib in job_description.lower() for lib in DATA_SCIENCE_LIBRARIES)
        data_libs_in_resume = len(detect_data_science_libraries(resume_text)) > 0
        
        if data_libs_in_job and not data_libs_in_resume:
            match_score = calculate_weighted_score(job_skills_by_variation, resume_skills_by_variation)
            match_score = max(0, min(35, round(match_score)))
        else:
            match_score = calculate_weighted_score(job_skills_by_variation, resume_skills_by_variation)
            match_score = max(0, min(100, round(match_score)))
    else:
        # Standard scoring for non-data roles
        match_score = calculate_weighted_score(job_skills_by_variation, resume_skills_by_variation)
        match_score = max(0, min(100, round(match_score)))
    
    # Calculate category breakdown
    category_breakdown = calculate_category_breakdown(job_skills_by_variation, resume_skills_by_variation, resume_text)
    
    # Determine match level
    if match_score >= 75:
        match_level = 'High'
    elif match_score >= 50:
        match_level = 'Medium'
    else:
        match_level = 'Low'
    
    # Calculate confidence score
    confidence_score = calculate_confidence_score(
        len(matched_skills),
        len(job_skills_by_variation),
        resume_text,
        match_score,
        len(missing_skills)
    )
    
    # Detect projects in resume
    has_projects = has_project_mention(resume_text)
    is_relevant_project = is_data_science_project(resume_text) if is_data_role else has_projects
    
    # Build strong matches list
    strong_matches = matched_skills.copy()
    if is_relevant_project:
        strong_matches.insert(0, 'Project Experience')
    
    if not strong_matches:
        strong_matches = ['Problem Solving']
    
    # Build recommendations
    recommendations = []
    
    if is_data_role:
        # Data science specific recommendations
        if not is_valid_python_for_data_science(resume_text) and 'python' in missing_skills:
            recommendations.append("Add data science libraries to your Python projects: Pandas, NumPy, scikit-learn")
        
        if 'machine learning' in missing_skills and not validate_machine_learning_claim(resume_text):
            recommendations.append("Include ML library experience: scikit-learn, TensorFlow, or PyTorch")
        
        if not is_data_science_project(resume_text):
            recommendations.append("Add a portfolio project using datasets and data visualization tools")
    else:
        # Generic recommendations
        if missing_skills:
            top_missing_display = ', '.join(missing_skills[:3])
            recommendations.append(f"Highlight or develop expertise in: {top_missing_display}")
    
    if not has_projects and job_skills_by_variation:
        recommendations.append(f"Add a project example related to {', '.join(job_skills_by_variation[:2])}")
    
    if match_score < 50:
        recommendations.append("Review job requirements and tailor your resume with relevant skills")
    
    if not recommendations:
        recommendations.append("Your profile aligns well with the role. Highlight impact and achievements.")
    
    # Build analysis summary
    if match_score >= 75:
        summary_prefix = "Strong alignment"
    elif match_score >= 50:
        summary_prefix = "Moderate alignment"
    else:
        summary_prefix = "Limited alignment"
    
    strengths = ', '.join(strong_matches[:2]) if strong_matches else 'relevant experience'
    gaps = ', '.join(missing_skills[:2]) if missing_skills else 'additional skills'
    
    analysis_summary = f"{summary_prefix} with required skills. Strengths: {strengths}. Gaps: {gaps}."
    
    course_recommendations = generate_course_recommendations(missing_skills, is_data_role)
    project_recommendations = generate_project_recommendations(missing_skills, job_skills_by_variation, is_data_role)
    
    return normalize_analysis_result({
        'match_score': match_score,
        'match_level': match_level,
        'confidence_score': confidence_score,
        'strong_matches': strong_matches,
        'missing_skills': missing_skills,
        'category_breakdown': category_breakdown,
        'analysis_summary': analysis_summary,
        'recommendations': recommendations,
        'course_recommendations': course_recommendations,
        'project_recommendations': project_recommendations
    })


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Resume Analyzer API is running"}), 200

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        resume_text = data.get('resume_text', '').strip()
        job_description = data.get('job_description', '').strip()
        
        if not resume_text:
            return jsonify({"error": "Resume text is required"}), 400
        
        if not job_description:
            return jsonify({"error": "Job description is required"}), 400
        
        analysis_result = analyze_match(resume_text, job_description)
        
        return jsonify({
            "success": True,
            "data": analysis_result,
            "message": "Analysis completed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Analysis failed"
        }), 500

@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        if 'resume_file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['resume_file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({"error": "Job description is required"}), 400
        
        filename = file.filename.lower()
        resume_text = ""
        
        if allowed_file(filename):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=app.config['UPLOAD_FOLDER'])
            temp_path = temp_file.name
            try:
                temp_file.close()
                file.save(temp_path)
                resume_text = extract_text_from_pdf(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            return jsonify({"error": "Unsupported file type. Please upload PDF files only."}), 400
        
        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from file. Please ensure the file contains readable text."}), 400
        
        analysis_result = analyze_match(resume_text, job_description)
        
        return jsonify({
            "success": True,
            "data": analysis_result,
            "message": "File processed and analyzed successfully",
            "file_info": {
                "filename": file.filename,
                "size": len(resume_text)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "File processing failed"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Resume Analyzer Backend...")
    print("📍 Server running at http://localhost:5000")
    print("📝 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /analyze-text - Analyze text input")
    print("   POST /upload-file - Upload and analyze file")
    app.run(debug=True, host='0.0.0.0', port=5000)