from djongo import models
from django.db import models as django_models

class UserProfile(models.Model):
    name = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=100, default='')
    passw = models.CharField(max_length=100, default='')
    email = models.EmailField(max_length=100, default='')
    dob = models.DateField(default=None)
    exp = models.CharField(max_length=100, default='0')

    POST = (
        ('Intern', 'Intern'),
        ('Cleark', 'Cleark'),
        # Add more post options as needed
    )
    post = models.CharField(max_length=13, choices=POST, default='')

    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other'),
    )
    gen = models.CharField(max_length=6, choices=GENDER_CHOICES, default='')

    applied = models.PositiveIntegerField(default=0)
    ad1 = models.CharField(max_length=100, default='')
    ad2 = models.CharField(max_length=100, default='')
    pho1 = models.CharField(max_length=100, default='0')
    pho2 = models.CharField(max_length=100, default='0')

    WORK = (
        ('Open to Work', 'Open to Work'),
        ('Viewer', 'Viewer'),
        # Add more work options as needed
    )
    work = models.CharField(max_length=13, choices=WORK, default='')
    edu = models.CharField(max_length=100, default='')
    per = models.CharField(max_length=100, default='')
    uni = models.CharField(max_length=100, default='')
    about = models.CharField(max_length=1000, default='')
    interviewres = models.CharField(max_length=1000, default='')

    # Use JSONField to store lists of references
    applied_jobs = models.JSONField(blank=True, default=list)
    applied_interview = models.JSONField(blank=True, default=list)

    ranking = models.IntegerField(default=0)
    skillstxt = models.TextField(default='')
    skills = models.IntegerField(default=0)
    match = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    interviewscore = models.IntegerField(default=0)
    hrreview = models.TextField(default='')
    resumetxt = models.TextField(default='')
    resume = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.username

    def append_to_applied_interview(self, interviews):
        
        if self.applied_interview is None:
            self.applied_interview = []
        self.applied_interview.append(interviews)
        self.save()

class InterviewQ(models.Model):
    questions_and_answers = models.JSONField(blank=True, default=dict)  # Store the dictionary of questions and answers
    video_blob = models.BinaryField(null=True)
    applicantid = models.CharField(max_length=100, default='0')
    jobid= models.CharField(max_length=100, default='0')    
    stuttfeature_names=models.CharField(max_length=100, default='0')    
    postureresults=models.JSONField(blank=True, default=dict)  
    analysis_resultpersonality=models.JSONField(blank=True, default=dict)  

    def __str__(self):
        return f"Interview {self.interview_id} at {self.timestamp}"



class UploadedFile(django_models.Model):
    file = django_models.FileField(upload_to='uploads/')
    uploaded_at = django_models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
