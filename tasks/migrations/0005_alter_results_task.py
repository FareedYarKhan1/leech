# Generated by Django 4.1.5 on 2023-01-25 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_alter_results_result_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='results',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task'),
        ),
    ]
