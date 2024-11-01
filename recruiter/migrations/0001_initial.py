# Generated by Django 4.1.13 on 2024-10-28 17:36

from django.db import migrations, models
import djongo.models.fields
import recruiter.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jobid', models.CharField(default='0', max_length=100)),
                ('jobname', models.CharField(max_length=100)),
                ('applied', models.PositiveIntegerField(default=0)),
                ('dobe', models.DateField(default=recruiter.models.default_dobe)),
                ('totalpeoplneed', models.PositiveIntegerField(default=0)),
                ('exp', models.CharField(max_length=100)),
                ('place', models.CharField(max_length=100)),
                ('typ', models.CharField(choices=[('p', 'Part Time'), ('f', 'Full Time'), ('i', 'Internship')], default='f', max_length=16)),
                ('status', models.IntegerField(default=0)),
                ('sector', models.CharField(max_length=100)),
                ('openings', models.CharField(max_length=100)),
                ('creteria1', models.CharField(max_length=100)),
                ('creteria2', models.CharField(max_length=100)),
                ('creteria3', models.CharField(max_length=100)),
                ('creteria4', models.CharField(max_length=100)),
                ('creteria5', models.CharField(max_length=100)),
                ('about', models.TextField()),
                ('applicants', djongo.models.fields.JSONField(blank=True, default=list)),
                ('interview_applicants', djongo.models.fields.JSONField(blank=True, default=list)),
                ('shortlisted_applicants', djongo.models.fields.JSONField(blank=True, default=list)),
                ('interviewed', djongo.models.fields.JSONField(blank=True, default=list)),
            ],
        ),
    ]
