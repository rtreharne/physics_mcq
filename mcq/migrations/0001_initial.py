# Generated by Django 5.2 on 2025-04-15 08:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExamBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'), ('hardcore', 'Hardcore')], default='medium', max_length=10)),
                ('question_text', models.TextField()),
                ('option_a', models.CharField(max_length=255)),
                ('option_b', models.CharField(max_length=255)),
                ('option_c', models.CharField(max_length=255)),
                ('option_d', models.CharField(max_length=255)),
                ('correct_option', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1)),
                ('explanation', models.TextField(blank=True)),
                ('exam_board', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mcq.examboard')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mcq.topic')),
            ],
        ),
    ]
