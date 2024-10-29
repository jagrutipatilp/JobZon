from django.contrib import admin
from django.urls import path
from . import views
from django.core.mail import send_mail
from django.http import HttpResponse
from django.urls import path
from .views import download_resume
from .views import contacts
urlpatterns = [
    path('', views.index,name='index'),
    path('index2', views.index2, name='index2'),
    path('checkprogress/<int:interview_id>/', views.check_progress, name='checkprogress'),
    path('contacts', views.contacts, name='contacts'),
    path('Guidlines', views.Guidlines,name='Guidlines'),
    path('jobs', views.jobs,name='jobs'),  
    path('initialque/', views.initialque, name='initialque'),
    path('get-next-question/', views.get_next_question, name='get_next_question'),
    path('submit_response/', views.submit_response, name='submit_response'),
    path('interviewapp/<int:job_id>/', views.interviewapp,name='interviewapp'),  
    path('apply_for_job/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('download_resume/<int:user_profile_id>/', download_resume, name='download_resume'),
    path('check_username/<str:username>/', views.check_username_availability, name='check_username'),
    path('signin', views.signin,name='signin'),
    path('signinrec', views.signinrec,name='signinrec'),
    path('signup', views.signup,name='signup'),
    path('StudenPrograms', views.StudenPrograms,name='StudenPrograms'),
    path('sample', views.sample,name='sample'),
    path('thankyou/', views.thankyou, name='thankyou'),
   ]