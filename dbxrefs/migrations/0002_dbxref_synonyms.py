# Generated by Django 3.2.5 on 2021-09-08 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbxrefs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbxref',
            name='synonyms',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
