from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from nltk.data import find
import unicodedata
from sklearn.neighbors import NearestNeighbors
import re
import inflect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
import re
import inflect
from sklearn.feature_extraction.text import TfidfVectorizer
from summarizer import Summarizer
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
model = Summarizer()
# Ensure NLTK data is downloaded
try:
    find('corpora/stopwords.zip')
except LookupError:
    from nltk import download
    download('stopwords')

try:
    find('corpora/wordnet.zip')
except LookupError:
    from nltk import download
    download('wordnet')

class ResultElement:
    def __init__(self, rank, filename):
        self.rank = rank
        self.filename = filename

def normalize(words):
    def remove_non_ascii(words):
        return [unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore') for word in words]

    def to_lowercase(words):
        return [word.lower() for word in words]

    def remove_punctuation(words):
        return [re.sub(r'[^\w\s]', '', word) for word in words if re.sub(r'[^\w\s]', '', word) != '']

    def replace_numbers(words):
        p = inflect.engine()
        return [p.number_to_words(word) if word.isdigit() else word for word in words]

    def remove_stopwords(words):
        return [word for word in words if word not in stopwords.words('english')]

    def stem_words(words):
        stemmer = LancasterStemmer()
        return [stemmer.stem(word) for word in words]

    def lemmatize_verbs(words):
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(word, pos='v') for word in words]

    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    words = stem_words(words)
    words = lemmatize_verbs(words)
    return words

def check_additional_fields(text, experience, place, sector, openings, skills):
    text = normalize(text)
    fields = normalize([experience, place, sector, openings] + skills)
    
    match_score = 0
    for field in fields:
        if field in text:
            match_score += 1

    return match_score

def vectorize_and_rank_resumes(resume_texts, job_desc_text, experience, place, sector, openings, skills):
    from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def vectorize_and_rank_resumes(resume_texts, job_desc_text, experience, place, sector, openings, skills):
    # Normalize job description
    job_desc_summary = model(job_desc_text)
    if isinstance(job_desc_summary, list):
        job_desc_summary = ' '.join(job_desc_summary)
    job_desc = ' '.join(job_desc_summary.split()[:100])

    # Filter out resumes with no text
    filtered_resume_texts = [(filename, text) for filename, text in resume_texts if text.strip()]
    if not filtered_resume_texts:
        raise ValueError("No valid resumes to process.")

    # Combine job description and resumes for vectorization
    texts = [job_desc] + [resume_text for _, resume_text in filtered_resume_texts]
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(texts)

    # Extract vectors
    job_desc_vector = vectors[0].toarray().reshape(1, -1)
    resume_vectors = vectors[1:]

    # Check if resume_vectors is empty
    if resume_vectors.shape[0] == 0:
        raise ValueError("No resume vectors to fit.")

    # Nearest Neighbors Scoring
    neighbor_scores = []
    for i in range(resume_vectors.shape[0]):
        neigh = NearestNeighbors(n_neighbors=1)
        neigh.fit(resume_vectors[i].reshape(1, -1))
        distances, _ = neigh.kneighbors(job_desc_vector)
        neighbor_scores.append(distances.flatten()[0])  # Only taking the distance score

    # TF-IDF Scoring
    tfidf_scores = cosine_similarity(job_desc_vector, resume_vectors).flatten()

    # Match Scores based on additional fields
    match_scores = [check_additional_fields(resume_text, experience, place, sector, openings, skills) for _, resume_text in filtered_resume_texts]

    # Ensure lengths match
    if len(tfidf_scores) != len(filtered_resume_texts):
        raise ValueError(f"Length mismatch: tfidf_scores ({len(tfidf_scores)}) vs resume_texts ({len(filtered_resume_texts)})")
    
    if len(match_scores) != len(filtered_resume_texts):
        raise ValueError(f"Length mismatch: match_scores ({len(match_scores)}) vs resume_texts ({len(filtered_resume_texts)})")

    # Combine Nearest Neighbors scores, TF-IDF scores, and Match scores
    combined_scores = [(neighbor_scores[i] + tfidf_scores[i] + match_scores[i], filename) 
                        for i, (filename, _) in enumerate(filtered_resume_texts)]
    
    # Sort by combined scores
    return sorted(combined_scores, key=lambda x: x[0])



def res(total,job_desc_text, experience, place, sector, openings, skills, resume_texts):
    
    ranked_resumes = vectorize_and_rank_resumes(resume_texts, job_desc_text, experience, place, sector, openings, skills)

    # Get the top 3 ranked resumes
    top_resumes = ranked_resumes[:total]
    
    flask_return = []
    for rank, (score, filename) in enumerate(top_resumes):
        rank += 1  # To start ranking from 1 instead of 0
        ml = [rank, filename, score]  # Corrected list creation
        flask_return.append(ml)

    return flask_return
