# Generated by Django 4.1.5 on 2023-01-25 08:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_alter_results_result_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
