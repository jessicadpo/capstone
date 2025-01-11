# Generated by Django 5.0.2 on 2025-01-06 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagme', '0003_alter_report_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='_subjects',
            field=models.TextField(blank=True, db_column='subjects', null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='authors',
            field=models.TextField(default='Unknown'),
        ),
        migrations.AddField(
            model_name='item',
            name='cover',
            field=models.TextField(blank=True, default=True),
        ),
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='No description available'),
        ),
        migrations.AddField(
            model_name='item',
            name='publication_date',
            field=models.TextField(default='No publication date available'),
        ),
        migrations.AddField(
            model_name='item',
            name='title',
            field=models.TextField(default='No title available'),
        ),
    ]
