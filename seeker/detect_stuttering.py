import librosa
import numpy as np
import os
from django.conf import settings
from keras.models import load_model

def analyze_audio(file_path):
    # Load the saved model
    model = load_model(os.path.join(settings.BASE_DIR, 'models', 'audio_clip_features_model.h5'))
    
    # Load the audio file
    audio, sr = librosa.load(file_path)

    # Extract the MFCC features from the audio file
    mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13).T, axis=0)

    # Reshape the MFCC features to match the input shape of the model
    mfccs = mfccs.reshape(1, -1)

    # Predict the audio clip features
    predictions = model.predict(mfccs)
    
    # Define feature names and their corresponding predicted values
    feature_names = [
        'Unsure', 'PoorAudioQuality', 'Prolongation', 'Block', 'SoundRep', 
        'WordRep', 'DifficultToUnderstand', 'Interjection', 'NoStutteredWords', 
        'NaturalPause', 'Music', 'NoSpeech'
    ]
    feature_values = predictions[0]  # Assuming predictions are an array of values

    # Define a threshold for small values
    threshold = 1e-5
    
    # Prepare data for later plotting
    data = prepare_plot_data(feature_names, feature_values, threshold)

    return data

def prepare_plot_data(feature_names, feature_values, threshold):
    # Filter features based on the threshold
    filtered_feature_names = [name for name, value in zip(feature_names, feature_values) if value > threshold]
    filtered_feature_values = [value for value in feature_values if value > threshold]

    # Add 'Other' category for very small values
    other_value = np.sum([value for value in feature_values if value <= threshold])
    filtered_feature_names.append('Other')
    filtered_feature_values.append(other_value)

    # Create a dictionary to store data for plotting
    plot_data = {
        'feature_names': feature_names,
        'feature_values': feature_values.tolist(),
        'filtered_feature_names': filtered_feature_names,
        'filtered_feature_values': filtered_feature_values
    }

    return plot_data
