# Generated by Django 3.2.7 on 2021-10-28 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0002_auto_20211020_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='ontology_id',
            field=models.CharField(help_text='GO:0003993', max_length=16, verbose_name='Ontology ID'),
        ),
        migrations.AlterField(
            model_name='annotationapproval',
            name='ontology_id',
            field=models.CharField(help_text='GO:0003993', max_length=16, verbose_name='Ontology ID'),
        ),
        migrations.AlterField(
            model_name='historicalannotation',
            name='ontology_id',
            field=models.CharField(help_text='GO:0003993', max_length=16, verbose_name='Ontology ID'),
        ),
    ]