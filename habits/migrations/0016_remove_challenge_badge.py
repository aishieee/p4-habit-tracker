# Generated by Django 5.2.1 on 2025-06-16 00:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0015_challenge_badge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='badge',
        ),
    ]
