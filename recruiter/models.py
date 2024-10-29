from djongo import models
from datetime import datetime


def default_dobe():
    return datetime.now().date

def default_dobetime():
    return datetime.now().time
    
class Jobs(models.Model):
    # _id = models.ObjectIdField()  # Use ObjectIdField for MongoDB's ObjectId
    jobid = models.CharField(max_length=100, default='0')
    jobname = models.CharField(max_length=100)
    applied = models.PositiveIntegerField(default=0)
    dobe = models.DateField(default=default_dobe)
    totalpeoplneed = models.PositiveIntegerField(default=0)
    exp = models.CharField(max_length=100)
    place = models.CharField(max_length=100)

    TY = (
        ('p', 'Part Time'),
        ('f', 'Full Time'),
        ('i', 'Internship'),
    )
    typ = models.CharField(max_length=16, choices=TY, default='f')  # Set a meaningful default
    status = models.IntegerField(default=0)
    sector = models.CharField(max_length=100)
    openings = models.CharField(max_length=100)
    creteria1 = models.CharField(max_length=100)  # Corrected 'creteria' to 'criteria'
    creteria2 = models.CharField(max_length=100)
    creteria3 = models.CharField(max_length=100)
    creteria4 = models.CharField(max_length=100)
    creteria5 = models.CharField(max_length=100)
    about = models.TextField()
    
    # Use JSONField to store lists of references
    applicants = models.JSONField(blank=True, default=list)
    interview_applicants = models.JSONField(blank=True, default=list)  # Renamed for clarity
    shortlisted_applicants = models.JSONField(blank=True, default=list)  # Renamed for clarity
    interviewed = models.JSONField(blank=True, default=list)  # Renamed for clarity

    def append_interview_applicant(self, applicant):
        if self.interview_applicants is None:
            self.interview_applicants = []
        self.interview_applicants.append(applicant)
        self.save()

        
    def append_interviewed(self, applicant):
        if self.interviewed is None:
            self.interviewed = []
        self.interviewed.append(applicant)
        self.save()

    def __str__(self):
        return self.jobname



