# Generated by Django 5.2 on 2025-04-18 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mcq', '0008_profile_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='chain_length',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_chain_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
