# Generated by Django 5.2.1 on 2025-06-14 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0006_alter_badge_slug_challenge_userchallenge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='badge_image',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='duration_days',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='required_habits',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='challenge',
            name='badge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='habits.badge'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='difficulty',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='end_date',
            field=models.DateField(default='2025-06-30'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='start_date',
            field=models.DateField(),
        ),
    ]
