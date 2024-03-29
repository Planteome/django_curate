# Generated by Django 3.2.7 on 2023-02-08 01:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0006_auto_20230207_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='ontology_term_link',
            field=models.ForeignKey(default=1, help_text='GO:0003993', on_delete=django.db.models.deletion.PROTECT, to='annotations.annotationontologyterm', verbose_name='Ontology ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='annotationapproval',
            name='ontology_term_link',
            field=models.ForeignKey(help_text='GO:0003993', on_delete=django.db.models.deletion.PROTECT, to='annotations.annotationontologyterm', verbose_name='Ontology ID'),
        ),
    ]
