# Generated by Django 5.2 on 2025-05-01 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mcq', '0017_alter_quizattempt_date_taken'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='accuracy_mean',
            field=models.FloatField(default=0.7),
        ),
        migrations.AddField(
            model_name='profile',
            name='accuracy_stddev',
            field=models.FloatField(default=0.1),
        ),
    ]
