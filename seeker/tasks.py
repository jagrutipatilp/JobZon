# # seeker/tasks.py
# your_app/tasks.py
from background_task import background

@background(schedule=60)  # Schedule to run 60 seconds from now
def my_background_task(param1, param2):
    # Your background task logic here
    print(f"Processing {param1} and {param2}")


# from celery import shared_task
# from .detect_stuttering import detect_stutter
# from .personality_predict import analyze_and_generate_data
# from .posture import analyze_video
# import os

# @shared_task
# def addinterview(video_path, audio_path, answerslong_string):
#     """
#     Celery task to process video and audio files asynchronously.
#     """
#     try:

#         with open(audio_path, 'rb') as audio_file:
#             stuttfeature_names, stuttfeature_values = detect_stutter(audio_file)

#         analysis_resultpersonality = analyze_and_generate_data(answerslong_string)

#         postureresults = analyze_video(video_path)

#         return stuttfeature_names, stuttfeature_values, analysis_resultpersonality, postureresults

#     except Exception as e:
#         print(f"An error occurred during processing: {e}")
#         return None, None, None, None
