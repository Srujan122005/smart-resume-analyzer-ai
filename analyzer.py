import re
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class ResumeAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def extract_text_from_file(self, file_content, file_extension):
        """Extract text from uploaded file"""
        # For text files or raw content
        if file_extension == 'txt' or file_extension == 'text':
            return file_content.decode('utf-8')
        return file_content
    
    def analyze_match(self, resume_text, job_description):
        """Analyze match between resume and job description"""
        if not resume_text or not job_description:
            return {
                "error": "Resume and job description are required",
                "match_score": 0
            }
        
        # Clean and tokenize texts
        resume_clean = self._clean_text(resume_text)
        jd_clean = self._clean_text(job_description)
        
        # Extract keywords
        resume_words = self._extract_keywords(resume_clean)
        jd_words = self._extract_keywords(jd_clean)
        
        # Calculate match score
        if len(jd_words) == 0:
            match_score = 0
        else:
            common_words = set(resume_words) & set(jd_words)
            match_score = len(common_words) / len(set(jd_words)) * 100
            match_score = min(100, max(0, match_score))
        
        # Extract missing keywords (important JD keywords not in resume)
        missing_keywords = list(set(jd_words) - set(resume_words))[:15]
        
        # Find strong keywords (present in both)
        matched_keywords = list(set(resume_words) & set(jd_words))[:15]
        
        # Simple skill extraction (common tech skills)
        common_skills = self._extract_skills(resume_clean)
        jd_skills = self._extract_skills(jd_clean)
        
        # Skill match analysis
        matched_skills = list(set(common_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(common_skills))[:10]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(match_score, missing_skills, missing_keywords)
        
        # Analyze resume structure
        resume_length = len(resume_text.split())
        jd_length = len(job_description.split())
        
        return {
            "match_score": round(match_score, 1),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations,
            "resume_stats": {
                "word_count": resume_length,
                "sentence_count": len(sent_tokenize(resume_text)),
                "has_contact_info": bool(re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', resume_text))
            },
            "job_stats": {
                "word_count": jd_length,
                "sentence_count": len(sent_tokenize(job_description))
            }
        }
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_keywords(self, text, top_n=50):
        """Extract important keywords from text"""
        words = word_tokenize(text)
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        # Get word frequencies
        word_freq = Counter(words)
        
        # Return most common words as keywords
        keywords = [word for word, freq in word_freq.most_common(top_n)]
        return keywords
    
    def _extract_skills(self, text):
        """Extract common technical and soft skills"""
        skill_patterns = [
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\breact\b', r'\bangular\b',
            r'\bvue\b', r'\bnod\.?js\b', r'\bdjango\b', r'\bflask\b', r'\bfastapi\b',
            r'\bsql\b', r'\bmongodb\b', r'\bpostgresql\b', r'\bmysql\b', r'\bdocker\b',
            r'\bkubernetes\b', r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\btensorflow\b',
            r'\bpytorch\b', r'\bpandas\b', r'\bnumpy\b', r'\bgit\b', r'\bjenkins\b',
            r'\bci/cd\b', r'\bagile\b', r'\bscrum\b', r'\bleadership\b', r'\bcommunication\b',
            r'\bteamwork\b', r'\bproblem[\s-]?solving\b', r'\bcritical thinking\b'
        ]
        
        found_skills = set()
        text_lower = text.lower()
        
        for pattern in skill_patterns:
            if re.search(pattern, text_lower):
                skill = pattern.replace(r'\b', '').replace(r'\?', '').replace(r'[\s-]?', ' ')
                found_skills.add(skill)
        
        return list(found_skills)
    
    def _generate_recommendations(self, match_score, missing_skills, missing_keywords):
        """Generate actionable recommendations"""
        recommendations = []
        
        if match_score < 30:
            recommendations.append("Your resume needs significant improvement. Focus on including relevant keywords and skills from the job description.")
        elif match_score < 60:
            recommendations.append("Your resume has some relevant content but could be stronger. Add more specific keywords and quantifiable achievements.")
        elif match_score < 80:
            recommendations.append("Good match! Consider fine-tuning your resume with a few missing keywords to improve your chances.")
        else:
            recommendations.append("Excellent match! Your resume aligns very well with the job requirements.")
        
        if missing_skills:
            top_skills = missing_skills[:3]
            recommendations.append(f"Highlight these missing skills if you have them: {', '.join(top_skills)}")
        
        if missing_keywords and len(missing_keywords) > 0:
            top_keywords = missing_keywords[:3]
            recommendations.append(f"Add these keywords to your resume: {', '.join(top_keywords)}")
        
        if not recommendations:
            recommendations.append("Your resume looks good! Consider tailoring it further to this specific role.")
        
        return recommendations