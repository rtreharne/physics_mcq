# Generated by Django 5.2 on 2025-04-30 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mcq', '0014_alter_question_difficulty_quanta_quantamembership'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_num_questions',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='profile',
            name='default_time_per_question',
            field=models.FloatField(default=1.0),
        ),
    ]
