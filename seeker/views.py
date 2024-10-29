from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import UserProfile, InterviewQ
from recruiter.models import Jobs 
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import threading
import time
from pydub import AudioSegment
from django.conf import settings

from collections import OrderedDict
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login
from .interview_system import InterviewAI 
from .detect_stuttering import analyze_audio
from .personality_predict import analyze_and_generate_data
from .posture import VideoAnalyzer 
from django.http import JsonResponse
import speech_recognition as sr
import json
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
import os
import uuid
airec = InterviewAI()
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

# from .tasks import addinterview
import os
os.environ["OPENAI_API_KEY"] = "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"


from django.shortcuts import get_object_or_404, redirect
from django import forms
from django.core.files.storage import default_storage
from django.db import transaction
import PyPDF2
from django.db.models import Count
from django.http import JsonResponse
from django.core.files.base import ContentFile
job_ids=None
loginu=True
profile_object={}
jid=0
jidinterview=0
user_profile=None
applied_jobs=None
cnt_que=0
preque=''
background_processing_taski=0

def index(request):
    request.session['loginu'] = True    
    global user_profile
    global applied_jobs
    user_profile=None
    applied_jobs=None
    jobs_datad = Jobs.objects.order_by('dobe')[:3]

    # Fetching data for annotation and chart
    jobs = Jobs.objects.annotate(application_count=Count('id'))

    return render(request,'index.html', {'login':  request.session.get('loginu', True),"job_data": jobs_datad})
    

def index2(request):
    global user_profile
    global applied_jobs

    return render(request, 'index2.html', {'user_profile': user_profile, 'applied_jobs': applied_jobs})


def download_resume(request, user_profile_id):
    user_profile = UserProfile.objects.get(id=user_profile_id)
    response = HttpResponse(user_profile.resume, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
    return response

def interviewapp(request, job_id):  
    for j in user_profile.applied_jobs:
        if(j['jobid']==job_id):
            print("set\n\nfgfgfgf\n\nghghh\n\nfgfg",j['jobname'])
            j['status']=9
        user_profile.save()
    if request.method == 'POST':
        
        
        if request.method == "POST":
            recognized_text = recognize_speech_with_gaps()
        

        return render(request, 'interviewapp.html', {'text': recognized_text,'job_id':job_id})

    
    else:
        recognized_text = ""
        initial_question = "Click Start Button to start this interview"
        return render(request, 'interviewapp.html' ,{'job_id':job_id})


def initialque(request):      
    question = "Tell me about yourself."
    # If a valid question is generated, add it to asked questions and increment the count
    airec.asked_questions.add(question)
    airec.asked_questions_order=question

    airec.question_count += 1
      # Store the question and corresponding response  # Store the question and corresponding response
    return JsonResponse({'question': question})

def recognize_speech_with_gaps():
    r = sr.Recognizer()
    r.pause_threshold = 1.5  # Adjust this to detect gaps
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            # Convert audio to text
            text = r.recognize_google(audio)
            # Split the text where pauses occur (this is a simplified version)
            segments = text.split('. ')
            return segments
        except sr.UnknownValueError:
            return ["Could not understand the audio"]
        except sr.RequestError:
            return ["Could not request results"]


@csrf_exempt
def thankyou(request):
    
    if request.method == 'POST':
        # try:
        # Retrieve files from the request
        video_file = request.FILES.get('videoBlob')
        
        if video_file:
            job_id = request.POST.get('job_id')
           
            # Save the files temporarily
            video_path = os.path.join(settings.BASE_DIR, 'media', 'recording.webm')
            with open(video_path, 'wb') as f:
                f.write(video_file.read())
            
            # Convert video to audio
            audio_path = os.path.join(settings.BASE_DIR, 'media', 'recording.wav')
            audio = AudioSegment.from_file(video_path, format="webm")
            audio.export(audio_path, format="wav")
            
            # Create an InterviewQ object
            interview = InterviewQ.objects.create(
                applicantid=user_profile.id,
                jobid=job_id,
                video_blob=video_file.read(),
            )

            
            jobinterview = Jobs.objects.get(id=job_id)
            for entry in jobinterview.interview_applicants:
                if isinstance(entry[2], OrderedDict):
                    # Extract the id and name
                    mylistforapplicant=[interview.id,entry[0],entry[1],entry[2]]
                    jobinterview.append_interviewed(mylistforapplicant)
                    jobinterview.save()

            # Start background processing
            threading.Thread(target=background_processing_task, args=(interview.id, video_path, audio_path)).start()

            # Return the interview ID for progress checking
            return JsonResponse({'status': 'success', 'message': 'Video and audio uploaded successfully', 'interview_id': interview.id})

        # except Exception as e:
        #     return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # If not POST, render the thank you page
    airec.question_count = 0
    airec.genralqueasked = 0
    airec.mustqueasked = 0
    airec.asked_questions.clear()
    airec.asked_topics.clear()

    # Pass a placeholder interview_id for progress check
    interview_id = None
    return render(request, 'thankyou.html', {'interview_id': interview_id})

def background_processing_task(interview_id, video_path, audio_path):
    # try:
    interview = InterviewQ.objects.get(id=interview_id)

    # Perform analysis
    answers = airec.responses.values()
    answerslong_string = ' '.join(answers)
    analysis_resultpersonality = analyze_and_generate_data(answerslong_string)
    postureresults = VideoAnalyzer(video_path).analyze_video()
    stuttfeature_names = analyze_audio(audio_path)

    # Update the interview response
    interview.questions_and_answers = airec.responses
    interview.stuttfeature_names = stuttfeature_names
    interview.analysis_resultpersonality = analysis_resultpersonality
    interview.postureresults = postureresults
    
    interview.save()
    background_processing_taski=1
    print('done')
    print("Processing completed")
    # except InterviewQ.DoesNotExist:
    #     pass  # Handle the error appropriately

def check_progress(request, interview_id):
    # try:
    interview = InterviewQ.objects.get(id=interview_id)
    if background_processing_taski==1:
        return JsonResponse({"status": "completed"})
    else:
        return JsonResponse({"status": "in_progress"})
    # except InterviewQ.DoesNotExist:
    #     return JsonResponse({"status": "error"})

def get_next_question(request):
    response_text = request.GET.get('response_text', '')
    
    question = airec.ask_next_question(response_text)
    

    return JsonResponse({'question': question})

def submit_response(request):
    # Handle the logic to receive and process responses
    if request.method == 'POST':
        response = request.POST.get('response')
        airec.store_response(airec.last_question, response)
        next_question = airec.ask_questions()
        return JsonResponse({'next_question': next_question})

def apply_for_job(request, job_id):
    global user_profile
    global applied_jobs
    global jid
    jid=job_id

    if user_profile and job_id:  # Check if user_profile is available and job_id is valid
        job = Jobs.objects.get(id=job_id)
        
        job.applied += 1
        job.applicants.append(serialize_user_profile(user_profile))
        
        job.save()
        user_profile.applied_jobs.append(serialize_jobs(job,1))  # Add the job to applied_jobs
        applied_jobs = user_profile.applied_jobs  # Update applied_jobs list
        user_profile.save()  # Save the user profile with the updated applied_jobs
    return redirect('index2')

def serialize_jobs(job,sts):
    return {
        "id": str(job.id),
        "jobid": job.id,
        "status": sts,
        "jobname": job.jobname,
        "applied": job.applied,
        "dobe": job.dobe.isoformat(),
        "exp": job.exp,
        "place": job.place,
        "typ": job.typ,
        "status": job.status,
        "sector": job.sector,
        "openings": job.openings,
        "creteria1": job.creteria1,
        "creteria2": job.creteria2,
        "creteria3": job.creteria3,
        "creteria4": job.creteria4,
        "creteria5": job.creteria5,
        "about": job.about,
    }

def serialize_user_profile(user_profile):
    return {
        "id": str(user_profile.id),
        "name": user_profile.name,
        "email": user_profile.email,
        "dob": user_profile.dob.isoformat(),
        "exp": user_profile.exp,
        "post": user_profile.post,
        "gen": user_profile.gen,
        "ad1": user_profile.ad1,
        "ad2": user_profile.ad2,
        "pho1": user_profile.pho1,
        "pho2": user_profile.pho2,
        "edu": user_profile.edu,
        "per": user_profile.per,
        "uni": user_profile.uni,
        "about": user_profile.about,
        "skills": user_profile.skills,
        "match": user_profile.match,
        "interviewscore": user_profile.interviewscore,
        "resumetxt": user_profile.resumetxt,
    }


def contacts(request):
    name_text = ""
    message_text = ""
    email_text = ""
    if request.method == 'POST':
        name_text = request.POST.get('name', '')
        email_text = request.POST.get('email', '')
        message_text = request.POST.get('message', '')


        subject = 'Contact Form Submission'
        message = f'Name: {name_text}\nEmail: {email_text}\nMessage: {message_text}'
        from_email = 'your_email@example.com'  # Replace with your email address
        recipient_list = ['jagrutipatil5433@gmail.com']

        # send_mail(subject, message, from_email, recipient_list)

    return render(request, 'contacts.html', {'name_text': name_text, 'email_text': email_text, 'message_text': message_text,'login': request.session.get('loginu', True),})


def Guidlines(request):
    return render(request, 'Guidlines.html', {'login': request.session.get('loginu', True),})

def jobs(request):
    if not loginu:
        jobs = user_profile.applied_jobs
        return render(request, 'jobs.html', {'jobs': jobs,'login': request.session.get('loginu', True),'user_profile': user_profile})
    else:
        jobs = Jobs.objects.all() 
        return render(request, 'jobs.html', {'jobs': jobs,'login': request.session.get('loginu', True),'user_profile': user_profile})
  

def signin(request):
    global loginu
    global user_profile
    global applied_jobs

    if request.method == 'POST':
        name_text = request.POST.get('Uname', '')
        Password_text = request.POST.get('Password', '')
        
        loginu = False
        matching_profiles = UserProfile.objects.filter(username=name_text)
        filtered_profiles = [profile for profile in matching_profiles if profile.passw == Password_text]
        
        if filtered_profiles:
            loginu = True
            request.session['loginu'] = False
            user_profile = filtered_profiles[0]
            
            # Safely retrieve applied jobs if they exist
            applied_jobs = user_profile.applied_jobs if user_profile.applied_jobs else []

            return render(request, 'index2.html', {'user_profile': user_profile, 'applied_jobs': applied_jobs})
        else:
            return render(request, 'signin.html', {'login_failed': True})

    return render(request, 'signin.html')



def signinrec(request):
    names = UserProfile.objects.values_list('name', flat=True)

    name_text = ""
    Password_text = ""
    if request.method == 'POST':
        name_text = request.POST.get('Uname', '')
        Password_text = request.POST.get('Password', '')
        if 'rec' == name_text and 'rec' == Password_text:
            return redirect('indexr')
        else :
            return render(request, 'signinrec.html',{'login_failed': True,})

    return render(request, 'signinrec.html', {'name_text': name_text,'login': request.session.get('loginu', True),})


def signup(request):
    name = ""
    email = ""
    dob = ""
    exp = ""
    post = ""
    gen = ""
    ad1 = ""
    ad2 = ""
    pho1 = ""
    pho2 = ""
    work = ""
    edu = ""
    per = ""
    uni = ""
    about=""
    username=""
    passw=""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        dob = request.POST.get('dob', '')
        exp = request.POST.get('exp', '')
        post = request.POST.get('post', '')
        gen = request.POST.get('gen', '')
        ad1 = request.POST.get('ad1', '')
        ad2 = request.POST.get('ad2', '')
        pho1 = request.POST.get('pho1', '')
        pho2 = request.POST.get('pho2', '')
        work = request.POST.get('work', '')
        edu = request.POST.get('edu', '')
        per = request.POST.get('per', '')
        uni = request.POST.get('uni', '')
        about = request.POST.get('about', '')
        username = request.POST.get('username', '')
        passw = request.POST.get('pass1', '')
        
        uploaded_file = request.FILES.get('resume')
        text = ""
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        num_pages = len(pdf_reader.pages)
        pdf_content = uploaded_file.read() 
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        UserProfile.objects.create(
            name = name,
            email = email,
            dob = dob,
            exp = exp,
            post = post,
            gen =gen,
            ad1 = ad1,
            ad2 = ad2,
            pho1 = pho1,
            pho2 = pho2,
            work = work,
            edu = edu,
            per = per,
            uni = uni,
            about = about,
            username=username,
            passw=passw,
            resumetxt=text,
            resume=pdf_content,
        )
        
        return redirect('signin')
    else:
        return render(request, 'signup.html', {'name  ': "",'email ': "",'dob   ': "",'exp   ': "",'post  ': "",'gen   ': "",'ad1   ': "",'ad2   ': "",'pho1  ': "",'pho2  ': "",'work  ': "",'edu   ': "",'per   ': "",'uni   ': "",'login': request.session.get('loginu', True),})



def StudenPrograms(request):
    return render(request, 'StudenPrograms.html', {'login': request.session.get('loginu', True),})

def sample(request):
    return render(request, 'sample.html', {'login': request.session.get('loginu', True),})

def check_username_availability(request, username):
    username_exists = UserProfile.objects.filter(username=username).exists()
    return JsonResponse({'exists': username_exists})

def pull_from_website(url):
    
    # Doing a try in case it doesn't work
    try:
           
        
        # Get your text
        text = "soup.get_text()"
    
         
        return text
    except:
        # In case it doesn't work
        print ("Whoops, error")
        return None