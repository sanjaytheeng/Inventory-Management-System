# Generated by Django 5.0.2 on 2025-04-18 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_agent_record_origin_assignment_agent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='record_origin',
            field=models.CharField(choices=[('manual', 'Manual Entry'), ('assignment_form', 'Created from Assignment')], default='manual', help_text='Indicates how the agent record was created', max_length=50),
        ),
    ]
