# Generated by Django 3.2.7 on 2023-02-08 01:35

from django.db import migrations


def link_onto_term(apps, schema_editor):
    Annotation = apps.get_model('annotations', 'Annotation')
    OntologyTerm = apps.get_model('annotations', 'AnnotationOntologyTerm')

    for annotation in Annotation.objects.all():
        onto_term, created = OntologyTerm.objects.get_or_create(onto_term=annotation.ontology_id)
        annotation.ontology_term_link = onto_term
        annotation.save()

class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0004_auto_20230207_1734'),
    ]

    operations = [
        migrations.RunPython(link_onto_term, reverse_code=migrations.RunPython.noop)
    ]
