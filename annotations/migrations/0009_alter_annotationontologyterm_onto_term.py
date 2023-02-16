# Generated by Django 3.2.7 on 2023-02-10 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0008_auto_20230207_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationontologyterm',
            name='onto_term',
            field=models.CharField(help_text='GO:0003993', max_length=16, unique=True, verbose_name='Ontology ID'),
        ),
    ]