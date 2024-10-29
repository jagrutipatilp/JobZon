import ast
import datetime
from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Jobs
from django.db.models import Count
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import re
from .ats import res
from bson import Binary
from collections import OrderedDict
import matplotlib
matplotlib.use('Agg')
from seeker.models import UserProfile, InterviewQ, UploadedFile


import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render


def indexr(request):
    # Fetching data for the chart
    jobs_datad = Jobs.objects.order_by('dobe')[:3]

    # Fetching data for annotation and chart
    jobs = Jobs.objects.annotate(application_count=Count('id'))

    # Creating a list of dictionaries containing job data
    job_data = [{'job_title': job.jobname, 'job_count': job.applied} for job in jobs]

    context = {'jobs': job_data}

    # Convert the context to a JSON string and escape it for safe use in JavaScript
    chart_data_json = json.dumps(context)
    jobs = Jobs.objects.all()
    jobonpriority = [] 
    today = datetime.date.today()

    # Fetch job details for each job ID and store in the dictionary applicants = Applicant.objects.filter(id__in=applicant_ids)
    for job in jobs:
        if today==job.dobe:
            jobonpriority.append(job)
       

    return render(request, 'indexr.html', {"job_data": jobs_datad, "chart_data_json": chart_data_json, 'jobp': jobonpriority})


def start_process(request, job_id):
    job = Jobs.objects.get(id=job_id)
    ids=[]
    resume_texts = []
    if job.applicants:
        for entry in job.applicants:
            ids.append(entry['id'])
            resume_tuple = (f"Resume {entry['name']} {entry['id']}", entry['resumetxt'])
            resume_texts.append(resume_tuple)

        # Correctly create the list of criteria
        criteria = [job.creteria1, job.creteria2, job.creteria3, job.creteria4, job.creteria5]

        # Call the res function with the correct arguments
        result = res(3, job.about, job.exp, job.place, job.sector, job.openings, criteria, resume_texts)
        for j in result:
            
            rank=j[0]
            score=j[2]
            parts = j[1].split()
            applicant = UserProfile.objects.get(id=parts[-1])
            
            if applicant:
                for z in applicant.applied_jobs:
                    if z['id']==str(job.id):
                        z['status']=2
                        print(z['id'],z['status'])
                applicant.applied_jobs=applicant.applied_jobs
                
                applicant.save()
                jobtoadd=serialize_jobs(job)
                applicanttoadd=serialize_user_profile(applicant)
            mylistforjobtoadd=[rank,score,jobtoadd]
            mylistforapplicant=[rank,score,applicanttoadd]
            applicant.append_to_applied_interview(mylistforjobtoadd)
            job.append_interview_applicant(mylistforapplicant)
            job.save()
            applicant.save()
        return render(request, 'ALlJobs.html')
    else:
        return HttpResponse('No Applicant Applied!')

   
    
    # Return a response to indicate success
    # return HttpResponse('Process started successfully!')

def serialize_jobs(job):
    return {
        "id": str(job.id),
        "jobid": job.jobid,
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

def interView_candidate(request, job_id, applicant_id):
    # Get the UserProfile and Job instances based on IDs
    user_profile = get_object_or_404(UserProfile, id=applicant_id)
    job = get_object_or_404(Jobs, id=job_id)
    job.applicants.remove(user_profile)
    user_profile.status += 1
    job.interviewednts.add(user_profile)
    for applicjob in user_profile.applied_jobs.all():
        if(applicjob.id==job_id):
            applicjob.status=2
            applicjob.save()
    user_profile.save()
    job.save()
    
    return redirect('ATS')


def shortlist_candidate(request, job_id, applicant_id):
    # Get the UserProfile and Job instances based on IDs
    user_profile = get_object_or_404(UserProfile, id=applicant_id)
    job = get_object_or_404(Jobs, id=job_id)
    job.interviewednts.remove(user_profile)
    print('infun')
    # Perform the actions on the retrieved instances
    user_profile.status += 1
    
    job.shortlistedappl.add(user_profile)
    for applicjob in user_profile.applied_jobs.all():
        if(applicjob.id==job_id):
            applicjob.status=3
            applicjob.save()
    user_profile.save()
    job.save()


    print(user_profile,job.interviewednts)
    return redirect('ATS')

def Review_candidate(request, job_id, applicant_id):
    # Get the UserProfile and Job instances based on IDs
    user_profile = get_object_or_404(UserProfile, id=applicant_id)
    job = get_object_or_404(Jobs, id=job_id)
    job.applicants.remove(user_profile)
    
    for applicjob in user_profile.applied_jobs.all():
        if(applicjob.id==job_id):
            applicjob.status=4
            applicjob.save()
    # Perform the actions on the retrieved instances
    user_profile.status += 1
    job.interviewednts.add(user_profile)
    user_profile.save()
    job.save()
    
    return redirect('Interview')


def view_shortlisted(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)
    
    shortlisted_applicants = job.applicants

    # # Extract the applicant IDs from the shortlisted_applicants JSONField
    # applicant_ids = [applicant['id'] for applicant in shortlisted_applicants]

    # # Get the corresponding Applicant objects
    # applicants = Applicant.objects.filter(id__in=applicant_ids)
    shr_no=len(shortlisted_applicants)
    app_no=job.applied
    context = {
        'job': job,
        'shortlisted_applicants': shortlisted_applicants,
        'shortlisted_no': shr_no,
        'no_applicants': app_no
    }
    
    return render(request, 'view_shortlisted.html', context)

def mail_candidate(request, job_id, applicant_id):
    # Get the UserProfile and Job instances based on IDs
    
    
    return redirect('Interview')

 # Replace np.float32() with just the float value inside
def replace_numpy_float(match):
    return match.group(1)  # Return the captured float value

def report(request, job_id, applicant_id):
    user_profile = UserProfile.objects.get(id=applicant_id)
    interview = get_object_or_404(InterviewQ, jobid=job_id, applicantid=applicant_id)

    # Logging interview ID
    print(interview.id)

    # Remove the outer parentheses and single quotes
    input_string = interview.stuttfeature_names.strip("()'")
    input_string = input_string.replace("np.float32(", "").replace(")", "")

    # Stuttering Analysis
    stutt = ast.literal_eval(input_string)
    print(stutt['feature_values'])

    stutt_feature_names = stutt['feature_names']  # Assuming this contains JSON string
    stutt_feature_values = stutt['feature_values']  # Replace with actual extraction logic

    # Posture Analysis
    stability_values = interview.postureresults['stability_values']  # Adjust according to actual data structure
    distance_values = interview.postureresults['distance_values']
    expression_changes = interview.postureresults['expression_changes']
    time_points = range(len(stability_values))

    # Personality Analysis
    predicted_personality = interview.analysis_resultpersonality['predicted_personality']
    probabilities = interview.analysis_resultpersonality['probabilities']
    classes = [
    'Protagonist', 'Campaigner', 'Commander', 'Debater', 'Consul', 
    'Entertainer', 'Executive', 'Entrepreneur', 'Advocate', 
    'Mediator', 'Architect', 'Logician', 'Defender', 'Adventurer', 
    'Logistician', 'Virtuoso'
]

    # Normalize the data to sum to 1 for pie chart
    filtered_feature_values_normalized = [value / sum(stutt_feature_values) for value in stutt_feature_values]

    # Create a figure
    plt.figure(figsize=(6, 6))

    # Function to display only non-zero values in the percentage labels
    def func(pct):
        return '{:1.1f}%'.format(pct) if pct > 0.1 else ''

    formatted_names = ['\n' + name for name in stutt_feature_names]
    
    # Append '\n\n' to the last element
    if formatted_names:
        formatted_names[-1] += '\n\n'
    

    # Create a pie chart with adjusted label distance
    wedges, texts, autotexts = plt.pie(
        filtered_feature_values_normalized,
        labels=formatted_names,
        autopct=func,  # Use the custom function for autopct
        startangle=0,
        colors=plt.cm.Set3.colors,
        labeldistance=1.1  # Adjust the distance of the labels
    )

    # Adjust font sizes for better readability
    for text in texts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_fontsize(8)

    # Draw a circle at the center of the pie to make it look like a donut chart
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # Add title
    plt.title('Stuttering Features Distribution', fontsize=16)

    # Save the figure to a BytesIO object
    stutt_img = io.BytesIO()
    plt.savefig(stutt_img, format='png', bbox_inches='tight')  # Use bbox_inches to prevent clipping
    plt.close()
    stutt_img.seek(0)

    # Convert to base64
    stutt_img_base64 = base64.b64encode(stutt_img.getvalue()).decode()
    # 2. Posture Analysis Line Graph
    # Create subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    # Stability Values
    axs[0].plot(time_points, stability_values, color='b', linewidth=2, label='Stability')
    axs[0].set_title('Stability Values Over Time')
    axs[0].set_ylabel('Stability')
    axs[0].legend()

    # Distance Values
    axs[1].plot(time_points, distance_values, color='g', linewidth=2, label='Distance')
    axs[1].set_title('Distance Values Over Time')
    axs[1].set_ylabel('Distance')
    axs[1].legend()

    # Expression Changes
    axs[2].plot(time_points, expression_changes, color='r', linewidth=2, label='Expression Changes')
    axs[2].set_title('Expression Changes Over Time')
    axs[2].set_ylabel('Expression Changes')
    axs[2].legend()

    # Set the x-axis label
    axs[2].set_xlabel('Time Points')

    # Adjust layout
    plt.tight_layout()

    # Save the plot to a BytesIO object
    posture_img = io.BytesIO()
    plt.savefig(posture_img, format='png')
    plt.close()  # Close the figure to free memory
    posture_img.seek(0)

    # Encode the image in base64 for embedding in HTML or returning in response
    posture_img_base64 = base64.b64encode(posture_img.getvalue()).decode()

    # 3. Personality Analysis Bar Graph
    # Create a figure
    plt.figure(figsize=(10, 6))

    # Create a horizontal bar graph for personality probabilities
    plt.barh(classes, probabilities, color='skyblue')

    # Add titles and labels
    plt.title(f'Personality Analysis: {predicted_personality}', fontsize=16)
    plt.xlabel('Probability', fontsize=14)
    plt.ylabel('Personality Types', fontsize=14)
    plt.xlim(0, 0.3)  # Set x-axis limit to better fit the probabilities

    # Save the figure to a BytesIO object
    personality_img = io.BytesIO()
    plt.savefig(personality_img, format='png')
    plt.close()
    personality_img.seek(0)

    # Encode the image in base64
    personality_img_base64 = base64.b64encode(personality_img.getvalue()).decode()
    
    # Render the template with the images
    return render(request, 'report.html', {
        'user': user_profile,
        'base64_string': user_profile.resume,
        'qa': list(interview.questions_and_answers.items()),
        'stutt_img': stutt_img_base64,
        'posture_img': posture_img_base64,
        'expression':interview.postureresults['expression_description'],
        'stability_description':interview.postureresults['stability_description'],
        'avg_stability':round(interview.postureresults['avg_stability'], 1),
        'distance_description':interview.postureresults['distance_description'],
        'avg_distance':interview.postureresults['avg_distance'],
        'predicted_personality':interview.analysis_resultpersonality['predicted_personality'],
        'description':interview.analysis_resultpersonality['description'],
        'personality_img': personality_img_base64,
    })

   

# Helper function to convert plot to base64
def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64


def downloadresume_candidate(request, job_id, applicant_id):
    # Get the UserProfile and Job instances based on IDs
    print('download')
    applicant = get_object_or_404(UserProfile, id=applicant_id)
    user_profile = UserProfile.objects.get(id=applicant_id)
    response = HttpResponse(user_profile.resume, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
    return response
    if applicant.resume:
        print("Resume found.")
        response = HttpResponse(applicant.resume, content_type='application/pdf')  # Adjust content type if needed
        response['Content-Disposition'] = 'attachment; filename="resume.pdf"'  # Adjust filename
        # response = HttpResponse(user_profile.resume, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
        print(response)
        return response
    return response

def ATS(request):
    usrs = UserProfile.objects.all()
    jobs = Jobs.objects.all()
    sections = {
        'experience': (['experience', 'work history', 'employment', 'professional background'], 10),
        'education': (['education', 'academic background', 'degrees'], 8),
        'skills': (['skills', 'proficiencies', 'technical skills', 'software'], 9),
        'achievements': (['achievements', 'accomplishments', 'results'], 7),
        'leadership': (['leadership', 'teamwork', 'collaboration'], 6),
        'finance': (['finance', 'financial knowledge'], 8),
        'compliance': (['compliance', 'regulatory', 'legal'], 7),
        'customer_service': (['customer service', 'client interactions'], 6),
        'communication': (['communication', 'written', 'verbal'], 7),
        'detail_oriented': (['attention to detail', 'precision', 'accuracy'], 8),
        'problem_solving': (['problem-solving', 'analytical skills'], 9),
        'memberships': (['memberships', 'professional organizations'], 5),
        'adaptability': (['adaptability', 'learning', 'flexibility'], 6)
    }
    
    cr1 =  ['Interpersonal Skills', 'Analytical Thinking', 'Customer Service', 'Marketing Proficiency', 'Operation Management', 'Business Acumen', 'Financial Management', 'Time Management', 'Leadership Skills', 'Commercial Awareness', 'Knowledge of financial principles and practices','Analytical mind', 'knowledge of banking products', 'markets and relevant regulations', 'Sales and negotiation skills', 'Strong communication & presentation skills', 'Ability to Work Under Pressure', 'Customer Service', 'Ledger balancing', 'Balance allocation', 'Cash drawer maintenance','Project management', 'Teamwork', 'Time management', 'Risk management', 'Skilled at receiving and processing banking transactions', 'Strong mathematical skills', 'Attention to detail', 'Knowledge of proper cash handling procedures', 'Loan processing', 'Tax preparation', 'Petty cash management', 'Numeracy skills']

    
    job_applicants_data={}
    for job in jobs:
        for u in job.applicants.all():
            text = u.resumetxt.lower()
            section_info = {section: {'present': False, 'score': 0} for section in sections}

            total_score = 0
            for section, (keywords, score) in sections.items():
                for keyword in keywords:
                    if keyword in text:
                        section_info[section]['present'] = True
                        section_info[section]['score'] = score
                        total_score += score
                        break

            section_info['total_score'] = total_score
            
            word_list = re.findall(r'\b\w+\b', text)
            cnt1 = 0
            for word in word_list:
                w = word.lower()
                if w in cr1:
                    cnt1 += 1
                    u.skillstxt = w
                
            u.skills= cnt1
            user_ranking = cnt1 + total_score  # Combine CV and section scores
            ranking_percentage = (user_ranking / 90) * 100
            u.match=ranking_percentage
            u.save()


    return render(request, 'ATS.html', {'jobs': jobs,'allapplicants': usrs,'job_applicants_data':job_applicants_data})


def Communication(request):
    return render(request,'Communication.html')

def ALlJobs(request):
    usrs = UserProfile.objects.all()
    
    usrs = UserProfile.objects.all()
    jobs = Jobs.objects.all()
        
    return render(request, 'ALlJobs.html', {'jobs': jobs,'allapplicants': usrs})


def Jobposting(request):
    
    if request.method == 'POST':
        jobname = request.POST.get('jobname', '').strip()
        dobe = request.POST.get('dobe', '').strip()
        totalpeoplneed =  request.POST.get('end_time', '').strip()
        exp = request.POST.get('exp', '').strip()
        place = request.POST.get('place', '').strip()
        typ = request.POST.get('typ', '').strip()
        sector = request.POST.get('sector', '').strip()
        openings = request.POST.get('openings', '').strip()
        creteria1 = request.POST.get('creteria1', '').strip()
        creteria2 = request.POST.get('creteria2', '').strip()
        creteria3 = request.POST.get('creteria3', '').strip()
        creteria4 = request.POST.get('creteria4', '').strip()
        creteria5 = request.POST.get('creteria5', '').strip()
        about = request.POST.get('about', '').strip()
        
        # Create a new job posting
        Jobs.objects.create(
            
            jobname=jobname,
            dobe=dobe,
            totalpeoplneed=totalpeoplneed,
            exp=exp,
            place=place,
            typ=typ,
            sector=sector,
            openings=openings,
            creteria1=creteria1,
            creteria2=creteria2,
            creteria3=creteria3,
            creteria4=creteria4,
            creteria5=creteria5,
            about=about,
        )
        return redirect('indexr')
    else:
        return render(request, 'Jobposting.html')

def Shortlisted(request):
    usrs = UserProfile.objects.all()
    jobs = Jobs.objects.all()
    return render(request, 'Shortlisted.html', {'jobs': jobs,'allapplicants': usrs})

def sample(request):
    return render(request,'sample.html')

