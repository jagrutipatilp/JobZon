import joblib
import os
from django.conf import settings
from django.http import JsonResponse
import matplotlib.cm as cm
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
# MBTI types and their descriptions
mbti_descriptions = {
    'INFJ': 'Insightful, idealistic, and empathetic. They seek meaning and connection in all that they do.',
    'ENTP': 'Enthusiastic, inventive, and analytical. They enjoy exploring new ideas and challenging the status quo.',
    'INTP': 'Curious, logical, and independent. They enjoy solving complex problems and understanding abstract concepts.',
    'INTJ': 'Strategic, determined, and analytical. They excel at planning and executing long-term goals.',
    'ENTJ': 'Confident, efficient, and decisive. They are natural leaders who thrive in strategic and high-stakes environments.',
    'ENFJ': 'Charismatic, compassionate, and inspiring. They are driven by a desire to help others and make a positive impact.',
    'INFP': 'Creative, idealistic, and empathetic. They are guided by their values and seek to understand others.',
    'ENFP': 'Enthusiastic, imaginative, and sociable. They enjoy exploring possibilities and connecting with people.',
    'ISFP': 'Artistic, sensitive, and spontaneous. They enjoy experiencing the world through their senses and expressing their creativity.',
    'ISTP': 'Practical, logical, and adventurous. They enjoy hands-on activities and solving immediate problems.',
    'ISFJ': 'Caring, meticulous, and reliable. They are dedicated to helping others and ensuring that their needs are met.',
    'ISTJ': 'Responsible, practical, and detail-oriented. They value order and structure and excel at organizing and managing tasks.',
    'ESTP': 'Energetic, action-oriented, and pragmatic. They thrive in dynamic environments and enjoy taking risks.',
    'ESFP': 'Spontaneous, outgoing, and fun-loving. They enjoy being the center of attention and living in the moment.',
    'ESTJ': 'Organized, assertive, and efficient. They are natural leaders who focus on getting things done and ensuring rules are followed.',
    'ESFJ': 'Warm, outgoing, and sociable. They value harmony and work hard to create a positive environment for others.'
}

trait_mapping = {
    'INFJ': 'Insightful', 'ENTP': 'Innovative', 'INTP': 'Analytical', 'INTJ': 'Strategic',
    'ENTJ': 'Assertive', 'ENFJ': 'Charismatic', 'INFP': 'Idealistic', 'ENFP': 'Enthusiastic',
    'ISFP': 'Artistic', 'ISTP': 'Practical', 'ISFJ': 'Nurturing', 'ISTJ': 'Responsible',
    'ESTP': 'Adventurous', 'ESFP': 'Spontaneous', 'ESTJ': 'Organized', 'ESFJ': 'Supportive'
}




def analyze_and_generate_data(input_text):
    model_filename =  os.path.join(settings.BASE_DIR, 'models', 'personality_model.pkl')
    vectorizer_filename =  os.path.join(settings.BASE_DIR, 'models', 'personality_model_vectorizer.pkl')
    
    model = joblib.load(model_filename)
    vectorizer = joblib.load(vectorizer_filename)
    
    # Predict personality probabilities
    text_transformed = vectorizer.transform([input_text])
    probabilities = model.predict_proba(text_transformed)[0]
   
    classes = model.classes_
    
    # Get predicted personality type and description
    predicted_personality = classes[np.argmax(probabilities)]
    description = mbti_descriptions.get(predicted_personality, 'No description available')
    
    # Prepare data for MongoDB
    result = {
        'predicted_personality': trait_mapping.get(predicted_personality, 'Unknown'),
        'description': description,
        'probabilities': probabilities.tolist(),
        'classes': classes.tolist()
    }
    
    return result
