# Generated by Django 5.0.2 on 2025-01-07 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagme', '0004_item__subjects_item_authors_item_cover_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercontribution',
            name='pin_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
