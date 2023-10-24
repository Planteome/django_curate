# Generated by Django 3.2.7 on 2023-10-18 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0009_alter_annotationontologyterm_onto_term'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotationontologyterm',
            name='term_name',
            field=models.TextField(blank=True, help_text='Term name', max_length=1000, verbose_name='Ontology term name'),
        ),
    ]
