# Generated by Django 5.2 on 2025-04-15 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mcq', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='exam_board',
        ),
        migrations.AddField(
            model_name='question',
            name='exam_boards',
            field=models.ManyToManyField(blank=True, to='mcq.examboard'),
        ),
    ]
